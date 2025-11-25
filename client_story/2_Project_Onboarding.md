# Client Storyline: New Project & Onboarding

## Scene 1 – Launchpad (1 min)
1. Start from the dashboard home page (left nav → `Projects`).
2. Highlight the Projects widget showing active engagements, owners, and current phase.
3. Explain that every onboarding journey flows through this workspace and powers downstream agents/reports.
4. Click "Create Project" to start the guided flow.

## Scene 2 – Project Creation (3 min)
1. Walk through the creation modal step-by-step:
   - Customer profile: industry, geography, executive sponsor, steering committee.
   - Target cloud(s), preferred regions, compliance regimes (HIPAA, FedRAMP, PCI).
   - Business priorities (cost, resilience, velocity) captured via sliders/badges.
2. Explain built-in templates (migration, greenfield, optimization) and how they preconfigure onboarding tasks, documentation checklists, and agent runbooks.
3. Attach sample artifacts (architecture PDFs, contracts) within the modal to show intake flexibility.
4. Emphasize required fields vs enrichment (tags, phase gates, scoring criteria, risk rating).
5. Submit and highlight the auto-generated workspace: project ID, default tabs, onboarding ribbon ready to fill.

## Scene 3 – Guided Onboarding Flow (5 min)
1. Show the onboarding tabs: Discovery → Credentials → Source Systems → Target Blueprint → Analytics.
2. For each tab:
   - Discovery: capture business drivers, SLAs, critical workloads; highlight inline guidance/examples and predefined picklists.
   - Credentials: explain IAM role requirements, secret rotation, masked storage; show per-environment grouping (prod/dev/test) and approval toggle.
   - Source Systems: demo inventory tables (servers, DBs, middleware) plus CSV import, auto-tagging, ownership assignment.
   - Target Blueprint: open the template library (Landing Zone, App Factory) and show diagram preview, approver assignment, and change log.
   - Analytics: preview readiness metrics that unlock once upstream tabs are green (cost baseline, modernization score, risk heatmap).
3. Call out validation hints (missing mandatory fields, conflicting regions, unsupported services) and how they block progression until resolved.
4. Demonstrate the progress ring and percentage updating live as each tab hits "complete."

## Scene 4 – Connect Existing Project to Cloud (4 min)
1. Open an existing project that has completed Discovery but still needs live credentials.
2. Navigate to the "Cloud Connections" tab:
   - Show cards per provider with environment slices (prod/dev/test) and KPIs (last test, rotation date).
   - Explain fields: account/subscription ID, IAM role ARN, external ID, secrets stored in Vault/KMS.
3. Add a credential live:
   - Click "Add Connection" → select cloud → paste role ARN/external ID.
   - Attach approval evidence (ticket, PDF sign-off), set owner, expiry date, rotation cadence.
4. Run "Test Connection":
   - Describe automated checks (assume role, list resources, CloudWatch/CloudTrail writes).
   - Show pass/fail output and remediation hints (e.g., add `s3:GetObject`, enable STS trust).
5. Link source systems:
   - Map the validated credential to inventories (EC2, SQL Server, VMware).
   - Upload CMDB exports to auto-match resources, dedupe, and assign ownership tags.
6. Highlight compliance guardrails:
   - Audit log showing who created/updated/revoked credentials with timestamps.
   - Rotation reminders, MFA enforcement toggles, policy templates (read-only vs admin).

## Scene 5 – Collaboration & Handoffs (3 min)
1. Point out the activity feed: comments, @mentions, automatic posts from credential tests or artifact uploads.
2. Highlight the Kanban/checklist view: tasks per phase, owners, due dates, dependency warnings.
3. Show alerts/notifications (email, Slack) triggered when validations fail or approvals are overdue.
4. Explain how onboarding artifacts unlock agents automatically—once credentials + inventory are green, the Discovery agent can run without rekeying.

## Scene 6 – Success Metrics (2 min)
1. Summarize the onboarding dashboard (overall percentage, per-tab status, open blockers, pending approvals).
2. Highlight readiness badges (Discovery Complete, Cloud Access Validated, Inventory Locked) that gate downstream workflows.
3. Reinforce that once everything is green, Quick Assess, Discovery, and Planning agents become one-click actions.
4. Close with next steps: launch Quick Assess, run Discovery/Planning agents, generate executive briefs, populate modernization backlog.
