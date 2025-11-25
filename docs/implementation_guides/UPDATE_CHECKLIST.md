# Documentation Update Checklist
## Fixing "6 agents" → "24 agents" References

**Created**: 2025-01-15  
**Status**: In Progress  
**Priority**: High (Customer-facing documentation accuracy)  

---

## Status Summary

### ✅ Completed Updates
1. **README.md** - Updated to show 24 agents in 4 phases
2. **docs/PROJECT_STATUS.md** - Already correct (24 agents documented)
3. **docs/PLATFORM_ARCHITECTURE_v2.md** - New file, correct from start
4. **docs/MIGRATION_TRANSITION_PLAN.md** - New file, correct from start
5. **WARP.md** - Already correct (references 24 agents)

### 🔄 Files That Need Updates

#### High Priority (Customer-Facing)
- [ ] **docs/architecture/ARCHITECTURE-ALIGNMENT.md** (Lines 46-83)
  - Currently states "6 Specialized Agents"
  - Update section 3 to show 24 agents in 4 phases
  
- [ ] **EXECUTIVE-OVERVIEW.md** (Lines 146, 383)
  - References "6 agents"
  - Update to "24 agents" and add phase breakdown

- [ ] **AWS-TCO-ESTIMATE.md** (Lines 191-192)
  - May reference "6 agents"
  - Update cost estimates based on 24 agents

#### Medium Priority (Internal Documentation)
- [ ] **.github/workflows/README.md** (Lines 17, 138)
  - Update CI/CD documentation to reflect 24 agents
  
- [ ] **docs/architecture/technical-architecture.md**
  - Check for agent count references
  - Update if needed

