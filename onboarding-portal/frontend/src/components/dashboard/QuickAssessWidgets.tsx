import {
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Typography,
  Button,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { format } from 'date-fns';
import { AssessmentListItem } from '@/types/quickAssess';

interface RecentAssessmentsCardProps {
  assessments: AssessmentListItem[];
  loading: boolean;
  error?: string | null;
  onNavigate: (assessmentId?: string) => void;
}

export function RecentAssessmentsCard({
  assessments,
  loading,
  error,
  onNavigate,
}: RecentAssessmentsCardProps) {
  return (
    <Card>
      <CardHeader
        title="Recent Quick Assessments"
        subheader="Latest automated assessments across all projects"
      />
      <CardContent>
        {loading && <Typography variant="body2">Loading assessments…</Typography>}
        {error && (
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        )}
        {!loading && assessments.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No recent assessments found.
          </Typography>
        )}

        <List dense disablePadding>
          {assessments.slice(0, 3).map((item) => (
            <ListItem
              key={item.assessment_id}
              divider
              secondaryAction={
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() =>
                    onNavigate(
                      item.status === 'completed' ? item.assessment_id : undefined
                    )
                  }
                >
                  {item.status === 'completed' ? 'View Report' : 'View Status'}
                </Button>
              }
            >
              <ListItemText
                primary={`Assessment ${item.assessment_id.slice(0, 8)}`}
                secondary={
                  <>
                    <Typography component="span" variant="body2" color="text.secondary">
                      {item.upload_time
                        ? format(new Date(item.upload_time), 'MMM d, HH:mm')
                        : '—'}
                    </Typography>
                    <Chip
                      label={item.status}
                      size="small"
                      sx={{
                        ml: 1,
                        textTransform: 'capitalize',
                        bgcolor:
                          item.status === 'completed'
                            ? 'success.light'
                            : item.status === 'failed'
                            ? 'error.light'
                            : 'warning.light',
                      }}
                    />
                    {item.cloud_readiness_score !== undefined && (
                      <Typography
                        component="span"
                        variant="body2"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        Readiness: {item.cloud_readiness_score}
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onNavigate()}>
          View All
        </Button>
      </CardActions>
    </Card>
  );
}

interface QuickAssessActionsCardProps {
  monthlyCount: number;
  onStart: () => void;
  disabled?: boolean;
  onUpgrade?: () => void;
}

export function QuickAssessActionsCard({
  monthlyCount,
  onStart,
  disabled,
  onUpgrade,
}: QuickAssessActionsCardProps) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader title="Start New Assessment" />
      <CardContent>
        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <UploadFileIcon color="primary" fontSize="large" />
          <Typography variant="body2" color="text.secondary">
            Upload documents and diagrams for instant architecture analysis.
          </Typography>
        </Stack>
        <Stack direction="row" spacing={1} alignItems="center" mb={2}>
          <AssessmentIcon color="action" />
          <Typography variant="body2" color="text.secondary">
            {monthlyCount} assessments this month
          </Typography>
        </Stack>
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          fullWidth
          onClick={disabled ? onUpgrade : onStart}
          startIcon={<UploadFileIcon />}
          disabled={disabled}
        >
          {disabled ? 'Upgrade to Unlock' : 'Quick Assess'}
        </Button>
        {disabled && (
          <Typography variant="caption" color="text.secondary">
            Quick Assess is available on Enterprise plans.
          </Typography>
        )}
      </CardActions>
    </Card>
  );
}

