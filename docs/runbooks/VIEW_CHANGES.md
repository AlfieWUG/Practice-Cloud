# How to View the New Navigation Design

## Quick Start

### 1. Run the Streamlit App

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
streamlit run app_streamlit.py
```

The app will start and automatically open in your browser at `http://localhost:8501`

### 2. What You'll See

#### Top Navigation Bar (Dark)
- **Left Side**: Nagarro logo + "Nagarro Agentic Services" text
- **Center**: Navigation links (Home, All Agents, Agent Showcase)
- **Right Side**: User profile with avatar

#### Left Sidebar (Dark)
- **Project** section with:
  - New Projects
  - Current Projects
- **Onboarding** section with:
  - Cloud Credentials
  - Source Infrastructure
  - Source Code
  - Target Configuration
- **Monitoring** section with:
  - Dashboard
  - Analytics
  - Reports

#### Main Content Area (Light Background)
- Light gray background (#F5F7FA)
- White cards with subtle shadows
- Dark text for readability

### 3. Test Navigation

1. **Top Navigation**: Click "Home", "All Agents", or "Agent Showcase"
2. **Sidebar Navigation**: Click any item in the left sidebar
3. **Observe**: 
   - Active states (highlighted in green)
   - Light background in main content
   - White cards with borders

### 4. Troubleshooting

If you see errors:

1. **Import Error**: Make sure you're in the project root directory
   ```bash
   cd /Users/aaldertoosthuizen/Projects/agentic-services
   ```

2. **Module Not Found**: Check that navigation.py exists
   ```bash
   ls src/agentic_services/ui/navigation.py
   ```

3. **Authentication Required**: You'll need to login first
   - Default credentials from `.env` file
   - Or set `DEMO_MODE=true` in `.env`

4. **Sidebar Not Showing**: 
   - Check browser console for errors
   - Try refreshing the page (Ctrl+R or Cmd+R)

### 5. Expected Visual Changes

**Before**: 
- Dark background throughout
- Navigation in left column
- All content dark themed

**After**:
- Dark top navigation bar
- Dark left sidebar
- **Light background** in main content area
- **White cards** with dark text
- Professional, clean look matching the reference image

## Next Steps

Once you can see the navigation:
1. Test all navigation links
2. Check that pages load correctly
3. Verify styling matches expectations
4. Report any issues or adjustments needed






