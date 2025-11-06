"""
Agent Service - Core agent orchestration
Integrates with Databricks Agent Framework or simulates agent behavior
"""

import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from pyspark.sql import SparkSession

from ..models.decision import AgentDecision, ToolCall
from ..dependencies import get_spark_session
from ..config import get_settings
from .tools import AgentTools

settings = get_settings()


class AgentService:
    """
    Agent Service that orchestrates agent decisions
    For now, simulates agent behavior (can be replaced with Databricks Agent Framework)
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.spark = get_spark_session()
        self.tools = AgentTools(tenant_id)
    
    def analyze_and_decide(
        self,
        customer_id: str,
        campaign_id: Optional[str] = None,
        journey_id: Optional[str] = None,
        journey_step_id: Optional[str] = None,
        agent_instructions: Optional[str] = None,
        channels: Optional[List[str]] = None
    ) -> AgentDecision:
        """
        Analyze customer and make decision
        Returns AgentDecision with action, reasoning, and generated content
        """
        start_time = time.time()
        
        # Gather context using tools
        tool_calls = []
        
        # 1. Get customer context
        customer_context = self.tools.get_customer_context(customer_id)
        tool_calls.append(ToolCall(
            tool_name="get_customer_context",
            parameters={"customer_id": customer_id},
            result=str(customer_context)
        ))
        
        if customer_context.get("error"):
            # Customer not found
            return self._create_decision(
                customer_id=customer_id,
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                action="skip",
                reasoning_summary="Customer not found",
                confidence_score=1.0,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # 2. Check communication fatigue
        fatigue = self.tools.get_communication_fatigue(customer_id)
        tool_calls.append(ToolCall(
            tool_name="get_communication_fatigue",
            parameters={"customer_id": customer_id},
            result=str(fatigue)
        ))
        
        # 3. Check consent
        email_consent = customer_context.get('email_consent', False)
        sms_consent = customer_context.get('sms_consent', False)
        
        # Decision logic (simplified - in production use actual LLM)
        is_fatigued = fatigue.get('is_fatigued', False)
        messages_last_7d = fatigue.get('messages_last_7d', 0)
        
        # Determine action
        if is_fatigued or messages_last_7d > 3:
            action = "skip"
            reasoning = f"Customer is fatigued (messages_last_7d={messages_last_7d})"
        elif not email_consent and not sms_consent:
            action = "skip"
            reasoning = "Customer has no consent for any channel"
        else:
            # Decide to contact
            action = "contact"
            
            # Choose channel
            preferred_channel = customer_context.get('preferred_channel', 'email')
            if preferred_channel in (channels or ['email']):
                channel = preferred_channel
            elif channels:
                channel = channels[0]
            else:
                channel = 'email' if email_consent else 'sms'
            
            # Generate personalized content (simplified)
            first_name = customer_context.get('first_name', 'Customer')
            segment = customer_context.get('segment', '')
            churn_risk = customer_context.get('churn_risk_score', 0.5)
            
            if channel == 'email':
                subject = f"We miss you, {first_name}!"
                body = self._generate_email_body(customer_context, segment, churn_risk)
                reasoning = f"Customer has good engagement scores. Personalized email sent via {channel}."
            else:
                subject = None
                body = f"Hi {first_name}, we have a special offer for you!"
                reasoning = f"Customer prefers SMS. Sending personalized SMS via {channel}."
        else:
            action = "skip"
            reasoning = "Customer context analysis suggests skipping"
        
        # Create decision record
        decision = self._create_decision(
            customer_id=customer_id,
            campaign_id=campaign_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            action=action,
            channel=channel if action == 'contact' else None,
            message_subject=subject if action == 'contact' else None,
            message_body=body if action == 'contact' else None,
            reasoning_summary=reasoning,
            reasoning_details=f"Customer segment: {segment}, Churn risk: {churn_risk}, Fatigue: {is_fatigued}",
            tool_calls=tool_calls,
            confidence_score=0.85,
            customer_segment=segment,
            churn_risk=churn_risk,
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        
        # If action is contact, trigger activation service
        if action == 'contact' and channel:
            from ..services.activation_service import ActivationService
            activation_service = ActivationService(self.tenant_id)
            
            if channel == 'email':
                delivery_id = activation_service.send_email(
                    customer_id=customer_id,
                    to_email=customer_context.get('email'),
                    subject=subject,
                    body=body,
                    campaign_id=campaign_id,
                    journey_id=journey_id,
                    journey_step_id=journey_step_id
                )
            elif channel == 'sms':
                delivery_id = activation_service.send_sms(
                    customer_id=customer_id,
                    to_phone=customer_context.get('phone'),
                    message=body,
                    campaign_id=campaign_id,
                    journey_id=journey_id,
                    journey_step_id=journey_step_id
                )
            else:
                delivery_id = None
            
            # Update decision with delivery_id
            if delivery_id:
                decision.delivery_id = delivery_id
                decision.delivered = True
        
        # Save decision to database
        self._save_decision(decision)
        
        return decision
    
    def _generate_email_body(self, customer_context: Dict, segment: str, churn_risk: float) -> str:
        """Generate personalized email body"""
        first_name = customer_context.get('first_name', 'Customer')
        
        if churn_risk > 0.6:
            return f"""Hi {first_name},

