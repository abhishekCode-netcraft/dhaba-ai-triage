import asyncio
import json

from app.schemas import Ticket
from app.triage import process_ticket

async def evaluate_tickets():

    with open("data/dhaba_tickets.json", "r") as file:
        data = json.load(file)
 
    tickets = data["tickets"]

    results = []

    for ticket_data in tickets:

        ticket = Ticket(**ticket_data)

        result = await process_ticket(ticket)

        results.append({
            "ticket_id": ticket.id,
            "category": result['category'],
            "severity": result['serverity'],
            # "refund": result.refund.model_dump(),
            "needs_human": result['need_human'],
            "confidence": result['confidence'],
            "reply_draft": result['reply_draft'],
        })

        print(f"Processed: {ticket.id}")

    with open("data/evaluation_results.json", "w") as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\nEvaluation completed!")
    print(f"Total tickets: {len(results)}")


if __name__ == "__main__":
    asyncio.run(evaluate_tickets())