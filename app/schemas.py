from typing import Literal
from pydantic import BaseModel, Field

TicketCategory = Literal[
    'billing_issue',
    'refund',
    'payment_issue',
    'technical_issue',
    'product_question',
    'fraud'
]

Servirity = Literal[
    'Low',
    'Medium',
    'High',
    'Critical'
]

class Purchase(BaseModel):
    id:str
    type: Literal[
        'trial',
        'renewal'
    ]
    amount_inr: int
    status: Literal[
        'pending',
        "initaite",
        'successful',
        'failed'
    ]
    at:str

class Ticket(BaseModel):
    id:str
    received_at:str
    subject:str
    body:str
    purchases:list[Purchase]

class RefundDecision(BaseModel):
    eligible:bool
    amount_inr:int
    reason:str

class TriageResult(BaseModel):
    category: TicketCategory
    serverity: Servirity
    # refund: RefundDecision
    reply_draft: str
    need_human:bool
    confidence: float