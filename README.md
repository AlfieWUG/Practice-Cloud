# Nagarro Agentic Services Platform

AI-powered cloud migration and modernization platform leveraging specialized AI agents to accelerate enterprise cloud transformations by 60-80% while reducing risk and improving accuracy.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-eu--central--1-orange.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 🚀 Overview

The Nagarro Agentic Services Platform deploys **24 specialized AI agents** organized in 4 migration phases to automate enterprise cloud migration to AWS:

### Discovery Phase (8 agents)
- Infrastructure Scanner, Application Profiler, Data Discovery, Integration Mapper
- Security Auditor, Network Analyzer, Performance Baseline, Licensing Analyzer

### Assessment Phase (5 agents)
- Dependency Mapper, Compliance Checker, Cost Estimator
- Risk Assessment, Capacity Planner

### Execution Phase (6 agents)
- Infrastructure Provisioner, Data Migration, Application Migration
- Configuration Manager, Testing Orchestrator, Rollback Manager

### Optimization Phase (5 agents)
- Performance Optimizer, Cost Optimizer, Security Hardening
- Monitoring Setup, Documentation Generator

## 📊 Key Benefits

- **60-80% faster** migration planning (days vs months)
- **40-60% cost reduction** compared to traditional consulting
- **Zero missed dependencies** with AI-powered mapping
- **99%+ accuracy** in discovery and analysis
- **Professional artifacts** generated automatically

## 🏗️ Architecture

**Deployment:** AWS eu-central-1 (Frankfurt)  
**Architecture:** 100% Serverless (Lambda, API Gateway, DynamoDB)  
**Core Technology:** AWS Bedrock (Claude 3 Sonnet), EventBridge, S3

See [Platform Architecture v2](docs/architecture/PLATFORM_ARCHITECTURE_v2.md) for complete technical details.
See [Migration Transition Plan](docs/MIGRATION_TRANSITION_PLAN.md) for E2E migration approach.

## 📁 Project Structure

```
agentic-services/
├── src/agentic_services/      # Main application code
│   ├── agents/                # 24 AI agent implementations
│   ├── orchestrator/          # Agent coordination engine
│   ├── tools/                 # AWS utilities and helpers
│   └── ui/                    # Streamlit interface
├── tests/                     # 24 comprehensive test suites
├── infrastructure/            # AWS IaC (Terraform + Lambda)
│   ├── terraform/             # Infrastructure as Code
│   └── lambda/                # 24 Lambda functions
├── docs/                      # Architecture & migration docs
│   ├── architecture/          # Platform architecture v2
│   ├── MIGRATION_TRANSITION_PLAN.md  # E2E migration approach
│   └── PROJECT_STATUS.md      # Current project status
└── .github/workflows/         # CI/CD pipeline (3 workflows)
```

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentic-services

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials
```

### Run Locally

```bash
# Start Streamlit UI
streamlit run src/agentic_services/app_streamlit.py

# Or run in demo mode
python -m src.agentic_services.demo.demo_mode
```

### Run with Docker

```bash
# Build image
docker build -t nagarro-agentic-services .

# Run container
docker run -p 8501:8501 --env-file .env nagarro-agentic-services
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agentic_services --cov-report=html

# Run specific test suite
pytest tests/agents/
```

## 🏗️ Deployment

### AWS Infrastructure (Serverless)

```bash
# Build Lambda packages
cd infrastructure/lambda
./build.sh

# Deploy infrastructure
cd ../terraform
terraform init
terraform plan
terraform apply

# Get API endpoint
terraform output api_gateway_endpoint
```

### Application Deployment

```bash
# Using CI/CD (GitHub Actions)
git push origin main  # Triggers automated deployment

# Manual deployment
./infrastructure/lambda/build.sh
cd infrastructure/terraform && terraform apply
```

## 📚 Documentation

- **[Project Status](docs/PROJECT_STATUS.md)** - Current status, metrics, and next steps
- **[Platform Architecture v2](docs/architecture/PLATFORM_ARCHITECTURE_v2.md)** - Complete technical architecture (654 lines)
- **[Migration Transition Plan](docs/MIGRATION_TRANSITION_PLAN.md)** - E2E migration approach (844 lines)
- **[WARP.md](WARP.md)** - Development guide (commands, architecture, agents)
- **[Deployment Guide](infrastructure/DEPLOYMENT_GUIDE.md)** - Step-by-step deployment (458 lines)
- **[Business Abstract](docs/business/business-abstract.md)** - Value proposition and market strategy

## 🔑 Key Features

### Discovery & Analysis
- Multi-source infrastructure discovery (vCenter, CMDB, AWS)
- AI-powered dependency mapping (1000+ connections)
- Risk scoring and compliance validation

### Planning & Architecture
- Automated wave planning with rollback strategies
- Target architecture design aligned with AWS Well-Architected
- Service sizing and cost estimation

### Artifact Generation
- Executive presentations (PowerPoint)
- Technical documentation (Markdown/PDF)
- Architecture diagrams (automated)
- Custom reports

### Testing & Validation
- Pre-migration checks
- Post-migration validation
- Performance benchmarking
- Compliance verification

## 🔐 Security

- Encryption at rest (AWS KMS)
- Encryption in transit (TLS 1.3)
- VPC isolation with security groups
- IAM role-based access control
- AWS Secrets Manager for credentials

## 🤝 Contributing

This is a proprietary Nagarro project. For internal contributions:

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit pull request for review

## 📝 License

Proprietary - Copyright (c) 2024 Nagarro. All rights reserved.

## 🆘 Support

- **Internal Wiki:** [Confluence Page]
- **Slack Channel:** #agentic-services
- **Email:** agentic-services@nagarro.com

## 🗺️ Roadmap

### Q4 2024
- ✅ AWS FTR validation
- ✅ Core agent implementation
- ⏳ AWS Marketplace listing

### Q1 2025
- ⏳ Multi-cloud support (Azure, GCP)
- ⏳ Enhanced visualization
- ⏳ Mobile application

### Q2-Q4 2025
- ⏳ Industry-specific solutions
- ⏳ Partner ecosystem
- ⏳ Advanced AI model training

---

**Built with ❤️ by Nagarro**
