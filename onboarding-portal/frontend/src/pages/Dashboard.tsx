/**
 * Dashboard page - shows all migration projects.
 */
import { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useNavigate } from 'react-router-dom';
import { Project } from '@/types';
import { AssessmentListItem } from '@/types/quickAssess';
import apiClient from '@/services/api';
import ProjectCard from '@/components/ProjectCard';
import {
  RecentAssessmentsCard,
  QuickAssessActionsCard,
} from '@/components/dashboard/QuickAssessWidgets';
import { usePermissions } from '@/hooks/usePermissions';

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [recentAssessments, setRecentAssessments] = useState<AssessmentListItem[]>([]);
  const [assessLoading, setAssessLoading] = useState(false);
  const [assessError, setAssessError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { canUseQuickAssess } = usePermissions();
  const handleUpgradeRedirect = () =>
    window.open('https://www.nagarro.com/en/contact', '_blank');

  useEffect(() => {
    loadProjects();
    loadAssessments();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getProjects();
      setProjects(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const loadAssessments = async () => {
    try {
      setAssessLoading(true);
      setAssessError(null);
      const response = await apiClient.listAssessments(5);
      setRecentAssessments(response.items);
    } catch (err: any) {
      setAssessError(err.message || 'Failed to load Quick Assess data');
    } finally {
      setAssessLoading(false);
    }
  };

  const monthlyCount = useMemo(() => {
    const now = new Date();
    return recentAssessments.filter((item) => {
      if (!item.upload_time) return false;
      const date = new Date(item.upload_time);
      return date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth();
    }).length;
  }, [recentAssessments]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          Migration Projects
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/projects/new')}
        >
          New Project
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6} lg={4}>
          <QuickAssessActionsCard
            monthlyCount={monthlyCount}
            onStart={() => navigate('/quick-assess')}
            disabled={!canUseQuickAssess}
            onUpgrade={handleUpgradeRedirect}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={8}>
          <RecentAssessmentsCard
            assessments={recentAssessments}
            loading={assessLoading}
            error={assessError}
            onNavigate={(assessmentId) =>
              canUseQuickAssess
                ? assessmentId
                  ? navigate(`/quick-assess?assessment=${assessmentId}`)
                  : navigate('/quick-assess')
                : handleUpgradeRedirect()
            }
          />
        </Grid>
      </Grid>

      {projects.length === 0 ? (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No projects yet
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Create your first migration project to get started
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/projects/new')}
          >
            Create Project
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} md={6} lg={4} key={project.id}>
              <ProjectCard
                project={project}
                onClick={() => navigate(`/projects/${project.id}`)}
              />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
