"""
Activation Service - Multi-channel message delivery
"""

import uuid
from datetime import datetime
from typing import Optional
from pyspark.sql import SparkSession

from ..dependencies import get_spark_session
from ..config import get_settings

settings = get_settings()


class ActivationService:
    """Multi-channel activation service for email, SMS, push notifications"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.spark = get_spark_session()
    
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
        """Send email via SendGrid"""
        delivery_id = f"del_{uuid.uuid4().hex}"
        
        # In production, integrate with SendGrid
        # For now, just record in database
        self.spark.sql(f"""
            INSERT INTO cdp_platform.core.deliveries
            (delivery_id, tenant_id, customer_id, campaign_id, journey_id,
             channel, sent_at, to_address, subject, message_preview, status)
            VALUES (
                '{delivery_id}',
                '{self.tenant_id}',
                '{customer_id}',
                {'NULL' if not campaign_id else "'" + campaign_id + "'"},
                {'NULL' if not journey_id else "'" + journey_id + "'"},
                'email',
                {'current_timestamp()' if not scheduled_time else f"timestamp('{scheduled_time.isoformat()}')"},
                '{to_email}',
                '{subject.replace("'", "\\'")}',
                '{body[:100].replace("'", "\\'")}',
                'sent'
            )
        """)
        
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
        """Send SMS via Twilio"""
        delivery_id = f"del_{uuid.uuid4().hex}"
        
        # In production, integrate with Twilio
        # For now, just record in database
        self.spark.sql(f"""
            INSERT INTO cdp_platform.core.deliveries
            (delivery_id, tenant_id, customer_id, campaign_id, journey_id,
             channel, sent_at, to_address, message_preview, status)
            VALUES (
                '{delivery_id}',
                '{self.tenant_id}',
                '{customer_id}',
                {'NULL' if not campaign_id else "'" + campaign_id + "'"},
                {'NULL' if not journey_id else "'" + journey_id + "'"},
                'sms',
                {'current_timestamp()' if not scheduled_time else f"timestamp('{scheduled_time.isoformat()}')"},
                '{to_phone}',
                '{message[:100].replace("'", "\\'")}',
                'sent'
            )
        """)
        
        return delivery_id

