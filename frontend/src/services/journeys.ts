import { apiClient } from './api';

export interface JourneyDefinition {
  journey_id: string;
  tenant_id: string;
  name: string;
  description?: string;
  entry_trigger: string;
  status: string;
  steps: JourneyStep[];
  [key: string]: any;
}

export interface JourneyStep {
  step_id: string;
  step_type: string;
  name: string;
  [key: string]: any;
}

export const journeysApi = {
  list: (params?: { status?: string }) =>
    apiClient.get<JourneyDefinition[]>('/journeys', params),
  
  get: (journeyId: string) =>
    apiClient.get<JourneyDefinition>(`/journeys/${journeyId}`),
  
  create: (data: Partial<JourneyDefinition>) =>
    apiClient.post<JourneyDefinition>('/journeys', data),
  
  update: (journeyId: string, data: Partial<JourneyDefinition>) =>
    apiClient.patch<JourneyDefinition>(`/journeys/${journeyId}`, data),
  
  activate: (journeyId: string) =>
    apiClient.post(`/journeys/${journeyId}/activate`),
  
  execute: (journeyId: string, data: { customer_ids?: string[]; segment?: string }) =>
    apiClient.post(`/journeys/${journeyId}/execute`, data),
  
  getProgress: (journeyId: string) =>
    apiClient.get(`/journeys/${journeyId}/progress`),
};

