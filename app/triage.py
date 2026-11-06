
from app.schemas import Ticket, TriageResult
from app.model import generate_triage
from app.refund_policy import calculate_refund

async def process_ticket(ticket: Ticket) -> TriageResult:
    
    try:
        # Step 1: Ask AI to classify the ticket
        ai_result = await generate_triage(
            ticket.model_dump()
        )

        # Step 2: Validate AI output
        # result = TriageResult(
        #     **{
        #         **ai_result,
        #         "refund": calculate_refund(ticket)
        #     }
        # )

        # # Step 3: Require human review for uncertain cases
        # if result.confidence < 0.70:
        #     result.need_human = True

        return ai_result

    except Exception:

        # Step 4: Safe fallback if AI fails
        return TriageResult(
            category="other",
            severity="medium",
            refund=calculate_refund(ticket),
            reply_draft=(
                "Thank you for contacting Dhaba. "
                "Our support team will review your "
                "request and get back to you."
            ),
            needs_human=True,
            confidence=0.0,
        )