We noticed you haven't shopped with us recently, and we wanted to reach out personally.

As a valued {segment} customer, we'd love to have you back. Here's a special 20% discount on your next purchase.

Use code: WELCOMEBACK20

Thank you for being part of our community!

Best regards,
The Team"""
        else:
            return f"""Hi {first_name},

We have some exciting new products that we think you'll love!

Check them out and enjoy 15% off your next order.

Shop now: [link]

Best regards,
The Team"""
    
    def _create_decision(
        self,
        customer_id: str,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        journey_step_id: Optional[str],
        action: str,
        channel: Optional[str] = None,
        message_subject: Optional[str] = None,
        message_body: Optional[str] = None,
        reasoning_summary: str = "",
        reasoning_details: Optional[str] = None,
        tool_calls: List[ToolCall] = None,
        confidence_score: float = 0.0,
        customer_segment: Optional[str] = None,
        churn_risk: Optional[float] = None,
        execution_time_ms: int = 0
    ) -> AgentDecision:
        """Create AgentDecision object"""
        
        decision_id = f"dec_{uuid.uuid4().hex}"
        
        return AgentDecision(
            decision_id=decision_id,
            tenant_id=self.tenant_id,
            campaign_id=campaign_id,
            customer_id=customer_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            timestamp=datetime.now(),
            action=action,
            channel=channel,
            message_subject=message_subject,
            message_body=message_body,
            reasoning_summary=reasoning_summary,
            reasoning_details=reasoning_details,
            tool_calls=tool_calls or [],
            confidence_score=confidence_score,
            customer_segment=customer_segment,
            churn_risk=churn_risk,
            model_version=settings.AGENT_MODEL,
            execution_time_ms=execution_time_ms
        )
    
    def _save_decision(self, decision: AgentDecision):
        """Save decision to database"""
        tool_calls_json = "["
        for i, tc in enumerate(decision.tool_calls):
            if i > 0:
                tool_calls_json += ","
            tool_calls_json += f"{{'tool_name': '{tc.tool_name}', 'parameters': '{tc.parameters}', 'result': '{tc.result or ''}'}}"
        tool_calls_json += "]"
        
        self.spark.sql(f"""
            INSERT INTO cdp_platform.core.agent_decisions
            (decision_id, tenant_id, campaign_id, customer_id, journey_id, timestamp,
             action, channel, message_subject, message_body, reasoning_summary,
             reasoning_details, confidence_score, customer_segment, churn_risk,
             model_version, execution_time_ms)
            VALUES (
                '{decision.decision_id}',
                '{self.tenant_id}',
                {'NULL' if not decision.campaign_id else "'" + decision.campaign_id + "'"},
                '{decision.customer_id}',
                {'NULL' if not decision.journey_id else "'" + decision.journey_id + "'"},
                current_timestamp(),
                '{decision.action}',
                {'NULL' if not decision.channel else "'" + decision.channel + "'"},
                {'NULL' if not decision.message_subject else "'" + decision.message_subject.replace("'", "\\'") + "'"},
                {'NULL' if not decision.message_body else "'" + decision.message_body.replace("'", "\\'") + "'"},
                '{decision.reasoning_summary.replace("'", "\\'")}',
                {'NULL' if not decision.reasoning_details else "'" + decision.reasoning_details.replace("'", "\\'") + "'"},
                {decision.confidence_score},
                {'NULL' if not decision.customer_segment else "'" + decision.customer_segment + "'"},
                {'NULL' if not decision.churn_risk else str(decision.churn_risk)},
                '{decision.model_version}',
                {decision.execution_time_ms}
            )
        """)

