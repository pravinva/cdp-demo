"""
Agent Decision Models
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal

class ToolCall(BaseModel):
    """Agent tool call"""
    tool_name: str
    parameters: Dict
    result: Optional[str] = None

class AgentDecision(BaseModel):
    """Agent decision record"""
    decision_id: str
    tenant_id: str
    campaign_id: Optional[str] = None
    customer_id: str
    journey_id: Optional[str] = None
    journey_step_id: Optional[str] = None
    
    timestamp: datetime
    
    # Decision
    action: str  # "contact", "skip", "wait"
    channel: Optional[str] = None
    scheduled_send_time: Optional[datetime] = None
    
    # Generated content
    message_subject: Optional[str] = None
    message_body: Optional[str] = None
    call_to_action: Optional[str] = None
    
    # Reasoning
    reasoning_summary: str
    reasoning_details: Optional[str] = None
    tool_calls: List[ToolCall] = []
    confidence_score: float
    
    # Context used
    customer_segment: Optional[str] = None
    churn_risk: Optional[float] = None
    ltv: Optional[Decimal] = None
    days_since_last_contact: Optional[int] = None
    household_context: Optional[str] = None
    
    # Outcome (populated after delivery)
    delivery_id: Optional[str] = None
    delivered: bool = False
    opened: bool = False
    clicked: bool = False
    converted: bool = False
    conversion_value: Optional[Decimal] = None
    
    # System
    model_version: str
    execution_time_ms: int
    
    class Config:
        from_attributes = True

class AgentDecisionCreate(BaseModel):
    """Request to create agent decision"""
    campaign_id: Optional[str] = None
    customer_id: str
    journey_id: Optional[str] = None
    journey_step_id: Optional[str] = None

