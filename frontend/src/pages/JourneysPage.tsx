import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { journeysApi } from '../../services/journeys';

const JourneysPage: React.FC = () => {
  const { data: journeys, isLoading } = useQuery({
    queryKey: ['journeys'],
    queryFn: () => journeysApi.list(),
  });

  if (isLoading) {
    return <Box>Loading...</Box>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Journeys
      </Typography>
      {journeys?.map((journey) => (
        <Card key={journey.journey_id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{journey.name}</Typography>
            <Typography variant="body2" color="textSecondary">
              {journey.description}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Status: {journey.status} • Steps: {journey.steps?.length || 0}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default JourneysPage;

