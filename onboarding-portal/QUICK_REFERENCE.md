# Quick Reference Card - Onboarding Portal

**Print this page and keep it handy!**

---

## 🚀 Quick Start (3 Commands)

```bash
cd onboarding-portal
docker-compose up
# Open http://localhost:3000
```

---

## 🔧 Essential Commands

### Start/Stop
```bash
docker-compose up -d              # Start in background
docker-compose down               # Stop services
docker-compose down -v            # Stop and delete data
docker-compose restart            # Restart all
docker-compose restart backend    # Restart one service
```

### Logs & Debug
```bash
docker-compose logs -f            # All logs (follow)
docker-compose logs -f backend    # Backend logs only
docker-compose ps                 # Check status
docker stats                      # Resource usage
```

### Database
```bash
# Backup
docker-compose exec postgres pg_dump -U agentic agentic_portal > backup.sql

# Restore
docker-compose exec -T postgres psql -U agentic agentic_portal < backup.sql

# Enter DB
docker-compose exec postgres psql -U agentic -d agentic_portal
```

### Rebuild
```bash
docker-compose up --build -d      # Rebuild and restart
docker system prune -a            # Clean up Docker
```

---

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |
| **Database** | localhost:5432 |

---

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `backend/.env` | Backend configuration |
| `frontend/.env` | Frontend configuration |
| `docker-compose.yml` | Docker services |

---

## 🔑 Critical Settings (Production)

```env
# backend/.env
SECRET_KEY=<generate-with-command-below>
DATABASE_URL=postgresql://agentic:SECURE_PWD@postgres:5432/agentic_portal
DEBUG=false
APP_ENV=production
DEMO_MODE=false
CORS_ORIGINS=https://yourdomain.com
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎨 Client Branding

| Change | File | Line |
|--------|------|------|
| Company Name | `frontend/src/components/Layout.tsx` | 34 |
| App Name | `backend/app/config.py` | 14 |
| Primary Color | `frontend/src/App.tsx` | 15 |
| Secondary Color | `frontend/src/App.tsx` | 18 |
| Logo | `frontend/public/logo.png` | - |

---

## 🐛 Common Issues

### Port Already in Use
```bash
lsof -i :3000                     # Find process
kill -9 <PID>                     # Kill process
```

### Database Connection Failed
```bash
docker-compose down -v            # Reset everything
docker-compose up
```

### Backend Won't Start
```bash
cd backend
cp .env.example .env
nano .env                         # Add SECRET_KEY
```

### CORS Error
Add frontend URL to `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## 📊 24 Agents by Phase

**Discovery** (8): infrastructure_scanner, application_profiler, data_discovery, network_topology_mapper, license_auditor, technical_debt_analyzer, api_catalog_builder, integration_discovery

**Assessment** (5): dependency_mapper, compliance_checker, security_hardening, cost_estimator, data_classifier

**Execution** (6): infrastructure_provisioner, application_migration, data_migration, cutover_coordinator, rollback_manager, validation_tester

**Optimization** (5): performance_monitor, cost_optimizer, security_validator, compliance_auditor, documentation_generator

---

## ✅ Production Checklist

- [ ] Change `SECRET_KEY`
- [ ] Change database password
- [ ] Set `DEBUG=false`
- [ ] Set `APP_ENV=production`
- [ ] Configure `CORS_ORIGINS`
- [ ] Enable HTTPS/SSL
- [ ] Test backup/restore
- [ ] Configure AWS credentials (if not demo)
- [ ] Update branding
- [ ] Test all phases

---

## 📞 Get Help

- **Full Docs**: `DEPLOYMENT_GUIDE.md`
- **Quick Start**: `QUICKSTART.md`
- **Architecture**: `docs/CUSTOMER_ONBOARDING_DESIGN.md`
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Default Credentials (Demo)

- **Database**: agentic / agentic123
- **Customer ID**: 00000000-0000-0000-0000-000000000001

---

**Last Updated**: 2025-01-15 | **Version**: 1.0.0
