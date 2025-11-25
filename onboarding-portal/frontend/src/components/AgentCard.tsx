/**
 * Agent card showing execution status.
 */
import {
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Box,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as QueuedIcon,
  PlayArrow as RunningIcon,
} from '@mui/icons-material';
import { AgentExecution, AgentExecutionStatus } from '@/types';

interface AgentCardProps {
  agentName: string;
  execution?: AgentExecution;
  onRefresh: () => void;
}

const STATUS_CONFIG: Record<
  AgentExecutionStatus,
  { icon: JSX.Element; color: 'default' | 'primary' | 'success' | 'error' | 'warning' }
> = {
  [AgentExecutionStatus.QUEUED]: {
    icon: <QueuedIcon fontSize="small" />,
    color: 'default',
  },
  [AgentExecutionStatus.RUNNING]: {
    icon: <RunningIcon fontSize="small" />,
    color: 'primary',
  },
  [AgentExecutionStatus.COMPLETED]: {
    icon: <CheckCircleIcon fontSize="small" />,
    color: 'success',
  },
  [AgentExecutionStatus.FAILED]: {
    icon: <ErrorIcon fontSize="small" />,
    color: 'error',
  },
  [AgentExecutionStatus.CANCELLED]: {
    icon: <ErrorIcon fontSize="small" />,
    color: 'warning',
  },
};

export default function AgentCard({ agentName, execution }: AgentCardProps) {
  const formatAgentName = (name: string) => {
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const status = execution?.status || AgentExecutionStatus.QUEUED;
  const config = STATUS_CONFIG[status];

  return (
    <Card
      sx={{
        height: '100%',
        border: execution?.status === AgentExecutionStatus.RUNNING ? 2 : 0,
        borderColor: 'primary.main',
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
          <Typography variant="subtitle2" sx={{ flex: 1 }}>
            {formatAgentName(agentName)}
          </Typography>
          <Chip
            icon={config.icon}
            label={status}
            color={config.color}
            size="small"
          />
        </Box>

        {execution && execution.status === AgentExecutionStatus.RUNNING && (
          <Box>
            <LinearProgress
              variant="determinate"
              value={execution.progress}
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              {execution.progress}%
            </Typography>
          </Box>
        )}

        {execution?.error && (
          <Typography variant="caption" color="error" display="block" mt={1}>
            {execution.error}
          </Typography>
        )}

        {execution?.result && execution.status === AgentExecutionStatus.COMPLETED && (
          <Typography variant="caption" color="success.main" display="block" mt={1}>
            ✓ Execution completed successfully
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
