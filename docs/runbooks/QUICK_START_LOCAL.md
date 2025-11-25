# Quick Start - Local Development

**Goal**: Get up and running locally in 5 minutes, $0 cost

---

## Step 1: Verify Your Environment (1 min)

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services

# Check Python
python3 --version  # Should be 3.9+

# Check if venv exists
ls venv/  # If exists, skip to Step 2
```

## Step 2: Set Up Virtual Environment (2 min)

```bash
# Create venv (if doesn't exist)
python3 -m venv venv

# Activate
source venv/bin/activate

# Install package in dev mode
pip install -e ".[dev]"

# Verify
python -c "import agentic_services; print('✅ Ready!')"
```

## Step 3: Test Dashboard (1 min)

```bash
# Enable demo mode (no AWS needed)
export DEMO_MODE=true

# Start Streamlit
streamlit run src/agentic_services/app_streamlit.py

# Opens browser at http://localhost:8501
```

## Step 4: Test CLI (1 min)

```bash
# In a new terminal
cd /Users/aaldertoosthuizen/Projects/agentic-services
source venv/bin/activate

# Test CLI
python -m agentic_services.cli --help

# Test an agent
python -m agentic_services.cli discovery --project-id test-001
```

---

## That's It!

You're now running locally with:
- ✅ Dashboard at http://localhost:8501
- ✅ CLI tool working
- ✅ All 24 agents available
- ✅ **$0/month cost**

---

## Next Steps

1. **Read**: `LOCAL_DEVELOPMENT.md` for full strategy
2. **Explore**: Run tests with `pytest`
3. **Develop**: Make changes and test locally
4. **Document**: As you go

---

## Troubleshooting

**Import errors?**
```bash
pip install -e ".[dev]"
```

**Dashboard won't start?**
```bash
export DEMO_MODE=true
streamlit run src/agentic_services/app_streamlit.py
```

**CLI not found?**
```bash
source venv/bin/activate
python -m agentic_services.cli --help
```

---

**Status**: Local development ready ✅  
**Cost**: $0 💰  
**Time to start**: 5 minutes ⏱️