#### Low Priority (Legacy/History)
- [x] **CHANGELOG.md** - Leave as-is (historical record)
- [x] **docs/session_notes/** - Leave as-is (historical audit trail)
- [x] **.github/workflows/ci.yml** - Accurate (tests 24 agents)

---

## Detailed Update Instructions

### 1. ARCHITECTURE-ALIGNMENT.md

**Location**: `docs/architecture/ARCHITECTURE-ALIGNMENT.md`  
**Lines**: 46-83

**Find**:
```markdown
**6 Specialized Agents:**

1. **Discovery Agent**
   - Infrastructure scanning and data collection
   ...
6. **Testing Agent** ⭐ NEW
   - Pre-migration validation
   ...
```

**Replace with**:
```markdown
**24 Specialized AI Agents** organized in 4 migration phases:

### Discovery Phase (8 agents)
1. **Infrastructure Scanner** - Infrastructure scanning and inventory
2. **Application Profiler** - Application analysis and profiling
3. **Data Discovery** - Data classification and PII detection
4. **Integration Mapper** - Integration point identification
5. **Security Auditor** - Security posture assessment
6. **Network Analyzer** - Network topology and security scanning
7. **Performance Baseline** - Performance metrics collection
8. **Licensing Analyzer** - License compliance checking

### Assessment Phase (5 agents)
9. **Dependency Mapper** - Dependency analysis and mapping
10. **Compliance Checker** - Regulatory compliance validation
11. **Cost Estimator** - Migration cost estimation and TCO
12. **Risk Assessment** - Risk identification and scoring
13. **Capacity Planner** - Resource capacity planning

### Execution Phase (6 agents)
14. **Infrastructure Provisioner** - AWS infrastructure deployment
15. **Data Migration** - Database and data migration
16. **Application Migration** - Application deployment and cutover
17. **Configuration Manager** - Configuration management
18. **Testing Orchestrator** - Testing orchestration and validation
19. **Rollback Manager** - Rollback and recovery automation

### Optimization Phase (5 agents)
20. **Performance Optimizer** - Performance tuning recommendations
21. **Cost Optimizer** - Cost optimization recommendations
22. **Security Hardening** - Security configuration hardening
23. **Monitoring Setup** - Monitoring and alerting setup
24. **Documentation Generator** - Documentation generation

**Note**: This is a significant expansion from the original 6-agent architecture to provide comprehensive E2E migration automation.
```

**Also Update**: Lines 81-84 to reflect 24 agents in aligned documents

---

### 2. EXECUTIVE-OVERVIEW.md

**Location**: `EXECUTIVE-OVERVIEW.md`  
**Lines**: 146, 383

**Find** (around line 146):
```markdown
The platform currently deploys 6 specialized AI agents...
```

**Replace with**:
```markdown
The platform deploys 24 specialized AI agents organized across 4 migration phases (Discovery, Assessment, Execution, Optimization)...
```

**Find** (around line 383):
```markdown
With just 6 agents...
```

**Replace with**:
```markdown
With 24 specialized agents covering the entire migration lifecycle...
```

---

### 3. AWS-TCO-ESTIMATE.md

**Location**: `AWS-TCO-ESTIMATE.md`  
**Lines**: 191-192

**Review**: Check if cost estimates are based on 6 vs 24 agents  
**Action**: Update compute costs if needed (24 Lambda functions vs 6)

**Lambda Cost Calculation**:
- 6 agents → 24 agents = 4x more functions
- However, per-invocation cost remains same
- Update monthly estimate if it was based on "6 agents running continuously"

---

### 4. .github/workflows/README.md

**Location**: `.github/workflows/README.md`  
**Lines**: 17, 138

**Find**:
```markdown
Testing 6 AI agents...
```

**Replace with**:
```markdown
Testing all 24 AI agents organized in 4 phases...
```

---

## Update Commands

To help find remaining references:

```bash
# Search for "6 agents" references (case insensitive)
grep -ri "6 agents" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md~" .

# Search for "six agents"
grep -ri "six agents" --exclude-dir=.git --exclude-dir=node_modules .

# Search for "6 specialized" 
grep -ri "6 specialized" --exclude-dir=.git --exclude-dir=node_modules .

# Count of agents in specific files
grep -c "agent" src/agentic_services/agents/*.py
```

---

## Testing After Updates

### 1. Documentation Consistency Check
```bash
# Verify all markdown files mention 24 agents
grep -r "24.*agents" docs/ README.md | wc -l

# Should find no "6 agents" in customer-facing docs
grep -ri "6 agents" docs/architecture/ docs/MIGRATION_TRANSITION_PLAN.md README.md
```

### 2. Build Test
```bash
# Ensure no broken links
cd docs
find . -name "*.md" -exec markdown-link-check {} \;
```

### 3. Content Review
- [ ] README.md - Scan full file
- [ ] docs/PROJECT_STATUS.md - Scan full file  
- [ ] docs/MIGRATION_TRANSITION_PLAN.md - Verify all agent counts
- [ ] docs/architecture/PLATFORM_ARCHITECTURE_v2.md - Verify all agent lists

---

## Priority Order

**Week 1 (High Priority)**:
1. ARCHITECTURE-ALIGNMENT.md
2. EXECUTIVE-OVERVIEW.md
3. AWS-TCO-ESTIMATE.md (if needed)

**Week 2 (Medium Priority)**:
4. .github/workflows/README.md
5. Any other internal documentation

**Low Priority** (Leave as-is):
- CHANGELOG.md (historical)
- Session notes (audit trail)
- Old architecture docs (marked as deprecated)

---

## Notes

### Why Some Files Are Left Unchanged

1. **CHANGELOG.md**: Historical record, shows evolution over time
2. **Session Notes**: Audit trail of development sessions
3. **CI/CD workflows (*.yml)**: Already correct (test all 24 agents)

### References That Are Correct

- ✅ WARP.md - Lists all 24 agents correctly
- ✅ PROJECT_STATUS.md - All 24 agents documented
- ✅ src/agentic_services/agents/ - 24 agent files present
- ✅ tests/agents/ - 24 test files present
- ✅ infrastructure/terraform/lambda.tf - Creates 24 functions

---

## Sign-off

Once all high-priority updates are complete:

- [ ] All customer-facing docs updated
- [ ] All architecture docs consistent
- [ ] README.md accurate
- [ ] Documentation tested and validated
- [ ] Commit with message: "docs: Update all references from 6 to 24 agents"

---

**Assigned To**: Team  
**Due Date**: Before next customer presentation  
**Estimated Time**: 1-2 hours  
