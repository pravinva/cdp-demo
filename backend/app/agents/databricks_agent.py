"""
Databricks Agent Framework Integration
Uses Databricks Foundation Model API for AI-powered decision making
"""

import json
import time
import os
from typing import Optional, List, Dict, Any
from databricks.sdk import WorkspaceClient
from openai import OpenAI
from ..dependencies import get_workspace_client
from ..config import get_settings
from ..agents.tools import AgentTools
from ..agents.prompts import MARKETING_AGENT_SYSTEM_PROMPT, get_campaign_specific_prompt
from ..models.decision import AgentDecision, ToolCall

settings = get_settings()


class DatabricksAgent:
    """
    Real Databricks Agent using Foundation Model API
    Uses chat completions with tool calling capabilities
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.tools = AgentTools(tenant_id)
        self.model = settings.AGENT_MODEL  # Configurable via AGENT_MODEL in config
        
        # Initialize OpenAI client for Databricks Foundation Model API
        # Uses OpenAI-compatible API endpoint
        databricks_host = settings.DATABRICKS_HOST or os.environ.get("DATABRICKS_HOST")
        databricks_token = settings.DATABRICKS_TOKEN or os.environ.get("DATABRICKS_TOKEN")
        
        if databricks_host and databricks_token:
            # Use explicit credentials
            self.client = OpenAI(
                api_key=databricks_token,
                base_url=f"{databricks_host}/serving-endpoints"
            )
        else:
            # Try to get from workspace client config
            # Databricks SDK will use ~/.databrickscfg
            try:
                # Get host from workspace client
                host = self.w.config.host if hasattr(self.w.config, 'host') else None
                token = self.w.config.token if hasattr(self.w.config, 'token') else None
                
                if host and token:
                    self.client = OpenAI(
                        api_key=token,
                        base_url=f"{host}/serving-endpoints"
                    )
                else:
                    # Fallback: will use environment or ~/.databrickscfg
                    self.client = None
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
    
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
        Use Databricks Foundation Model API to analyze customer and make decision
        """
        start_time = time.time()
        
        # Build system prompt
        system_prompt = MARKETING_AGENT_SYSTEM_PROMPT
        if campaign_goal:
            system_prompt = get_campaign_specific_prompt(campaign_goal, agent_instructions)
        
        # Gather initial context using tools
        tool_calls = []
        customer_context = self.tools.get_customer_context(customer_id)
        tool_calls.append(ToolCall(
            tool_name="get_customer_context",
            parameters={"customer_id": customer_id},
            result=str(customer_context)
        ))
        
        if customer_context.get("error"):
            return self._create_skip_decision(
                customer_id=customer_id,
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                reasoning="Customer not found",
                tool_calls=tool_calls,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Check fatigue
        fatigue = self.tools.get_communication_fatigue(customer_id)
        tool_calls.append(ToolCall(
            tool_name="get_communication_fatigue",
            parameters={"customer_id": customer_id},
            result=str(fatigue)
        ))
        
        # Build user message with context
        user_message = self._build_user_message(
            customer_id=customer_id,
            customer_context=customer_context,
            fatigue=fatigue,
            campaign_id=campaign_id,
            journey_id=journey_id,
            channels=channels
        )
        
        # Call Databricks Foundation Model API
        try:
            decision = self._call_foundation_model(
                system_prompt=system_prompt,
                user_message=user_message,
                customer_id=customer_id,
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                tool_calls=tool_calls,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            return decision
        except Exception as e:
            print(f"Error calling foundation model: {e}")
            # Fallback to rule-based decision
            return self._fallback_decision(
                customer_id=customer_id,
                customer_context=customer_context,
                fatigue=fatigue,
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                tool_calls=tool_calls,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _call_foundation_model(
        self,
        system_prompt: str,
        user_message: str,
        customer_id: str,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        journey_step_id: Optional[str],
        tool_calls: List[ToolCall],
        execution_time_ms: int
    ) -> AgentDecision:
        """
        Call Databricks Foundation Model API (Llama 70B) for decision making
        Model is configurable via AGENT_MODEL in config file
        """
        
        if not self.client:
            print("Warning: OpenAI client not initialized, using fallback decision")
            return self._fallback_decision(
                customer_id=customer_id,
                customer_context={},
                fatigue={},
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                tool_calls=tool_calls,
                execution_time_ms=execution_time_ms
            )
        
        try:
            # Call Databricks Foundation Model API using OpenAI-compatible interface
            # Model name is configurable via AGENT_MODEL setting
            response = self.client.chat.completions.create(
                model=self.model,  # e.g., "databricks-meta-llama-3-1-70b-instruct"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.settings.AGENT_TEMPERATURE,
                max_tokens=2000,
                response_format={"type": "json_object"}  # Request JSON response
            )
            
            # Extract response content
            decision_text = response.choices[0].message.content
            
            # Parse decision from LLM response
            return self._parse_decision_response(
                decision_text=decision_text,
                customer_id=customer_id,
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                tool_calls=tool_calls,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            print(f"Error calling Foundation Model API: {e}")
            # Fallback to rule-based decision
            return self._fallback_decision(
                customer_id=customer_id,
                customer_context={},
                fatigue={},
                campaign_id=campaign_id,
                journey_id=journey_id,
                journey_step_id=journey_step_id,
                tool_calls=tool_calls,
                execution_time_ms=execution_time_ms
            )
    
    def _build_user_message(
        self,
        customer_id: str,
        customer_context: Dict,
        fatigue: Dict,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        channels: Optional[List[str]]
    ) -> str:
        """Build user message for LLM"""
        
        message = f"""Analyze this customer and make a decision:

Customer ID: {customer_id}
Segment: {customer_context.get('segment', 'Unknown')}
Churn Risk: {customer_context.get('churn_risk_score', 0.5)}
LTV: ${customer_context.get('lifetime_value', 0)}
Email Consent: {customer_context.get('email_consent', False)}
SMS Consent: {customer_context.get('sms_consent', False)}
Preferred Channel: {customer_context.get('preferred_channel', 'email')}
Messages Last 7 Days: {fatigue.get('messages_last_7d', 0)}
Is Fatigued: {fatigue.get('is_fatigued', False)}
"""
        
        if campaign_id:
            message += f"\nCampaign ID: {campaign_id}"
        if journey_id:
            message += f"\nJourney ID: {journey_id}"
        if channels:
            message += f"\nAvailable Channels: {', '.join(channels)}"
        
        message += "\n\nMake a decision: Should we contact this customer? If yes, choose channel and generate personalized content."
        message += "\n\nReturn your decision as a JSON object with the following structure:"
        message += '\n{\n  "action": "contact" or "skip",\n  "channel": "email" or "sms" (if action is contact),'
        message += '\n  "reasoning": "Your reasoning for this decision",\n  "subject": "Email subject" (if email),'
        message += '\n  "body": "Message body"\n}'
        
        return message
    
    def _parse_llm_response(self, user_message: str) -> str:
        """Parse LLM response (simplified - in production would parse actual JSON)"""
        # This is a placeholder - in production, the LLM would return structured JSON
        # For now, return a decision format
        return json.dumps({
            "action": "contact",
            "channel": "email",
            "reasoning": "Customer analysis indicates good engagement opportunity",
            "subject": "Personalized offer",
            "body": "Hi there, we have something special for you!"
        })
    
    def _parse_decision_response(
        self,
        decision_text: str,
        customer_id: str,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        journey_step_id: Optional[str],
        tool_calls: List[ToolCall],
        execution_time_ms: int
    ) -> AgentDecision:
        """Parse LLM decision response into AgentDecision"""
        
        try:
            decision_json = json.loads(decision_text)
        except:
            # If not JSON, create a basic decision
            decision_json = {"action": "skip", "reasoning": decision_text}
        
        action = decision_json.get("action", "skip")
        channel = decision_json.get("channel") if action == "contact" else None
        subject = decision_json.get("subject") if action == "contact" else None
        body = decision_json.get("body") if action == "contact" else None
        reasoning = decision_json.get("reasoning", "AI decision")
        
        return self._create_decision(
            customer_id=customer_id,
            campaign_id=campaign_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            action=action,
            channel=channel,
            message_subject=subject,
            message_body=body,
            reasoning_summary=reasoning,
            reasoning_details=decision_text,
            tool_calls=tool_calls,
            confidence_score=0.9,
            execution_time_ms=execution_time_ms
        )
    
    def _fallback_decision(
        self,
        customer_id: str,
        customer_context: Dict,
        fatigue: Dict,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        journey_step_id: Optional[str],
        tool_calls: List[ToolCall],
        execution_time_ms: int
    ) -> AgentDecision:
        """Fallback rule-based decision if LLM fails"""
        
        is_fatigued = fatigue.get('is_fatigued', False)
        messages_last_7d = fatigue.get('messages_last_7d', 0)
        email_consent = customer_context.get('email_consent', False)
        sms_consent = customer_context.get('sms_consent', False)
        
        if is_fatigued or messages_last_7d > 3:
            action = "skip"
            reasoning = f"Customer is fatigued (messages_last_7d={messages_last_7d})"
        elif not email_consent and not sms_consent:
            action = "skip"
            reasoning = "Customer has no consent for any channel"
        else:
            action = "contact"
            channel = 'email' if email_consent else 'sms'
            reasoning = f"Customer has consent and is not fatigued. Contacting via {channel}."
        
        return self._create_decision(
            customer_id=customer_id,
            campaign_id=campaign_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            action=action,
            channel=channel if action == 'contact' else None,
            message_subject=None,
            message_body=None,
            reasoning_summary=reasoning,
            reasoning_details="Fallback rule-based decision",
            tool_calls=tool_calls,
            confidence_score=0.7,
            execution_time_ms=execution_time_ms
        )
    
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
        execution_time_ms: int = 0
    ) -> AgentDecision:
        """Create AgentDecision object"""
        import uuid
        from datetime import datetime
        
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
            customer_segment=None,
            churn_risk=None,
            model_version=self.model,
            execution_time_ms=execution_time_ms
        )
    
    def _create_skip_decision(
        self,
        customer_id: str,
        campaign_id: Optional[str],
        journey_id: Optional[str],
        journey_step_id: Optional[str],
        reasoning: str,
        tool_calls: List[ToolCall],
        execution_time_ms: int
    ) -> AgentDecision:
        """Create a skip decision"""
        return self._create_decision(
            customer_id=customer_id,
            campaign_id=campaign_id,
            journey_id=journey_id,
            journey_step_id=journey_step_id,
            action="skip",
            reasoning_summary=reasoning,
            tool_calls=tool_calls,
            confidence_score=1.0,
            execution_time_ms=execution_time_ms
        )

