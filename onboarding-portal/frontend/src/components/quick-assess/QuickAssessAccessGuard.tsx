import { Navigate, Outlet, useLocation, Link as RouterLink } from 'react-router-dom';
import { Alert, Button, Stack, Typography, Link } from '@mui/material';
import { usePermissions } from '@/hooks/usePermissions';

export default function QuickAssessAccessGuard() {
  const { canUseQuickAssess } = usePermissions();
  const location = useLocation();

  if (canUseQuickAssess) {
    return <Outlet />;
  }

  if (!canUseQuickAssess) {
    return (
      <Stack spacing={3}>
        <Alert severity="warning" variant="outlined">
          <Typography variant="h6" gutterBottom>
            Quick Assess is not available for your account.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upgrade to the Enterprise plan or contact your administrator to enable Quick Assess.
          </Typography>
          <Stack direction="row" spacing={2} mt={2}>
            <Button variant="contained" component={RouterLink} to="/contact-sales">
              Contact Sales
            </Button>
            <Button variant="outlined" component={RouterLink} to="/">
              Back to Dashboard
            </Button>
          </Stack>
        </Alert>
      </Stack>
    );
  }

  return <Navigate to="/" state={{ from: location }} replace />;
}

