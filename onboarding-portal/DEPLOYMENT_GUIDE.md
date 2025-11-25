# Deployment Guide - Customer Onboarding Portal

**Version**: 1.0.0  
**Last Updated**: 2025-01-15  
**Audience**: Engineers deploying for clients

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start (5 Minutes)](#quick-start-5-minutes)
4. [Local Development Setup](#local-development-setup)
5. [Production Deployment](#production-deployment)
6. [Client Customization](#client-customization)
7. [Configuration Reference](#configuration-reference)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Overview

This portal enables customers to:
- Create migration projects
- Execute 24 AI agents across 4 phases (Discovery, Assessment, Execution, Optimization)
- Track progress in real-time
- View results and download artifacts

**Tech Stack**:
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React + TypeScript + Material-UI
- **Deployment**: Docker + Docker Compose

---

## Prerequisites

### Required Software

#### For Demo/Development:
- **Docker Desktop** 4.0+ ([Install](https://www.docker.com/products/docker-desktop))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** (to clone/share repository)

#### For Local Development (without Docker):
- **Python** 3.11+
- **Node.js** 18+ and npm
- **PostgreSQL** 15+

### System Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space
- **Ports**: 3000, 8000, 5432 must be available
- **OS**: macOS, Linux, or Windows with WSL2

---

## Quick Start (5 Minutes)

This gets the portal running with **zero configuration** for demos.

### Step 1: Navigate to Portal Directory

```bash
cd /path/to/agentic-services/onboarding-portal
```

### Step 2: Start All Services

```bash
docker-compose up
```

**What happens**:
- PostgreSQL database starts on port 5432
- Backend API starts on port 8000
- Frontend UI starts on port 3000

### Step 3: Access the Portal

Open in browser: **http://localhost:3000**

### Step 4: Test It

1. Click **"New Project"**
2. Fill in project details
3. Click **"Create Project"**
4. Click on your project
5. Click **"Run All"** on any phase
6. Watch agents execute (5 seconds each in demo mode)

### Step 5: Verify APIs

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 6: Stop Services

```bash
# Ctrl+C to stop, then:
docker-compose down

# To remove all data and start fresh:
docker-compose down -v
```

✅ **Done!** Portal is now running in demo mode.

---

## Local Development Setup

For engineers who need to modify code.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration (see below)

# Start backend (with hot reload)
uvicorn main:app --reload --port 8000
```

**Backend will be at**: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
nano .env  # Edit if needed

# Start development server (with hot reload)
npm run dev
```

**Frontend will be at**: http://localhost:3000

### Database Setup (if running locally)

```bash
# Install PostgreSQL (if not installed)
brew install postgresql  # macOS
# OR
sudo apt install postgresql  # Linux

# Start PostgreSQL
brew services start postgresql  # macOS
# OR
sudo systemctl start postgresql  # Linux

# Create database
createdb agentic_portal

# Create user
psql -c "CREATE USER agentic WITH PASSWORD 'agentic123';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE agentic_portal TO agentic;"
```

---

## Production Deployment

### Option 1: Docker Compose (Recommended for Small-Medium Deployments)

#### Step 1: Clone Repository on Server

```bash
# On production server
git clone <your-repo-url>
cd agentic-services/onboarding-portal
```

#### Step 2: Configure for Production

```bash
# Create production environment file
cp backend/.env.example backend/.env

# Edit backend/.env
nano backend/.env
```

**Required changes for production**:

```env
# CRITICAL: Change these for production
SECRET_KEY=<generate-secure-random-32-char-string>
DATABASE_URL=postgresql://agentic:SECURE_PASSWORD@postgres:5432/agentic_portal
DEBUG=false
APP_ENV=production

# Set to false to use real AWS agents
DEMO_MODE=false

# AWS Configuration (if DEMO_MODE=false)
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AGENTIC_SERVICES_API_ENDPOINT=https://your-api-gateway-url.execute-api.eu-central-1.amazonaws.com

# CORS (set to your domain)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

**Generate secure SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 3: Create Production Docker Compose File

```bash
# Create docker-compose.prod.yml
nano docker-compose.prod.yml
```

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: agentic
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Set via environment variable
      POSTGRES_DB: agentic_portal
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - backend/.env
    depends_on:
      - postgres
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
```

#### Step 4: Deploy

```bash
# Set database password
export DB_PASSWORD="secure-random-password"

# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Step 5: Set Up Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt install nginx  # Ubuntu/Debian

# Create Nginx config
sudo nano /etc/nginx/sites-available/agentic-portal
```

```nginx
server {
    listen 80;
    server_name portal.yourdomain.com;

    # Redirect to HTTPS (after setting up SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/agentic-portal /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 6: Set Up SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d portal.yourdomain.com

# Certificate will auto-renew
```

### Option 2: AWS ECS/Fargate Deployment

See `deployment/aws/README.md` for detailed AWS deployment instructions.

**Quick Overview**:
1. Push Docker images to ECR
2. Create RDS PostgreSQL instance
3. Deploy backend to ECS Fargate
4. Deploy frontend to S3 + CloudFront
5. Configure ALB for routing

### Option 3: Kubernetes Deployment

See `deployment/k8s/README.md` for Kubernetes deployment.

---

## Client Customization

### Branding

#### Update Company Name

**Frontend** (`frontend/src/components/Layout.tsx`):
```typescript
// Line 34
Nagarro Agentic Services
// Change to:
{CLIENT_NAME} Migration Portal
```

**Backend** (`backend/app/config.py`):
```python
# Line 14
app_name: str = "Nagarro Agentic Services Portal"
# Change to:
app_name: str = "CLIENT_NAME Migration Portal"
```

#### Update Logo

Replace logo in `frontend/public/logo.png` with client logo.

#### Update Colors

**Frontend** (`frontend/src/App.tsx`):
```typescript
// Line 13-16
primary: {
  main: '#1976d2',  // Change to client's primary color
},
secondary: {
  main: '#dc004e',  // Change to client's secondary color
},
```

### Multi-Customer Setup

#### Option 1: Single Deployment (Multi-Tenant)

Each customer gets a unique `customer_id`. Already built-in.

**Frontend**: Update `NewProject.tsx` to capture customer selection.

#### Option 2: Separate Deployments

Deploy separate instance per customer:
1. Clone repository
2. Update branding
3. Deploy to customer-specific subdomain
4. Configure customer-specific AWS credentials

### Custom Agent Configuration

To add/remove agents, edit `backend/app/api/agents.py`:

```python
# Line 23-56
AGENTS_BY_PHASE = {
    "discovery": [
        "infrastructure_scanner",
        "application_profiler",
        # Add custom agents here
        "custom_discovery_agent",
    ],
    # ... other phases
}
```

---

## Configuration Reference

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | No | `development` | Environment: development/production |
| `DEBUG` | No | `false` | Enable debug mode |
| `SECRET_KEY` | **Yes** | - | JWT secret (min 32 chars) |
| `DATABASE_URL` | **Yes** | - | PostgreSQL connection string |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `DEMO_MODE` | No | `false` | Enable demo mode (no AWS) |
| `AWS_REGION` | No | `eu-central-1` | AWS region |
| `AWS_ACCESS_KEY_ID` | No* | - | AWS access key (*required if DEMO_MODE=false) |
| `AWS_SECRET_ACCESS_KEY` | No* | - | AWS secret key (*required if DEMO_MODE=false) |
| `AGENTIC_SERVICES_API_ENDPOINT` | No* | - | Main platform API URL (*required if DEMO_MODE=false) |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://localhost:8000` | Backend API URL |
| `VITE_ENV` | No | `development` | Environment |

### Database Connection Strings

**Format**: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

**Examples**:
```env
# Local
DATABASE_URL=postgresql://agentic:agentic123@localhost:5432/agentic_portal

# Docker Compose
DATABASE_URL=postgresql://agentic:agentic123@postgres:5432/agentic_portal

# AWS RDS
DATABASE_URL=postgresql://agentic:SECURE_PWD@mydb.abc123.eu-central-1.rds.amazonaws.com:5432/agentic_portal
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution**:
```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

#### 2. Database Connection Failed

**Error**: `FATAL: password authentication failed for user "agentic"`

**Solution**:
```bash
# Check DATABASE_URL in backend/.env
# Make sure password matches docker-compose.yml

# Reset database
docker-compose down -v
docker-compose up
```

#### 3. Backend Won't Start

**Error**: `SECRET_KEY field required`

**Solution**:
```bash
# Copy .env.example
cd backend
cp .env.example .env

# Generate secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
echo "SECRET_KEY=<generated-key>" >> .env
```

#### 4. Frontend Shows Blank Page

**Solution**:
```bash
# Check browser console for errors
# Usually means backend is not running

# Verify backend is running
curl http://localhost:8000/health

# Check API URL
cat frontend/.env
# Should be: VITE_API_URL=http://localhost:8000
```

#### 5. CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
```bash
# Add frontend URL to backend CORS_ORIGINS
nano backend/.env

# Add:
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com
```

### Debug Commands

```bash
# Check service status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart single service
docker-compose restart backend

# Rebuild and restart
docker-compose up --build -d

# Enter backend container
docker-compose exec backend bash

# Enter database
docker-compose exec postgres psql -U agentic -d agentic_portal

# Check database tables
docker-compose exec postgres psql -U agentic -d agentic_portal -c "\dt"
```

### Logs Location

**Docker Compose**:
```bash
docker-compose logs > debug.log
```

**Local Development**:
- Backend: Console output
- Frontend: Browser console + terminal
- Database: `/var/log/postgresql/` (Linux)

---

## Maintenance

### Backup Database

```bash
# Backup
docker-compose exec postgres pg_dump -U agentic agentic_portal > backup.sql

# With timestamp
docker-compose exec postgres pg_dump -U agentic agentic_portal > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T postgres psql -U agentic agentic_portal < backup.sql
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose up --build -d

# Check status
docker-compose ps
```

### Monitor Resources

```bash
# View resource usage
docker stats

# View disk usage
docker system df

# Clean up unused images
docker system prune -a
```

### Database Maintenance

```bash
# Enter database
docker-compose exec postgres psql -U agentic -d agentic_portal

# Check database size
\l+

# Check table sizes
SELECT 
    schemaname AS schema,
    tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Vacuum database (optimize)
VACUUM ANALYZE;
```

### Security Updates

```bash
# Update base images
docker-compose pull

# Rebuild with latest
docker-compose up --build -d

# Update Python packages
cd backend
pip install --upgrade -r requirements.txt

# Update Node packages
cd frontend
npm update
```

---

## Production Checklist

Before deploying to client:

### Security
- [ ] Change `SECRET_KEY` to secure random value
- [ ] Change database password
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (only ports 80, 443 open)
- [ ] Set `DEBUG=false`
- [ ] Restrict `CORS_ORIGINS` to known domains
- [ ] Review AWS IAM permissions
- [ ] Enable rate limiting (if needed)

### Configuration
- [ ] Set `APP_ENV=production`
- [ ] Configure proper `DATABASE_URL`
- [ ] Set client-specific branding
- [ ] Configure AWS credentials (if not using demo mode)
- [ ] Set `AGENTIC_SERVICES_API_ENDPOINT`
- [ ] Configure logging

### Testing
- [ ] Create test project
- [ ] Execute agents in all phases
- [ ] Verify results
- [ ] Test API endpoints
- [ ] Load test (if high traffic expected)
- [ ] Test backup/restore
- [ ] Test failure scenarios

### Documentation
- [ ] Document client-specific configuration
- [ ] Provide admin credentials
- [ ] Share API documentation URL
- [ ] Create runbook for common issues
- [ ] Document backup schedule

### Monitoring
- [ ] Set up health checks
- [ ] Configure alerts
- [ ] Set up log aggregation
- [ ] Monitor disk usage
- [ ] Monitor database performance

---

## Getting Help

### Documentation
- **Quick Start**: `QUICKSTART.md`
- **Development**: `NEXT_STEPS.md`
- **Architecture**: `docs/CUSTOMER_ONBOARDING_DESIGN.md`
- **API Docs**: http://localhost:8000/docs (when running)

### Support Contacts
- **Technical Issues**: [Add your support email]
- **AWS Issues**: [Add AWS support contact]
- **Emergency**: [Add emergency contact]

---

## Appendix

### Useful Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up --build -d

# Reset everything
docker-compose down -v && docker-compose up -d

# Backup DB
docker-compose exec postgres pg_dump -U agentic agentic_portal > backup.sql

# Check health
curl http://localhost:8000/health

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment Templates

**backend/.env** (Development):
```env
APP_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://agentic:agentic123@localhost:5432/agentic_portal
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
DEMO_MODE=true
```

**backend/.env** (Production):
```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<generate-secure-random-32-char-string>
DATABASE_URL=postgresql://agentic:SECURE_PASSWORD@postgres:5432/agentic_portal
CORS_ORIGINS=https://portal.yourdomain.com
DEMO_MODE=false
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AGENTIC_SERVICES_API_ENDPOINT=https://your-api.execute-api.eu-central-1.amazonaws.com
```

---

**Last Updated**: 2025-01-15  
**Version**: 1.0.0  
**Maintained By**: Nagarro Agentic Services Team
