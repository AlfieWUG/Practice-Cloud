/**
 * TypeScript type definitions for the application.
 */

// Project types
export enum ProjectStatus {
  PLANNING = 'planning',
  DISCOVERY = 'discovery',
  ASSESSMENT = 'assessment',
  EXECUTION = 'execution',
  OPTIMIZATION = 'optimization',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum MigrationPhase {
  DISCOVERY = 'discovery',
  ASSESSMENT = 'assessment',
  EXECUTION = 'execution',
  OPTIMIZATION = 'optimization',
}

export interface Project {
  id: string;
  customer_id: string;
  name: string;
  description?: string;
  requirements?: string;
  target_cloud: string;
  status: ProjectStatus;
  current_phase?: MigrationPhase;
  progress: number;
  created_at: string;
  updated_at: string;
}

// Agent Execution types
export enum AgentExecutionStatus {
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface AgentExecution {
  id: string;
  project_id: string;
  agent_name: string;
  phase: MigrationPhase;
  status: AgentExecutionStatus;
  progress: number;
  result?: Record<string, any>;
  error?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

// Artifact types
export enum ArtifactType {
  REPORT = 'report',
  DIAGRAM = 'diagram',
  EXCEL = 'excel',
  PDF = 'pdf',
  JSON = 'json',
  YAML = 'yaml',
}

export interface Artifact {
  id: string;
  project_id: string;
  agent_execution_id?: string;
  artifact_type: ArtifactType;
  file_name: string;
  s3_url: string;
  size_bytes?: number;
  created_at: string;
}

// Project with related data
export interface ProjectWithExecutions extends Project {
  agent_executions: AgentExecution[];
  artifacts: Artifact[];
}

// Agent metadata
export interface AgentMetadata {
  name: string;
  phase: MigrationPhase;
  description: string;
  icon: string;
}

// API request/response types
export interface CreateProjectRequest {
  customer_id: string;
  name: string;
  description?: string;
  requirements?: string;
  target_cloud?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  requirements?: string;
  status?: ProjectStatus;
  current_phase?: MigrationPhase;
  progress?: number;
}

export interface ExecuteAgentRequest {
  project_id: string;
  agent_name: string;
  phase: MigrationPhase;
}

// UI state types
export interface PhaseGroup {
  phase: MigrationPhase;
  agents: string[];
  executions: AgentExecution[];
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
}
