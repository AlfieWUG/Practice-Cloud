# Dashboard Features Roadmap

## 🎯 Implementation Progress

### ✅ Phase 1: Foundation & Analytics (COMPLETED)

#### 1. Persistent Storage with SQLite ✅
**Location**: `src/agentic_services/database/`

**Features Implemented:**
- Complete SQLite database layer with 7 tables:
  - `projects` - All project data with JSON fields
  - `agent_executions` - Track all agent runs with status
  - `artifacts` - Store generated migration artifacts
  - `notifications` - Alert system
  - `checklist_items` - Migration readiness tracking
  - `cost_tracking` - Cost management data
  - `activity_log` - Audit trail
- Singleton pattern with `get_db()` helper
- Comprehensive CRUD operations for all entities
- Activity logging for audit compliance
- Indexes for performance optimization

**Benefits:**
- ✅ Data persists across sessions
- ✅ Foundation for all advanced features
- ✅ Performance optimized with indexes
- ✅ Foreign key relationships maintain data integrity

#### 2. Analytics Dashboard ✅
**Location**: `pages/8_📈_Analytics.py`

**Features Implemented:**
- **KPI Cards**: Total projects, executions, success rate, avg execution time, completion rate
- **Interactive Charts** (using Plotly):
  - Project Status Distribution (Donut chart)
  - Projects by Phase (Bar chart)
  - Execution Status by Agent (Stacked bar)
  - Top Performing Agents (Success rate cards)
  - Project Progress Timeline (Horizontal bar chart)
- **Recent Activity Feed**: Last 20 activities with time-ago formatting
- **Real-time Refresh** button
- Dark theme Plotly charts matching Nagarro branding

**Navigation:**
- Added "Analytics & Reports" section to main nav
- Accessible via sidebar button

---

## 🚀 Phase 2: Reports & Readiness (NEXT)

### 3. Reports & Artifacts Hub 📊
**Planned Location**: `pages/9_📊_Reports.py`

**To Implement:**
- Display all generated artifacts by project
- Filter by type (wave plans, diagrams, docs, configs)
- Download artifacts as PDF/Word/Excel
- Preview inline (PDF viewer, markdown renderer)
- Search across artifact content
- Version history for artifacts
- Share links with expiry

**Database Support:**
- Already in place via `artifacts` table
- Need to add file storage integration (S3 or local)

---

### 4. Migration Checklist & Readiness ✅
**Planned Location**: `pages/10_✅_Readiness.py`

**To Implement:**
- Pre-migration checklist by category:
  - Infrastructure Discovery (100%)
  - Assessment Complete (100%)
  - Planning Approved (100%)
  - Credentials Configured (100%)
  - Testing Strategy (100%)
- **Readiness Score** (0-100%) calculator
- **Blocker Identification**: Show critical missing items
- Progress bar for each category
- Mark items complete with timestamp
- Export checklist as PDF

**Database Support:**
- Already in place via `checklist_items` table
- Needs default checklist seeding logic

---

## 📋 Phase 3: Collaboration & Monitoring (PLANNED)

### 5. Notifications & Alerts Center 🔔
**Planned Location**: `pages/11_🔔_Notifications.py`

**To Implement:**
- **Notification Types**:
  - Agent execution (success/failure)
  - Budget alerts
  - Security findings
  - Milestone achievements
  - System health warnings
- **Severity Levels**: Info, Warning, Error, Critical
- **Actions**: Mark as read, dismiss, snooze
- **Bell icon** in header with unread count
- **Toast notifications** for real-time alerts
- Filter by severity, type, project
- Notification settings (email, Slack, webhooks)

**Database Support:**
- Already in place via `notifications` table

---

### 6. Cost Management Dashboard 💰
**Planned Location**: `pages/12_💰_Cost_Management.py`

**To Implement:**
- **Budget Tracking**:
  - Total budget vs actual spend
  - Budget by phase (Discovery, Assessment, Execution, Optimization)
  - Cost alerts (80%, 90%, 100% thresholds)
- **Cost Trends**:
  - Daily/Weekly/Monthly cost charts
  - Cost by AWS service
  - Cost by resource type
- **TCO Calculator**:
  - Current state vs target state
  - 3-year cost comparison
  - Savings projection
- **Optimization Recommendations**:
  - From cost_optimizer agent
  - Implement recommendations with one click

**Database Support:**
- Already in place via `cost_tracking` table
- Need integration with AWS Cost Explorer API

---

## 🔍 Phase 4: Visualization & Discovery (PLANNED)

### 7. Infrastructure Discovery Visualization 🗺️
**Planned Location**: `pages/13_🗺️_Infrastructure.py`

**To Implement:**
- **Interactive Dependency Graph**:
  - Using `vis.js` or `cytoscape.js`
  - Nodes: Applications, databases, services
  - Edges: Dependencies (database, network, API)
  - Color-code by criticality/complexity
  - Click to drill down
- **Network Topology Viewer**:
  - VPC, subnets, security groups
  - Visual representation of network architecture
- **Resource Inventory Table**:
  - Filterable/sortable list
  - Export to CSV/Excel
  - Bulk actions (tag, migrate wave)
- **Compliance Status Matrix**:
  - Pass/Fail by resource
  - Remediation actions

**Implementation:**
- Embed JavaScript library (vis.js)
- Fetch data from `discovery` and `dependency_mapper` agents
- Store in new table or parse from artifacts

---

## ⚙️ Phase 5: Settings & Configuration (PLANNED)

### 8. Settings & Configuration ⚙️
**Planned Location**: `pages/14_⚙️_Settings.py`

**To Implement:**
- **User Profile**:
  - Name, email, role
  - Avatar upload
