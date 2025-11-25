/**
 * Project card component for dashboard.
 */
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Box,
} from '@mui/material';
import { format } from 'date-fns';
import { Project, ProjectStatus } from '@/types';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface ProjectCardProps {
  project: Project;
  onClick: () => void;
}

const statusColors: Record<ProjectStatus, 'default' | 'primary' | 'success' | 'error' | 'warning'> = {
  [ProjectStatus.PLANNING]: 'default',
  [ProjectStatus.DISCOVERY]: 'primary',
  [ProjectStatus.ASSESSMENT]: 'primary',
  [ProjectStatus.EXECUTION]: 'warning',
  [ProjectStatus.OPTIMIZATION]: 'warning',
  [ProjectStatus.COMPLETED]: 'success',
  [ProjectStatus.FAILED]: 'error',
};

export default function ProjectCard({ project, onClick }: ProjectCardProps) {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
          <Typography variant="h6" component="h2" gutterBottom>
            {project.name}
          </Typography>
          <Chip
            label={project.status}
            color={statusColors[project.status]}
            size="small"
          />
        </Box>

        {project.description && (
          <Typography variant="body2" color="text.secondary" mb={2}>
            {project.description.length > 100
              ? `${project.description.substring(0, 100)}...`
              : project.description}
          </Typography>
        )}

        {project.current_phase && (
          <Typography variant="body2" color="text.secondary" mb={1}>
            <strong>Phase:</strong> {project.current_phase}
          </Typography>
        )}

        <Box mt={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Progress
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {project.progress}%
            </Typography>
          </Box>
          <LinearProgress variant="determinate" value={project.progress} />
        </Box>

        <Typography variant="caption" color="text.secondary" display="block" mt={2}>
          Created {format(new Date(project.created_at), 'MMM dd, yyyy')}
        </Typography>
      </CardContent>

      <CardActions>
        <Button
          size="small"
          endIcon={<ArrowForwardIcon />}
          onClick={onClick}
        >
          View Details
        </Button>
      </CardActions>
    </Card>
  );
}
