/**
 * Phase panel showing agents and their execution status.
 */
import { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Button,
  Collapse,
  IconButton,
  Grid,
  LinearProgress,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { MigrationPhase, AgentExecution } from '@/types';
import AgentCard from './AgentCard';

interface PhasePanelProps {
  phase: MigrationPhase;
  agents: string[];
  executions: AgentExecution[];
  onExecutePhase: () => void;
  onRefresh: () => void;
}

const PHASE_COLORS: Record<MigrationPhase, string> = {
  [MigrationPhase.DISCOVERY]: '#2196f3',
  [MigrationPhase.ASSESSMENT]: '#ff9800',
  [MigrationPhase.EXECUTION]: '#f44336',
  [MigrationPhase.OPTIMIZATION]: '#4caf50',
};

const PHASE_LABELS: Record<MigrationPhase, string> = {
  [MigrationPhase.DISCOVERY]: 'Discovery Phase',
  [MigrationPhase.ASSESSMENT]: 'Assessment Phase',
  [MigrationPhase.EXECUTION]: 'Execution Phase',
  [MigrationPhase.OPTIMIZATION]: 'Optimization Phase',
};

export default function PhasePanel({
  phase,
  agents,
  executions,
  onExecutePhase,
  onRefresh,
}: PhasePanelProps) {
  const [expanded, setExpanded] = useState(true);

  const completedCount = executions.filter(e => e.status === 'completed').length;
  const runningCount = executions.filter(e => e.status === 'running').length;
  const failedCount = executions.filter(e => e.status === 'failed').length;
  const progress = agents.length > 0 ? (completedCount / agents.length) * 100 : 0;

  return (
    <Paper sx={{ p: 2, borderLeft: 4, borderColor: PHASE_COLORS[phase] }}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center" gap={2} flex={1}>
          <IconButton onClick={() => setExpanded(!expanded)} size="small">
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
          
          <Box flex={1}>
            <Typography variant="h6">
              {PHASE_LABELS[phase]} ({agents.length} agents)
            </Typography>
            <Box display="flex" gap={2} mt={1}>
              <Typography variant="body2" color="text.secondary">
                Completed: {completedCount}
              </Typography>
              {runningCount > 0 && (
                <Typography variant="body2" color="primary">
                  Running: {runningCount}
                </Typography>
              )}
              {failedCount > 0 && (
                <Typography variant="body2" color="error">
                  Failed: {failedCount}
                </Typography>
              )}
            </Box>
          </Box>

          <Box width={200}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary" align="right" display="block">
              {Math.round(progress)}%
            </Typography>
          </Box>
        </Box>

        <Button
          variant="outlined"
          size="small"
          startIcon={<PlayArrowIcon />}
          onClick={onExecutePhase}
          disabled={runningCount > 0}
          sx={{ ml: 2 }}
        >
          Run All
        </Button>
      </Box>

      <Collapse in={expanded}>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {agents.map((agentName) => {
            const execution = executions.find(e => e.agent_name === agentName);
            return (
              <Grid item xs={12} sm={6} md={4} key={agentName}>
                <AgentCard
                  agentName={agentName}
                  execution={execution}
                  onRefresh={onRefresh}
                />
              </Grid>
            );
          })}
        </Grid>
      </Collapse>
    </Paper>
  );
}
