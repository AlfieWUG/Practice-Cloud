/**
 * Layout component with app bar and navigation.
 */
import { ReactNode } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import CloudIcon from '@mui/icons-material/Cloud';
import { FileSearch } from 'lucide-react';
import { usePermissions } from '@/hooks/usePermissions';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { canUseQuickAssess } = usePermissions();

  const navItems = [
    { label: 'Dashboard', path: '/' },
    ...(canUseQuickAssess
      ? [{ label: 'Quick Assess', path: '/quick-assess', icon: <FileSearch size={18} /> }]
      : []),
    { label: 'New Project', path: '/projects/new' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <CloudIcon sx={{ mr: 2 }} />
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, cursor: 'pointer' }}
            onClick={() => navigate('/')}
          >
            Nagarro Agentic Services
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 1, sm: 2 },
              alignItems: { xs: 'flex-start', sm: 'center' },
            }}
          >
            {navItems.map((item) => {
              const active = isActive(item.path);
              return (
                <Button
                  key={item.path}
                  color="inherit"
                  startIcon={item.icon}
                  onClick={() => navigate(item.path)}
                  sx={{
                    bgcolor: active ? '#00D9C1' : 'transparent',
                    color: active ? '#00313C' : 'inherit',
                    '&:hover': {
                      bgcolor: active ? '#00c3ae' : 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  {item.label}
                </Button>
              );
            })}
          </Box>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {children}
      </Container>
      
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Container maxWidth="xl">
          <Typography variant="body2" color="text.secondary" align="center">
            Nagarro Agentic Services Portal © 2025
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
