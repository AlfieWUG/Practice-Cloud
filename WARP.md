# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AI-powered cloud migration and modernization platform leveraging specialized AI agents. This is a Python-based platform using AWS Bedrock (Claude 3), deployed on AWS with ECS Fargate. The system orchestrates 20+ specialized agents for enterprise cloud transformations.

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run with verbose output and coverage report
pytest -v --cov=src/agentic_services --cov-report=html --cov-report=term-missing

# Run specific test suite
pytest tests/agents/                    # All agent tests
pytest tests/integration/               # Integration tests only
pytest tests/agents/test_discovery.py   # Single test file

# Run tests by marker
pytest -m unit                          # Unit tests only
pytest -m integration                   # Integration tests only
pytest -m "not slow"                    # Exclude slow tests

# Run single test function
pytest tests/agents/test_discovery.py::TestDiscoveryAgent::test_execute
```

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting (CI/CD)
black --check src/ tests/
isort --check-only src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/ --ignore-missing-imports
```

### Running the Application
```bash
# Start Streamlit UI
streamlit run src/agentic_services/app_streamlit.py

# Run CLI tool
python -m agentic_services.cli --help

# Run specific agent workflow
python -m agentic_services.cli discovery \
  --requirements "Build a REST API for task management" \
  --project-id my-project

# Run complete workflow
python -m agentic_services.cli workflow \
  --requirements-file examples/sample_requirements.txt \
  --project-id demo-project \
  --output results.json

# Run with demo mode (no AWS required)
DEMO_MODE=true streamlit run src/agentic_services/app_streamlit.py
```

### Docker
```bash
# Build image
docker build -t agentic-services .

# Run container
docker run -p 8501:8501 --env-file .env agentic-services

# Run with demo mode
docker run -p 8501:8501 -e DEMO_MODE=true agentic-services
```

### Infrastructure & Deployment
```bash
# Deploy infrastructure with Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Deploy to specific environment
terraform workspace select dev
terraform apply -var="environment=dev"

# Update ECS service
aws ecs update-service \
  --cluster agentic-services-dev-cluster \
  --service agentic-services-dev-service \
  --force-new-deployment \
  --region eu-central-1
```

## Architecture

### High-Level Structure

The platform follows an **event-driven, multi-agent architecture**:

1. **Orchestrator Layer**: `src/agentic_services/orchestrator/`
   - `WorkflowOrchestrator` coordinates agent execution
   - Manages workflow state transitions (PENDING → RUNNING → COMPLETED/FAILED)
   - Supports full workflow or individual agent execution
   - Standard workflow: Discovery → Analysis → Planning → Artifact Generation

2. **Agent Layer**: `src/agentic_services/agents/`
   - All agents inherit from `BaseAgent` (base.py)
   - 20+ specialized agents including:
     - **Core workflow agents**: discovery, analysis, planning, artifact_generation
     - **Migration specialists**: application_migration, data_migration, infrastructure_provisioner
     - **Analysis agents**: dependency_mapper, data_classifier, security_hardening
     - **Operations**: compliance_checker, performance_monitor, cost_optimizer
   - Each agent follows async execution pattern with `execute(task)` method
   - Agents emit events via EventBridge for workflow coordination

3. **Tools Layer**: `src/agentic_services/tools/`
   - `aws_helper.py`: AWS service clients (Bedrock, S3, DynamoDB, EventBridge)
   - Shared utilities for AWS interactions

4. **Configuration**: `src/agentic_services/config/`
   - `settings.py`: Environment-based configuration management
   - Loads from environment variables with sensible defaults
   - Validates required settings for production deployments

5. **UI Layer**: `src/agentic_services/ui/` and `pages/`
   - Streamlit-based interface
   - `app_streamlit.py`: Main application entry point
   - Multi-page application in `pages/` directory

### Agent Base Class Pattern

All agents follow this pattern (see `agents/base.py`):

```python
class BaseAgent(ABC):
    """Provides common functionality:
    - AWS service clients (bedrock, s3, dynamodb, eventbridge)
    - State management (save_state, load_state)
    - Event publishing (emit_event)
    - AI invocation (invoke_ai)
    - Data storage (store_data)
    """
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method - must be implemented by subclasses"""
        pass
```

### Workflow Execution Pattern

