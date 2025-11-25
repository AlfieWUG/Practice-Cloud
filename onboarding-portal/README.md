# Nagarro Agentic Services - Customer Onboarding Portal

**Version**: 1.0 (MVP)  
**Status**: Development  
**Tech Stack**: React + TypeScript (Frontend), FastAPI + PostgreSQL (Backend)

---

## Overview

Customer-facing web portal for onboarding, project management, and agent execution. This portal enables customers to:
- Self-service onboard to the platform
- Deploy agents to their AWS accounts
- Create and manage migration projects
- Execute agents through an intuitive UI
- View results and download artifacts

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (React + TypeScript)                           │
│ • Dashboard                                              │
│ • Agent Execution UI                                     │
│ • Onboarding Wizard                                      │
│ • Results Viewer                                         │
│ Port: 3000                                               │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────────────────┐
│ BACKEND (FastAPI + PostgreSQL)                          │
│ • Customer Management API                                │
│ • Project CRUD API                                       │
│ • Agent Execution Proxy                                  │
│ • Real-time Status (WebSocket)                           │
│ Port: 8000                                               │
└─────────────────┬───────────────────────────────────────┘
                  │ Cross-Account IAM
┌─────────────────▼───────────────────────────────────────┐
│ CUSTOMER AWS ACCOUNT                                     │
│ • 24 Lambda Functions                                    │
│ • API Gateway                                            │
│ • DynamoDB, S3, Bedrock                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- **Node.js**: 18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **Docker**: (optional, for containerized dev)
- **PostgreSQL**: 14+ (or use Docker)

### Option 1: Local Development

```bash
# 1. Start Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Start Frontend (new terminal)
cd frontend
npm install
npm start  # Opens http://localhost:3000
```

### Option 2: Docker Compose

```bash
# Start everything with one command
docker-compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5432
```

---

## Project Structure

```
onboarding-portal/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── onboarding.py  # POST /onboarding/start
│   │   │   ├── projects.py    # CRUD /projects
│   │   │   ├── agents.py      # POST /agents/{name}/execute
│   │   │   └── results.py     # GET /results/{task_id}
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   ├── db.py              # Database connection
│   │   └── config.py          # Settings
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Main dashboard
│   │   │   ├── ProjectDetail.tsx      # Agent execution UI
│   │   │   ├── Onboarding.tsx         # Onboarding wizard
│   │   │   └── Results.tsx            # Results viewer
│   │   ├── components/
│   │   │   ├── AgentCard.tsx          # Agent status card
│   │   │   ├── PhaseAccordion.tsx     # Collapsible phase
│   │   │   ├── ExecutionControls.tsx  # Play/pause buttons
│   │   │   └── LiveLog.tsx            # Real-time logs
│   │   ├── hooks/
│   │   │   ├── useAgentExecution.ts   # Execute agent
│   │   │   ├── useRealtimeStatus.ts   # WebSocket status
│   │   │   └── useProjects.ts         # Project management
│   │   ├── services/
│   │   │   ├── api.ts                 # Axios client
│   │   │   └── websocket.ts           # WebSocket client
│   │   └── App.tsx                    # Main app component
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── deployment/                 # Deployment configs
│   ├── docker-compose.yml     # Local dev environment
│   ├── customer-stackset.yaml # CloudFormation for customer AWS
│   └── terraform/             # Terraform for control plane
│
└── README.md                  # This file
```

---

## Development Workflow

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start dev server (auto-reload)
uvicorn main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/ && isort app/

# Type checking
mypy app/
```

**Key Endpoints**:
- `GET /` - Health check
- `POST /api/v1/onboarding/start` - Start onboarding
- `POST /api/v1/projects` - Create project
- `POST /api/v1/agents/{name}/execute` - Execute agent
- `GET /api/v1/results/{task_id}` - Get agent results
- `WS /ws/{project_id}` - Real-time status updates

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (hot reload)
npm start  # http://localhost:3000

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint

# Type check
npm run type-check
```

**Key Pages**:
- `/` - Dashboard (project list)
- `/projects/:id` - Agent execution page
- `/onboarding` - Onboarding wizard
- `/results/:taskId` - Results viewer

---

## Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_portal

# JWT Secret
SECRET_KEY=your-super-secret-key-change-in-production

