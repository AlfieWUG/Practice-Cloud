import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Divider,
} from '@mui/material';
import UploadIcon from '@mui/icons-material/CloudUpload';
import { useState } from 'react';
import { AssessmentStatusPolling } from '@/components/quick-assess/AssessmentStatusPolling';
import { AssessmentResults } from '@/components/quick-assess/AssessmentResults';

export default function QuickAssess() {
  const [assessmentId, setAssessmentId] = useState<string | null>(null);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Quick Assess
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Upload discovery artifacts and monitor automated assessment progress in one place.
      </Typography>

      <Paper variant="outlined" sx={{ p: 3, mb: 4 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <UploadIcon color="primary" />
          <Box flexGrow={1}>
            <Typography variant="subtitle1">Upload assessment package</Typography>
            <Typography variant="body2" color="text.secondary">
              Use the Quick Assess API or upload form (coming soon) to kick off a run. Paste the returned assessment ID below to watch progress.
            </Typography>
          </Box>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              const id = window.prompt('Enter assessment ID');
              if (id) {
                setAssessmentId(id.trim());
              }
            }}
          >
            Enter ID
          </Button>
        </Stack>
      </Paper>

      {assessmentId && (
        <Stack spacing={4}>
          <AssessmentStatusPolling assessmentId={assessmentId} />
          <Divider />
          <AssessmentResults assessmentId={assessmentId} />
        </Stack>
      )}
    </Box>
  );
}

