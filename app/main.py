from fastapi import FastAPI
from app.schemas import Ticket, TriageResult
from app.triage import process_ticket
from app.queue import enqueue_ticket, get_ticket_status
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Dhaba AI Triage Service",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post(
    "/triage",
    response_model=TriageResult
)
async def triage_ticket(ticket: Ticket):
    result = await process_ticket(ticket)
    return result

# New asynchronous submission endpoint
@app.post("/triage/submit")
async def submit_ticket(ticket: Ticket):
    result = enqueue_ticket(ticket.model_dump())

    return JSONResponse(
        status_code=202 if not result["duplicate"] else 200,
        content={
            **result,
            "message": (
                "Ticket already exists."
                if result["duplicate"]
                else "Ticket received and queued for processing."
            )
        }
    )


# Check processing status
@app.get("/triage/{ticket_id}")
async def ticket_status(ticket_id: str):

    result = get_ticket_status(ticket_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return result