1. User provides requirements via CLI or UI
2. `WorkflowOrchestrator` creates agent instances
3. Agents execute sequentially, passing data forward:
   - DiscoveryAgent → analyzes requirements → discovery_data
   - AnalysisAgent → technical deep-dive → analysis_data
   - PlanningAgent → creates roadmap → planning_data
   - ArtifactGenerationAgent → generates deliverables → artifacts
4. Each agent:
   - Validates input via `validate_task()`
   - Emits start event to EventBridge
   - Invokes Claude via AWS Bedrock for AI processing
   - Stores results to S3
   - Saves state to DynamoDB
   - Emits completion event
5. Results are returned and optionally persisted

### AWS Integration

- **AWS Bedrock**: Claude 3 Sonnet for AI agent reasoning
- **S3**: Discovery data, analysis results, generated artifacts
- **DynamoDB**: Agent state persistence, workflow tracking
- **EventBridge**: Event-driven agent coordination
- **ECS Fargate**: Container orchestration for production
- **VPC**: Network isolation with private subnets

## Development Guidelines

### Adding New Agents

1. Create new file in `src/agentic_services/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute(task)` method
4. Define `SYSTEM_PROMPT` class variable for AI behavior
5. Add to `__init__.py` exports
6. Write tests in `tests/agents/test_<agent_name>.py`

Example:
```python
from agentic_services.agents.base import BaseAgent

class MyAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a specialized agent that..."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_task(task, ['required_field'])
        # Implementation
        result = await self.invoke_ai(prompt=..., system_prompt=self.SYSTEM_PROMPT)
        return {'status': 'completed', 'result': result}
```

### Testing Strategy

- **Unit tests**: `tests/agents/`, `tests/tools/`, `tests/orchestrator/`
  - Mock AWS services using `tests/mocks/`
  - Use `pytest-asyncio` for async test support
  - Test fixtures in `tests/conftest.py`
  
- **Integration tests**: `tests/integration/`
  - May require AWS credentials or use LocalStack
  - Marked with `@pytest.mark.integration`

### Environment Configuration

Key environment variables (see `.env.example`):
- `AWS_REGION`: Default `eu-central-1`
- `BEDROCK_MODEL_ID`: Claude model (default: `anthropic.claude-3-sonnet-20240229-v1:0`)
- `APP_ENV`: `development` or `production`
- `DEMO_MODE`: Set to `true` for local testing without AWS
- S3 buckets: `S3_DISCOVERY_BUCKET`, `S3_ARTIFACTS_BUCKET`, `S3_LOGS_BUCKET`
- DynamoDB: `DYNAMODB_TABLE_PREFIX`

### CI/CD Pipeline (GitHub Actions)

The `.github/workflows/` directory contains 3 workflows:
1. **ci.yml**: Testing all 24 agents, linting, security scanning
2. **cd.yml**: Automated deployment to dev/staging/prod
3. **scheduled.yml**: Nightly tests and security scans

Key features:
- Parallel testing across 4 agent groups (Discovery, Assessment, Execution, Optimization)
- Automated coverage reporting with Codecov
- Security scanning (Safety, pip-audit, Bandit, Semgrep)
- Automated AWS deployments via Terraform
- PR checks and coverage comments

### Version Control

This project uses **GitHub** as the primary code repository with GitHub Actions for CI/CD.

## Project-Specific Notes

### Entry Points
- **CLI**: `src/agentic_services/cli.py` - Command-line interface with subcommands
- **Streamlit UI**: `src/agentic_services/app_streamlit.py` - Web interface
- **Module execution**: `python -m agentic_services.cli`

### Key Dependencies
- `anthropic==0.28.0`: Claude API client
- `boto3>=1.34.0`: AWS SDK
- `streamlit==1.32.0`: Web UI framework
- `pytest>=7.4.0`: Testing framework
- Code quality: `ruff`, `black`, `isort`, `mypy`

### Demo Mode
Set `DEMO_MODE=true` in `.env` to run without AWS credentials. Uses local mock data from `demo/artifacts/`.

### AWS Bedrock Access
Production deployment requires:
- AWS account with Bedrock access enabled
- Model access requested for Claude 3 Sonnet
- Proper IAM roles and permissions configured

### Troubleshooting Common Issues

**Import errors**: Ensure package is installed with `pip install -e .`

**AWS connection errors in local dev**: Either configure AWS credentials or enable `DEMO_MODE=true`

**Test failures**: Check that test database/fixtures are properly set up in `tests/conftest.py`

**Streamlit port conflicts**: Default port is 8501, change with `--server.port` flag
