import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import CustomersPage from './pages/CustomersPage';
import CustomerDetailPage from './pages/CustomerDetailPage';
import CampaignsPage from './pages/CampaignsPage';
import CampaignBuilderPage from './pages/CampaignBuilderPage';
import JourneysPage from './pages/JourneysPage';
import JourneyBuilderPage from './pages/JourneyBuilderPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AgentInsightsPage from './pages/AgentInsightsPage';
import IdentityGraphPage from './pages/IdentityGraphPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<AnalyticsPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/customers/:customerId" element={<CustomerDetailPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/campaigns/new" element={<CampaignBuilderPage />} />
        <Route path="/journeys" element={<JourneysPage />} />
        <Route path="/journeys/new" element={<JourneyBuilderPage />} />
        <Route path="/agents" element={<AgentInsightsPage />} />
        <Route path="/identity" element={<IdentityGraphPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </Layout>
  );
}

export default App;

