/**
 * Project Detail page - view and execute agents for a project.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Divider,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { ProjectWithExecutions, MigrationPhase } from '@/types';
import apiClient from '@/services/api';
import PhasePanel from '@/components/PhasePanel';

const PHASES = [
  MigrationPhase.DISCOVERY,
  MigrationPhase.ASSESSMENT,
  MigrationPhase.EXECUTION,
  MigrationPhase.OPTIMIZATION,
];

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectWithExecutions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agentsByPhase, setAgentsByPhase] = useState<Record<string, string[]>>({});

  useEffect(() => {
    loadProject();
    loadAgents();
  }, [projectId]);

  const loadProject = async () => {
    if (!projectId) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getProject(projectId);
      setProject(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const loadAgents = async () => {
    try {
      const agents = await apiClient.getAgents();
      setAgentsByPhase(agents);
    } catch (err: any) {
      console.error('Failed to load agents:', err);
    }
  };

  const handleExecutePhase = async (phase: MigrationPhase) => {
    if (!projectId || !agentsByPhase[phase]) return;

    try {
      await apiClient.bulkExecuteAgents(
        projectId,
        phase,
        agentsByPhase[phase]
      );
      
      // Reload project to see new executions
      await loadProject();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to execute agents');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!project) {
    return (
      <Alert severity="error">Project not found</Alert>
    );
  }

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/')}
        sx={{ mb: 3 }}
      >
        Back to Dashboard
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start">
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {project.name}
            </Typography>
            <Chip label={project.status} color="primary" sx={{ mr: 1 }} />
            {project.current_phase && (
              <Chip label={`Phase: ${project.current_phase}`} variant="outlined" />
            )}
          </Box>
          <Typography variant="h5" color="primary">
            {project.progress}%
          </Typography>
        </Box>

        {project.description && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body1" color="text.secondary">
              {project.description}
            </Typography>
          </>
        )}

        {project.requirements && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2">
              <strong>Requirements:</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
              {project.requirements}
            </Typography>
          </>
        )}
      </Paper>

      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Agent Execution
      </Typography>

      <Grid container spacing={3}>
        {PHASES.map((phase) => (
          <Grid item xs={12} key={phase}>
            <PhasePanel
              phase={phase}
              agents={agentsByPhase[phase] || []}
              executions={project.agent_executions.filter(e => e.phase === phase)}
              onExecutePhase={() => handleExecutePhase(phase)}
              onRefresh={loadProject}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
