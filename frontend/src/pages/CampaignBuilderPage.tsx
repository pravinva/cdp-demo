import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  FormControlLabel,
  Checkbox,
  Chip,
  Grid,
} from '@mui/material';
import { Save } from '@mui/icons-material';
import { campaignsApi } from '../services/campaigns';

const CampaignBuilderPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    goal: 'retention',
    agent_mode: true,
    agent_instructions: '',
    channels: ['email'],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await campaignsApi.create(formData);
      navigate('/campaigns');
    } catch (error) {
      alert('Error creating campaign');
    }
  };

  const channelOptions = ['email', 'sms', 'push'];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Create Campaign
      </Typography>

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Campaign Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Goal"
                  value={formData.goal}
                  onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                  SelectProps={{ native: true }}
                >
                  <option value="retention">Retention</option>
                  <option value="winback">Winback</option>
                  <option value="cross-sell">Cross-sell</option>
                  <option value="upsell">Upsell</option>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.agent_mode}
                      onChange={(e) => setFormData({ ...formData, agent_mode: e.target.checked })}
                    />
                  }
                  label="Enable Agent Mode (AI-powered personalization)"
                />
              </Grid>
              {formData.agent_mode && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Agent Instructions"
                    multiline
                    rows={4}
                    value={formData.agent_instructions}
                    onChange={(e) => setFormData({ ...formData, agent_instructions: e.target.value })}
                    placeholder="E.g., Focus on personalized offers based on past purchases"
                  />
                </Grid>
              )}
              <Grid item xs={12}>
                <Typography variant="body2" gutterBottom>
                  Channels
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {channelOptions.map((channel) => (
                    <Chip
                      key={channel}
                      label={channel}
                      onClick={() => {
                        const channels = formData.channels.includes(channel)
                          ? formData.channels.filter((c) => c !== channel)
                          : [...formData.channels, channel];
                        setFormData({ ...formData, channels });
                      }}
                      color={formData.channels.includes(channel) ? 'primary' : 'default'}
                      variant={formData.channels.includes(channel) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button onClick={() => navigate('/campaigns')}>Cancel</Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<Save />}
                  >
                    Create Campaign
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CampaignBuilderPage;

