"""
Simple passcode gate to protect demo deployments that run outside the corporate network.
"""

import os
from pathlib import Path
from typing import Optional

import streamlit as st


def _has_local_secrets_file() -> bool:
    candidates = [
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    ]
    return any(path.exists() for path in candidates)


def _get_secret(name: str) -> Optional[str]:
    """Read a secret from environment variables or Streamlit secrets."""
    # First check environment variables
    env_value = os.getenv(name)
    if env_value:
        return env_value
    
    # Then check Streamlit secrets (available in Streamlit Cloud or when secrets.toml exists)
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except (RuntimeError, AttributeError, KeyError):
        # st.secrets not available or key not found - that's okay
        pass
    
    return None


def enforce_demo_passcode():
    """
    Require users to enter DEMO_PASSCODE before rendering the dashboard.
    Set DEMO_PASSCODE in Streamlit secrets or environment variables.
    """
    passcode = _get_secret("DEMO_PASSCODE")
    if not passcode:
        return

    if st.session_state.get("demo_passcode_granted"):
        return

    st.title("Secure Demo Access")
    st.caption("Enter the one-time passcode provided by Aaldert Oosthuizen.")

    with st.form("demo_access_form"):
        entered = st.text_input("Demo Passcode", type="password")
        submitted = st.form_submit_button("Enter", use_container_width=True)

        if submitted:
            if entered and entered.strip() == passcode:
                st.session_state.demo_passcode_granted = True
                st.success("Access granted. Loading dashboard…")
                st.rerun()
            else:
                st.error("Incorrect passcode. Please try again or contact Aaldert.")

    st.stop()

