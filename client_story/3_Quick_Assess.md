# Client Storyline: Quick Assess

## Scene 1 – Problem Framing (1 min)
1. Introduce Quick Assess as the “rapid x-ray” of a client’s current environment.
2. Explain that it ingests documents/diagrams, orchestrates AI agents, and outputs an assessment in minutes.

## Scene 2 – Upload Experience (3 min)
1. Navigate to the Quick Assess page (Streamlit tab or sidebar button).
2. Show the upload widget; drag in sample DOCX, PDF, Visio, draw.io files.
3. Mention file validation (type, size) and security (stored in client’s tenant / S3 bucket).
4. Start the upload and highlight the progress indicators + assessment ID creation.

## Scene 3 – Execute & Monitor (4 min)
1. Click “Execute Assessment” and point out the workflow status card.
2. Walk through each stage on the status timeline (Document Parsing → Diagram Parsing → Environment Analysis → Report Generation).
3. Emphasize that LangGraph agents run sequentially/parallel as needed, with retries and logging.
4. Show how the status card updates every few seconds; highlight error handling (retry, view logs) if a stage fails.

## Scene 4 – Results Experience (5 min)
1. When complete, switch to the Results tab.
2. Present the headline metrics: Cloud Readiness Score, key findings, risk indicators.
3. Scroll through Infrastructure Inventory, Technology Stack, Architecture Assessment, Risk Overview.
4. Highlight visual elements: score dial, component charts, risk badges.
5. Demonstrate export actions: download PDF (ReportLab brand styling), view JSON, share link.

## Scene 5 – Business Impact (2 min)
1. Reinforce the speed-to-insight (hours → minutes) and repeatability.
2. Explain how results feed downstream: roadmap planning, modernization backlog, executive reporting.
3. Close with a call to action: “Let’s run Quick Assess on your environment to prioritize your 2025 initiatives.”
