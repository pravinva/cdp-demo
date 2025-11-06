import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
} from '@mui/material';
import {
  Dashboard,
  People,
  Campaign,
  Route,
  Psychology,
  Analytics,
  AccountTree,
} from '@mui/icons-material';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/analytics' },
  { text: 'Customers', icon: <People />, path: '/customers' },
  { text: 'Campaigns', icon: <Campaign />, path: '/campaigns' },
  { text: 'Journeys', icon: <Route />, path: '/journeys' },
  { text: 'Agent Insights', icon: <Psychology />, path: '/agents' },
  { text: 'Identity Graph', icon: <AccountTree />, path: '/identity' },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid rgba(0, 0, 0, 0.12)',
        },
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            component="img"
            src="/databricks-logo.svg"
            alt="Databricks"
            sx={{ height: 24, display: { xs: 'none', sm: 'block' } }}
            onError={(e) => {
              // Fallback if logo not found
              e.currentTarget.style.display = 'none';
            }}
          />
          <Box sx={{ fontWeight: 600, fontSize: '1.1rem', color: 'primary.main' }}>
            CDP Platform
          </Box>
        </Box>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.main',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? 'white' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar;

