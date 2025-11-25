# Testing Guide

## Overview

This project uses **pytest** for testing with **mock AWS services** to avoid costs during development.

**Current Status:**
- ✅ **52 tests** (100% pass rate)
- ✅ **47% overall coverage**
- ✅ **88% agent coverage** (Discovery, Analysis, Planning, Artifact Generation)
- ✅ **$0 AWS costs** during testing

---

## Quick Start

### Run All Tests
```bash
# Activate virtual environment
source venv-test/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/agentic_services --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/agents/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific agent
pytest tests/agents/test_discovery_agent.py -v

# Single test
pytest tests/agents/test_discovery_agent.py::TestDiscoveryAgent::test_execute_success -v
```

---

## Test Structure

```
tests/
├── mocks/
│   ├── __init__.py
│   └── aws_mocks.py              # Mock AWS services (Bedrock, S3, DynamoDB, EventBridge)
├── agents/
│   ├── test_discovery_agent.py       # 13 tests (98% coverage)
│   ├── test_analysis_agent.py        # 12 tests (90% coverage)
│   ├── test_planning_agent.py        # 13 tests (92% coverage)
│   └── test_artifact_generation_agent.py # 12 tests (72% coverage)
├── integration/
│   └── test_workflow_orchestrator.py  # 2 E2E tests
└── conftest.py                        # Shared fixtures
```

---

## Mock AWS Services

All tests use **mock AWS services** to avoid costs:

### Available Mocks
- `mock_bedrock_client` - AI responses
- `mock_s3_client` - File storage
- `mock_dynamodb_client` - State management
- `mock_eventbridge_client` - Event publishing

### Usage Example
```python
from tests.mocks import mock_bedrock_client

# Set custom AI response
mock_bedrock_client.set_mock_response("keyword", json.dumps({...}))

# Check invocation count
assert mock_bedrock_client.invocation_count == 1
```

All mocks are automatically reset between tests via `conftest.py`.

---

## Writing New Tests

### 1. Unit Test Template
```python
import pytest
from unittest.mock import patch
from tests.mocks import mock_bedrock_client, mock_s3_client

@pytest.mark.asyncio
class TestYourAgent:
    async def test_initialization(self):
        agent = YourAgent()
        assert agent.agent_id is not None
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    async def test_execute_success(self, sample_project_id):
        agent = YourAgent()
        result = await agent.execute({'project_id': sample_project_id})
        assert result['status'] == 'completed'
```

### 2. Use Fixtures
Available fixtures in `conftest.py`:
- `sample_project_id` - Test project ID
- `sample_requirements` - Sample requirements text
- `sample_discovery_data` - Mock discovery results
- `sample_analysis_data` - Mock analysis results  
- `sample_planning_data` - Mock planning results

### 3. Test Naming Convention
- `test_<feature>_success` - Happy path
- `test_<feature>_failure` - Error cases
- `test_<feature>_missing_<param>` - Validation
- `test_<feature>_with_<condition>` - Edge cases

---

## Coverage Guidelines

### Targets
- **New Code**: 80%+ coverage required
- **Agents**: 85%+ coverage target
- **Critical Paths**: 100% coverage (auth, payment, data migration)

### Check Coverage
```bash
# Terminal report
pytest tests/ --cov=src/agentic_services --cov-report=term-missing

# HTML report (recommended)
pytest tests/ --cov=src/agentic_services --cov-report=html
open htmlcov/index.html

# Fail if coverage below threshold
pytest tests/ --cov=src/agentic_services --cov-fail-under=45
```

---

## CI/CD Integration

### GitLab CI Pipeline
Tests run automatically on:
- ✅ Every merge request
- ✅ Commits to `main` branch
- ✅ Commits to `develop` branch

### Pipeline Stages
1. **Test**: Lint, unit tests, integration tests, security scans
2. **Build**: Docker image creation
3. **Validate**: Terraform validation
4. **Deploy**: Production deployment (manual)

### Test Job Details
```yaml
test:unit:
  stage: test
  script:
    - pytest tests/ -v --cov=src/agentic_services --cov-report=xml
  artifacts:
    reports:
      coverage_report: coverage.xml
      junit: junit.xml
```

### Viewing Results
- **Coverage**: Visible in merge request widget
- **Test Report**: In pipeline job output
- **HTML Report**: Download from CI artifacts

---

## Debugging Failed Tests

### Run with Verbose Output
```bash
pytest tests/ -vv --tb=short
```

### Run Specific Failed Test
```bash
pytest tests/agents/test_discovery_agent.py::TestDiscoveryAgent::test_execute_success -vv
```

### Debug with PDB
```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

### Check Logs
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

---

## Common Issues

### Issue: Import Errors
**Solution:** Ensure virtual environment is activated
```bash
source venv-test/bin/activate
pip install -r requirements.txt
```

### Issue: Async Warnings
**Solution:** Add `pytest-asyncio` to requirements
```bash
pip install pytest-asyncio
```

### Issue: Mock State Bleeding
**Solution:** Mocks are auto-reset via conftest. If issues persist, manually call:
```python
from tests.mocks import reset_all_mocks
reset_all_mocks()
```

---

## Performance

### Test Execution Time
- **Unit Tests**: ~1 second (52 tests)
- **Integration Tests**: ~0.7 seconds (2 tests)
- **Total**: < 2 seconds

### Parallel Execution
```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4
```

---

## Best Practices

### DO ✅
- Write tests for all new features
- Use mock AWS services
- Test both success and failure paths
- Keep tests fast (< 100ms each)
- Use descriptive test names
- Clean up resources in tests

### DON'T ❌
- Call real AWS services in tests
- Hardcode credentials in tests
- Skip writing tests for "simple" code
- Write flaky tests
- Test implementation details
- Leave commented-out test code

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- Project Confluence: [Testing Strategy]

---

## Questions?

- **Slack**: #agentic-services
- **Email**: agentic-services@nagarro.com
- **Wiki**: [Testing Best Practices]

---

**Last Updated**: 2024-11-11
**Test Count**: 52 tests
**Coverage**: 47% overall, 88% agents
