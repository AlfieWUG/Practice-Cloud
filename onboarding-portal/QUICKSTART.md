# Quickstart Guide - Onboarding Portal MVP

This guide will get you up and running with the Nagarro Agentic Services Onboarding Portal in minutes.

## 🚀 Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# From the onboarding-portal directory
cd /Users/aaldertoosthuizen/Projects/agentic-services/onboarding-portal

# Start all services (database, backend, frontend)
docker-compose up

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
```

**That's it!** Open http://localhost:3000 in your browser.

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 🛠️ Option 2: Local Development (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (running locally)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and set your SECRET_KEY and DATABASE_URL

# Set DEMO_MODE=true for testing without AWS
echo "DEMO_MODE=true" >> .env

# Start backend
uvicorn main:app --reload --port 8000

# Backend will be at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Start development server
npm run dev

# Frontend will be at: http://localhost:3000
```

---

## 📊 Using the Portal

### 1. Create a Project

1. Open http://localhost:3000
2. Click **"New Project"**
3. Fill in:
   - **Project Name**: e.g., "E-Commerce Migration"
   - **Description**: Brief overview
   - **Requirements**: Migration goals
4. Click **"Create Project"**

### 2. Execute Agents

1. Click on your project
2. You'll see 4 phases with agents:
   - **Discovery** (8 agents)
   - **Assessment** (5 agents)
   - **Execution** (6 agents)
   - **Optimization** (5 agents)
3. Click **"Run All"** on a phase to execute all agents
4. Watch real-time progress updates

### 3. View Results

- Each agent shows its status: Queued → Running → Completed
- Progress bars track execution
- Results are stored and displayed when complete

---

## 🔧 Configuration

### Backend (.env)

```env
# Demo Mode (no AWS required)
DEMO_MODE=true

# Database
DATABASE_URL=postgresql://agentic:agentic123@localhost:5432/agentic_portal

# Security
SECRET_KEY=your-secret-key-min-32-chars

# AWS (only needed if DEMO_MODE=false)
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AGENTIC_SERVICES_API_ENDPOINT=https://your-api-gateway-url
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Type Check

```bash
cd frontend
npm run type-check
```

---

## 📦 What's Included

### Backend API
- **FastAPI** application with async support
- **PostgreSQL** database with SQLAlchemy ORM
- **24 agents** organized by 4 phases
- **Demo mode** for testing without AWS
- **RESTful API** with automatic docs

### Frontend UI
- **React 18** with TypeScript
- **Material-UI** components
- **Real-time** agent execution tracking
- **Responsive** design
- **Phase-based** agent organization

### Database
- **Projects** table for migration projects
- **Agent Executions** table for tracking runs
- **Artifacts** table for generated files
- **Customers** table for multi-tenant support

---

## 🌐 API Endpoints

Visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

**Projects**
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project details

**Agents**
- `GET /api/v1/agents` - List all 24 agents
- `POST /api/v1/agents/{name}/execute` - Execute agent
- `POST /api/v1/agents/bulk-execute` - Execute multiple agents
- `GET /api/v1/agents/executions/project/{id}` - Get project executions

---

## 🐛 Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure SECRET_KEY is set

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check VITE_API_URL in frontend/.env
- Check CORS settings in backend

### Docker issues
- Try: `docker-compose down -v` then `docker-compose up`
- Check Docker is running
- Ensure ports 3000, 8000, 5432 are available

---

## 🎯 Next Steps

1. **Explore the UI** - Create projects, run agents
2. **Check API docs** - http://localhost:8000/docs
3. **Review the code** - See how agents are organized
4. **Connect to AWS** - Set DEMO_MODE=false and configure AWS credentials
5. **Deploy** - Use Docker Compose for production deployment

---

## 💡 Demo Mode

In demo mode (DEMO_MODE=true):
- No AWS credentials required
- Agent executions are simulated (5 seconds each)
- Mock results are returned
- Perfect for development and testing

To use real agents:
1. Set DEMO_MODE=false
2. Configure AWS credentials
3. Set AGENTIC_SERVICES_API_ENDPOINT to your deployed platform

---

## 📞 Need Help?

- Check README.md for detailed documentation
- Review NEXT_STEPS.md for development guidance
- See docs/CUSTOMER_ONBOARDING_DESIGN.md for architecture

---

**Ready to migrate!** 🚀