- **Notification Preferences**:
  - Email notifications (on/off by type)
  - Slack integration (webhook URL)
  - Webhook endpoints for external systems
- **API Keys Management**:
  - Generate/revoke API keys
  - View usage statistics
- **Integration Settings**:
  - GitHub/GitLab tokens
  - Jira integration (link issues to migrations)
  - ServiceNow CMDB sync
- **Theme Settings**:
  - Dark/Light mode toggle (if implemented)
  - Logo upload for custom branding

---

## 🎨 Phase 6: UI/UX Enhancements (ONGOING)

### 9. Global Search 🔍
**Location**: Add to `app_streamlit.py` header

**To Implement:**
- Search bar in top navigation
- Search across:
  - Projects (name, description)
  - Agents (name, results)
  - Artifacts (content)
  - Activity log
- Keyboard shortcut: `Ctrl+K` or `/`
- Search results page with relevance scoring

---

### 10. Breadcrumb Navigation 🍞
**Location**: Add to all pages

**To Implement:**
- Show current path: Home > Projects > Project Name > Agent Execution
- Clickable breadcrumbs to navigate back
- Add to top of each page below header

---

### 11. Export Capabilities 📤
**Location**: Add to each page

**To Implement:**
- Export project data as JSON/CSV
- Export charts as PNG/SVG
- Export reports as PDF
- "Export" button on each page
- Bulk export (all projects)

---

### 12. Keyboard Shortcuts ⌨️
**Location**: Global

**To Implement:**
- `Ctrl+K`: Global search
- `Ctrl+N`: New project
- `Ctrl+P`: Projects page
- `Ctrl+A`: Analytics
- `?`: Show keyboard shortcuts modal
- Implement with JavaScript injection

---

## 🔐 Phase 7: Security & Auth (PLANNED)

### 13. Authentication System 🔐
**Location**: New module `src/agentic_services/auth/`

**To Implement:**
- **User Roles**:
  - Admin (full access)
  - Operator (create/execute projects)
  - Viewer (read-only)
- **Login Page**: Username/password or SSO
- **Session Management**: Secure cookies
- **Password Reset**: Email-based
- **Audit Log**: Track all user actions
- **RBAC**: Role-based access control

**Integration:**
- Streamlit native auth (simple)
- OR external auth (Auth0, Okta, AWS Cognito)

---

## 📊 Success Metrics

### Phase 1 Achievements:
- ✅ Persistent storage: Data survives restarts
- ✅ Analytics dashboard: Real-time insights
- ✅ Visual charts: 6 interactive Plotly charts
- ✅ Activity tracking: Full audit trail

### Target Metrics (End of Phase 2):
- [ ] 100% feature parity with user requirements
- [ ] < 2s page load time
- [ ] 90%+ test coverage on new features
- [ ] Zero data loss incidents

---

## 🛠️ Technical Stack

### Current:
- **Frontend**: Streamlit 1.32.0
- **Database**: SQLite (serverless, embedded)
- **Charts**: Plotly 5.18.0
- **Data**: Pandas 2.1.4

### Future Additions:
- **Search**: SQLite FTS5 (Full-Text Search)
- **Graphs**: vis.js or cytoscape.js
- **Exports**: ReportLab (PDF), openpyxl (Excel)
- **Auth**: Streamlit-authenticator or Auth0

---

## 📅 Timeline Estimate

| Phase | Features | Est. Time | Priority |
|-------|----------|-----------|----------|
| Phase 1 (Done) | Storage + Analytics | 4 hours | ✅ DONE |
| Phase 2 | Reports + Readiness | 6 hours | 🔥 HIGH |
| Phase 3 | Notifications + Cost | 8 hours | 🔥 HIGH |
| Phase 4 | Visualization | 10 hours | MEDIUM |
| Phase 5 | Settings | 4 hours | MEDIUM |
| Phase 6 | UI/UX Polish | 6 hours | LOW |
| Phase 7 | Auth | 8 hours | HIGH (Production) |

**Total Estimated Time**: ~46 hours of development

---

## 🚀 Next Steps

1. **Test Current Implementation**:
   ```bash
   cd /Users/aaldertoosthuizen/Projects/agentic-services
   streamlit run app_streamlit.py
   ```

2. **Verify Database Creation**:
   - Check `data/agentic_services.db` exists
   - Create a test project
   - View in Analytics dashboard

3. **Start Phase 2**:
   - Build Reports & Artifacts Hub (page 9)
   - Build Migration Readiness Checklist (page 10)

4. **Integration with Existing Agents**:
   - Update agent execution pages to log to database
   - Generate notifications on agent completion
   - Store artifacts after generation

---

## 🐛 Known Issues / Future Improvements

1. **Database Migration Strategy**: Need to add Alembic for schema changes
2. **Database Backup**: Implement automated SQLite backups
3. **Performance**: Consider PostgreSQL for production (100+ projects)
4. **Real-time Updates**: Use WebSocket instead of manual refresh
5. **Mobile Responsive**: Optimize charts for mobile devices
6. **Internationalization**: Add multi-language support
7. **Accessibility**: WCAG 2.1 AA compliance

---

## 📝 Notes for Development

### Database Location:
- Development: `data/agentic_services.db` (gitignored)
- Production: Configure via environment variable `DB_PATH`

### Adding New Features:
1. Add table to `db_manager.py` if needed
2. Create CRUD methods in `DatabaseManager`
3. Create Streamlit page in `pages/`
4. Add navigation button to `app_streamlit.py`
5. Write tests in `tests/database/` or `tests/pages/`

### Testing Database:
```python
from src.agentic_services.database import get_db

db = get_db()
projects = db.get_all_projects()
print(f"Found {len(projects)} projects")
```

---

**Last Updated**: 2025-11-18
**Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🚧
