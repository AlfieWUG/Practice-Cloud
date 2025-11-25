# Document-Based Discovery Feature - Technical & Functional Design

## Executive Summary

This document outlines the design for a **Document-Based Discovery Mode** that allows clients to provide documentation (diagrams, spreadsheets, documents) instead of granting live infrastructure access. The system will use AI to extract entities, relationships, and metadata to populate the discovery phase of migration projects.

---

## Table of Contents

1. [Business Context & Requirements](#1-business-context--requirements)
2. [Functional Design](#2-functional-design)
3. [Technical Architecture](#3-technical-architecture)
4. [Data Model](#4-data-model)
5. [AI/ML Strategy](#5-aiml-strategy)
6. [User Interface Design](#6-user-interface-design)
7. [Integration Points](#7-integration-points)
8. [Security & Compliance](#8-security--compliance)
9. [Performance & Scalability](#9-performance--scalability)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Risk Analysis](#11-risk-analysis)
12. [Success Metrics](#12-success-metrics)

---

## 1. Business Context & Requirements

### 1.1 Problem Statement

**Current State:**
- Platform assumes live infrastructure access via scanning agents
- Discovery agents connect to client infrastructure (AWS, Azure, on-prem)
- Security-conscious clients are reluctant to grant access

**Client Scenario:**
> "We cannot provide access to our production environment. However, we have comprehensive documentation: architecture diagrams (Visio), application inventories (Excel), network diagrams, and technical documentation (Word/PDF). Can you work with these instead?"

**Business Impact:**
- Lost opportunities with security-conscious enterprises
- Delays in engagement due to access approval processes
- Inability to serve clients with air-gapped environments

### 1.2 Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-1 | Support multiple file formats (Excel, PDF, Visio, images, etc.) | MUST | System accepts 10+ file types |
| FR-2 | Extract structured entities from unstructured documents | MUST | 80%+ accuracy on test corpus |
| FR-3 | Identify dependencies between entities | MUST | AI identifies relationships from diagrams |
| FR-4 | Support batch document upload (multiple files) | MUST | Upload 50+ files in one session |
| FR-5 | Provide human review/correction workflow | MUST | Low-confidence entities flagged for review |
| FR-6 | Generate discovery report equivalent to live scan | MUST | Same format as existing discovery output |
| FR-7 | Support incremental updates (upload more docs later) | SHOULD | Re-analyze without losing existing data |
| FR-8 | Visual dependency graph from extracted data | SHOULD | Interactive graph like infrastructure mode |
| FR-9 | Export discovered entities to standard formats | COULD | JSON, CSV, Excel export |
| FR-10 | Confidence scoring for AI extractions | MUST | Each entity has 0-1 confidence score |

### 1.3 Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | Document processing time | < 5 min for 100MB | Median processing time |
| NFR-2 | AI extraction accuracy | > 80% | Precision/recall on test set |
| NFR-3 | System availability | 99.5% uptime | Monthly uptime % |
| NFR-4 | Concurrent document processing | 10 projects | Load test results |
| NFR-5 | Data security | Encryption at rest & transit | Security audit |
| NFR-6 | File size limits | 500MB per file, 2GB per project | Enforced limits |

### 1.4 Out of Scope

- ❌ Automated conversion of Visio to Draw.io
- ❌ Real-time collaborative document editing
- ❌ Integration with SharePoint/Google Drive (future enhancement)
- ❌ OCR for handwritten notes (future enhancement)
- ❌ Video/audio file analysis

---

## 2. Functional Design

### 2.1 User Journeys

#### Journey 1: Document-Based Project Creation (Happy Path)

```
1. User creates new project
2. User selects "Document-Based Discovery" mode
3. User uploads 15 files:
   - 5 Visio diagrams (architecture, network, data flow)
   - 3 Excel inventories (servers, applications, databases)
   - 4 PDF documents (technical specs)
   - 3 Draw.io diagrams (exported as XML)
4. System validates file types and sizes
5. System displays upload summary with file categorization
6. User clicks "Start Analysis"
7. System triggers DocumentAnalysisAgent
8. System processes files in parallel:
   - Vision AI parses diagrams → extracts boxes, arrows, labels
   - Pandas reads Excel → structures inventory data
   - PyPDF2 extracts text from PDFs → AI identifies entities
   - XML parser reads Draw.io → extracts shapes and connections
9. System consolidates entities and deduplicates
10. System displays discovered entities (127 found)
11. System flags 12 low-confidence entities for review
12. User reviews flagged entities, corrects 3, approves rest
13. User clicks "Approve & Continue"
14. System marks discovery phase as COMPLETE
15. User proceeds to Planning phase with discovered entities
```

#### Journey 2: Incremental Document Addition

```
1. User has existing project with 50 discovered entities
2. Client provides 5 additional Excel sheets (new applications)
3. User navigates to project → "Documents" tab
4. User uploads 5 new files
5. User clicks "Re-Analyze"
6. System processes only new files
7. System merges results with existing entities
8. System detects 3 duplicates and prompts user
9. User chooses "Merge" for 2, "Keep Both" for 1
10. System updates entity count: 50 → 68
11. System regenerates dependency graph
```

#### Journey 3: Error Handling - Unsupported Format

```
1. User uploads .pptx file
2. System rejects file with message:
   "PowerPoint files are not supported. Please convert to PDF or images."
3. User converts to PDF, re-uploads
4. System accepts file
```

### 2.2 Feature Breakdown

#### Feature 2.2.1: Discovery Mode Selection

**Location:** Onboarding page (step 2)

**UI Elements:**
- Radio button group:
  - ○ Live Infrastructure Scan (existing)
  - ○ Document-Based Discovery (new)
- Help text explaining each mode
- Visual comparison table

**Business Logic:**
```python
if discovery_mode == "Document-Based":
    # Skip infrastructure connection fields
    # Show file upload section
    # Disable live discovery agents
    project_metadata['discovery_type'] = 'document_based'
else:
    # Existing flow
    project_metadata['discovery_type'] = 'live_scan'
```

#### Feature 2.2.2: Multi-File Upload

**Location:** Onboarding page (conditional on document mode)

**UI Elements:**
- Drag-and-drop zone (Streamlit `file_uploader`)
- Supported formats badge
- File list with icons, sizes, types
- "Add More Files" button
- Upload progress bar (if processing)

**Supported File Types:**

| Category | Extensions | Max Size | Handler |
|----------|-----------|----------|---------|
| Diagrams | .png, .jpg, .jpeg, .svg | 50MB | Vision AI |
| Visio | .vsdx, .vsd | 50MB | Convert → Vision AI |
| Draw.io | .drawio, .xml | 10MB | XML Parser |
| Spreadsheets | .xlsx, .xls, .csv | 100MB | Pandas |
| Documents | .pdf, .docx, .doc | 100MB | PyPDF2/python-docx |
| Configs | .json, .yaml, .yml, .tf | 10MB | Text parser + AI |

**Validation Rules:**
- Max 100 files per project
- Max 2GB total per project
- File name must be unique within project
- Virus scan (if enabled)

#### Feature 2.2.3: Document Categorization

**Automatic Categorization:**

```python
def categorize_file(filename: str, content: bytes) -> str:
    """Categorize uploaded file into processing pipeline"""
    
    ext = filename.lower().split('.')[-1]
    
    if ext in ['png', 'jpg', 'jpeg', 'svg', 'vsdx', 'vsd']:
        return 'diagram'
    elif ext in ['drawio', 'xml']:
        # Check if it's Draw.io XML
        if b'mxGraphModel' in content[:1000]:
            return 'diagram'
        return 'config'
    elif ext in ['xlsx', 'xls', 'csv']:
        return 'spreadsheet'
    elif ext in ['pdf', 'docx', 'doc']:
        return 'document'
    elif ext in ['json', 'yaml', 'yml', 'tf']:
        return 'config'
    else:
        return 'unknown'
```

**User-Visible Categorization:**
- 📊 Diagrams (12 files) - For architecture/network visualization
- 📋 Spreadsheets (8 files) - For inventory data
- 📄 Documents (5 files) - For technical specifications
- ⚙️ Configurations (3 files) - For IaC/config files

#### Feature 2.2.4: Document Analysis Orchestration

**Processing Pipeline:**

```
Upload → Store → Categorize → Process → Extract → Consolidate → Review
```

**Step 1: Store**
- Save file to storage (S3 or local)
- Create `uploaded_documents` record
- Set status = 'pending'

**Step 2: Process (by category)**

```python
async def process_documents(project_id: str):
    """Orchestrate document processing"""
    
    docs = db.get_project_documents(project_id, status='pending')
    job = db.create_analysis_job(project_id, document_ids=[d['id'] for d in docs])
    
    try:
        all_entities = []
        
        # Process in parallel by category
        diagram_tasks = [process_diagram(d) for d in docs if d['file_type'] == 'diagram']
        spreadsheet_tasks = [process_spreadsheet(d) for d in docs if d['file_type'] == 'spreadsheet']
        document_tasks = [process_document(d) for d in docs if d['file_type'] == 'document']
        
        results = await asyncio.gather(*diagram_tasks, *spreadsheet_tasks, *document_tasks)
        
        for entities in results:
            all_entities.extend(entities)
        
        # Step 3: Consolidate (deduplication)
        unique_entities = deduplicate_entities(all_entities)
        
        # Step 4: Store
        for entity in unique_entities:
            db.create_discovered_entity(entity)
        
        db.update_analysis_job(job['id'], status='completed', entities_found=len(unique_entities))
        
    except Exception as e:
        db.update_analysis_job(job['id'], status='failed', error_message=str(e))
```

#### Feature 2.2.5: Entity Extraction (Diagram Processing)

**Vision AI Approach:**

```python
async def process_diagram(doc: Dict) -> List[Dict]:
    """Extract entities from architecture diagram using Claude Vision"""
    
    # Read image
    with open(doc['storage_path'], 'rb') as f:
        image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode()
    
    prompt = """
    Analyze this architecture/network diagram and extract ALL visible components.
    
    For each component/box/shape, identify:
    1. Entity name (label on the shape)
    2. Entity type: application, service, database, server, network, load_balancer, queue, storage, other
    3. Technology (if labeled, e.g., "PostgreSQL", "Node.js", "AWS S3")
    4. Visual attributes (color, size, position) - helps with deduplication
    
    For each arrow/connection between components:
    1. Source component name
    2. Target component name
    3. Connection type (if labeled, e.g., "HTTPS", "TCP/443", "REST API")
    
    Output JSON:
    {
      "entities": [
        {"name": "User Service", "type": "application", "technology": "Spring Boot", "position": {"x": 100, "y": 200}},
        {"name": "Users DB", "type": "database", "technology": "PostgreSQL"}
      ],
      "connections": [
        {"from": "User Service", "to": "Users DB", "type": "JDBC"}
      ]
    }
    
    Be thorough. Extract EVERYTHING you can see. If unsure about a label, include it with lower confidence.
    """
    
    # Call Claude Vision API
    response = await bedrock_client.invoke_model(
        modelId='anthropic.claude-3-opus-20240229-v1:0',  # Best vision model
        contentType='application/json',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4096,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': image_b64
                            }
                        },
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ]
                }
            ]
        })
    )
    
    result = json.loads(response['body'].read())
    extracted = json.loads(result['content'][0]['text'])
    
    # Convert to internal entity format
    entities = []
    for e in extracted['entities']:
        entity = {
            'entity_type': e['type'],
            'entity_name': e['name'],
            'technology': e.get('technology'),
            'attributes': {
                'position': e.get('position'),
                'visual_context': f"From diagram: {doc['filename']}"
            },
            'dependencies': [],  # Will populate from connections
            'confidence_score': 0.85,  # Vision AI typical confidence
            'extraction_source': doc['filename'],
            'document_id': doc['id']
        }
        entities.append(entity)
    
    # Process connections
    for conn in extracted['connections']:
        # Find source entity and add dependency
        for e in entities:
            if e['entity_name'] == conn['from']:
                e['dependencies'].append({
                    'target': conn['to'],
                    'type': conn.get('type', 'unknown')
                })
    
    return entities
```

**Visio Handling:**

```python
def convert_visio_to_image(vsdx_path: str) -> str:
    """Convert Visio to PNG for Vision AI processing"""
    
    # Option 1: Use vsdx library (Python)
    import vsdx
    doc = vsdx.VisioFile(vsdx_path)
    page = doc.pages[0]
    # Export to SVG, then convert to PNG
    
    # Option 2: Use LibreOffice headless (more reliable)
    import subprocess
    output_path = vsdx_path.replace('.vsdx', '.png')
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'png',
        vsdx_path, '--outdir', os.path.dirname(vsdx_path)
    ])
    
    return output_path
```

#### Feature 2.2.6: Entity Extraction (Spreadsheet Processing)

**Excel/CSV Parsing:**

```python
async def process_spreadsheet(doc: Dict) -> List[Dict]:
    """Extract entities from inventory spreadsheet"""
    
    import pandas as pd
    
    # Read spreadsheet
    if doc['filename'].endswith('.csv'):
        df = pd.read_csv(doc['storage_path'])
    else:
        df = pd.read_excel(doc['storage_path'], sheet_name=None)  # Read all sheets
        
        # If multiple sheets, process each
        if isinstance(df, dict):
            all_entities = []
            for sheet_name, sheet_df in df.items():
                entities = extract_from_dataframe(sheet_df, doc, sheet_name)
                all_entities.extend(entities)
            return all_entities
        
    return extract_from_dataframe(df, doc)


def extract_from_dataframe(df: pd.DataFrame, doc: Dict, sheet_name: str = None) -> List[Dict]:
    """Extract entities from a dataframe with intelligent column mapping"""
    
    # Normalize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Intelligent column mapping (use AI if ambiguous)
    column_mapping = infer_column_mapping(df.columns)
    
    entities = []
    for idx, row in df.iterrows():
        # Determine entity type from sheet name or content
        entity_type = infer_entity_type(row, sheet_name)
        
        entity = {
            'entity_type': entity_type,
            'entity_name': row.get(column_mapping['name'], f"Unknown_{idx}"),
            'technology': row.get(column_mapping.get('technology')),
            'attributes': {
                col: str(val) for col, val in row.items() 
                if pd.notna(val) and col not in [column_mapping['name']]
            },
            'dependencies': parse_dependencies(row.get(column_mapping.get('dependencies', ''))),
            'confidence_score': 0.95,  # High confidence for structured data
            'extraction_source': f"{doc['filename']}" + (f" (Sheet: {sheet_name})" if sheet_name else ""),
            'document_id': doc['id']
        }
        entities.append(entity)
    
    return entities


def infer_column_mapping(columns: List[str]) -> Dict[str, str]:
    """Map spreadsheet columns to entity fields"""
    
    mapping = {}
    
    # Name column
    name_candidates = ['name', 'hostname', 'server name', 'application', 'app name', 'service']
    mapping['name'] = next((col for col in columns if any(c in col for c in name_candidates)), columns[0])
    
    # Technology column
    tech_candidates = ['technology', 'tech stack', 'platform', 'os', 'framework']
    mapping['technology'] = next((col for col in columns if any(c in col for c in tech_candidates)), None)
    
    # Dependencies column
    dep_candidates = ['dependencies', 'depends on', 'connections', 'integrates with']
    mapping['dependencies'] = next((col for col in columns if any(c in col for c in dep_candidates)), None)
    
    return mapping


def infer_entity_type(row: pd.Series, sheet_name: str = None) -> str:
    """Infer entity type from row content or sheet name"""
    
    # From sheet name
    if sheet_name:
        sheet_lower = sheet_name.lower()
        if 'server' in sheet_lower or 'vm' in sheet_lower:
            return 'server'
        elif 'app' in sheet_lower:
            return 'application'
        elif 'db' in sheet_lower or 'database' in sheet_lower:
            return 'database'
        elif 'network' in sheet_lower:
            return 'network'
    
    # From row content (keywords in name or type column)
    row_str = ' '.join([str(v).lower() for v in row.values if pd.notna(v)])
    
    if any(kw in row_str for kw in ['postgres', 'mysql', 'oracle', 'mongodb', 'redis']):
        return 'database'
    elif any(kw in row_str for kw in ['api', 'service', 'microservice']):
        return 'service'
    elif any(kw in row_str for kw in ['app', 'application', 'web']):
        return 'application'
    elif any(kw in row_str for kw in ['server', 'vm', 'ec2', 'compute']):
        return 'server'
    
    return 'unknown'


def parse_dependencies(dep_string: Any) -> List[Dict]:
    """Parse dependency field (e.g., 'UserDB, PaymentService, CacheLayer')"""
    
    if pd.isna(dep_string) or not dep_string:
        return []
    
    # Split by common delimiters
    deps = re.split(r'[,;|\n]', str(dep_string))
    
    return [{'target': d.strip(), 'type': 'unknown'} for d in deps if d.strip()]
```

#### Feature 2.2.7: Entity Extraction (Document Processing)

**PDF/Word Analysis:**

```python
async def process_document(doc: Dict) -> List[Dict]:
    """Extract entities from technical documentation"""
    
    # Extract text
    if doc['filename'].endswith('.pdf'):
        text = extract_text_from_pdf(doc['storage_path'])
    elif doc['filename'].endswith('.docx'):
        text = extract_text_from_docx(doc['storage_path'])
    else:
        return []
    
    # Use AI to extract structured entities from unstructured text
    prompt = f"""
    Analyze this technical documentation and extract infrastructure components.
    
    Look for mentions of:
    - Applications and services (names, technologies)
    - Databases (names, types)
    - Servers and infrastructure (hostnames, IPs)
    - Dependencies and integrations
    - Technology stack mentions
    
    Document text:
    {text[:20000]}  # Limit to avoid token overflow
    
    Output JSON array:
    [
      {{"type": "application", "name": "OrderService", "technology": "Java Spring", "confidence": 0.8}},
      {{"type": "database", "name": "OrderDB", "technology": "PostgreSQL", "confidence": 0.9}}
    ]
    
    Only include components explicitly mentioned. Assign confidence based on clarity.
    """
    
    response = await bedrock_client.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4096,
            'messages': [{'role': 'user', 'content': prompt}],
            'system': 'You are an expert at extracting structured data from technical documentation.'
        })
    )
    
    result = json.loads(response['body'].read())
    extracted = json.loads(result['content'][0]['text'])
    
    # Convert to internal format
    entities = []
    for e in extracted:
        entity = {
            'entity_type': e['type'],
            'entity_name': e['name'],
            'technology': e.get('technology'),
            'attributes': {'mentioned_in': doc['filename']},
            'dependencies': [],
            'confidence_score': e.get('confidence', 0.7),
            'extraction_source': doc['filename'],
            'document_id': doc['id']
        }
        entities.append(entity)
    
    return entities
```

#### Feature 2.2.8: Entity Deduplication

**Challenge:** Same entity mentioned in multiple documents

**Algorithm:**

```python
def deduplicate_entities(entities: List[Dict]) -> List[Dict]:
    """Merge duplicate entities using fuzzy matching and confidence scoring"""
    
    from fuzzywuzzy import fuzz
    
    unique = []
    duplicates = []
    
    for entity in entities:
        # Find potential matches
        matches = []
        for u in unique:
            if u['entity_type'] == entity['entity_type']:
                # Name similarity
                name_sim = fuzz.ratio(u['entity_name'].lower(), entity['entity_name'].lower())
                
                # Technology match (if both specified)
                tech_match = (
                    u.get('technology') == entity.get('technology') 
                    if u.get('technology') and entity.get('technology') 
                    else True
                )
                
                if name_sim > 85 and tech_match:
                    matches.append((u, name_sim))
        
        if matches:
            # Merge with best match
            best_match, score = max(matches, key=lambda x: x[1])
            merged = merge_entities(best_match, entity)
            unique[unique.index(best_match)] = merged
            duplicates.append((entity, best_match, score))
        else:
            unique.append(entity)
    
    # Log duplicates for audit
    for dup, original, score in duplicates:
        print(f"Merged: {dup['entity_name']} → {original['entity_name']} (similarity: {score}%)")
    
    return unique


def merge_entities(e1: Dict, e2: Dict) -> Dict:
    """Merge two entities, preferring higher confidence data"""
    
    merged = e1.copy()
    
    # Use higher confidence name
    if e2['confidence_score'] > e1['confidence_score']:
        merged['entity_name'] = e2['entity_name']
    
    # Merge technologies (prefer more specific)
    if e2.get('technology') and not e1.get('technology'):
        merged['technology'] = e2['technology']
    
    # Merge attributes (union)
    merged['attributes'] = {**e1.get('attributes', {}), **e2.get('attributes', {})}
    
    # Merge dependencies (union, deduplicate)
    deps1 = e1.get('dependencies', [])
    deps2 = e2.get('dependencies', [])
    all_deps = deps1 + deps2
    unique_deps = {d['target']: d for d in all_deps}.values()
    merged['dependencies'] = list(unique_deps)
    
    # Track sources
    sources = [e1.get('extraction_source'), e2.get('extraction_source')]
    merged['extraction_source'] = ', '.join(filter(None, sources))
    
    # Average confidence
    merged['confidence_score'] = (e1['confidence_score'] + e2['confidence_score']) / 2
    
    return merged
```

#### Feature 2.2.9: Human Review Workflow

**Low Confidence Threshold:** < 0.75

**Review UI:**

```python
# pages/4_📄_Document_Analysis.py

st.markdown("### ⚠️ Entities Requiring Review")

low_conf = [e for e in entities if e['confidence_score'] < 0.75]

if low_conf:
    st.warning(f"{len(low_conf)} entities need verification")
    
    for entity in low_conf:
        with st.expander(f"🔍 {entity['entity_name']} (Confidence: {entity['confidence_score']:.0%})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Extracted From:** {entity['extraction_source']}")
                st.write(f"**Original Type:** {entity['entity_type']}")
                st.write(f"**Technology:** {entity.get('technology', 'Unknown')}")
            
            with col2:
                # Edit fields
                new_name = st.text_input("Name", entity['entity_name'], key=f"name_{entity['id']}")
                new_type = st.selectbox(
                    "Type",
                    ['application', 'service', 'database', 'server', 'network', 'storage', 'other'],
                    index=['application', 'service', 'database', 'server', 'network', 'storage', 'other'].index(entity['entity_type']),
                    key=f"type_{entity['id']}"
                )
                new_tech = st.text_input("Technology", entity.get('technology', ''), key=f"tech_{entity['id']}")
            
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("✅ Approve", key=f"approve_{entity['id']}"):
                    db.update_discovered_entity(
                        entity['id'],
                        entity_name=new_name,
                        entity_type=new_type,
                        technology=new_tech,
                        confidence_score=1.0  # Human-verified
                    )
                    st.success("Approved!")
                    st.rerun()
            
            with action_col2:
                if st.button("❌ Delete", key=f"delete_{entity['id']}", type="secondary"):
                    db.delete_discovered_entity(entity['id'])
                    st.success("Deleted!")
                    st.rerun()
            
            with action_col3:
                if st.button("🔀 Merge", key=f"merge_{entity['id']}", type="secondary"):
                    # Show merge UI
                    st.info("Merge functionality coming soon")
else:
    st.success("✅ All entities have high confidence!")
```

---

## 3. Technical Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Streamlit)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Onboarding │  │   Document   │  │  Entity Review &       │ │
│  │  Page       │→ │   Upload     │→ │  Dependency Graph      │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Backend Services                             │
│  ┌──────────────────┐    ┌─────────────────────────────────┐   │
│  │  File Upload     │    │  Document Analysis              │   │
│  │  Handler         │→   │  Orchestrator                   │   │
│  └──────────────────┘    └─────────────────────────────────┘   │
│                                    │                             │
│                           ┌────────┴────────┐                   │
│                           │                  │                   │
│                           ↓                  ↓                   │
│  ┌────────────────────────────────┐  ┌─────────────────────┐   │
│  │  DocumentAnalysisAgent         │  │  Entity             │   │
│  │  ├─ DiagramProcessor (Vision)  │  │  Consolidation      │   │
│  │  ├─ SpreadsheetProcessor       │  │  Service            │   │
│  │  ├─ DocumentProcessor           │  │  ├─ Deduplication  │   │
│  │  └─ ConfigProcessor             │  │  └─ Merging        │   │
│  └────────────────────────────────┘  └─────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │   SQLite     │  │   File Storage   │  │   AWS Bedrock   │   │
│  │   Database   │  │   (S3 or Local)  │  │   (Claude API)  │   │
│  └──────────────┘  └──────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Frontend** | Streamlit | Existing framework, rapid development |
| **Backend** | Python 3.9+ | Current platform language |
| **Database** | SQLite | Existing choice, sufficient for workload |
| **File Storage** | S3 (prod) / Local (dev) | Scalable, secure |
| **Vision AI** | Claude 3 Opus (Bedrock) | Best-in-class vision capabilities |
| **Text AI** | Claude 3 Sonnet (Bedrock) | Cost-effective for text |
| **Excel Parsing** | Pandas | Industry standard |
| **PDF Parsing** | PyPDF2 + pdfplumber | Robust text extraction |
| **Word Parsing** | python-docx | Native .docx support |
| **Visio Conversion** | LibreOffice CLI | Open-source, reliable |
| **Fuzzy Matching** | fuzzywuzzy | Entity deduplication |
| **Graph Visualization** | Plotly / vis.js | Interactive dependency graphs |

### 3.3 File Storage Strategy

**Development Environment:**
```
data/
  uploads/
    {project_id}/
      {document_id}_{filename}
```

**Production Environment:**
```
S3 Bucket: agentic-services-uploads
Structure:
  {environment}/
    {project_id}/
      documents/
        {document_id}_{filename}
      analysis_results/
        {job_id}_entities.json
```

**File Lifecycle:**
1. Upload → Temp storage (Streamlit)
2. Validation → Permanent storage (S3/Local)
3. Processing → Keep original
4. Analysis Complete → Optional: Delete originals (GDPR), keep entities
5. Project Archive → Move to glacier (S3) or archive folder

---

## 4. Data Model

### 4.1 Database Schema

#### Table: `uploaded_documents`

```sql
CREATE TABLE uploaded_documents (
    id TEXT PRIMARY KEY,  -- UUID
    project_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT,  -- User's original name
    file_type TEXT NOT NULL,  -- 'diagram', 'spreadsheet', 'document', 'config'
    file_format TEXT,  -- 'pdf', 'xlsx', 'png', etc.
    file_size INTEGER NOT NULL,  -- bytes
    storage_path TEXT NOT NULL,  -- S3 key or local path
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,  -- User ID (future)
    processing_status TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,  -- Error message if failed
    entities_extracted INTEGER DEFAULT 0,
    metadata JSON,  -- {sheet_count, page_count, dimensions, etc}
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_uploaded_documents_project ON uploaded_documents(project_id);
CREATE INDEX idx_uploaded_documents_status ON uploaded_documents(processing_status);
```

#### Table: `discovered_entities`

```sql
CREATE TABLE discovered_entities (
    id TEXT PRIMARY KEY,  -- UUID
    project_id TEXT NOT NULL,
    document_id TEXT,  -- Source document (can be NULL if merged)
    entity_type TEXT NOT NULL,  -- 'application', 'service', 'database', 'server', 'network', 'storage', 'other'
    entity_name TEXT NOT NULL,
    technology TEXT,  -- 'PostgreSQL', 'Spring Boot', etc.
    version TEXT,  -- Technology version if available
    environment TEXT,  -- 'prod', 'dev', 'staging' if mentioned
    attributes JSON,  -- {os, cpu, memory, location, ip, port, etc}
    dependencies JSON,  -- [{"target": "entity_name", "type": "http", "port": 443}]
    confidence_score REAL NOT NULL,  -- 0.0 to 1.0
    review_status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'needs_review'
    reviewed_by TEXT,  -- User ID
    reviewed_at TIMESTAMP,
    extraction_source TEXT,  -- Filename(s) where found
    extraction_method TEXT,  -- 'vision_ai', 'spreadsheet_parse', 'text_ai', 'manual'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES uploaded_documents(id) ON DELETE SET NULL
);

CREATE INDEX idx_discovered_entities_project ON discovered_entities(project_id);
CREATE INDEX idx_discovered_entities_type ON discovered_entities(entity_type);
CREATE INDEX idx_discovered_entities_confidence ON discovered_entities(confidence_score);
CREATE INDEX idx_discovered_entities_review ON discovered_entities(review_status);
```

#### Table: `document_analysis_jobs`

```sql
CREATE TABLE document_analysis_jobs (
    id TEXT PRIMARY KEY,  -- UUID
    project_id TEXT NOT NULL,
    document_ids JSON NOT NULL,  -- ["doc_id_1", "doc_id_2"]
    job_type TEXT DEFAULT 'full_analysis',  -- 'full_analysis', 'incremental', 're_analysis'
    status TEXT DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    progress_percentage INTEGER DEFAULT 0,
    total_documents INTEGER,
    documents_processed INTEGER DEFAULT 0,
    entities_found INTEGER DEFAULT 0,
    entities_deduplicated INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    error_message TEXT,
    metadata JSON,  -- {diagram_count, spreadsheet_count, ai_model_used, etc}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_analysis_jobs_project ON document_analysis_jobs(project_id);
CREATE INDEX idx_analysis_jobs_status ON document_analysis_jobs(status);
```

#### Table: `entity_relationships` (Optional - for explicit relationship tracking)

```sql
CREATE TABLE entity_relationships (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    relationship_type TEXT,  -- 'depends_on', 'connects_to', 'hosted_on', 'stores_in'
    protocol TEXT,  -- 'http', 'tcp', 'jdbc', etc.
    port INTEGER,
    confidence_score REAL,
    extracted_from TEXT,  -- Document source
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (source_entity_id) REFERENCES discovered_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entity_id) REFERENCES discovered_entities(id) ON DELETE CASCADE,
    UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

CREATE INDEX idx_relationships_source ON entity_relationships(source_entity_id);
CREATE INDEX idx_relationships_target ON entity_relationships(target_entity_id);
```

### 4.2 Entity Attributes JSON Schema

```json
{
  "application": {
    "os": "Linux",
    "language": "Java",
    "framework": "Spring Boot",
    "version": "2.7.0",
    "port": 8080,
    "environment": "production",
    "location": "AWS us-east-1",
    "team_owner": "Platform Team"
  },
  "server": {
    "hostname": "app-server-01",
    "ip_address": "10.0.1.50",
    "os": "Ubuntu 20.04",
    "cpu_cores": 8,
    "memory_gb": 32,
    "disk_gb": 500,
    "environment": "production"
  },
  "database": {
    "db_type": "PostgreSQL",
    "version": "14.2",
    "size_gb": 250,
    "connections_max": 100,
    "backup_enabled": true,
    "environment": "production"
  }
}
```

### 4.3 Data Relationships

```
projects (1) ──→ (N) uploaded_documents
projects (1) ──→ (N) document_analysis_jobs
projects (1) ──→ (N) discovered_entities

uploaded_documents (1) ──→ (N) discovered_entities
document_analysis_jobs (1) ──→ (N) uploaded_documents [via JSON array]

discovered_entities (N) ←→ (N) discovered_entities [via dependencies JSON or entity_relationships table]
```

---

## 5. AI/ML Strategy

### 5.1 Model Selection

| Use Case | Model | Justification | Cost |
|----------|-------|---------------|------|
| Diagram Analysis | Claude 3 Opus | Best vision capabilities | $15/MTok |
| Document Text | Claude 3 Sonnet | Good balance | $3/MTok |
| Spreadsheet NLU | Claude 3 Haiku | Fast, cheap for structured data | $0.25/MTok |
| Re-analysis | Claude 3 Sonnet | Consistency with initial | $3/MTok |

### 5.2 Prompt Engineering

**Prompt Template for Diagrams:**

```python
DIAGRAM_ANALYSIS_PROMPT = """
You are analyzing an architecture/network diagram for a cloud migration project.

TASK: Extract ALL components and connections visible in this diagram.

COMPONENTS TO FIND:
- Applications (web apps, services, APIs)
- Databases (SQL, NoSQL, caches)
- Servers (VMs, containers, physical)
- Networks (VPCs, subnets, zones)
- Load balancers, gateways, proxies
- Storage (S3, NFS, SAN)
- Queues, message brokers
- External services (third-party integrations)

FOR EACH COMPONENT:
1. Name: Exact label from diagram
2. Type: {application|service|database|server|network|load_balancer|queue|storage|external|other}
3. Technology: If labeled (e.g., "PostgreSQL", "NGINX", "AWS S3")
4. Position: Approximate x,y coordinates (helps with layout)
5. Visual notes: Color, shape type (helps with identification)

FOR EACH CONNECTION (arrow):
1. From: Source component name
2. To: Target component name
3. Type: If labeled (e.g., "HTTPS", "REST", "JDBC", "TCP/443")
4. Bidirectional: true/false

OUTPUT FORMAT:
{
  "entities": [
    {
      "name": "User Service",
      "type": "application",
      "technology": "Node.js",
      "position": {"x": 150, "y": 200},
      "visual": {"color": "blue", "shape": "rectangle"}
    }
  ],
  "connections": [
    {
      "from": "User Service",
      "to": "User Database",
      "type": "PostgreSQL",
      "bidirectional": false
    }
  ]
}

IMPORTANT:
- Extract EVERYTHING you can see, even if labels are unclear
- If a label is ambiguous, include it anyway with lower confidence
- Group related components if obvious (e.g., "User Service Cluster")
- Preserve original names exactly as shown
- If technology icons are visible (AWS logos, database symbols), identify them

Be thorough and precise. This data feeds into migration planning.
"""
```

**Prompt Template for Documents:**

```python
DOCUMENT_ANALYSIS_PROMPT = """
You are analyzing technical documentation for a cloud migration discovery phase.

TASK: Extract mentions of infrastructure components, applications, and services.

LOOK FOR:
1. Application/Service names and technologies
2. Database names and types
3. Server hostnames and specifications
4. Integration points and dependencies
5. Technology stack details
6. IP addresses, ports, URLs
7. Environment information (prod, staging, dev)

FOR EACH COMPONENT FOUND:
{
  "type": "application|service|database|server|network|other",
  "name": "Exact name from document",
  "technology": "Technology/platform if mentioned",
  "confidence": 0.0-1.0,  // How certain are you?
  "context": "Brief quote showing where it was mentioned"
}

CONFIDENCE SCORING:
- 0.9-1.0: Explicitly named with details
- 0.7-0.9: Clear mention but limited details
- 0.5-0.7: Implied or ambiguous reference
- <0.5: Don't include (too uncertain)

DOCUMENT TEXT:
{document_text}

OUTPUT: JSON array of components
"""
```

### 5.3 Accuracy Improvement Strategies

**1. Multi-Pass Analysis:**
```python
# First pass: Extract entities
entities_pass1 = await analyze_diagram(image, DIAGRAM_ANALYSIS_PROMPT)

# Second pass: Validate and enrich
validation_prompt = f"""
Here are entities I extracted from a diagram:
{json.dumps(entities_pass1)}

Please:
1. Verify entity types are correct
2. Fix any obvious errors
3. Infer missing technologies from context
4. Add confidence scores

Return corrected JSON.
"""
entities_final = await analyze_with_prompt(validation_prompt)
```

**2. Cross-Document Validation:**
```python
# If entity appears in multiple documents, boost confidence
entity_sources = {}
for entity in all_entities:
    key = entity['entity_name'].lower()
    if key not in entity_sources:
        entity_sources[key] = []
    entity_sources[key].append(entity)

# Merge entities with 2+ sources
for name, entities in entity_sources.items():
    if len(entities) >= 2:
        merged = merge_entities(entities)
        merged['confidence_score'] = min(0.95, merged['confidence_score'] + 0.1)
```

**3. Feedback Loop:**
```python
# Track user corrections
if user_corrected_entity:
    # Store correction
    db.create_entity_correction(
        original=old_entity,
        corrected=new_entity,
        user_id=user_id
    )
    
    # Use corrections to fine-tune prompts (future)
    # For now: Log for analysis
```

### 5.4 Cost Estimation

**Typical Project:**
- 20 diagrams (PNG, ~2MB each) → 40MB
- 10 Excel files → 50MB
- 5 PDFs (200 pages total) → 20MB text

**Token Estimation:**
- Diagrams: 20 × 1,500 tokens (image) + 500 (prompt) = 40,000 tokens
- Documents: 200 pages × 500 tokens/page = 100,000 tokens
- Excel: Minimal (structured data, Haiku)

**Cost Calculation:**
- Vision (Opus): 40K input × $15/MTok = $0.60
- Text (Sonnet): 100K input × $3/MTok = $0.30
- Total: **~$1 per project**

**Optimization:**
- Use Haiku for re-analysis: $0.25/MTok
- Cache diagram analysis results
- Batch similar documents

---

## 6. User Interface Design

### 6.1 Page Structure

#### Page: Onboarding (Enhanced)

**Step 1: Project Info** (unchanged)

**Step 2: Discovery Mode** (NEW)
```
┌─────────────────────────────────────────────────────────┐
│ 🔍 How would you like to discover your infrastructure?  │
│                                                          │
│  ○ Live Infrastructure Scan                             │
│    Connect to your AWS/Azure/on-prem environment        │
│    Agents will scan and inventory automatically         │
│                                                          │
│  ● Document-Based Discovery [SELECTED]                  │
│    Upload diagrams, inventories, and documentation      │
│    AI will extract components and relationships         │
│                                                          │
│  [Why choose this?] [Compare approaches]                │
└─────────────────────────────────────────────────────────┘
```

**Step 3: File Upload** (conditional, NEW)
```
┌─────────────────────────────────────────────────────────┐
│ 📤 Upload Your Documentation                            │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Drag & drop files here                           │  │
│  │  or click to browse                               │  │
│  │                                                    │  │
│  │  Supported: PDF, Excel, Word, images, Visio,     │  │
│  │  Draw.io, configs                                 │  │
│  │  Max 100 files, 2GB total                         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  Uploaded Files (8):                                    │
│  📊 architecture_v3.vsdx           (12 MB)   [Remove]  │
│  📊 network_diagram.png            (3 MB)    [Remove]  │
│  📋 server_inventory.xlsx          (2 MB)    [Remove]  │
│  📋 application_list.csv           (500 KB)  [Remove]  │
│  📄 tech_spec_overview.pdf         (8 MB)    [Remove]  │
│  📄 integration_guide.docx         (4 MB)    [Remove]  │
│  ⚙️  terraform_configs.tf           (200 KB)  [Remove]  │
│  📊 data_flow_diagram.drawio       (1 MB)    [Remove]  │
│                                                          │
│  Summary:                                               │
│  • Diagrams: 3 files (16 MB)                           │
│  • Inventories: 2 files (2.5 MB)                       │
│  • Documentation: 2 files (12 MB)                      │
│  • Configurations: 1 file (200 KB)                     │
│                                                          │
│  [Add More Files]    [Clear All]    [▶ Start Analysis] │
└─────────────────────────────────────────────────────────┘
```

#### Page: Document Analysis (NEW)

**URL:** `/pages/4_📄_Document_Analysis.py`

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ 📄 Document Analysis - Project: E-Commerce Migration        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ 📊 Analysis Status                                           │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Status: ✅ Completed                                   │   │
│ │ Duration: 3 minutes 24 seconds                        │   │
│ │ Documents Processed: 8 / 8                            │   │
│ │ Entities Discovered: 127                              │   │
│ │ Entities Deduplicated: 18                             │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ 📤 Uploaded Documents                                        │
│ [View All] [Filter: All Types ▼] [Sort: Name ▼]            │
│                                                               │
│ ┌─ 📊 architecture_v3.vsdx (Diagram) ───────────────────┐   │
│ │ Size: 12 MB | Status: ✅ Processed | Entities: 45     │   │
│ │ [Preview] [Download] [Reprocess]                      │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                               │
│ ┌─ 📋 server_inventory.xlsx (Spreadsheet) ──────────────┐   │
│ │ Size: 2 MB | Status: ✅ Processed | Entities: 38      │   │
│ │ Sheets: Servers (25), Databases (13)                  │   │
│ │ [Preview] [Download] [Reprocess]                      │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                               │
│ ... (6 more documents)                                       │
│                                                               │
│ 🎯 Discovered Entities                                       │
│ [Applications (42)] [Databases (18)] [Servers (35)]          │
│ [Networks (12)] [Services (20)] [All (127)]                  │
│                                                               │
│ ┌─ Applications (42) ──────────────────────────────────┐    │
│ │ [Filter] [Export CSV]                                 │    │
│ │                                                        │    │
│ │ ✅ UserService (Spring Boot)           Confidence: 95%│    │
│ │    From: architecture_v3.vsdx, application_list.csv   │    │
│ │    Dependencies: UserDB, AuthService (2)              │    │
│ │    [View Details] [Edit] [Delete]                     │    │
│ │                                                        │    │
│ │ ⚠️  PaymentAPI (Unknown tech)          Confidence: 68%│    │
│ │    From: tech_spec_overview.pdf                       │    │
│ │    Dependencies: PaymentDB, Stripe (2)                │    │
│ │    [Review Required] [Edit] [Delete]                  │    │
│ │                                                        │    │
│ │ ... (40 more applications)                            │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                               │
│ ⚠️  Entities Requiring Review (12)                           │
│ [Show Low Confidence Items]                                  │
│                                                               │
│ 🕸️ Dependency Graph                                          │
│ [View Interactive Graph] [Export as Image]                   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │  [Interactive graph visualization here]               │   │
│ │   - Nodes: Entities                                    │   │
│ │   - Edges: Dependencies                                │   │
│ │   - Colors: Entity types                               │   │
│ │   - Size: Number of dependencies                       │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ [✅ Approve Discovery] [Upload More Documents] [Export All]  │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Wireframes

*Note: Detailed wireframes would be created in Figma/Sketch, but here's the conceptual flow:*

**User Flow Diagram:**
```
Start
  │
  ├─→ Create Project
  │     │
  │     ├─→ Choose Discovery Mode
  │     │     │
  │     │     ├─→ [Live Scan] → (existing flow)
  │     │     │
  │     │     └─→ [Document Upload]
  │               │
  │               ├─→ Upload Files
  │               │     │
  │               │     ├─→ Add More
  │               │     │
  │               │     └─→ Start Analysis
  │               │           │
  │               │           ├─→ Processing... (show progress)
  │               │           │
  │               │           └─→ Analysis Complete
  │               │                 │
  │               │                 ├─→ View Entities
  │               │                 │     │
  │               │                 │     ├─→ Review Low Confidence
  │               │                 │     │     │
  │               │                 │     │     ├─→ Approve/Edit/Delete
  │               │                 │     │     │
  │               │                 │     │     └─→ Back to List
  │               │                 │     │
  │               │                 │     └─→ View Graph
  │               │                 │
  │               │                 └─→ Approve Discovery
  │               │                       │
  │               │                       └─→ Continue to Planning
  │               │
  │               └─→ Upload More Docs (incremental)
  │
  └─→ End
```

---

## 7. Integration Points

### 7.1 Integration with Existing Agents

**Discovery Phase:**
- **Current:** `DiscoveryAgent` scans live infrastructure
- **New:** `DocumentAnalysisAgent` extracts from documents
- **Output Format:** SAME (stored in `discovered_entities` table)

**Key Point:** Downstream agents (Analysis, Planning, Execution) don't need to know the source of discovery data. They work with the unified `discovered_entities` table.

**Workflow Integration:**

```python
# orchestrator/workflow_orchestrator.py

async def execute_discovery_phase(self, project: Dict):
    """Execute discovery - either live scan or document analysis"""
    
    if project['discovery_type'] == 'document_based':
        # Use DocumentAnalysisAgent
        agent = DocumentAnalysisAgent()
        result = await agent.execute({
            'project_id': project['id'],
            'document_ids': self.get_pending_documents(project['id'])
        })
        
        # Wait for human review if low confidence entities
        if result.get('low_confidence_count', 0) > 0:
            self.update_project_status(project['id'], 'awaiting_review')
            return {'status': 'paused', 'reason': 'awaiting_human_review'}
        
    else:
        # Use existing DiscoveryAgent (live scan)
        agent = DiscoveryAgent()
        result = await agent.execute({
            'project_id': project['id'],
            'infrastructure_config': project['infrastructure_config']
        })
    
    # Store discovery data (same format for both)
    self.store_discovery_results(project['id'], result)
    
    # Proceed to Analysis phase
    return {'status': 'completed', 'next_phase': 'analysis'}
```

### 7.2 Data Flow Between Components

```
Upload
  │
  ├─→ Store files (S3/Local)
  │
  ├─→ Create uploaded_documents records
  │
  └─→ Trigger document_analysis_jobs
        │
        ├─→ DocumentAnalysisAgent
        │     │
        │     ├─→ Process by type
        │     │     ├─→ DiagramProcessor → Vision AI
        │     │     ├─→ SpreadsheetProcessor → Pandas
        │     │     ├─→ DocumentProcessor → Text AI
        │     │     └─→ ConfigProcessor → Parser
        │     │
        │     └─→ Return raw entities
        │
        ├─→ EntityConsolidationService
        │     │
        │     ├─→ Deduplicate
        │     ├─→ Merge
        │     └─→ Return unique entities
        │
        ├─→ Store in discovered_entities
        │
        └─→ Notify UI (status update)
              │
              └─→ User reviews
                    │
                    ├─→ Approve → Continue workflow
                    └─→ Edit → Update entities → Continue
```

### 7.3 API Contracts

**Internal API (Agent Interface):**

```python
class DocumentAnalysisAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        {
            "project_id": "uuid",
            "document_ids": ["doc1", "doc2"],
            "options": {
                "skip_deduplication": false,
                "confidence_threshold": 0.5
            }
        }
        
        Output:
        {
            "status": "completed" | "failed",
            "entities_found": 127,
            "entities_unique": 109,
            "low_confidence_count": 12,
            "processing_time_seconds": 204,
            "error": null | "error message"
        }
        """
```

**Database Service Interface:**

```python
class DocumentService:
    def upload_document(self, project_id: str, file: UploadedFile) -> str:
        """Returns document_id"""
    
    def get_project_documents(self, project_id: str, status: str = None) -> List[Dict]:
        """Returns list of documents"""
    
    def start_analysis(self, project_id: str, document_ids: List[str]) -> str:
        """Returns job_id"""
    
    def get_analysis_status(self, job_id: str) -> Dict:
        """Returns job status and progress"""

class EntityService:
    def get_discovered_entities(self, project_id: str, entity_type: str = None) -> List[Dict]:
        """Returns list of entities"""
    
    def update_entity(self, entity_id: str, updates: Dict) -> None:
        """Update entity fields"""
    
    def delete_entity(self, entity_id: str) -> None:
        """Delete entity"""
    
    def get_entity_graph(self, project_id: str) -> Dict:
        """Returns graph data for visualization"""
```

---

## 8. Security & Compliance

### 8.1 Data Security

**File Upload Security:**
1. **Size Limits:** Enforce at Streamlit level (500MB/file, 2GB/project)
2. **Type Validation:** Whitelist file extensions + MIME type check
3. **Virus Scanning:** Optional integration with ClamAV or AWS GuardDuty
4. **Encryption:**
   - **In Transit:** HTTPS only
   - **At Rest:** S3 server-side encryption (SSE-S3 or SSE-KMS)

**Access Control:**
- Projects are isolated by `project_id`
- Future: Add user authentication, ensure users only access their projects
- File paths include project_id to prevent path traversal

**Sensitive Data:**
- **PII Detection:** Scan extracted entities for emails, SSNs, credit cards
- **Redaction:** Option to redact sensitive fields before storage
- **Audit Log:** Track all document uploads, entity modifications

### 8.2 Compliance Considerations

**GDPR:**
- **Right to Erasure:** Implement project/document deletion
- **Data Minimization:** Only extract necessary entity attributes
- **Consent:** User acknowledges data processing during upload

**SOC 2:**
- **Encryption:** All data encrypted at rest and in transit
- **Logging:** All actions logged (upload, analysis, review, approval)
- **Access Control:** Role-based access (future)

**HIPAA (if applicable):**
- **BAA Required:** With AWS if storing PHI
- **Audit Trails:** All entity access logged
- **Encryption:** KMS keys for S3

### 8.3 Data Retention

**Policy:**
- **Uploaded Documents:** Retain 90 days by default, then archive or delete
- **Discovered Entities:** Retain for project lifetime + 1 year
- **Analysis Jobs:** Retain metadata indefinitely, logs 1 year

**Implementation:**
```python
def archive_old_documents():
    """Run daily: Archive documents > 90 days old"""
    threshold = datetime.now() - timedelta(days=90)
    docs = db.get_documents_older_than(threshold)
    
    for doc in docs:
        # Move to S3 Glacier or delete
        if doc['storage_path'].startswith('s3://'):
            s3_client.copy_object(
                CopySource=doc['storage_path'],
                Bucket='agentic-services-archive',
                Key=f"archived/{doc['id']}",
                StorageClass='GLACIER'
            )
            s3_client.delete_object(Bucket='agentic-services-uploads', Key=doc['storage_path'])
        
        db.update_document(doc['id'], storage_path=f"archived/{doc['id']}", archived=True)
```

---

## 9. Performance & Scalability

### 9.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| File Upload Speed | > 10 MB/s | User-perceived upload time |
| Analysis Time (per file) | < 30s (diagram), < 10s (spreadsheet) | Server processing time |
| Total Analysis Time | < 5 min for typical project (20 files) | End-to-end job duration |
| Concurrent Projects | 10 simultaneous analyses | Load test with 10 projects |
| Database Query Time | < 500ms for entity list | P95 latency |
| UI Page Load | < 2s | First contentful paint |

### 9.2 Bottlenecks & Mitigations

**Bottleneck 1: Vision AI Latency**
- **Problem:** Claude Vision takes 10-20s per diagram
- **Mitigation:**
  - Process diagrams in parallel (5 at a time)
  - Cache results (if same file re-uploaded)
  - Use async processing with progress updates

**Bottleneck 2: Large File Processing**
- **Problem:** 50MB Visio file takes time to convert
- **Mitigation:**
  - Stream file upload (don't load entirely in memory)
  - Process in background worker (Celery or async task)
  - Show progress bar to user

**Bottleneck 3: Database Writes (127 entities)**
- **Problem:** Inserting 127 entities one-by-one is slow
- **Mitigation:**
  - Bulk insert: `db.bulk_create_entities(entities)`
  - Use SQLite transactions
  - Index optimization

**Bottleneck 4: Dependency Graph Rendering (127 nodes)**
- **Problem:** Large graph is slow to render in browser
- **Mitigation:**
  - Server-side graph layout computation
  - Progressive rendering (show nodes first, edges later)
  - Limit to 50 nodes by default, paginate

### 9.3 Scalability Strategy

**Current Architecture (MVP):**
- Single server (Streamlit + SQLite)
- Local or S3 file storage
- Synchronous processing

**Future Scale (100+ concurrent users):**

```
┌─────────────────────────────────────────────────────┐
│             Load Balancer (ALB)                     │
└───────────────┬─────────────────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼──────┐ ┌─────▼───────┐
│ Streamlit    │ │ Streamlit   │  (Auto-scaling ECS)
│ Instance 1   │ │ Instance 2  │
└───────┬──────┘ └─────┬───────┘
        │               │
        └───────┬───────┘
                │
┌───────────────▼─────────────────┐
│      RDS PostgreSQL              │  (Replace SQLite)
│      (Multi-AZ)                  │
└──────────────────────────────────┘
                │
┌───────────────▼─────────────────┐
│      S3 (File Storage)           │
│      + CloudFront (CDN)          │
└──────────────────────────────────┘
                │
┌───────────────▼─────────────────┐
│   SQS + Lambda Workers           │  (Async processing)
│   - Document analysis            │
│   - Entity extraction            │
└──────────────────────────────────┘
```

**Optimization Techniques:**
1. **Caching:** Redis for entity lists, graph data
2. **CDN:** CloudFront for static assets (diagrams)
3. **Async Workers:** SQS + Lambda for heavy processing
4. **Database:** Migrate to PostgreSQL with read replicas
5. **File Chunking:** Upload large files in chunks (multipart)

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal:** Basic document upload and storage

| Task | Effort | Owner | Deliverable |
|------|--------|-------|-------------|
| Design database schema | 4h | Tech Lead | SQL migration scripts |
| Implement `uploaded_documents` table | 2h | Backend Dev | DB migration |
| Add file upload UI to onboarding | 6h | Frontend Dev | Streamlit page update |
| Implement file storage (local + S3) | 8h | Backend Dev | Storage service |
| Add file validation and categorization | 4h | Backend Dev | Validator module |
| **TOTAL** | **24h (3 days)** | | |

**Acceptance Criteria:**
- ✅ User can upload 10+ files in onboarding
- ✅ Files stored in database with metadata
- ✅ Files stored in S3 (or local for dev)
- ✅ Files categorized automatically

### Phase 2: Document Processing (Week 3-4)

**Goal:** Extract entities from uploaded documents

| Task | Effort | Owner | Deliverable |
|------|--------|-------|-------------|
| Create `DocumentAnalysisAgent` scaffold | 4h | Agent Dev | Python class |
| Implement spreadsheet processor (Pandas) | 8h | Agent Dev | Processor module |
| Implement diagram processor (Vision AI) | 16h | Agent Dev | Vision processor |
| Implement document processor (Text AI) | 8h | Agent Dev | Text processor |
| Implement Visio conversion (LibreOffice) | 8h | DevOps | Conversion script |
| Create `discovered_entities` table | 2h | Backend Dev | DB migration |
| Implement entity storage service | 6h | Backend Dev | Service module |
| **TOTAL** | **52h (6-7 days)** | | |

**Acceptance Criteria:**
- ✅ Agent processes Excel files, extracts entities
- ✅ Agent processes PNG diagrams, extracts entities
- ✅ Agent processes PDFs, extracts entities
- ✅ Entities stored in database with confidence scores
- ✅ Basic deduplication works

### Phase 3: UI & Review (Week 5-6)

**Goal:** Allow users to view and review extracted entities

| Task | Effort | Owner | Deliverable |
|------|--------|-------|-------------|
| Create Document Analysis page | 12h | Frontend Dev | Streamlit page |
| Display uploaded documents list | 4h | Frontend Dev | UI component |
| Display discovered entities (table view) | 6h | Frontend Dev | UI component |
| Implement entity review workflow | 8h | Full Stack | Review UI + backend |
| Add entity edit/delete functionality | 6h | Full Stack | CRUD operations |
| Implement dependency graph visualization | 12h | Frontend Dev | Plotly/vis.js graph |
| Add analysis job status tracking | 4h | Backend Dev | Job service |
| **TOTAL** | **52h (6-7 days)** | | |

**Acceptance Criteria:**
- ✅ User sees analysis progress in real-time
- ✅ User sees list of discovered entities
- ✅ User can review low-confidence entities
- ✅ User can edit/delete entities
- ✅ User sees dependency graph
- ✅ User can approve discovery and proceed

### Phase 4: Integration & Testing (Week 7-8)

**Goal:** Integrate with existing workflow, test end-to-end

| Task | Effort | Owner | Deliverable |
|------|--------|-------|-------------|
| Integrate with WorkflowOrchestrator | 6h | Backend Dev | Orchestrator update |
| Update downstream agents (Analysis, Planning) | 8h | Agent Dev | Agent updates |
| Write unit tests (80% coverage) | 16h | QA Dev | Test suite |
| Write integration tests | 12h | QA Dev | Test suite |
| User acceptance testing | 8h | Product + Users | Test report |
| Bug fixes | 16h | Dev Team | Bug-free release |
| Documentation (user guide, API docs) | 8h | Tech Writer | Markdown docs |
| **TOTAL** | **74h (9-10 days)** | | |

**Acceptance Criteria:**
- ✅ Document-based discovery integrates with workflow
- ✅ All tests pass (unit + integration)
- ✅ No critical bugs
- ✅ User documentation complete
- ✅ Ready for deployment

### Phase 5: Production Deployment (Week 9)

**Goal:** Deploy to production, monitor

| Task | Effort | Owner | Deliverable |
|------|--------|-------|-------------|
| Setup S3 bucket + permissions | 2h | DevOps | Infrastructure |
| Deploy to staging environment | 4h | DevOps | Staging deploy |
| Performance testing (load test) | 6h | QA Dev | Test report |
| Security review | 4h | Security | Audit report |
| Deploy to production | 2h | DevOps | Prod deploy |
| Monitor for 1 week | 8h | On-call | Monitoring dashboards |
| **TOTAL** | **26h (3-4 days)** | | |

**Acceptance Criteria:**
- ✅ Feature live in production
- ✅ No P0/P1 incidents in first week
- ✅ Performance meets targets
- ✅ Security approved

### **Total Effort: ~228 hours (~29 days, ~6 weeks with 1 FTE)**

**With 2 developers:** ~3-4 weeks
**With 3 developers:** ~2-3 weeks

---

## 11. Risk Analysis

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Vision AI accuracy < 80% | Medium | High | - Multi-pass validation<br>- Human review workflow<br>- Fallback to manual entry |
| Large file (100MB) causes timeout | Medium | Medium | - Implement async processing<br>- Progress bars<br>- File size limits |
| Visio conversion fails | Medium | Low | - Multiple conversion methods<br>- Manual PNG upload fallback |
| S3 costs exceed budget | Low | Medium | - Lifecycle policies (90-day archive)<br>- Optional file deletion |
| Deduplication misses duplicates | Medium | Low | - Adjustable similarity threshold<br>- Manual merge tool |
| Database performance degrades with 1000+ entities | Low | Medium | - Pagination<br>- Indexing<br>- Future: PostgreSQL migration |

### 11.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Users don't trust AI extractions | Medium | High | - Show confidence scores<br>- Highlight sources<br>- Mandatory review for low confidence |
| Competitors release similar feature first | Medium | Medium | - MVP in 6 weeks<br>- Beta with select customers |
| Adoption is low (users prefer live scan) | Low | Medium | - Market research<br>- Clear value proposition<br>- Hybrid mode option |
| Extraction quality varies by document quality | High | Low | - Document quality guidelines<br>- Validation step in UI |

### 11.3 Contingency Plans

**If Vision AI is too expensive:**
- Fallback to manual diagram annotation tool
- Partner with specialized OCR vendors

**If deduplication is too slow:**
- Pre-compute similarity matrix
- Use clustering algorithms (DBSCAN)

**If users reject AI suggestions:**
- Make human review mandatory (not optional)
- Track user corrections, improve prompts

---

## 12. Success Metrics

### 12.1 Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Extraction Accuracy (Precision) | > 80% | Manual validation on 50 test docs |
| Extraction Recall | > 75% | % of actual entities found |
| Analysis Time (typical project) | < 5 min | P95 processing time |
| User Correction Rate | < 20% | % of entities edited by user |
| System Uptime | > 99% | Monthly uptime monitoring |
| Page Load Time | < 2s | P95 frontend load time |

### 12.2 Business KPIs

| Metric | Target (6 months) | Measurement |
|--------|-------------------|-------------|
| Adoption Rate | 30% of new projects | % using document mode |
| Customer Satisfaction (document mode) | > 4.0 / 5.0 | Post-project survey |
| Time to Discovery Complete | < 1 day | Avg time from upload to approval |
| Deals Won (security-conscious clients) | 5 new clients | Sales tracking |
| Cost per Project (AI costs) | < $2 | Bedrock billing |

### 12.3 Success Criteria

**Phase 1 (MVP):**
- ✅ 10 beta customers use feature successfully
- ✅ > 75% extraction accuracy on test corpus
- ✅ Zero data loss incidents
- ✅ Positive user feedback (> 3.5/5)

**Phase 2 (GA):**
- ✅ 30% adoption rate among new projects
- ✅ Feature parity with live discovery mode
- ✅ < $2 cost per project
- ✅ 5+ customer success stories

**Phase 3 (Scale):**
- ✅ Support 100+ concurrent analyses
- ✅ Hybrid mode (combine docs + live scan)
- ✅ Enterprise features (SSO, RBAC, audit logs)

---

## Appendices

### Appendix A: File Format Support Matrix

| Format | Extension | Library | Vision AI | Text AI | Structured |
|--------|-----------|---------|-----------|---------|------------|
| PNG | .png | PIL | ✅ | ❌ | ❌ |
| JPEG | .jpg, .jpeg | PIL | ✅ | ❌ | ❌ |
| SVG | .svg | cairosvg → PNG | ✅ | ❌ | ❌ |
| Visio | .vsdx, .vsd | LibreOffice → PNG | ✅ | ❌ | ❌ |
| Draw.io | .drawio, .xml | XML parser | ❌ | ❌ | ✅ |
| Excel | .xlsx, .xls | pandas | ❌ | ❌ | ✅ |
| CSV | .csv | pandas | ❌ | ❌ | ✅ |
| PDF | .pdf | PyPDF2, pdfplumber | ❌ | ✅ | ❌ |
| Word | .docx | python-docx | ❌ | ✅ | ❌ |
| JSON | .json | json | ❌ | ✅ | ✅ |
| YAML | .yaml, .yml | PyYAML | ❌ | ✅ | ✅ |
| Terraform | .tf | HCL parser | ❌ | ✅ | ✅ |

### Appendix B: Entity Attribute Examples

See Section 4.2 for JSON schemas.

### Appendix C: Sample Prompts

See Section 5.2 for full prompts.

### Appendix D: Cost Analysis

**Scenario: Typical Enterprise Project**

**Inputs:**
- 20 architecture diagrams (PNG, 2MB each)
- 10 Excel inventories (5MB each)
- 5 PDF documents (200 pages total)

**Bedrock API Costs:**

| Operation | Tokens | Model | Cost per Token | Total Cost |
|-----------|--------|-------|----------------|------------|
| Diagram Analysis (20 images) | 40,000 | Claude 3 Opus | $15 / MTok | $0.60 |
| Document Analysis (200 pages) | 100,000 | Claude 3 Sonnet | $3 / MTok | $0.30 |
| Spreadsheet NLU (10 files) | 10,000 | Claude 3 Haiku | $0.25 / MTok | $0.03 |
| **Total** | **150,000** | | | **$0.93** |

**S3 Storage Costs:**

| Item | Size | Duration | Cost |
|------|------|----------|------|
| File Storage (20+10+5 files, ~80MB) | 80 MB | 90 days | $0.02 |
| Data Transfer (download artifacts) | 10 MB | | $0.001 |
| **Total** | | | **$0.021** |

**Total Cost per Project:** ~$0.95

**At Scale (100 projects/month):**
- AI Costs: $95
- Storage Costs: $2
- **Total: $97/month**

**Comparison to Live Discovery:**
- No infrastructure scanning costs
- No agent compute time
- Higher AI costs, but one-time per project

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-18 | AI Architect | Initial design document |

---

## Next Steps

1. **Review & Approval:**
   - Technical review by engineering team
   - Security review by security team
   - Product approval by product owner

2. **Detailed Design:**
   - Database schema finalization
   - API contract definitions
   - UI mockups in Figma

3. **Proof of Concept:**
   - Build diagram processor with 5 test images
   - Validate Vision AI accuracy
   - Measure performance

4. **Implementation:**
   - Follow roadmap in Section 10
   - Weekly sprint planning
   - Daily standups

**Estimated Timeline to MVP:** 6-8 weeks with 2-3 developers

---

*End of Design Document*
