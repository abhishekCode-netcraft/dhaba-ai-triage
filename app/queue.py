
import json

from app.database import get_connection

def enqueue_ticket(ticket_data: dict):
    ticket_id = ticket_data["id"]

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, status FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        if existing:
            return {
                "ticket_id": ticket_id,
                "status": existing["status"],
                "duplicate": True
            }

        conn.execute(
            """
            INSERT INTO tickets (id, ticket_data, status)
            VALUES (?, ?, 'pending')
            """,
            (
                ticket_id,
                json.dumps(ticket_data, ensure_ascii=False)
            )
        )

        conn.execute(
            """
            INSERT INTO jobs (ticket_id, status)
            VALUES (?, 'pending')
            """,
            (ticket_id,)
        )

        conn.execute(
            """
            INSERT INTO processing_events
            (ticket_id, event_type, status)
            VALUES (?, 'ticket_received', 'success')
            """,
            (ticket_id,)
        )

    return {
        "ticket_id": ticket_id,
        "status": "pending",
        "duplicate": False
    }


def get_next_job():

    with get_connection() as conn:

        # Reserve one job atomically.
        conn.execute("BEGIN IMMEDIATE")

        job = conn.execute(
            """
            SELECT id, ticket_id
            FROM jobs
            WHERE status = 'pending'
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if not job:
            return None

        conn.execute(
            """
            UPDATE jobs
            SET status = 'processing',
                attempts = attempts + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (job["id"],)
        )

        conn.execute(
            """
            UPDATE tickets
            SET status = 'processing'
            WHERE id = ?
            """,
            (job["ticket_id"],)
        )

        return dict(job)


def save_result(ticket_id: str, result: dict):

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO triage_results (ticket_id, result)
            VALUES (?, ?)
            """,
            (
                ticket_id,
                json.dumps(result, ensure_ascii=False)
            )
        )

        conn.execute(
            """
            UPDATE jobs
            SET status = 'completed',
                error = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        )

        conn.execute(
            """
            UPDATE tickets
            SET status = 'completed'
            WHERE id = ?
            """,
            (ticket_id,)
        )

        conn.execute(
            """
            INSERT INTO processing_events
            (ticket_id, event_type, status)
            VALUES (?, 'triage_completed', 'success')
            """,
            (ticket_id,)
        )


def mark_failed(ticket_id: str, error_type: str):

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE jobs
            SET status = 'failed',
                error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
            """,
            (error_type, ticket_id)
        )

        conn.execute(
            """
            UPDATE tickets
            SET status = 'failed'
            WHERE id = ?
            """,
            (ticket_id,)
        )

        conn.execute(
            """
            INSERT INTO processing_events
            (ticket_id, event_type, status)
            VALUES (?, 'triage_failed', 'failed')
            """,
            (ticket_id,)
        )


def get_ticket_status(ticket_id: str):

    with get_connection() as conn:

        ticket = conn.execute(
            """
            SELECT id, status, created_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if not ticket:
            return None

        job = conn.execute(
            """
            SELECT attempts, error
            FROM jobs
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        result = conn.execute(
            """
            SELECT result
            FROM triage_results
            WHERE ticket_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (ticket_id,)
        ).fetchone()

        return {
            "ticket_id": ticket["id"],
            "status": ticket["status"],
            "attempts": job["attempts"],
            "error": job["error"],
            "result": json.loads(result["result"]) if result else None
        }
