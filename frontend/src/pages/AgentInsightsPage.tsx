import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material';
import {
  Psychology,
  CheckCircle,
  Cancel,
  Schedule,
  Email,
  Sms,
  ExpandMore,
  Visibility,
  TrendingUp,
  Speed,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { agentsApi, AgentDecision } from '../services/agents';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#FF3621', '#1B3139', '#00A972', '#F39C12', '#E74C3C'];

const MetricCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: string;
}> = ({ title, value, subtitle, icon, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box sx={{ color: `${color}.main`, fontSize: 40 }}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const AgentInsightsPage: React.FC = () => {
  const [selectedDecision, setSelectedDecision] = useState<AgentDecision | null>(null);
  const [filter, setFilter] = useState<'all' | 'contact' | 'skip'>('all');

  const { data: decisions, isLoading } = useQuery({
    queryKey: ['agent-decisions', filter],
    queryFn: () => agentsApi.getDecisions(),
  });

  const filteredDecisions = decisions?.filter((d) => {
    if (filter === 'all') return true;
    return d.action === filter;
  }) || [];

  // Calculate metrics
  const metrics = React.useMemo(() => {
    if (!decisions || decisions.length === 0) {
      return {
        total: 0,
        contact: 0,
        skip: 0,
        avgConfidence: 0,
        avgExecutionTime: 0,
        conversionRate: 0,
        openRate: 0,
        clickRate: 0,
        byChannel: {} as Record<string, number>,
        bySegment: {} as Record<string, number>,
      };
    }

    const contactDecisions = decisions.filter((d) => d.action === 'contact');
    const converted = decisions.filter((d) => d.converted).length;
    const opened = decisions.filter((d) => d.opened).length;
    const clicked = decisions.filter((d) => d.clicked).length;

    const byChannel: Record<string, number> = {};
    const bySegment: Record<string, number> = {};

    decisions.forEach((d) => {
      if (d.channel) {
        byChannel[d.channel] = (byChannel[d.channel] || 0) + 1;
      }
      if (d.customer_segment) {
        bySegment[d.customer_segment] = (bySegment[d.customer_segment] || 0) + 1;
      }
    });

    return {
      total: decisions.length,
      contact: contactDecisions.length,
      skip: decisions.filter((d) => d.action === 'skip').length,
      avgConfidence:
        decisions.reduce((sum, d) => sum + d.confidence_score, 0) / decisions.length,
      avgExecutionTime:
        decisions.reduce((sum, d) => sum + d.execution_time_ms, 0) / decisions.length,
      conversionRate: contactDecisions.length > 0 ? (converted / contactDecisions.length) * 100 : 0,
      openRate: contactDecisions.length > 0 ? (opened / contactDecisions.length) * 100 : 0,
      clickRate: opened > 0 ? (clicked / opened) * 100 : 0,
      byChannel,
      bySegment,
    };
  }, [decisions]);

  const channelData = Object.entries(metrics.byChannel).map(([name, value]) => ({
    name: name.toUpperCase(),
    value,
  }));

  const segmentData = Object.entries(metrics.bySegment).map(([name, value]) => ({
    name,
    value,
  }));

  const getActionColor = (action: string) => {
    switch (action) {
      case 'contact':
        return 'success';
      case 'skip':
        return 'default';
      case 'wait':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getChannelIcon = (channel?: string) => {
    switch (channel) {
      case 'email':
        return <Email fontSize="small" />;
      case 'sms':
        return <Sms fontSize="small" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading agent insights...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Agent Insights
        </Typography>
        <Typography color="textSecondary">
          Monitor AI agent decisions, reasoning, and performance metrics
        </Typography>
      </Box>

      {/* Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Decisions"
            value={metrics.total}
            icon={<Psychology />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Contact Decisions"
            value={metrics.contact}
            subtitle={`${metrics.total > 0 ? ((metrics.contact / metrics.total) * 100).toFixed(1) : 0}% of total`}
            icon={<CheckCircle />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Confidence"
            value={`${metrics.avgConfidence.toFixed(2)}`}
            icon={<TrendingUp />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Execution"
            value={`${metrics.avgExecutionTime.toFixed(0)}ms`}
            icon={<Speed />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversion Rate
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 600, color: 'success.main' }}>
                {metrics.conversionRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {decisions?.filter((d) => d.converted).length || 0} conversions from{' '}
                {metrics.contact} contacts
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Open Rate
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {metrics.openRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {decisions?.filter((d) => d.opened).length || 0} opened out of{' '}
                {metrics.contact} sent
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Click Rate
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 600, color: 'info.main' }}>
                {metrics.clickRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {decisions?.filter((d) => d.clicked).length || 0} clicked out of{' '}
                {decisions?.filter((d) => d.opened).length || 0} opened
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Decisions by Channel
              </Typography>
              {channelData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={channelData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {channelData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="textSecondary">No channel data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Decisions by Segment
              </Typography>
              {segmentData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={segmentData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#FF3621" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="textSecondary">No segment data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Decision List */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Recent Decisions</Typography>
            <Box>
              <Button
                variant={filter === 'all' ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setFilter('all')}
                sx={{ mr: 1 }}
              >
                All
              </Button>
              <Button
                variant={filter === 'contact' ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setFilter('contact')}
                sx={{ mr: 1 }}
              >
                Contact
              </Button>
              <Button
                variant={filter === 'skip' ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setFilter('skip')}
              >
                Skip
              </Button>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Channel</TableCell>
                  <TableCell>Segment</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Reasoning</TableCell>
                  <TableCell>Outcome</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDecisions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      <Typography color="textSecondary">No decisions found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDecisions.slice(0, 20).map((decision) => (
                    <TableRow key={decision.decision_id}>
                      <TableCell>
                        {new Date(decision.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>{decision.customer_id.slice(0, 12)}...</TableCell>
                      <TableCell>
                        <Chip
                          label={decision.action}
                          color={getActionColor(decision.action) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {decision.channel ? (
                          <Chip
                            icon={getChannelIcon(decision.channel)}
                            label={decision.channel}
                            size="small"
                            variant="outlined"
                          />
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {decision.customer_segment || (
                          <Typography variant="body2" color="textSecondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={decision.confidence_score * 100}
                            sx={{ width: 60, height: 6, borderRadius: 3 }}
                          />
                          <Typography variant="body2">
                            {(decision.confidence_score * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {decision.reasoning_summary}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {decision.opened && (
                            <Chip label="Opened" size="small" color="info" />
                          )}
                          {decision.clicked && (
                            <Chip label="Clicked" size="small" color="warning" />
                          )}
                          {decision.converted && (
                            <Chip label="Converted" size="small" color="success" />
                          )}
                          {!decision.opened && !decision.clicked && !decision.converted && (
                            <Typography variant="body2" color="textSecondary">
                              -
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          onClick={() => setSelectedDecision(decision)}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Decision Detail Dialog */}
      <Dialog
        open={!!selectedDecision}
        onClose={() => setSelectedDecision(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedDecision && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Decision Details</Typography>
                <Chip
                  label={selectedDecision.action}
                  color={getActionColor(selectedDecision.action) as any}
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Decision ID
                  </Typography>
                  <Typography variant="body1">{selectedDecision.decision_id}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Customer ID
                  </Typography>
                  <Typography variant="body1">{selectedDecision.customer_id}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedDecision.timestamp).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Confidence Score
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={selectedDecision.confidence_score * 100}
                      sx={{ flex: 1, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body1">
                      {(selectedDecision.confidence_score * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Execution Time
                  </Typography>
                  <Typography variant="body1">
                    {selectedDecision.execution_time_ms}ms
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Model Version
                  </Typography>
                  <Typography variant="body1">{selectedDecision.model_version}</Typography>
                </Grid>

                {selectedDecision.channel && (
                  <>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="textSecondary">
                        Channel
                      </Typography>
                      <Chip
                        icon={getChannelIcon(selectedDecision.channel)}
                        label={selectedDecision.channel}
                        sx={{ mt: 0.5 }}
                      />
                    </Grid>
                    {selectedDecision.message_subject && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="textSecondary">
                          Subject
                        </Typography>
                        <Typography variant="body1">{selectedDecision.message_subject}</Typography>
                      </Grid>
                    )}
                    {selectedDecision.message_body && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="textSecondary">
                          Message Body
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{
                            mt: 0.5,
                            p: 2,
                            bgcolor: 'grey.50',
                            borderRadius: 1,
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {selectedDecision.message_body}
                        </Typography>
                      </Grid>
                    )}
                  </>
                )}

                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Reasoning Summary
                  </Typography>
                  <Typography variant="body1">{selectedDecision.reasoning_summary}</Typography>
                </Grid>

                {selectedDecision.reasoning_details && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Detailed Reasoning
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        p: 2,
                        bgcolor: 'grey.50',
                        borderRadius: 1,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {selectedDecision.reasoning_details}
                    </Typography>
                  </Grid>
                )}

                {selectedDecision.tool_calls && selectedDecision.tool_calls.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Tool Calls ({selectedDecision.tool_calls.length})
                    </Typography>
                    {selectedDecision.tool_calls.map((toolCall, index) => (
                      <Accordion key={index} sx={{ mt: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {toolCall.tool_name}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Parameters:
                            </Typography>
                            <Typography
                              variant="body2"
                              component="pre"
                              sx={{
                                p: 1,
                                bgcolor: 'grey.50',
                                borderRadius: 1,
                                fontSize: '0.75rem',
                                overflow: 'auto',
                              }}
                            >
                              {JSON.stringify(toolCall.parameters, null, 2)}
                            </Typography>
                          </Box>
                          {toolCall.result && (
                            <Box>
                              <Typography variant="body2" color="textSecondary" gutterBottom>
                                Result:
                              </Typography>
                              <Typography
                                variant="body2"
                                component="pre"
                                sx={{
                                  p: 1,
                                  bgcolor: 'grey.50',
                                  borderRadius: 1,
                                  fontSize: '0.75rem',
                                  overflow: 'auto',
                                }}
                              >
                                {toolCall.result}
                              </Typography>
                            </Box>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Grid>
                )}

                {selectedDecision.customer_segment && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      Customer Segment
                    </Typography>
                    <Typography variant="body1">{selectedDecision.customer_segment}</Typography>
                  </Grid>
                )}

                {selectedDecision.churn_risk !== undefined && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      Churn Risk
                    </Typography>
                    <Typography variant="body1">
                      {(selectedDecision.churn_risk * 100).toFixed(1)}%
                    </Typography>
                  </Grid>
                )}

                {selectedDecision.delivered && (
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                      Delivery Outcome
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label="Delivered"
                        color={selectedDecision.delivered ? 'success' : 'default'}
                      />
                      {selectedDecision.opened && (
                        <Chip label="Opened" color="info" />
                      )}
                      {selectedDecision.clicked && (
                        <Chip label="Clicked" color="warning" />
                      )}
                      {selectedDecision.converted && (
                        <Chip label="Converted" color="success" />
                      )}
                      {selectedDecision.conversion_value && (
                        <Chip
                          label={`Value: $${selectedDecision.conversion_value.toFixed(2)}`}
                          color="success"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedDecision(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AgentInsightsPage;
