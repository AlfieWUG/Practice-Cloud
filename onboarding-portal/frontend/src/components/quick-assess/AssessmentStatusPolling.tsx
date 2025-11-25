import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import apiClient from '@/services/api';
import { AssessmentStatus } from '@/types/quickAssess';

interface AssessmentStatusPollingProps {
  assessmentId: string;
  onComplete?: (status: AssessmentStatus) => void;
}

const STAGE_ORDER: Record<
  NonNullable<AssessmentStatus['stage']>,
  { label: string; progress: number }
> = {
  ingestion: { label: 'Gathering files...', progress: 10 },
  parsing: { label: 'Parsing documents...', progress: 25 },
  analysis: { label: 'Analyzing architecture...', progress: 50 },
  report: { label: 'Generating report...', progress: 75 },
  completed: { label: 'Complete!', progress: 100 },
};

export function AssessmentStatusPolling({
  assessmentId,
  onComplete,
}: AssessmentStatusPollingProps) {
  const [status, setStatus] = useState<AssessmentStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      setError(null);
      const response = await apiClient.getAssessmentStatus(assessmentId);
      setStatus(response);
      if (response.status === 'completed' && onComplete) {
        onComplete(response);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load');
    }
  }, [assessmentId, onComplete]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const stageInfo = status?.stage
    ? STAGE_ORDER[status.stage]
    : { label: 'Starting...', progress: 0 };

  const estimatedTime = useMemo(() => {
    if (!status?.estimated_seconds_remaining) return 'Calculating...';
    const minutes = Math.floor(status.estimated_seconds_remaining / 60);
    const seconds = status.estimated_seconds_remaining % 60;
    if (minutes === 0) return `${seconds}s remaining`;
    return `${minutes}m ${seconds}s remaining`;
  }, [status]);

  const files = status?.files ?? [];

  const handleRetry = async () => {
    setIsRetrying(true);
    await fetchStatus();
    setIsRetrying(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Assessment Status</CardTitle>
        <CardDescription>
          Tracking assessment {assessmentId.slice(0, 8)}...
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-slate-600">
              {stageInfo.label}
            </p>
            <span className="text-sm text-slate-500">{stageInfo.progress}%</span>
          </div>
          <Progress value={stageInfo.progress} />
          <p className="text-xs text-slate-500 mt-2">
            Estimated time remaining: {estimatedTime}
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold text-slate-700">
            Processing stages
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {Object.entries(STAGE_ORDER).map(([key, info]) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"
              >
                <span className="text-sm text-slate-600">{info.label}</span>
                {status?.stage === key ? (
                  <Badge variant="secondary">In progress</Badge>
                ) : info.progress < stageInfo.progress ? (
                  <Badge variant="success">Done</Badge>
                ) : (
                  <Badge variant="secondary">Pending</Badge>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold text-slate-700 mb-2">
            Files in queue
          </p>
          <div className="space-y-2 max-h-48 overflow-auto pr-1">
            {files.length === 0 && (
              <p className="text-sm text-slate-500">
                Waiting for file metadata...
              </p>
            )}
            {files.map((file) => (
              <div
                key={file.filename}
                className="flex items-center justify-between rounded border border-slate-100 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {file.filename}
                  </p>
                  {file.message && (
                    <p className="text-xs text-slate-500">{file.message}</p>
                  )}
                </div>
                <Badge
                  variant={
                    file.status === 'completed'
                      ? 'success'
                      : file.status === 'failed'
                      ? 'destructive'
                      : 'secondary'
                  }
                >
                  {file.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            <p className="font-semibold">Status check failed</p>
            <p>{error}</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={handleRetry}
              disabled={isRetrying}
            >
              {isRetrying ? 'Retrying...' : 'Retry now'}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

