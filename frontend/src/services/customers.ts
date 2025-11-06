import { apiClient } from './api';

export interface Customer {
  customer_id: string;
  tenant_id: string;
  email: string;
  first_name: string;
  last_name: string;
  segment?: string;
  lifetime_value?: number;
  churn_risk_score?: number;
  [key: string]: any;
}

export interface CustomerListResponse {
  customers: Customer[];
  total: number;
  page: number;
  page_size: number;
}

export interface Customer360 {
  profile: Customer;
  recent_events: any[];
  campaign_history: any[];
  agent_decisions: any[];
  household_members?: any[];
}

export const customersApi = {
  list: (params?: { segment?: string; search?: string; page?: number; page_size?: number }) =>
    apiClient.get<CustomerListResponse>('/customers', params),
  
  get: (customerId: string) =>
    apiClient.get<Customer360>(`/customers/${customerId}`),
  
  create: (data: Partial<Customer>) =>
    apiClient.post<Customer>('/customers', data),
  
  update: (customerId: string, data: Partial<Customer>) =>
    apiClient.patch<Customer>(`/customers/${customerId}`, data),
};

