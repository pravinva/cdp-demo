import { apiClient } from './api';

export interface DashboardData {
  customers: { total: number };
  campaigns: { active: number };
  messages: { sent_last_30d: number; conversion_rate: number };
  journeys: { active: number };
}

export const analyticsApi = {
  getDashboard: () =>
    apiClient.get<DashboardData>('/analytics/dashboard'),
  
  getSegments: () =>
    apiClient.get('/analytics/customers/segments'),
  
  getCampaignPerformance: (days: number = 30) =>
    apiClient.get('/analytics/campaigns/performance', { days }),
};

