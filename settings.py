"""
settings.py — Settings & Credential Management
"""

import streamlit as st
import os
from data_manager import get_business, set_business


def init_settings():
    """Initialize session state for settings."""
    if "sender_phone" not in st.session_state:
        st.session_state["sender_phone"] = ""
    if "sender_phone_set" not in st.session_state:
        st.session_state["sender_phone_set"] = False
    if "gmail_user_prefill" not in st.session_state:
        st.session_state["gmail_user_prefill"] = ""
    if "ultramsg_token" not in st.session_state:
        st.session_state["ultramsg_token"] = ""
    if "gmail_app_password" not in st.session_state:
        st.session_state["gmail_app_password"] = ""


def render_settings_page():
    """Render settings page."""
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Configure WhatsApp (UltraMsg) and Gmail for invoice delivery</div>', unsafe_allow_html=True)
    
    # Business Profile Section
    st.markdown("### 👤 Business Profile")
    
    biz = get_business()
    
    with st.form("business_profile"):
        name = st.text_input("Business Name", value=biz.get("name", ""))
        phone = st.text_input("Phone (+91 ...)", value=biz.get("phone", ""))
        email = st.text_input("Email", value=biz.get("email", ""))
        bank_name = st.text_input("Bank Name", value=biz.get("bank_name", ""))
        bank_account = st.text_input("Account Number", value=biz.get("bank_account", ""))
        ifsc = st.text_input("IFSC Code", value=biz.get("ifsc", ""))
        gstin = st.text_input("GSTIN", value=biz.get("gstin", ""))
        
        if st.form_submit_button("Save Business Profile", type="primary"):
            set_business({
                "name": name,
                "phone": phone,
                "email": email,
                "bank_name": bank_name,
                "bank_account": bank_account,
                "ifsc": ifsc,
                "gstin": gstin,
            })
            st.success("✅ Business profile saved!")
    
    st.markdown("---")
    
    # WhatsApp Setup
    st.markdown("### 📱 WhatsApp Setup (UltraMsg)")
    st.markdown(
        """
        **Steps:**
        1. Sign up at [ultramsg.com](https://ultramsg.com)
        2. Create instance → scan QR with your phone
        3. Copy Instance ID and Token from dashboard
        4. Paste below
        """
    )
    
    with st.form("whatsapp_form"):
        ultramsg_instance = st.text_input("Instance ID", value="")
        ultramsg_token = st.text_input("Token", value="", type="password")
        
        if st.form_submit_button("Save WhatsApp Credentials"):
            st.session_state["ultramsg_token"] = ultramsg_token
            st.success("✅ WhatsApp credentials saved to session!")
    
    st.markdown("---")
    
    # Gmail Setup
    st.markdown("### 📧 Gmail Setup (App Password)")
    st.markdown(
        """
        **Steps:**
        1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
        2. Enable 2-Step Verification
        3. Search "App Passwords" → Generate → Copy
        4. Paste below
        """
    )
    
    with st.form("gmail_form"):
        gmail_user = st.text_input("Gmail Address", value=st.session_state.get("gmail_user_prefill", ""))
        gmail_password = st.text_input("App Password", value="", type="password")
        
        if st.form_submit_button("Save Gmail Credentials"):
            st.session_state["gmail_user"] = gmail_user
            st.session_state["gmail_app_password"] = gmail_password
            st.success("✅ Gmail credentials saved to session!")
    
    st.markdown("---")
    
    st.markdown(
        '<div class="alert-info">🔐 <strong>Security:</strong> Credentials are stored in session only (not persistent). '
        'For production, use environment variables or Streamlit secrets.</div>',
        unsafe_allow_html=True,
    )
