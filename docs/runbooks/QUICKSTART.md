# Quick Start Guide - Agentic Services

Get up and running with the Agentic Services platform in 5 minutes!

## Prerequisites

- Python 3.11+
- pip
- (Optional) AWS account for deployment

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd agentic-services

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install project in development mode
pip install -e .
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional for local testing)
# For local testing without AWS, you can skip AWS configuration
```

## Running Your First Workflow

### Option 1: CLI Tool (Recommended)

```bash
# Run a simple discovery
python -m agentic_services.cli discovery \
  --requirements "Build a REST API for task management" \
  --project-id my-first-project

# Run complete workflow with sample requirements
python -m agentic_services.cli workflow \
  --requirements-file examples/sample_requirements.txt \
  --project-id ecommerce-demo \
  --output results.json
```

### Option 2: Python Script

```bash
# Run the example workflow
python examples/simple_workflow.py
```

### Option 3: Interactive (Python REPL)

```python
import asyncio
from agentic_services.agents import DiscoveryAgent

async def test():
    agent = DiscoveryAgent()
    result = await agent.execute({
        'project_id': 'test-123',
        'requirements': 'Build a simple blog platform'
    })
    print(result)

asyncio.run(test())
```

## CLI Commands Cheat Sheet

```bash
# Full workflow
python -m agentic_services.cli workflow --requirements "Your requirements" --project-id myproject

# Discovery only
python -m agentic_services.cli discovery --requirements "Your requirements" --output discovery.json

# Analysis (requires discovery.json)
python -m agentic_services.cli analysis --discovery-file discovery.json --output analysis.json

# Planning (requires analysis.json)
python -m agentic_services.cli planning --analysis-file analysis.json --output planning.json

# Artifacts (requires planning.json)
python -m agentic_services.cli artifacts --planning-file planning.json --output artifacts.json

# Help
python -m agentic_services.cli --help
python -m agentic_services.cli workflow --help
```

## Project Structure

```
agentic-services/
├── src/agentic_services/
│   ├── agents/              # AI agents (Discovery, Analysis, Planning, Artifacts)
│   ├── orchestrator/        # Workflow orchestration
│   ├── tools/               # AWS helpers and utilities
│   ├── config/              # Configuration
│   └── cli.py               # Command-line interface
├── examples/                # Usage examples
├── tests/                   # Test suite
├── infrastructure/          # Terraform IaC
│   └── terraform/           # AWS deployment configs
└── .gitlab-ci.yml           # CI/CD pipeline
```

## Understanding the Workflow

The platform follows a 4-agent workflow:

```
User Requirements
      ↓
1. DISCOVERY AGENT
   → Analyzes requirements
   → Identifies project type & tech stack
   → Extracts components
      ↓
2. ANALYSIS AGENT  
   → Technical deep-dive
   → Architecture analysis
   → Risk assessment
      ↓
3. PLANNING AGENT
   → Implementation roadmap
   → Task breakdown
   → Timeline estimation
      ↓
4. ARTIFACT GENERATION AGENT
   → Generate code scaffolds
   → Create documentation
   → Setup configs
      ↓
   Final Deliverables
```

## Next Steps

### For Local Development

1. ✅ Review example scripts in `examples/`
2. ✅ Check agent implementations in `src/agentic_services/agents/`
3. ✅ Customize prompts and workflows
4. ✅ Add tests in `tests/`

### For AWS Deployment

1. ⏳ Get AWS account credentials
2. ⏳ Follow `CI-CD-SETUP.md` for GitLab CI/CD
3. ⏳ Follow `infrastructure/terraform/README.md` for IaC deployment
4. ⏳ Configure Bedrock model access

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the project root and have installed the package
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### AWS Errors (Local Testing)

If testing locally without AWS, you'll see connection errors for:
- Bedrock (AI model)
- S3 (storage)
- DynamoDB (state management)
- EventBridge (events)

**Solution**: Mock these services or configure AWS credentials:

```bash
aws configure
# Enter your credentials
```

### Dependencies Not Found

```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt
```

## Example: Quick Test

Create a file `test_quick.py`:

```python
#!/usr/bin/env python3
import asyncio
import logging
from agentic_services.agents import DiscoveryAgent

logging.basicConfig(level=logging.INFO)

async def main():
    print("Testing Discovery Agent...")
    agent = DiscoveryAgent()
    
    result = await agent.execute({
        'project_id': 'quick-test',
        'requirements': '''
        Build a simple REST API for a todo list application.
        - CRUD operations for tasks
        - User authentication
        - PostgreSQL database
        - Docker containerization
        '''
    })
    
    print("\n=== DISCOVERY RESULTS ===")
    print(f"Project Type: {result.get('project_type')}")
    print(f"Status: {result.get('status')}")
    print(f"S3 URI: {result.get('s3_uri')}")
    print("="*50)

if __name__ == '__main__':
    asyncio.run(main())
```

Run it:
```bash
python test_quick.py
```

## Documentation

- **Agent Documentation**: See `src/agentic_services/agents/`
- **Orchestrator**: See `src/agentic_services/orchestrator/workflow.py`
- **Examples**: See `examples/README.md`
- **Infrastructure**: See `infrastructure/terraform/README.md`
- **CI/CD**: See `CI-CD-SETUP.md`

## Support

- Check existing documentation in the project
- Review error logs in `logs/`
- Test with example requirements first
- Verify AWS configuration (if using AWS features)

---

**Ready to build something awesome? Start with the CLI or examples!** 🚀
