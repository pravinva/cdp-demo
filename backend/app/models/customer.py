"""
Pydantic models for Customer entities
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal

class DeviceInfo(BaseModel):
    """Device information"""
    device_id: str
    device_family: str
    last_seen: datetime
    push_token: Optional[str] = None

class CustomerBase(BaseModel):
    """Base customer model"""
    email: EmailStr
    phone: Optional[str] = None
    first_name: str
    last_name: str
    segment: Optional[str] = None
    
class CustomerCreate(CustomerBase):
    """Customer creation model"""
    tenant_id: str
    
class CustomerUpdate(BaseModel):
    """Customer update model (all fields optional)"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    segment: Optional[str] = None
    preferred_channel: Optional[str] = None
    email_consent: Optional[bool] = None
    sms_consent: Optional[bool] = None
    push_consent: Optional[bool] = None

class Customer(CustomerBase):
    """Full customer model"""
    customer_id: str
    tenant_id: str
    match_id: Optional[str] = None
    
    # Profile
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    
    # Address
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    
    # Household
    household_id: Optional[str] = None
    household_role: Optional[str] = None
    
    # Segmentation
    lifecycle_stage: Optional[str] = None
    
    # Metrics
    lifetime_value: Optional[Decimal] = None
    total_purchases: int = 0
    total_spend: Optional[Decimal] = None
    avg_order_value: Optional[Decimal] = None
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    days_since_purchase: Optional[int] = None
    
    # Engagement
    email_engagement_score: Optional[float] = None
    sms_engagement_score: Optional[float] = None
    push_engagement_score: Optional[float] = None
    
    # ML Scores
    churn_risk_score: Optional[float] = None
    purchase_propensity_score: Optional[float] = None
    upsell_propensity_score: Optional[float] = None
    
    # Preferences
    preferred_channel: Optional[str] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None
    
    # Consent
    email_consent: bool = False
    sms_consent: bool = False
    push_consent: bool = False
    
    # Devices
    registered_devices: List[DeviceInfo] = []
    
    # System
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Customer360(BaseModel):
    """Complete customer 360 view"""
    profile: Customer
    recent_events: List[Dict]
    campaign_history: List[Dict]
    agent_decisions: List[Dict]
    household_members: Optional[List[Dict]] = None
    
class CustomerListResponse(BaseModel):
    """Customer list response"""
    customers: List[Customer]
    total: int
    page: int
    page_size: int

