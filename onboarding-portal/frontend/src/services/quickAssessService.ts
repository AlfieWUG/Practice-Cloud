import apiClient from './api';
import {
  AssessmentStatus,
  AssessmentResultSummary,
  AssessmentListResponse,
  QuickAssessUploadResponse,
  WorkflowLaunchResponse,
} from '@/types/quickAssess';

const http = apiClient.getHttpClient();
const BASE = '/api/v1/quick-assess';

type FileInput = File[] | FileList;

interface StatusRetryOptions {
  retries?: number;
  delayMs?: number;
}

const DEFAULT_RETRY: Required<StatusRetryOptions> = {
  retries: 3,
  delayMs: 1500,
};

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const handleError = (error: any): never => {
  const detail = error?.response?.data?.detail;
  const message =
    typeof detail === 'string'
      ? detail
      : detail?.message || error?.message || 'Quick Assess request failed';
  throw new Error(message);
};

const normalizeFiles = (files: FileInput): File[] =>
  Array.isArray(files) ? files : Array.from(files);

export async function uploadFiles(
  files: FileInput,
  onProgress?: (percent: number) => void
): Promise<QuickAssessUploadResponse> {
  const formData = new FormData();
  normalizeFiles(files).forEach((file) => formData.append('files', file));

  try {
    const { data } = await http.post<QuickAssessUploadResponse>(`${BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt) => {
        if (!onProgress || !evt.total) return;
        onProgress(Math.round((evt.loaded / evt.total) * 100));
      },
    });
    return data;
  } catch (error) {
    return handleError(error);
  }
}

export async function executeAssessment(
  assessmentId: string
): Promise<WorkflowLaunchResponse> {
  try {
    const { data } = await http.post<WorkflowLaunchResponse>(
      `${BASE}/${assessmentId}/execute`
    );
    return data;
  } catch (error) {
    return handleError(error);
  }
}

export async function getAssessmentStatus(
  assessmentId: string,
  options: StatusRetryOptions = {}
): Promise<AssessmentStatus> {
  const { retries, delayMs } = { ...DEFAULT_RETRY, ...options };

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const { data } = await http.get<AssessmentStatus>(`${BASE}/${assessmentId}/status`);
      return data;
    } catch (error) {
      if (attempt === retries) {
        return handleError(error);
      }
      await delay(delayMs);
    }
  }

  throw new Error('Unable to fetch assessment status');
}

export async function getAssessmentResults(
  assessmentId: string
): Promise<AssessmentResultSummary> {
  try {
    const { data } = await http.get<AssessmentResultSummary>(
      `${BASE}/${assessmentId}/results`
    );
    return data;
  } catch (error) {
    return handleError(error);
  }
}

export async function downloadReport(assessmentId: string): Promise<Blob> {
  try {
    const { data } = await http.get(`${BASE}/${assessmentId}/report`, {
      responseType: 'blob',
    });
    return data;
  } catch (error) {
    return handleError(error);
  }
}

export async function getRecentAssessments(
  limit = 5
): Promise<AssessmentListResponse> {
  try {
    const { data } = await http.get<AssessmentListResponse>(`${BASE}/list`, {
      params: { limit },
    });
    return data;
  } catch (error) {
    return handleError(error);
  }
}

export async function getAssessmentHistory(
  pageToken?: string,
  limit = 20
): Promise<AssessmentListResponse> {
  try {
    const { data } = await http.get<AssessmentListResponse>(`${BASE}/list`, {
      params: { limit, page_token: pageToken },
    });
    return data;
  } catch (error) {
    return handleError(error);
  }
}

