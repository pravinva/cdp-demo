"""
Delivery Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Delivery(BaseModel):
    """Message delivery record"""
    delivery_id: str
    tenant_id: str
    decision_id: Optional[str] = None
    customer_id: str
    campaign_id: Optional[str] = None
    journey_id: Optional[str] = None
    journey_step_id: Optional[str] = None
    
    channel: str
    sent_at: datetime
    
    # Recipient
    to_address: str
    
    # Content
    subject: Optional[str] = None
    message_preview: Optional[str] = None
    
    # Status
    status: str
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    
    # Engagement
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    conversion_value: Optional[Decimal] = None
    
    # Cost
    cost_usd: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

