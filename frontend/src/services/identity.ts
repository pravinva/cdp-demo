import { apiClient } from './api';

export interface MatchGroup {
  match_id: string;
  total_events: number;
  anonymous_events: number;
  known_events: number;
  is_household: boolean;
  household_size?: number;
  first_seen: string;
  last_seen: string;
}

export interface GraphEdge {
  edge_id: string;
  from: {
    type: string;
    id: string;
  };
  to: {
    type: string;
    id: string;
  };
  relationship_type: string;
  strength: number;
  evidence_count: number;
}

export interface HouseholdMember {
  customer_id: string;
  first_name: string;
  last_name: string;
  email: string;
  household_role?: string;
}

export const identityApi = {
  getMatchGroups: (params?: { is_household?: boolean }) =>
    apiClient.get<{ match_groups: MatchGroup[] }>('/identity/match-groups', params),

  getGraphEdges: (params?: { relationship_type?: string }) =>
    apiClient.get<{ edges: GraphEdge[] }>('/identity/identity-graph/edges', params),

  getHouseholdGraph: (customerId: string) =>
    apiClient.get<{ customer_id: string; household_members: HouseholdMember[] }>(
      `/identity/graph/household/${customerId}`
    ),

  runIdentityResolution: (batchSize?: number) => {
    const url = batchSize ? `/identity/resolve?batch_size=${batchSize}` : '/identity/resolve';
    return apiClient.post<{ status: string; processed: number; match_groups_created: number }>(url);
  },

  detectHouseholds: () =>
    apiClient.post<{ status: string; households_detected: number }>(
      '/identity/households/detect'
    ),
};

