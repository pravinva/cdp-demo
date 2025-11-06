import { apiClient } from './api';

export interface Campaign {
  campaign_id: string;
  tenant_id: string;
  name: string;
  description?: string;
  goal: string;
  status: string;
  agent_mode: boolean;
  channels: string[];
  [key: string]: any;
}

export const campaignsApi = {
  list: (params?: { status?: string }) =>
    apiClient.get<Campaign[]>('/campaigns', params),
  
  get: (campaignId: string) =>
    apiClient.get<Campaign>(`/campaigns/${campaignId}`),
  
  create: (data: Partial<Campaign>) =>
    apiClient.post<Campaign>('/campaigns', data),
  
  activate: (campaignId: string) =>
    apiClient.post(`/campaigns/${campaignId}/activate`),
  
  execute: (campaignId: string) =>
    apiClient.post(`/campaigns/${campaignId}/execute`),
};

