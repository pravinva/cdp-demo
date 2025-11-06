import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Tabs,
  Tab,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { customersApi } from '../services/customers';

const CustomerDetailPage: React.FC = () => {
  const { customerId } = useParams<{ customerId: string }>();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = React.useState(0);

  const { data: customer360, isLoading } = useQuery({
    queryKey: ['customer', customerId],
    queryFn: () => customersApi.get(customerId!),
    enabled: !!customerId,
  });

  if (isLoading) {
    return <Box>Loading...</Box>;
  }

  if (!customer360) {
    return <Box>Customer not found</Box>;
  }

  const { profile } = customer360;

  return (
    <Box>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/customers')}
        sx={{ mb: 2 }}
      >
        Back to Customers
      </Button>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                {profile.first_name} {profile.last_name}
              </Typography>
              <Typography variant="body1" color="textSecondary" gutterBottom>
                {profile.email}
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={profile.segment || 'Unknown'}
                  color={profile.segment === 'VIP' ? 'primary' : 'default'}
                />
                {profile.churn_risk_score && (
                  <Chip
                    label={`Churn Risk: ${(profile.churn_risk_score * 100).toFixed(0)}%`}
                    color={profile.churn_risk_score > 0.6 ? 'error' : 'warning'}
                  />
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Lifetime Value
                  </Typography>
                  <Typography variant="h4" color="primary">
                    ${profile.lifetime_value?.toLocaleString() || '0'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
            <Tab label="Overview" />
            <Tab label="Recent Events" />
            <Tab label="Campaign History" />
            <Tab label="Agent Decisions" />
          </Tabs>

          {tabValue === 0 && (
            <Box sx={{ mt: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Total Purchases
                  </Typography>
                  <Typography variant="h6">{profile.total_purchases || 0}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Preferred Channel
                  </Typography>
                  <Typography variant="h6">{profile.preferred_channel || 'N/A'}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 1 && (
            <Box sx={{ mt: 3 }}>
              {customer360.recent_events.length > 0 ? (
                <Box>
                  {customer360.recent_events.slice(0, 10).map((event: any, idx: number) => (
                    <Box key={idx} sx={{ py: 1, borderBottom: '1px solid #eee' }}>
                      <Typography variant="body2">
                        <strong>{event.event_type}</strong> - {event.page_url}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(event.event_timestamp).toLocaleString()}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography>No recent events</Typography>
              )}
            </Box>
          )}

          {tabValue === 2 && (
            <Box sx={{ mt: 3 }}>
              {customer360.campaign_history.length > 0 ? (
                <Box>
                  {customer360.campaign_history.map((history: any, idx: number) => (
                    <Box key={idx} sx={{ py: 1, borderBottom: '1px solid #eee' }}>
                      <Typography variant="body2">
                        <strong>{history.campaign_name}</strong> via {history.channel}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(history.sent_at).toLocaleString()}
                        {history.opened && ' • Opened'}
                        {history.clicked && ' • Clicked'}
                        {history.converted && ' • Converted'}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography>No campaign history</Typography>
              )}
            </Box>
          )}

          {tabValue === 3 && (
            <Box sx={{ mt: 3 }}>
              {customer360.agent_decisions.length > 0 ? (
                <Box>
                  {customer360.agent_decisions.map((decision: any, idx: number) => (
                    <Card key={idx} variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="body2" gutterBottom>
                          <strong>Action:</strong> {decision.action} via {decision.channel}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          {decision.reasoning_summary}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Confidence: {(decision.confidence_score * 100).toFixed(0)}% •{' '}
                          {new Date(decision.timestamp).toLocaleString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Typography>No agent decisions</Typography>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default CustomerDetailPage;

