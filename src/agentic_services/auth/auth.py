"""
Authentication module for Nagarro Agentic Services Dashboard
Provides secure login functionality with local and AWS Secrets Manager support
"""
import os
import hashlib
import json
import streamlit as st
from typing import Optional, Dict


class DashboardAuth:
    """Handles authentication for the Streamlit Dashboard"""
    
    def __init__(self):
        """Initialize authentication with environment-based config"""
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        self.use_aws_secrets = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _get_credentials_local(self) -> Dict[str, str]:
        """Get credentials from environment variables (local dev)"""
        username = os.getenv("DASHBOARD_USERNAME")
        password = os.getenv("DASHBOARD_PASSWORD")
        
        if not username or not password:
            raise ValueError(
                "DASHBOARD_USERNAME and DASHBOARD_PASSWORD must be set in environment variables. "
                "Please check your .env file."
            )
        
        return {
            username: self._hash_password(password)
        }
    
    def _get_credentials_aws(self) -> Dict[str, str]:
        """Get credentials from AWS Secrets Manager (production)"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            secret_name = os.getenv("DASHBOARD_SECRET_NAME", "agentic-services/dashboard-credentials")
            region = os.getenv("AWS_REGION", "eu-central-1")
            
            client = boto3.client("secretsmanager", region_name=region)
            
            response = client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response["SecretString"])
            
            # Return username -> hashed_password mapping
            credentials = {}
            for username, password in secret.items():
                credentials[username] = self._hash_password(password)
            
            return credentials
            
        except Exception as e:
            st.error(f"Failed to load credentials from AWS: {str(e)}")
            # Fallback to local credentials
            return self._get_credentials_local()
    
    def get_credentials(self) -> Dict[str, str]:
        """Get credentials based on environment configuration"""
        if self.demo_mode or not self.use_aws_secrets:
            return self._get_credentials_local()
        else:
            return self._get_credentials_aws()
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials
        
        Args:
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        credentials = self.get_credentials()
        hashed_password = self._hash_password(password)
        
        return username in credentials and credentials[username] == hashed_password
    
    def login_form(self) -> bool:
        """
        Display login form and handle authentication
        
        Returns:
            True if user is authenticated, False otherwise
        """
        # Initialize session state for authentication
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        
        # Check if already authenticated
        if st.session_state.authenticated:
            return True
        
        # Login page styling
        st.markdown("""
        <style>
            .login-container {
                max-width: 400px;
                margin: 8rem auto;
                padding: 2rem;
                background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
                border: 2px solid #2A2F4A;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            }
            .login-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .login-title {
                color: #60c8b1;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            .login-subtitle {
                color: #B0B0B0;
                font-size: 0.9rem;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Logo and header
            logo_path = "assets/images/nagarro_logo.png"
            if os.path.exists(logo_path):
                st.image(logo_path, width=120)
            
            st.markdown("""
            <div class="login-header">
                <div class="login-title">Nagarro Agentic Services</div>
                <div class="login-subtitle">Secure Dashboard Access</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        if self.authenticate(username, password):
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        return False
    
    def logout(self):
        """Clear authentication state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    def require_auth(self):
        """
        Decorator-style function to require authentication
        Call this at the start of your Streamlit app
        """
        if not self.login_form():
            st.stop()
    
    def get_current_user(self) -> Optional[str]:
        """Get currently authenticated username"""
        return st.session_state.get("username")