# AWS (for cross-account deployment)
AWS_REGION=eu-central-1
AWS_ACCOUNT_ID=your-nagarro-account-id

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,https://app.nagarro-agentic.com

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Environment
ENVIRONMENT=development
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENVIRONMENT=development
```

---

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Deployment

### Development
```bash
docker-compose up -d
```

### Staging/Production

1. **Backend**: Deploy to AWS ECS/Fargate or Lambda
   ```bash
   cd deployment/terraform
   terraform init
   terraform apply -var="environment=production"
   ```

2. **Frontend**: Deploy to S3 + CloudFront
   ```bash
   cd frontend
   npm run build
   aws s3 sync build/ s3://nagarro-agentic-portal-prod/
   aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
   ```

---

## Testing

### Backend Tests
```bash
cd backend
pytest -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test -- --coverage
```

### End-to-End Tests
```bash
# Coming soon: Playwright/Cypress tests
```

---

## Features Status

### ✅ Phase 1: MVP (Current)
- [x] Backend API structure
- [x] Frontend app scaffold
- [x] Dashboard page
- [x] Agent execution UI
- [ ] Onboarding wizard (in progress)
- [ ] Real-time status updates
- [ ] Results viewer

### 🔄 Phase 2: Enterprise (Next)
- [ ] SSO integration (SAML, OAuth)
- [ ] Multi-user & RBAC
- [ ] Advanced visualizations
- [ ] Mobile responsive design
- [ ] White-label support

### ⏳ Phase 3: Advanced (Future)
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Workflow orchestration UI
- [ ] AI-powered recommendations
- [ ] Cost optimization dashboard
- [ ] Partner marketplace

---

## Tech Stack Details

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **PostgreSQL**: Primary database
- **Redis**: Caching & sessions (future)
- **WebSockets**: Real-time updates

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Material-UI (MUI)**: Component library
- **Redux Toolkit**: State management
- **RTK Query**: Data fetching
- **React Router v6**: Routing
- **Socket.IO**: WebSocket client
- **Recharts**: Data visualization
- **React Flow**: Topology diagrams

---

## Development Guidelines

### Code Style

**Python** (Backend):
- Follow PEP 8
- Use `black` for formatting
- Use `isort` for import sorting
- Type hints required
- Docstrings for all public functions

**TypeScript** (Frontend):
- Follow Airbnb style guide
- Use Prettier for formatting
- ESLint for linting
- Strict TypeScript mode
- Component documentation

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/agent-execution-ui

# Make changes, commit often
git commit -m "feat: add agent execution controls"

# Push and create PR
git push origin feature/agent-execution-ui
```

**Commit Convention**: Use [Conventional Commits](https://www.conventionalcommits.org/)
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

---

## Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check environment variables
cat backend/.env

# Check logs
tail -f backend/logs/app.log
```

### Frontend won't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/

# Check CORS settings
# Ensure CORS_ORIGINS includes http://localhost:3000

# Check browser console for errors
```

### Database connection issues
```bash
# Reset database
cd backend
alembic downgrade base
alembic upgrade head

# Or recreate with Docker
docker-compose down -v
docker-compose up -d postgres
```

---

## Security

### Authentication
- JWT tokens for API authentication
- HTTPOnly cookies for session
- Token expiration (15 min access, 7 day refresh)

### Authorization
- Role-based access control (RBAC)
- Customer data isolation (tenant ID in all queries)

### Data Protection
- All passwords hashed (bcrypt)
- Secrets stored in AWS Secrets Manager
- TLS/SSL enforced in production
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (React escaping + CSP headers)

---

## Performance

### Backend Optimizations
- Database connection pooling
- Query optimization (eager loading)
- Redis caching for frequent queries
- Async I/O for external API calls

### Frontend Optimizations
- Code splitting (React.lazy)
- Image optimization
- Service worker (PWA)
- Memoization (useMemo, useCallback)
- Virtual scrolling for large lists

---

## Monitoring

### Metrics to Track
- API response times (p50, p95, p99)
- Error rates (4xx, 5xx)
- User activity (DAU, MAU)
- Agent execution success rate
- Customer onboarding funnel

### Tools
- **Backend**: Prometheus + Grafana
- **Frontend**: Google Analytics / Mixpanel
- **Errors**: Sentry
- **Logs**: CloudWatch / ELK Stack

---

## Support

### Documentation
- [API Docs](http://localhost:8000/docs)
- [Architecture Design](../docs/CUSTOMER_ONBOARDING_DESIGN.md)
- [Migration Transition Plan](../docs/MIGRATION_TRANSITION_PLAN.md)

### Contact
- **Email**: agentic-services@nagarro.com
- **Slack**: #onboarding-portal (internal)
- **Issues**: GitHub Issues

---

## License

Proprietary - Copyright (c) 2025 Nagarro. All rights reserved.

---

## Changelog

### v1.0.0 (2025-01-15)
- Initial MVP release
- Backend API with core endpoints
- Frontend dashboard and agent execution UI
- Docker development environment

---

**Last Updated**: 2025-01-15  
**Maintained By**: Nagarro Cloud Engineering Team
