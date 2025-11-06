import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
} from '@mui/material';
import { Add, PlayArrow } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { campaignsApi, Campaign } from '../../services/campaigns';

const CampaignsPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.list(),
  });

  const handleExecute = async (campaignId: string) => {
    try {
      await campaignsApi.execute(campaignId);
      alert('Campaign execution started');
    } catch (error) {
      alert('Error executing campaign');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Campaigns
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/campaigns/new')}
        >
          New Campaign
        </Button>
      </Box>

      {isLoading ? (
        <Box>Loading...</Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Goal</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Channels</TableCell>
                <TableCell>Agent Mode</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {campaigns?.map((campaign: Campaign) => (
                <TableRow key={campaign.campaign_id} hover>
                  <TableCell>{campaign.name}</TableCell>
                  <TableCell>{campaign.goal}</TableCell>
                  <TableCell>
                    <Chip
                      label={campaign.status}
                      size="small"
                      color={campaign.status === 'active' ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    {campaign.channels.map((ch) => (
                      <Chip key={ch} label={ch} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>
                    {campaign.agent_mode ? (
                      <Chip label="Enabled" size="small" color="primary" />
                    ) : (
                      <Chip label="Disabled" size="small" />
                    )}
                  </TableCell>
                  <TableCell align="right">
                    {campaign.status === 'active' && (
                      <IconButton
                        size="small"
                        onClick={() => handleExecute(campaign.campaign_id)}
                        color="primary"
                      >
                        <PlayArrow />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default CampaignsPage;

