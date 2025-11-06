import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Grid,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
} from '@mui/material';
import { Search, Add, Edit, Visibility } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { customersApi, Customer } from '../../services/customers';

const CustomersPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [segment, setSegment] = useState<string | undefined>();

  const { data, isLoading } = useQuery({
    queryKey: ['customers', { search, segment }],
    queryFn: () => customersApi.list({ search, segment }),
  });

  const handleViewCustomer = (customerId: string) => {
    navigate(`/customers/${customerId}`);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Customers
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/customers/new')}
        >
          Add Customer
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                placeholder="Search customers..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label="All"
                  onClick={() => setSegment(undefined)}
                  color={segment === undefined ? 'primary' : 'default'}
                  variant={segment === undefined ? 'filled' : 'outlined'}
                />
                <Chip
                  label="VIP"
                  onClick={() => setSegment('VIP')}
                  color={segment === 'VIP' ? 'primary' : 'default'}
                  variant={segment === 'VIP' ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Active"
                  onClick={() => setSegment('Active')}
                  color={segment === 'Active' ? 'primary' : 'default'}
                  variant={segment === 'Active' ? 'filled' : 'outlined'}
                />
                <Chip
                  label="At Risk"
                  onClick={() => setSegment('AtRisk')}
                  color={segment === 'AtRisk' ? 'primary' : 'default'}
                  variant={segment === 'AtRisk' ? 'filled' : 'outlined'}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {isLoading ? (
        <Box>Loading...</Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Segment</TableCell>
                <TableCell>Lifetime Value</TableCell>
                <TableCell>Churn Risk</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.customers.map((customer: Customer) => (
                <TableRow key={customer.customer_id} hover>
                  <TableCell>
                    {customer.first_name} {customer.last_name}
                  </TableCell>
                  <TableCell>{customer.email}</TableCell>
                  <TableCell>
                    <Chip
                      label={customer.segment || 'Unknown'}
                      size="small"
                      color={
                        customer.segment === 'VIP'
                          ? 'primary'
                          : customer.segment === 'AtRisk'
                          ? 'error'
                          : 'default'
                      }
                    />
                  </TableCell>
                  <TableCell>
                    ${customer.lifetime_value?.toLocaleString() || '0'}
                  </TableCell>
                  <TableCell>
                    {customer.churn_risk_score ? (
                      <Chip
                        label={`${(customer.churn_risk_score * 100).toFixed(0)}%`}
                        size="small"
                        color={customer.churn_risk_score > 0.6 ? 'error' : 'default'}
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleViewCustomer(customer.customer_id)}
                    >
                      <Visibility />
                    </IconButton>
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

export default CustomersPage;

