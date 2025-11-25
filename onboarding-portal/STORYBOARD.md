# UI/UX Storyboard - Customer Onboarding Portal

**Complete Screen-by-Screen User Journey**

---

## 📖 Table of Contents

1. [User Journey Overview](#user-journey-overview)
2. [Screen 1: Dashboard (Landing Page)](#screen-1-dashboard-landing-page)
3. [Screen 2: New Project Form](#screen-2-new-project-form)
4. [Screen 3: Project Detail / Agent Execution](#screen-3-project-detail--agent-execution)
5. [Screen 4: Execution in Progress](#screen-4-execution-in-progress)
6. [Screen 5: Execution Complete](#screen-5-execution-complete)
7. [User Flows](#user-flows)
8. [Component Library](#component-library)

---

## User Journey Overview

```
┌──────────────┐
│   Dashboard  │ ──┐
│  (Home Page) │   │ Create New Project
└──────────────┘   │
       │           ▼
       │    ┌─────────────────┐
       │    │ New Project Form│
       │    └─────────────────┘
       │           │
       │           │ Submit
       │           ▼
       │    ┌──────────────────────┐
       └───▶│  Project Detail Page │
            │  (Agent Execution)   │
            └──────────────────────┘
                     │
                     │ Click "Run All"
                     ▼
            ┌──────────────────────┐
            │  Agents Running      │
            │  (Real-time Updates) │
            └──────────────────────┘
                     │
                     │ Complete
                     ▼
            ┌──────────────────────┐
            │  Results & Artifacts │
            └──────────────────────┘
```

---

## Screen 1: Dashboard (Landing Page)

### Purpose
First screen users see. Shows all migration projects at a glance.

### Layout
```
┌────────────────────────────────────────────────────────────────┐
│ 🌥️ Nagarro Agentic Services    [Dashboard] [New Project]     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Migration Projects                             [+ New Project]│
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │ 📊 E-Commerce Mig.   │  │ 📊 CRM Modernization │           │
│  │ Status: Running 🟡   │  │ Status: Planning 🔵  │           │
│  │ Phase: Execution     │  │ Phase: Discovery     │           │
│  │ Progress: 65%        │  │ Progress: 15%        │           │
│  │ ████████░░░░         │  │ ███░░░░░░░░░         │           │
│  │                      │  │                      │           │
│  │ [View Details]       │  │ [View Details]       │           │
│  └──────────────────────┘  └──────────────────────┘           │
│                                                                 │
│  ┌──────────────────────┐                                     │
│  │ 📊 Legacy App Mig.   │                                     │
│  │ Status: Completed ✅  │                                     │
│  │ Phase: Optimization  │                                     │
│  │ Progress: 100%       │                                     │
│  │ ████████████         │                                     │
│  │                      │                                     │
│  │ [View Details]       │                                     │
│  └──────────────────────┘                                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
│ Nagarro Agentic Services Portal © 2025                         │
└────────────────────────────────────────────────────────────────┘
```

### Components
- **Header Bar**
  - Logo/Title: "Nagarro Agentic Services"
  - Navigation: Dashboard, New Project
  - User menu (Settings, Profile)

- **Project Cards** (Grid Layout)
  - Project name with icon
  - Status chip (color-coded)
  - Current phase
  - Progress bar (0-100%)
  - "View Details" button
  - Created date

### Status Colors
- 🔵 **Planning** - Blue
- 🟢 **Discovery** - Green
- 🟠 **Assessment** - Orange
- 🟡 **Execution** - Yellow
- 🟣 **Optimization** - Purple
- ✅ **Completed** - Green checkmark
- ❌ **Failed** - Red

### Empty State
When no projects exist:
```
┌────────────────────────────────────────────────────────┐
│                                                         │
│                    📦                                   │
│                                                         │
│            No projects yet                              │
│                                                         │
│    Create your first migration project to get started  │
│                                                         │
│              [+ Create Project]                         │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### User Actions
1. **Click "+ New Project"** → Go to Screen 2 (New Project Form)
2. **Click "View Details"** on any card → Go to Screen 3 (Project Detail)
3. **Click project name** → Go to Screen 3 (Project Detail)

---

## Screen 2: New Project Form

### Purpose
Create a new migration project with requirements.

### Layout
```
┌────────────────────────────────────────────────────────────────┐
│ 🌥️ Nagarro Agentic Services    [Dashboard] [New Project]     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ← Back to Dashboard                                            │
│                                                                 │
│  Create New Migration Project                                  │
│  ═══════════════════════════                                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  Project Name *                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ E-Commerce Platform Migration                        │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  A descriptive name for your migration project            │ │
│  │                                                            │ │
│  │  Description                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Migrate legacy e-commerce platform to AWS cloud      │ │ │
│  │  │ with modern microservices architecture               │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  Brief overview of the project                             │ │
│  │                                                            │ │
│  │  Requirements                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ - Migrate 100+ microservices                         │ │ │
│  │  │ - 5TB of product and customer data                   │ │ │
│  │  │ - Zero-downtime migration                            │ │ │
│  │  │ - Maintain PCI-DSS compliance                        │ │ │
│  │  │ - Target: 3-month timeline                           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │  Detailed requirements and goals for the migration         │ │
│  │                                                            │ │
│  │                                                            │ │
│  │              [Cancel]  [Create Project ✓]                  │ │
│  │                                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Form Fields

1. **Project Name** (Required)
   - Single line text input
   - Max 255 characters
   - Validation: Cannot be empty
   - Placeholder: "E-Commerce Migration"

2. **Description** (Optional)
   - Multi-line text area (3 rows)
   - Max 1000 characters
   - Placeholder: "Brief overview of the project"

3. **Requirements** (Optional)
   - Multi-line text area (5 rows)
   - No character limit
   - Placeholder: "Detailed requirements and goals"

### Validation
- **Empty name**: "Project name is required"
- **Name too long**: "Project name must be less than 255 characters"

### User Actions
1. **Fill form** → Enable "Create Project" button
2. **Click "Cancel"** → Return to Dashboard
3. **Click "Create Project"** → 
   - Validate form
   - Create project in database
   - Redirect to Screen 3 (Project Detail)

---

## Screen 3: Project Detail / Agent Execution

### Purpose
Main execution screen. View project details and run agents by phase.

### Layout
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🌥️ Nagarro Agentic Services    [Dashboard] [New Project]             │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ← Back to Dashboard                                                    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  E-Commerce Platform Migration              Progress: 35% 📊   │  │
│  │                                                                   │  │
│  │  🔵 Planning  │  Phase: Discovery                                │  │
│  │                                                                   │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                   │  │
│  │  Description:                                                     │  │
│  │  Migrate legacy e-commerce platform to AWS cloud with modern     │  │
│  │  microservices architecture                                       │  │
│  │                                                                   │  │
│  │  Requirements:                                                    │  │
│  │  - Migrate 100+ microservices                                    │  │
│  │  - 5TB of product and customer data                              │  │
│  │  - Zero-downtime migration                                       │  │
│  │  - Maintain PCI-DSS compliance                                   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Agent Execution                                                        │
│  ═══════════════                                                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 🔵 Discovery Phase (8 Agents)         [▶ Run All] [⏸ Pause]    │  │
│  │ ─────────────────────────────────────────────────────────────   │  │
│  │ Completed: 3/8  ████████░░░░░░░░░░░░  35%                       │  │
│  │                                                                   │  │
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │  │
│  │ │ ✅ Infrastructure│ │ ✅ Application  │ │ 🟡 Data Discovery│   │  │
│  │ │    Scanner       │ │    Profiler     │ │                 │   │  │
│  │ │ Completed        │ │ Completed       │ │ Running... 45%  │   │  │
│  │ │ 2m 15s          │ │ 3m 42s         │ │ ████████░░░     │   │  │
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘   │  │
│  │                                                                   │  │
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │  │
│  │ │ ⏸ Network       │ │ ⏸ License       │ │ ⏸ Technical     │   │  │
│  │ │    Topology     │ │    Auditor      │ │    Debt Analyzer│   │  │
│  │ │ Queued          │ │ Queued          │ │ Queued          │   │  │
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘   │  │
│  │                                                                   │  │
│  │ ┌─────────────────┐ ┌─────────────────┐                        │  │
│  │ │ ⏸ API Catalog   │ │ ⏸ Integration   │                        │  │
│  │ │    Builder      │ │    Discovery    │                        │  │
│  │ │ Queued          │ │ Queued          │                        │  │
│  │ └─────────────────┘ └─────────────────┘                        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 🟠 Assessment Phase (5 Agents)        [▶ Run All]               │  │
│  │ ─────────────────────────────────────────────────────────────   │  │
│  │ Completed: 0/5  ░░░░░░░░░░░░░░░░░░░░  0%                        │  │
│  │                                                                   │  │
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │  │
│  │ │ ⏸ Dependency    │ │ ⏸ Compliance    │ │ ⏸ Security      │   │  │
│  │ │    Mapper       │ │    Checker      │ │    Hardening    │   │  │
│  │ │ Queued          │ │ Queued          │ │ Queued          │   │  │
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘   │  │
│  │                                                                   │  │
│  │ ┌─────────────────┐ ┌─────────────────┐                        │  │
│  │ │ ⏸ Cost Estimator│ │ ⏸ Data         │                        │  │
│  │ │                 │ │    Classifier   │                        │  │
│  │ │ Queued          │ │ Queued          │                        │  │
│  │ └─────────────────┘ └─────────────────┘                        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 🔴 Execution Phase (6 Agents)         [▶ Run All]               │  │
│  │ ... (Collapsed by default)                                       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 🟢 Optimization Phase (5 Agents)      [▶ Run All]               │  │
│  │ ... (Collapsed by default)                                       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Phase Panels

Each phase has:
- **Header**
  - Phase icon and name
  - Agent count
  - Progress bar
  - "Run All" button
  - Expand/Collapse toggle

- **Agent Cards** (3 per row)
  - Agent name (formatted nicely)
  - Status icon (✅ ❌ 🟡 ⏸)
  - Progress bar (if running)
  - Execution time

### Agent Status Icons
- ⏸ **Queued** - Not started (gray)
- 🟡 **Running** - In progress (yellow, animated)
- ✅ **Completed** - Success (green)
- ❌ **Failed** - Error (red)
- 🔄 **Cancelled** - User stopped (orange)

### User Actions
1. **Click "Run All"** → Start all agents in that phase
2. **Click "Pause"** → Stop running agents
3. **Click expand/collapse** → Show/hide agent cards
4. **Click agent card** → View detailed results (future)
5. **Click "← Back"** → Return to Dashboard

---

## Screen 4: Execution in Progress

### Purpose
Show real-time progress as agents execute.

### Layout
Same as Screen 3, but with live updates:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔵 Discovery Phase (8 Agents)         [⏸ Pause] [🔄 Refresh]  │
│ ─────────────────────────────────────────────────────────────   │
│ Completed: 3/8  Running: 2  ████████░░░░░░░░░░░░  62%          │
│                                                                  │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│ │ ✅ Infrastructure│ │ ✅ Application  │ │ ✅ Data Discovery│  │
│ │    Scanner       │ │    Profiler     │ │                 │  │
│ │ Completed ✓      │ │ Completed ✓     │ │ Completed ✓     │  │
│ │ 2m 15s          │ │ 3m 42s         │ │ 5m 18s         │  │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│                                                                  │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│ │ 🟡 Network      │ │ 🟡 License      │ │ ⏸ Technical     │  │
│ │    Topology     │ │    Auditor      │ │    Debt Analyzer│  │
│ │ Running... 78%  │ │ Running... 23%  │ │ Queued          │  │
│ │ ███████████░    │ │ ████░░░░░░░     │ │                 │  │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│                                                                  │
│ ┌─────────────────┐ ┌─────────────────┐                       │
│ │ ⏸ API Catalog   │ │ ⏸ Integration   │                       │
│ │    Builder      │ │    Discovery    │                       │
│ │ Queued          │ │ Queued          │                       │
│ └─────────────────┘ └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### Real-time Updates
- Progress bars animate
- Status changes: Queued → Running → Completed
- Execution time counts up
- Phase progress bar updates
- Page polls backend every 5 seconds for updates

### User Actions
1. **Click "Pause"** → Stop all running agents
2. **Click "Refresh"** → Force update of status
3. **Wait for completion** → See Screen 5

---

## Screen 5: Execution Complete

### Purpose
Show completed execution with results and artifacts.

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ 🔵 Discovery Phase (8 Agents)         ✅ All Complete          │
│ ─────────────────────────────────────────────────────────────   │
│ Completed: 8/8  ████████████████████████  100%                  │
│                                                                  │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│ │ ✅ Infrastructure│ │ ✅ Application  │ │ ✅ Data Discovery│  │
│ │    Scanner       │ │    Profiler     │ │                 │  │
│ │ Completed ✓      │ │ Completed ✓     │ │ Completed ✓     │  │
│ │ 2m 15s          │ │ 3m 42s         │ │ 5m 18s         │  │
│ │ [View Report]    │ │ [View Report]   │ │ [View Report]   │  │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│                                                                  │
│ │ All agents completed successfully! ✓                         │
│ │                                                                │
│ │ Generated Artifacts:                                          │
│ │ 📄 Infrastructure_Analysis.pdf (2.3 MB)    [Download]        │
│ │ 📄 Application_Profile.xlsx (890 KB)       [Download]        │
│ │ 📄 Data_Discovery_Report.pdf (1.5 MB)      [Download]        │
│ │ 📄 Network_Topology_Diagram.png (456 KB)   [Download]        │
│ │ ... and 12 more files                                         │
│ │                                                                │
│ │ Next Steps:                                                   │
│ │ • Review discovery findings                                   │
│ │ • Run Assessment phase for detailed analysis                  │
│ │ • Download reports for stakeholder review                     │
│ │                                                                │
│ │                     [Run Assessment Phase →]                  │
│ └─────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### Success Indicators
- ✅ Green checkmarks on all agents
- "All Complete" message
- 100% progress bar
- List of generated artifacts
- "Next Steps" suggestions

### Artifacts Display
Each artifact shows:
- File type icon (📄 📊 📈)
- File name
- File size
- [Download] button

### User Actions
1. **Click "View Report"** → Open artifact details (future)
2. **Click "Download"** → Download artifact file
3. **Click "Run Assessment Phase"** → Start next phase
4. **Navigate to next phase** → Scroll down and click "Run All"

---

## User Flows

### Flow 1: Create First Project
```
Start (Empty Dashboard)
  ↓
Click "+ New Project"
  ↓
Fill Project Name: "E-Commerce Migration"
Fill Description: "Migrate to AWS"
Fill Requirements: "100 services, 5TB data"
  ↓
Click "Create Project"
  ↓
Redirected to Project Detail Page
  ↓
See all 4 phases with agents (24 total)
```

### Flow 2: Execute Discovery Phase
```
Project Detail Page
  ↓
Scroll to "Discovery Phase" panel
  ↓
Click "Run All" button
  ↓
8 agents start executing:
  - Status changes from ⏸ Queued to 🟡 Running
  - Progress bars animate
  - Execution timers count up
  ↓
Page auto-refreshes every 5 seconds
  ↓
Agents complete one by one:
  - Status changes to ✅ Completed
  - Progress bar fills to 100%
  ↓
All 8 agents completed
  - Phase progress: 100%
  - "All Complete" message
  - Artifacts listed
```

### Flow 3: Complete Migration (All Phases)
```
Discovery Phase Complete (8/8)
  ↓
Run Assessment Phase (5 agents)
  ↓
Assessment Complete (5/5)
  ↓
Run Execution Phase (6 agents)
  ↓
Execution Complete (6/6)
  ↓
Run Optimization Phase (5 agents)
  ↓
Optimization Complete (5/5)
  ↓
PROJECT 100% COMPLETE 🎉
  - 24/24 agents executed
  - All artifacts generated
  - Ready for final review
```

### Flow 4: View Existing Project
```
Dashboard with existing projects
  ↓
Click "View Details" on project card
  ↓
Project Detail Page loads
  ↓
See execution history:
  - Completed phases: green checkmarks
  - In-progress phases: progress bars
  - Pending phases: grayed out
  ↓
Scroll to view artifacts
  ↓
Download reports as needed
```

---

## Component Library

### 1. Project Card
```
┌──────────────────────┐
│ 📊 Project Name      │
│ Status: Running 🟡   │
│ Phase: Execution     │
│ Progress: 65%        │
│ ████████░░░░         │
│                      │
│ Created: Jan 15      │
│ [View Details]       │
└──────────────────────┘
```

**Props:**
- `project`: Project object
- `onClick`: Handler function

### 2. Agent Card
```
┌─────────────────┐
│ 🟡 Agent Name   │
│ Running... 45%  │
│ ████████░░░     │
│ Time: 2m 15s    │
│ [View Logs]     │
└─────────────────┘
```

**Props:**
- `agentName`: string
- `status`: 'queued' | 'running' | 'completed' | 'failed'
- `progress`: number (0-100)
- `startedAt`: timestamp

### 3. Phase Panel
```
┌─────────────────────────────────────────────────┐
│ 🔵 Phase Name (X Agents)  [▶ Run All] [▼]     │
│ ─────────────────────────────────────────────  │
│ Completed: X/Y  ████████░░░░  XX%              │
│                                                 │
│ [Agent Cards Grid]                              │
└─────────────────────────────────────────────────┘
```

**Props:**
- `phase`: Phase enum
- `agents`: Array of agent names
- `executions`: Array of execution records
- `onRunAll`: Handler function

### 4. Progress Bar
```
Progress: 65%
████████████░░░░░░░░
```

**Props:**
- `value`: number (0-100)
- `color`: 'primary' | 'success' | 'warning' | 'error'

### 5. Status Chip
```
[Running 🟡] [Completed ✅] [Failed ❌]
```

**Props:**
- `status`: Status enum
- `label`: string

---

## Design Tokens

### Colors
- **Primary**: #1976d2 (Blue)
- **Secondary**: #dc004e (Red/Pink)
- **Success**: #4caf50 (Green)
- **Warning**: #ff9800 (Orange)
- **Error**: #f44336 (Red)
- **Info**: #2196f3 (Light Blue)

### Phase Colors
- **Discovery**: #2196f3 (Blue)
- **Assessment**: #ff9800 (Orange)
- **Execution**: #f44336 (Red)
- **Optimization**: #4caf50 (Green)

### Typography
- **Heading 1**: 32px, Bold
- **Heading 2**: 24px, Bold
- **Heading 3**: 20px, Medium
- **Body**: 16px, Regular
- **Caption**: 14px, Regular

### Spacing
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px

---

## Responsive Behavior

### Desktop (1200px+)
- 3 project cards per row
- 3 agent cards per row
- Full sidebar navigation

### Tablet (768px - 1199px)
- 2 project cards per row
- 2 agent cards per row
- Collapsible sidebar

### Mobile (< 768px)
- 1 project card per row
- 1 agent card per row
- Bottom navigation
- Stacked layout

---

## Loading States

### Initial Page Load
```
┌─────────────────────────┐
│                          │
│    ⏳ Loading...         │
│    Please wait...        │
│                          │
└─────────────────────────┘
```

### Agent Execution
```
┌─────────────────┐
│ 🟡 Agent Name   │
│ Starting...     │
│ ⏳              │
└─────────────────┘
```

### Data Refresh
```
Top right corner: 🔄 Updating...
```

---

## Error States

### Network Error
```
❌ Network Error
Unable to connect to server.
Please check your connection.
[Retry]
```

### Agent Failure
```
┌─────────────────┐
│ ❌ Agent Name   │
│ Failed          │
│ Error: timeout  │
│ [Retry] [Logs]  │
└─────────────────┘
```

### Form Validation
```
⚠️ Project name is required
```

---

## Animation & Transitions

### Progress Bars
- Smooth fill animation (0.3s ease)
- Pulse effect while running

### Agent Cards
- Fade in on status change (0.2s)
- Border highlight on completion
- Shake effect on error

### Page Transitions
- Fade between routes (0.3s)
- Slide-in for modals (0.2s)

---

## Accessibility

### Keyboard Navigation
- Tab through all interactive elements
- Enter to activate buttons
- Escape to close modals

### Screen Reader Support
- Aria labels on all icons
- Status announcements
- Progress updates

### Color Contrast
- WCAG AA compliant
- High contrast mode support

---

**Last Updated**: 2025-01-15  
**Version**: 1.0.0  
**Status**: Ready for Implementation
