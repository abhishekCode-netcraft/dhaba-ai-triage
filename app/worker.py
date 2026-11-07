
import asyncio
import json
import logging
import time

from app.database import get_connection, init_db
from app.queue import (
    get_next_job,
    save_result,
    mark_failed
)
from app.schemas import Ticket
from app.triage import process_ticket


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("dhaba.worker")

async def process_job(job):
    ticket_id = job["ticket_id"]

    try:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT ticket_data
                FROM tickets
                WHERE id = ?
                """,
                (ticket_id,)
            ).fetchone()

        if not row:
            raise ValueError("Ticket record not found")

        ticket_data = json.loads(row["ticket_data"])
        ticket = Ticket(**ticket_data)

        result = await process_ticket(ticket)

        save_result(
            ticket_id,
            result.model_dump()
        )

        logger.info(
            "Ticket processed",
            extra={
                "ticket_id": ticket_id,
                "needs_human": result.needs_human
            }
        )

    except Exception as exc:
        # Do not log exception messages because they may
        # contain customer data from upstream errors.
        mark_failed(
            ticket_id,
            type(exc).__name__
        )

        logger.error(
            "Ticket processing failed",
            extra={
                "ticket_id": ticket_id,
                "error_type": type(exc).__name__
            }
        )


async def run_worker():

    init_db()

    logger.info("Dhaba worker started")

    while True:

        job = get_next_job()

        if job is None:
            await asyncio.sleep(1)
            continue

        await process_job(job)


if __name__ == "__main__":

    try:
        asyncio.run(run_worker())

    except KeyboardInterrupt:
        logger.info("Worker stopped")
