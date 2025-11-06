"""Campaign models"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    goal: str
    agent_mode: bool = True
    agent_instructions: Optional[str] = None
    channels: List[str] = ["email"]

class CampaignCreate(CampaignBase):
    tenant_id: str
    target_segment: Optional[str] = None
    audience_filter: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Campaign(CampaignBase):
    campaign_id: str
    tenant_id: str
    status: str
    target_segment: Optional[str] = None
    estimated_audience_size: Optional[int] = None
    customers_targeted: int = 0
    messages_sent: int = 0
    messages_delivered: int = 0
    messages_opened: int = 0
    conversions: int = 0
    revenue_attributed: Optional[Decimal] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    total_cost: Optional[Decimal] = None
    roas: Optional[float] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

