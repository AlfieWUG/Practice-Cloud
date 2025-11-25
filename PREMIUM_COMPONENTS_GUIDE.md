# How to Add Premium Components to Streamlit

## Step 1: Install Libraries

Add these to your `requirements.txt`:

```txt
# Premium Streamlit Components
streamlit-aggrid==0.3.4          # Professional data tables
streamlit-option-menu==0.3.6     # Better navigation
streamlit-elements==0.1.0        # Advanced layouts
streamlit-lottie==0.0.5          # Animations
streamlit-plotly-events==0.0.6   # Interactive charts
```

Then install:
```bash
pip install -r requirements.txt
```

---

## Step 2: Usage Examples

### 1. Professional Data Tables (streamlit-aggrid)

**Before (Basic Streamlit):**
```python
st.dataframe(df)  # Basic, limited features
```

**After (Premium):**
```python
from st_aggrid import AgGrid, GridOptionsBuilder

# Configure grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(enabled=True)
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
gridOptions = gb.build()

# Display
AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True)
```

**Features:**
- ✅ Sorting, filtering, pagination
- ✅ Column resizing, reordering
- ✅ Excel-like experience
- ✅ Export to CSV/Excel
- ✅ Row selection

---

### 2. Better Navigation (streamlit-option-menu)

**Before (Basic Streamlit):**
```python
st.sidebar.button("Home")
st.sidebar.button("Projects")
```

**After (Premium):**
```python
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None,
    options=["Home", "Projects", "Agents", "Analytics"],
    icons=["house", "folder", "robot", "graph-up"],
    menu_icon="cast",
    default_index=0,
    orientation="vertical",
    styles={
        "container": {"padding": "0!important", "background-color": "#1A1F3A"},
        "icon": {"color": "#60c8b1", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0px",
            "color": "#B0B0B0",
            "padding": "12px",
        },
        "nav-link-selected": {"background-color": "#60c8b1", "color": "#FFFFFF"},
    }
)
```

**Features:**
- ✅ Icons for each menu item
- ✅ Better styling
- ✅ Active state highlighting
- ✅ Professional look

---

### 3. Advanced Layouts (streamlit-elements)

**Before (Basic Streamlit):**
```python
col1, col2 = st.columns(2)
```

**After (Premium):**
```python
from streamlit_elements import elements, mui, html

with elements("dashboard"):
    with mui.Paper(elevation=3, sx={"p": 3, "bgcolor": "#1A1F3A"}):
        mui.Typography("Professional Card", variant="h6")
        mui.Typography("Content here", variant="body1")
```

**Features:**
- ✅ Material-UI components
- ✅ Better card layouts
- ✅ Professional containers
- ✅ More design options

---

### 4. Better Charts (Already have Plotly!)

**Enhance existing Plotly charts:**
```python
import plotly.graph_objects as go
import plotly.express as px

# Professional styled chart
fig = px.line(
    df, 
    x='date', 
    y='value',
    title="Migration Progress",
    template="plotly_dark"  # Dark theme matching Nagarro
)

# Custom styling
fig.update_layout(
    plot_bgcolor='#1A1F3A',
    paper_bgcolor='#0A0E27',
    font_color='#FFFFFF',
    title_font_color='#60c8b1'
)

st.plotly_chart(fig, use_container_width=True)
```

---

## Step 3: Update Your Code

### Example: Update Projects Page

**Current code:**
```python
# pages/2_Projects.py
st.dataframe(projects_df)
```

**Enhanced code:**
```python
# pages/2_Projects.py
from st_aggrid import AgGrid, GridOptionsBuilder

# Build professional grid
gb = GridOptionsBuilder.from_dataframe(projects_df)
gb.configure_pagination(enabled=True, paginationPageSize=10)
gb.configure_side_bar()
gb.configure_default_column(
    groupable=True,
    value=True,
    enableRowGroup=True,
    editable=False
)
gb.configure_selection('single')
gridOptions = gb.build()

# Display with AgGrid
selected_rows = AgGrid(
    projects_df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    height=400,
    theme='dark'  # Match Nagarro theme
)
```

---

## Step 4: Update Navigation

**Current navigation:**
```python
# src/agentic_services/ui/unified_navigation.py
st.sidebar.button("Home")
st.sidebar.button("Projects")
```

**Enhanced navigation:**
```python
# src/agentic_services/ui/unified_navigation.py
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title="Navigation",
    options=["Home", "All Agents", "About", "Agent Showcase"],
    icons=["house", "robot", "info-circle", "play-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="vertical",
    styles={
        "container": {
            "padding": "0!important",
            "background-color": "#0A0E27",
        },
        "icon": {"color": "#60c8b1", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0px",
            "color": "#B0B0B0",
            "padding": "12px",
        },
        "nav-link-selected": {
            "background-color": "#60c8b1",
            "color": "#FFFFFF",
        },
    }
)
```

---

## Quick Start: Install Now

Run this command:
```bash
pip install streamlit-aggrid streamlit-option-menu streamlit-elements
```

Then update `requirements.txt` to include these packages.

---

## Next Steps

1. **Install libraries** (5 min)
2. **Update one page** as a test (30 min)
3. **See the improvement**
4. **Roll out to all pages** if you like it

Would you like me to:
- **A)** Install the libraries now and update requirements.txt
- **B)** Update one of your pages (e.g., Projects page) as an example
- **C)** Show you a complete before/after comparison






