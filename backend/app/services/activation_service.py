"""
Activation Service - Multi-channel message delivery
Supports multiple testing modes for email and SMS
"""

import uuid
from datetime import datetime
from typing import Optional
from ..dependencies import get_workspace_client
from ..config import get_settings
from .providers import EmailProvider, SMSProvider

settings = get_settings()


class ActivationService:
    """Multi-channel activation service for email, SMS, push notifications"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    def send_email(
        self,
        customer_id: str,
        to_email: str,
        subject: str,
        body: str,
        campaign_id: Optional[str] = None,
        journey_id: Optional[str] = None,
        journey_step_id: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """Send email via configured provider (SendGrid, Mailtrap, MailHog, Console, etc.)"""
        delivery_id = f"del_{uuid.uuid4().hex}"
        
        # Send email using configured provider
        if scheduled_time and scheduled_time > datetime.now():
            # Schedule for later - just record in database
            sent = True
            status = "scheduled"
        else:
            # Send immediately
            sent = EmailProvider.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                from_email=settings.SENDGRID_FROM_EMAIL
            )
            status = "sent" if sent else "failed"
        
        # Record delivery in database
        campaign_val = "NULL" if not campaign_id else f"'{campaign_id}'"
        journey_val = "NULL" if not journey_id else f"'{journey_id}'"
        journey_step_val = "NULL" if not journey_step_id else f"'{journey_step_id}'"
        sent_at_val = "current_timestamp()" if not scheduled_time else f"timestamp('{scheduled_time.isoformat()}')"
        
        insert_query = f"""
            INSERT INTO cdp_platform.core.deliveries
            (delivery_id, tenant_id, customer_id, campaign_id, journey_id, journey_step_id,
             channel, sent_at, to_address, subject, message_preview, status)
            VALUES (
                '{delivery_id}',
                '{self.tenant_id}',
                '{customer_id}',
                {campaign_val},
                {journey_val},
                {journey_step_val},
                'email',
                {sent_at_val},
                '{to_email.replace("'", "''")}',
                '{subject.replace("'", "''")}',
                '{body[:100].replace("'", "''")}',
                '{status}'
            )
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=insert_query,
                wait_timeout=30
            )
        except Exception as e:
            print(f"Error recording email delivery: {e}")
            raise
        
        return delivery_id
    
    def send_sms(
        self,
        customer_id: str,
        to_phone: str,
        message: str,
        campaign_id: Optional[str] = None,
        journey_id: Optional[str] = None,
        journey_step_id: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """Send SMS via configured provider (Twilio, Twilio Test, Console, etc.)"""
        delivery_id = f"del_{uuid.uuid4().hex}"
        
        # Send SMS using configured provider
        if scheduled_time and scheduled_time > datetime.now():
            # Schedule for later - just record in database
            sent = True
            status = "scheduled"
        else:
            # Send immediately
            sent = SMSProvider.send_sms(
                to_phone=to_phone,
                message=message,
                from_number=settings.TWILIO_FROM_NUMBER
            )
            status = "sent" if sent else "failed"
        
        # Record delivery in database
        campaign_val = "NULL" if not campaign_id else f"'{campaign_id}'"
        journey_val = "NULL" if not journey_id else f"'{journey_id}'"
        journey_step_val = "NULL" if not journey_step_id else f"'{journey_step_id}'"
        sent_at_val = "current_timestamp()" if not scheduled_time else f"timestamp('{scheduled_time.isoformat()}')"
        
        insert_query = f"""
            INSERT INTO cdp_platform.core.deliveries
            (delivery_id, tenant_id, customer_id, campaign_id, journey_id, journey_step_id,
             channel, sent_at, to_address, message_preview, status)
            VALUES (
                '{delivery_id}',
                '{self.tenant_id}',
                '{customer_id}',
                {campaign_val},
                {journey_val},
                {journey_step_val},
                'sms',
                {sent_at_val},
                '{to_phone.replace("'", "''")}',
                '{message[:100].replace("'", "''")}',
                '{status}'
            )
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=insert_query,
                wait_timeout=30
            )
        except Exception as e:
            print(f"Error recording SMS delivery: {e}")
            raise
        
        return delivery_id

