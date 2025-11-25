/**
 * API client for backend communication.
 */
import axios, { AxiosInstance } from 'axios';
import {
  Project,
  ProjectWithExecutions,
  CreateProjectRequest,
  UpdateProjectRequest,
  AgentExecution,
  Artifact,
  MigrationPhase,
} from '@/types';
import {
  AssessmentStatus,
  AssessmentResultSummary,
  AssessmentListResponse,
} from '@/types/quickAssess';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

        // Attach API key header to every request
      this.client.interceptors.request.use((config) => {
        config.headers = config.headers ?? {};
        config.headers['X-API-Key'] = import.meta.env.VITE_QUICK_ASSESS_API_KEY ?? '';
        return config;
      });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Projects API
  async getProjects(customerId?: string): Promise<Project[]> {
    const params = customerId ? { customer_id: customerId } : {};
    const response = await this.client.get('/api/v1/projects', { params });
    return response.data;
  }

  async getProject(projectId: string): Promise<ProjectWithExecutions> {
    const response = await this.client.get(`/api/v1/projects/${projectId}`);
    return response.data;
  }

  async createProject(data: CreateProjectRequest): Promise<Project> {
    const response = await this.client.post('/api/v1/projects', data);
    return response.data;
  }

  async updateProject(
    projectId: string,
    data: UpdateProjectRequest
  ): Promise<Project> {
    const response = await this.client.put(`/api/v1/projects/${projectId}`, data);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.client.delete(`/api/v1/projects/${projectId}`);
  }

  // Agents API
  async getAgents(): Promise<Record<string, string[]>> {
    const response = await this.client.get('/api/v1/agents');
    return response.data;
  }

  async executeAgent(
    agentName: string,
    projectId: string,
    phase: MigrationPhase
  ): Promise<AgentExecution> {
    const response = await this.client.post(
      `/api/v1/agents/${agentName}/execute`,
      {
        project_id: projectId,
        agent_name: agentName,
        phase: phase,
      }
    );
    return response.data;
  }

  async bulkExecuteAgents(
    projectId: string,
    phase: MigrationPhase,
    agentNames: string[]
  ): Promise<AgentExecution[]> {
    const response = await this.client.post('/api/v1/agents/bulk-execute', {
      project_id: projectId,
      phase: phase,
      agent_names: agentNames,
    });
    return response.data;
  }

  async getAgentStatus(
    agentName: string,
    executionId: string
  ): Promise<AgentExecution> {
    const response = await this.client.get(
      `/api/v1/agents/${agentName}/status/${executionId}`
    );
    return response.data;
  }

  async getProjectExecutions(projectId: string): Promise<AgentExecution[]> {
    const response = await this.client.get(
      `/api/v1/agents/executions/project/${projectId}`
    );
    return response.data;
  }

  // Artifacts API
  async getProjectArtifacts(projectId: string): Promise<Artifact[]> {
    const response = await this.client.get(
      `/api/v1/projects/${projectId}/artifacts`
    );
    return response.data;
  }

  // Quick Assess
  async getAssessmentStatus(assessmentId: string): Promise<AssessmentStatus> {
    const response = await this.client.get(
      `/api/v1/quick-assess/${assessmentId}/status`
    );
    return response.data;
  }

  async getAssessmentResults(
    assessmentId: string
  ): Promise<AssessmentResultSummary> {
    const response = await this.client.get(
      `/api/v1/quick-assess/${assessmentId}/results`
    );
    return response.data;
  }

  async shareAssessmentReport(
    assessmentId: string
  ): Promise<{ share_url: string }> {
    const response = await this.client.post(
      `/api/v1/quick-assess/${assessmentId}/share`
    );
    return response.data;
  }

  async listAssessments(limit = 5): Promise<AssessmentListResponse> {
    const response = await this.client.get('/api/v1/quick-assess/list', {
      params: { limit },
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  getHttpClient(): AxiosInstance {
    return this.client;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
