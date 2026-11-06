from app.schemas import RefundDecision, Ticket


def calculate_refund(ticket: Ticket) -> RefundDecision:

    successful_payments = [
        payment
        for payment in ticket.purchases
        if payment.status == "successful"
    ]

    if not successful_payments:
        return RefundDecision(
            eligible=False,
            amount_inr=0,
            reason="No successful payment found."
        )

    # Refunds require human approval in this assignment.
    # We only calculate the maximum amount that could
    # be considered for review.

    latest_payment = successful_payments[-1]

    return RefundDecision(
        eligible=False,
        amount_inr=0,
        reason=(
            f"Latest successful payment was "
            f"₹{latest_payment.amount_inr}. "
            "Refund eligibility requires policy review."
        )
    )