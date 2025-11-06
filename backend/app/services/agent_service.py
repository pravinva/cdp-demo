"""
Agent Service - Core agent orchestration
Integrates with Databricks Agent Framework using Foundation Model APIs
"""

import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..models.decision import AgentDecision, ToolCall
from ..dependencies import get_workspace_client
from ..config import get_settings
from ..agents.tools import AgentTools
from ..agents.databricks_agent import DatabricksAgent

settings = get_settings()


class AgentService:
    """
    Agent Service that orchestrates agent decisions
    Uses Databricks Foundation Model API for AI-powered decision making
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.warehouse_id = self.settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
        self.tools = AgentTools(tenant_id)
        # Use real Databricks Agent Framework
        self.agent = DatabricksAgent(tenant_id)
    
    def analyze_and_decide(
        self,
        customer_id: str,
        campaign_id: Optional[str] = None,
        journey_id: Optional[str] = None,
        journey_step_id: Optional[str] = None,
        agent_instructions: Optional[str] = None,
        channels: Optional[List[str]] = None,
        campaign_goal: Optional[str] = None
    ) -> AgentDecision:
        """
        Analyze customer and make decision using Databricks Agent Framework
        Returns AgentDecision with action, reasoning, and generated content
        """
        # Use Databricks Agent Framework
        decision = self.agent.analyze_and_decide(
            customer_id=customer_id,
            campaign_id=campaign_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            agent_instructions=agent_instructions,
            channels=channels,
            campaign_goal=campaign_goal
        )
        
        # If action is contact, trigger activation service
        if decision.action == 'contact' and decision.channel:
            from ..services.activation_service import ActivationService
            activation_service = ActivationService(self.tenant_id)
            
            # Get customer context for email/phone
            customer_context = self.tools.get_customer_context(customer_id)
            
            if decision.channel == 'email':
                delivery_id = activation_service.send_email(
                    customer_id=customer_id,
                    to_email=customer_context.get('email'),
                    subject=decision.message_subject,
                    body=decision.message_body,
                    campaign_id=campaign_id,
                    journey_id=journey_id,
                    journey_step_id=journey_step_id
                )
            elif decision.channel == 'sms':
                delivery_id = activation_service.send_sms(
                    customer_id=customer_id,
                    to_phone=customer_context.get('phone'),
                    message=decision.message_body,
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
        import json
        
        # Serialize tool_calls to JSON
        tool_calls_list = []
        for tc in decision.tool_calls:
            tool_calls_list.append({
                'tool_name': tc.tool_name,
                'parameters': tc.parameters,
                'result': tc.result or ''
            })
        tool_calls_json = json.dumps(tool_calls_list).replace("'", "''")
        
        # Escape single quotes in strings
        message_subject = decision.message_subject.replace("'", "''") if decision.message_subject else None
        message_body = decision.message_body.replace("'", "''") if decision.message_body else None
        reasoning_summary = decision.reasoning_summary.replace("'", "''") if decision.reasoning_summary else ""
        reasoning_details = decision.reasoning_details.replace("'", "''") if decision.reasoning_details else None
        
        insert_query = f"""
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
                {'NULL' if not message_subject else "'" + message_subject + "'"},
                {'NULL' if not message_body else "'" + message_body + "'"},
                '{reasoning_summary}',
                {'NULL' if not reasoning_details else "'" + reasoning_details + "'"},
                {decision.confidence_score},
                {'NULL' if not decision.customer_segment else "'" + decision.customer_segment + "'"},
                {'NULL' if decision.churn_risk is None else str(decision.churn_risk)},
                '{decision.model_version}',
                {decision.execution_time_ms}
            )
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=insert_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error saving decision: {e}")

