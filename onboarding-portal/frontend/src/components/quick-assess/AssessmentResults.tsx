import { useEffect, useMemo, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import apiClient from '@/services/api';
import { AssessmentResultSummary } from '@/types/quickAssess';
import {
  Bar,
  BarChart,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from 'recharts';

interface AssessmentResultsProps {
  assessmentId: string;
  initialData?: AssessmentResultSummary;
  onStartNew?: () => void;
}

export function AssessmentResults({
  assessmentId,
  initialData,
  onStartNew,
}: AssessmentResultsProps) {
  const [results, setResults] = useState<AssessmentResultSummary | null>(
    initialData || null
  );
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [shareMessage, setShareMessage] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) return;
    (async () => {
      try {
        setLoading(true);
        const response = await apiClient.getAssessmentResults(assessmentId);
        setResults(response);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, [assessmentId, initialData]);

  const readinessChartData = useMemo(() => {
    if (!results) return [];
    return [
      {
        name: 'Readiness',
        value: results.cloud_readiness_score,
        fill: '#00D9C1',
      },
    ];
  }, [results]);

  const infrastructureData = useMemo(() => {
    if (!results) return [];
    return Object.entries(results.infrastructure_counts || {}).map(
      ([key, value]) => ({ name: key, value })
    );
  }, [results]);

  const handleDownloadReport = () => {
    if (!results?.report_url) return;
    window.open(results.report_url, '_blank');
  };

  const handleViewJson = () => {
    if (results?.report_json_url) {
      window.open(results.report_json_url, '_blank');
    } else {
      setShowJson((prev) => !prev);
    }
  };

  const handleShare = async () => {
    try {
      const response = await apiClient.shareAssessmentReport(assessmentId);
      setShareUrl(response.share_url);
      navigator.clipboard?.writeText(response.share_url);
      setShareMessage('Share link copied to clipboard');
      setTimeout(() => setShareMessage(null), 4000);
    } catch (err: any) {
      setShareMessage(
        err.response?.data?.detail || err.message || 'Share failed'
      );
      setTimeout(() => setShareMessage(null), 5000);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Assessment Results</CardTitle>
          <CardDescription>Preparing insights...</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">Loading assessment results...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !results) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Assessment Results</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">
            {error || 'Results unavailable.'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const riskVariant =
    results.risk_level === 'low'
      ? 'success'
      : results.risk_level === 'medium'
      ? 'warning'
      : 'destructive';

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle>Assessment Results</CardTitle>
            <CardDescription>
              Completed Quick Assess report ready for review.
            </CardDescription>
          </div>
          <Badge variant={riskVariant} className="text-sm capitalize">
            Risk: {results.risk_level}
          </Badge>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-3">
          <div className="flex flex-col items-center justify-center">
            <p className="text-sm text-slate-500 mb-2">
              Cloud Readiness Score
            </p>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="60%"
                  outerRadius="100%"
                  data={readinessChartData}
                  startAngle={180}
                  endAngle={-180}
                >
                  <RadialBar
                    minAngle={15}
                    clockWise
                    dataKey="value"
                    cornerRadius={20}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {results.cloud_readiness_score}
            </p>
          </div>

          <div className="lg:col-span-2 space-y-4">
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">
                Key Findings
              </p>
              <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
                {(results.key_findings || []).slice(0, 5).map((finding) => (
                  <li key={finding}>{finding}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">
                Infrastructure Summary
              </p>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={infrastructureData}>
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <Tooltip />
                    <Bar dataKey="value" fill="#00D9C1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Technology Stack</CardTitle>
          <CardDescription>Technologies identified across workloads.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(results.technology_stack).map(([key, values]) => (
            <div key={key}>
              <p className="text-sm font-semibold text-slate-700 mb-2 capitalize">
                {key.replace('_', ' ')}
              </p>
              <div className="flex flex-wrap gap-2">
                {values.length === 0 && (
                  <span className="text-sm text-slate-500">No data</span>
                )}
                {values.map((value) => (
                  <Badge key={value} variant="secondary">
                    {value}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>Review, share, or start a new assessment.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button onClick={handleDownloadReport}>Download PDF</Button>
          <Button variant="outline" onClick={handleViewJson}>
            {showJson ? 'Hide details' : 'View detailed JSON'}
          </Button>
          <Button variant="secondary" onClick={handleShare}>
            Share report
          </Button>
          <Button variant="ghost" onClick={onStartNew}>
            Start new assessment
          </Button>
        </CardContent>
        {(shareMessage || shareUrl) && (
          <div className="px-4 pb-4 text-sm text-slate-500 space-y-1">
            {shareMessage && <p>{shareMessage}</p>}
            {shareUrl && (
              <p>
                Share URL:{' '}
                <a
                  href={shareUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-teal-600 underline"
                >
                  {shareUrl}
                </a>
              </p>
            )}
          </div>
        )}
        {showJson && (
          <pre className="max-h-80 overflow-auto bg-slate-900 text-slate-100 text-xs p-4 rounded-b-xl">
            {JSON.stringify(results, null, 2)}
          </pre>
        )}
      </Card>
    </div>
  );
}

