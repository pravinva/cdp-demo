import { apiClient } from './api';

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result?: string;
}

export interface AgentDecision {
  decision_id: string;
  tenant_id: string;
  campaign_id?: string;
  customer_id: string;
  journey_id?: string;
  journey_step_id?: string;
  timestamp: string;
  action: 'contact' | 'skip' | 'wait';
  channel?: string;
  scheduled_send_time?: string;
  message_subject?: string;
  message_body?: string;
  call_to_action?: string;
  reasoning_summary: string;
  reasoning_details?: string;
  tool_calls: ToolCall[];
  confidence_score: number;
  customer_segment?: string;
  churn_risk?: number;
  ltv?: number;
  days_since_last_contact?: number;
  household_context?: string;
  delivery_id?: string;
  delivered: boolean;
  opened: boolean;
  clicked: boolean;
  converted: boolean;
  conversion_value?: number;
  model_version: string;
  execution_time_ms: number;
}

export interface AgentDecisionCreate {
  customer_id: string;
  campaign_id?: string;
  journey_id?: string;
  journey_step_id?: string;
}

export interface AgentMetrics {
  total_decisions: number;
  contact_decisions: number;
  skip_decisions: number;
  avg_confidence_score: number;
  avg_execution_time_ms: number;
  conversion_rate: number;
  open_rate: number;
  click_rate: number;
  decisions_by_channel: Record<string, number>;
  decisions_by_segment: Record<string, number>;
  top_reasons: Array<{ reason: string; count: number }>;
}

export const agentsApi = {
  getDecisions: (params?: {
    customer_id?: string;
    campaign_id?: string;
    journey_id?: string;
  }) => apiClient.get<AgentDecision[]>('/agents/decisions', params),

  getDecision: (decisionId: string) =>
    apiClient.get<AgentDecision>(`/agents/decisions/${decisionId}`),

  makeDecision: (data: AgentDecisionCreate) =>
    apiClient.post<AgentDecision>('/agents/decide', data),

  getMetrics: () =>
    apiClient.get<AgentMetrics>('/agents/metrics'),
};

