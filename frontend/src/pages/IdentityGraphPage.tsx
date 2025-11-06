import React, { useState, useMemo, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Autocomplete,
  Chip,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  AccountTree,
  Search,
  Refresh,
  Home,
  People,
  Link as LinkIcon,
  Visibility,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { identityApi, GraphEdge, MatchGroup, HouseholdMember } from '../services/identity';
import { customersApi } from '../services/customers';
import ForceGraph2D from 'react-force-graph-2d';

interface GraphNode {
  id: string;
  label: string;
  type: 'customer' | 'household' | 'match_group';
  group: number;
  size: number;
  color?: string;
}

interface GraphLink {
  source: string;
  target: string;
  relationship_type: string;
  strength: number;
  color?: string;
}

const IdentityGraphPage: React.FC = () => {
  const [searchCustomer, setSearchCustomer] = useState<string>('');
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const graphRef = useRef<any>();

  const { data: customers } = useQuery({
    queryKey: ['customers-search'],
    queryFn: () => customersApi.list({ page_size: 1000 }),
  });

  const { data: matchGroups, refetch: refetchMatchGroups } = useQuery({
    queryKey: ['match-groups'],
    queryFn: () => identityApi.getMatchGroups(),
  });

  const { data: graphEdges, refetch: refetchEdges } = useQuery({
    queryKey: ['graph-edges'],
    queryFn: () => identityApi.getGraphEdges(),
  });

  const { data: householdData, refetch: refetchHousehold } = useQuery({
    queryKey: ['household', selectedCustomer],
    queryFn: () => identityApi.getHouseholdGraph(selectedCustomer!),
    enabled: !!selectedCustomer,
  });

  // Build graph data from edges
  useEffect(() => {
    if (!graphEdges?.edges) return;

    const nodesMap = new Map<string, GraphNode>();
    const links: GraphLink[] = [];

    graphEdges.edges.forEach((edge) => {
      // Add source node
      if (!nodesMap.has(edge.from.id)) {
        nodesMap.set(edge.from.id, {
          id: edge.from.id,
          label: edge.from.id.slice(0, 12),
          type: edge.from.type === 'customer' ? 'customer' : 'match_group',
          group: edge.from.type === 'customer' ? 1 : 2,
          size: 8,
          color: edge.from.type === 'customer' ? '#FF3621' : '#1B3139',
        });
      }

      // Add target node
      if (!nodesMap.has(edge.to.id)) {
        nodesMap.set(edge.to.id, {
          id: edge.to.id,
          label: edge.to.id.slice(0, 12),
          type: edge.to.type === 'customer' ? 'customer' : 'match_group',
          group: edge.to.type === 'customer' ? 1 : 2,
          size: 8,
          color: edge.to.type === 'customer' ? '#FF3621' : '#1B3139',
        });
      }

      // Add link
      links.push({
        source: edge.from.id,
        target: edge.to.id,
        relationship_type: edge.relationship_type,
        strength: edge.strength,
        color: edge.relationship_type === 'household' ? '#00A972' : '#F39C12',
      });
    });

    setGraphData({
      nodes: Array.from(nodesMap.values()),
      links,
    });
  }, [graphEdges]);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    if (node.type === 'customer') {
      setSelectedCustomer(node.id);
    }
  };

  const handleRefresh = () => {
    refetchMatchGroups();
    refetchEdges();
    if (selectedCustomer) {
      refetchHousehold();
    }
  };

  const customerOptions = useMemo(() => {
    return customers?.customers.map((c) => ({
      label: `${c.first_name} ${c.last_name} (${c.email})`,
      value: c.customer_id,
    })) || [];
  }, [customers]);

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Identity Graph
          </Typography>
          <Typography color="textSecondary">
            Visualize customer relationships, households, and identity connections
          </Typography>
        </Box>
        <Button
          startIcon={<Refresh />}
          onClick={handleRefresh}
          variant="outlined"
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Left Panel - Search and Controls */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Search Customer
              </Typography>
              <Autocomplete
                options={customerOptions}
                getOptionLabel={(option) => option.label}
                value={customerOptions.find((c) => c.value === selectedCustomer) || null}
                onChange={(_, newValue) => {
                  if (newValue) {
                    setSelectedCustomer(newValue.value);
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Search by name or email"
                    variant="outlined"
                    size="small"
                  />
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
                <Tab label="Match Groups" />
                <Tab label="Households" />
              </Tabs>

              {tabValue === 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Identity Match Groups
                  </Typography>
                  <List>
                    {matchGroups?.match_groups.slice(0, 10).map((group) => (
                      <ListItem
                        key={group.match_id}
                        sx={{
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                          mb: 1,
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {group.match_id.slice(0, 12)}...
                              </Typography>
                              {group.is_household && (
                                <Chip
                                  icon={<Home />}
                                  label="Household"
                                  size="small"
                                  color="success"
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">
                                Events: {group.total_events} ({group.anonymous_events} anonymous,{' '}
                                {group.known_events} known)
                              </Typography>
                              {group.household_size && (
                                <Typography variant="caption" display="block">
                                  Household Size: {group.household_size}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {tabValue === 1 && selectedCustomer && householdData && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Household Members
                  </Typography>
                  {householdData.household_members.length === 0 ? (
                    <Typography variant="body2" color="textSecondary">
                      No household members found
                    </Typography>
                  ) : (
                    <List>
                      {householdData.household_members.map((member) => (
                        <ListItem
                          key={member.customer_id}
                          sx={{
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 1,
                            mb: 1,
                          }}
                        >
                          <ListItemText
                            primary={`${member.first_name} ${member.last_name}`}
                            secondary={
                              <Box>
                                <Typography variant="caption" display="block">
                                  {member.email}
                                </Typography>
                                {member.household_role && (
                                  <Chip
                                    label={member.household_role}
                                    size="small"
                                    sx={{ mt: 0.5 }}
                                  />
                                )}
                              </Box>
                            }
                          />
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedCustomer(member.customer_id);
                              setGraphData((prev) => ({
                                ...prev,
                                nodes: prev.nodes.map((n) =>
                                  n.id === member.customer_id
                                    ? { ...n, color: '#FF3621', size: 12 }
                                    : n
                                ),
                              }));
                            }}
                          >
                            <Visibility />
                          </IconButton>
                        </ListItem>
                      ))}
                    </List>
                  )}
                </Box>
              )}

              {tabValue === 1 && !selectedCustomer && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    Select a customer to view household members
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Panel - Graph Visualization */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Relationship Graph</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    icon={<People />}
                    label="Customers"
                    size="small"
                    sx={{ bgcolor: '#FF3621', color: 'white' }}
                  />
                  <Chip
                    icon={<AccountTree />}
                    label="Match Groups"
                    size="small"
                    sx={{ bgcolor: '#1B3139', color: 'white' }}
                  />
                  <Chip
                    icon={<LinkIcon />}
                    label="Households"
                    size="small"
                    sx={{ bgcolor: '#00A972', color: 'white' }}
                  />
                </Box>
              </Box>

              {graphData.nodes.length === 0 ? (
                <Box
                  sx={{
                    height: 600,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '1px dashed',
                    borderColor: 'divider',
                    borderRadius: 1,
                  }}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <AccountTree sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="textSecondary" gutterBottom>
                      No graph data available
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Run identity resolution to generate relationship graph
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                  }}
                >
                  <ForceGraph2D
                    ref={graphRef}
                    graphData={graphData}
                    nodeLabel={(node: GraphNode) => `${node.label} (${node.type})`}
                    nodeColor={(node: GraphNode) => node.color || '#999'}
                    nodeVal={(node: GraphNode) => node.size}
                    linkLabel={(link: GraphLink) => `${link.relationship_type} (${(link.strength * 100).toFixed(0)}%)`}
                    linkColor={(link: GraphLink) => link.color || '#999'}
                    linkWidth={(link: GraphLink) => link.strength * 3}
                    onNodeClick={handleNodeClick}
                    nodeCanvasObjectMode={() => 'after'}
                    nodeCanvasObject={(node: GraphNode, ctx: CanvasRenderingContext2D) => {
                      const label = node.label;
                      const fontSize = 10;
                      ctx.font = `${fontSize}px Sans-Serif`;
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'middle';
                      ctx.fillStyle = '#333';
                      ctx.fillText(label, node.x || 0, (node.y || 0) + node.size + 4);
                    }}
                    width={800}
                    height={600}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Node Detail Dialog */}
      <Dialog open={!!selectedNode} onClose={() => setSelectedNode(null)} maxWidth="sm" fullWidth>
        {selectedNode && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccountTree />
                <Typography variant="h6">Node Details</Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    ID
                  </Typography>
                  <Typography variant="body1">{selectedNode.id}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Type
                  </Typography>
                  <Chip
                    label={selectedNode.type}
                    size="small"
                    color={selectedNode.type === 'customer' ? 'primary' : 'default'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => {
                      if (selectedNode.type === 'customer') {
                        window.location.href = `/customers/${selectedNode.id}`;
                      }
                    }}
                  >
                    View Details
                  </Button>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedNode(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default IdentityGraphPage;

