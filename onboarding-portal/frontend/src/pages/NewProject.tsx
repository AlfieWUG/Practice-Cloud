/**
 * New Project page - create a new migration project.
 */
import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import SaveIcon from '@mui/icons-material/Save';
import apiClient from '@/services/api';

export default function NewProject() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // For demo, use a hardcoded customer ID
  const DEMO_CUSTOMER_ID = '00000000-0000-0000-0000-000000000001';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const project = await apiClient.createProject({
        customer_id: DEMO_CUSTOMER_ID,
        name: name.trim(),
        description: description.trim() || undefined,
        requirements: requirements.trim() || undefined,
        target_cloud: 'aws',
      });

      navigate(`/projects/${project.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxWidth="md" mx="auto">
      <Typography variant="h4" component="h1" gutterBottom>
        Create New Migration Project
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <TextField
            label="Project Name"
            fullWidth
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{ mb: 3 }}
            helperText="A descriptive name for your migration project"
          />

          <TextField
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            sx={{ mb: 3 }}
            helperText="Brief overview of the project"
          />

          <TextField
            label="Requirements"
            fullWidth
            multiline
            rows={5}
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            sx={{ mb: 3 }}
            helperText="Detailed requirements and goals for the migration"
          />

          <Box display="flex" gap={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={<SaveIcon />}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Project'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
}
