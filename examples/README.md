# Agentic Services - Usage Examples

This directory contains examples demonstrating how to use the Agentic Services platform.

## Files

- **`simple_workflow.py`** - Complete workflow example with hardcoded requirements
- **`sample_requirements.txt`** - Sample requirements file for CLI testing

## Running Examples

### 1. Using the Python Script

```bash
# Run the simple workflow example
python examples/simple_workflow.py
```

### 2. Using the CLI Tool

```bash
# Run full workflow with requirements file
python -m agentic_services.cli workflow \
  --requirements-file examples/sample_requirements.txt \
  --project-id ecommerce-platform \
  --output results.json

# Run full workflow with inline requirements
python -m agentic_services.cli workflow \
  --requirements "Build a REST API for task management" \
  --project-id task-api

# Run discovery only
python -m agentic_services.cli discovery \
  --requirements-file examples/sample_requirements.txt \
  --output discovery_results.json

# Run with context and constraints
python -m agentic_services.cli workflow \
  --requirements "Build a mobile app" \
  --context "iOS and Android, React Native preferred" \
  --constraints '{"timeline": "8 weeks", "team_size": 3, "budget": "low"}' \
  --output mobile_app_results.json
```

### 3. Running Individual Agents

```bash
# Discovery
python -m agentic_services.cli discovery \
  --requirements "Build a chat application" \
  --output discovery.json

# Analysis (requires discovery results)
python -m agentic_services.cli analysis \
  --discovery-file discovery.json \
  --output analysis.json

# Planning (requires analysis results)
python -m agentic_services.cli planning \
  --analysis-file analysis.json \
  --constraints '{"timeline": "6 weeks"}' \
  --output planning.json

# Artifacts (requires planning results)
python -m agentic_services.cli artifacts \
  --planning-file planning.json \
  --types code documentation \
  --output artifacts.json
```

## CLI Options

### Global Options
- `--debug` - Enable debug logging
- `--version` - Show version information

### Workflow Command
- `--requirements, -r` - Requirements text (inline)
- `--requirements-file, -f` - Path to requirements file
- `--context, -c` - Additional context
- `--project-id, -p` - Project ID (auto-generated if not provided)
- `--output, -o` - Output file (prints to stdout if not specified)
- `--constraints` - JSON string with constraints

### Constraints Format
```json
{
  "timeline": "4 weeks",
  "team_size": 2,
  "budget": "low|medium|high",
  "experience_level": "beginner|intermediate|expert"
}
```

## Expected Output

When running a workflow, you'll see:

```
2025-01-01 10:00:00 - INFO - Starting workflow for project: task-api
2025-01-01 10:00:00 - INFO - Step 1/4: Running DiscoveryAgent...
2025-01-01 10:00:15 - INFO - Discovery completed for project: task-api
2025-01-01 10:00:15 - INFO - Step 2/4: Running AnalysisAgent...
2025-01-01 10:00:30 - INFO - Analysis completed for project: task-api
2025-01-01 10:00:30 - INFO - Step 3/4: Running PlanningAgent...
2025-01-01 10:00:45 - INFO - Planning completed for project: task-api
2025-01-01 10:00:45 - INFO - Step 4/4: Running ArtifactGenerationAgent...
2025-01-01 10:01:00 - INFO - Artifacts generated for project: task-api
2025-01-01 10:01:00 - INFO - Workflow completed successfully in 60.00s
```

## Results Structure

The output JSON contains:

```json
{
  "workflow_id": "uuid",
  "project_id": "task-api",
  "start_time": "2025-01-01T10:00:00Z",
  "end_time": "2025-01-01T10:01:00Z",
  "duration_seconds": 60.0,
  "status": "completed",
  "agents_executed": ["DiscoveryAgent", "AnalysisAgent", "PlanningAgent", "ArtifactGenerationAgent"],
  "discovery": {
    "project_type": "web_api",
    "technology_stack": {},
    "s3_uri": "s3://bucket/path",
    ...
  },
  "analysis": {
    "architecture_analysis": {},
    "s3_uri": "s3://bucket/path",
    ...
  },
  "planning": {
    "implementation_plan": {},
    "s3_uri": "s3://bucket/path",
    ...
  },
  "artifacts": {
    "generated_artifacts": {},
    "s3_uri": "s3://bucket/path",
    ...
  }
}
```

## Troubleshooting

### AWS Credentials Not Configured

If you see AWS credential errors, set up local mocks or configure AWS:

```bash
# Option 1: Configure AWS CLI
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Import Errors

Make sure you're running from the project root:

```bash
# Install in development mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Next Steps

1. Modify `simple_workflow.py` with your own requirements
2. Create custom workflows by composing agents
3. Integrate with your own systems via the Python API
4. Deploy to AWS using the Terraform infrastructure

## Need Help?

- Check the main README: `../README.md`
- Review agent documentation: `../src/agentic_services/agents/`
- See the orchestrator: `../src/agentic_services/orchestrator/workflow.py`
