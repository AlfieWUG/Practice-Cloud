export interface AssessmentFile {
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
}

export type AssessmentStage =
  | 'ingestion'
  | 'parsing'
  | 'analysis'
  | 'report'
  | 'completed';

export interface AssessmentStatus {
  assessment_id: string;
  status: 'processing' | 'completed' | 'failed';
  stage: AssessmentStage;
  progress: number;
  estimated_seconds_remaining?: number;
  files: AssessmentFile[];
  error?: string;
  report_url?: string;
  report_json_url?: string;
  updated_at?: string;
}

export interface AssessmentResultSummary {
  cloud_readiness_score: number;
  key_findings: string[];
  infrastructure_counts: Record<string, number>;
  technology_stack: {
    languages: string[];
    frameworks: string[];
    cloud_services: string[];
    databases: string[];
    storage: string[];
  };
  risk_level: 'low' | 'medium' | 'high';
  report_url: string;
  report_json_url?: string;
  share_url?: string;
  recommendations?: {
    actions: {
      priority: 'High' | 'Medium' | 'Low';
      description: string;
    }[];
    timeline?: string;
  };
}

export interface AssessmentListItem {
  assessment_id: string;
  status: string;
  stage?: string;
  progress?: number;
  upload_time?: string;
  report_url?: string;
  cloud_readiness_score?: number;
}

export interface AssessmentListResponse {
  items: AssessmentListItem[];
  next_token?: string | null;
}

export interface UploadedAssessmentFileSummary {
  filename: string;
  size_bytes: number;
}

export interface QuickAssessUploadResponse {
  assessment_id: string;
  status: string;
  files: UploadedAssessmentFileSummary[];
}

export interface WorkflowLaunchResponse {
  assessment_id: string;
  workflow_id: string;
  status: string;
}

