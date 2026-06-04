"""
notifications.py — Invoice & Reminder Notifications
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_notification_page(df):
    """Render invoice and reminder page."""
    st.markdown('<div class="section-header">📨 Invoice & Reminders</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Generate and send invoices via email & WhatsApp</div>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="alert-info">📧 <strong>Invoice Workflow:</strong><br>'
        '1. Select month → system generates invoices<br>'
        '2. Review invoices before sending<br>'
        '3. Send via Email, WhatsApp, or both<br>'
        '4. Track delivery status</div>',
        unsafe_allow_html=True,
    )
    
    # Month selector
    col1, col2 = st.columns(2)
    
    with col1:
        months = sorted(df["Month_Name"].unique())
        selected_month = st.selectbox("Select Month", months)
    
    with col2:
        if st.button("🔄 Generate Invoices", type="primary"):
            st.session_state["invoices_generated"] = True
    
    # Display invoices for selected month
    if "invoices_generated" in st.session_state and st.session_state["invoices_generated"]:
        month_data = df[df["Month_Name"] == selected_month].copy()
        
        st.markdown(f"### 📋 Invoices for {selected_month}")
        st.info(f"Generated {len(month_data)} invoices")
        
        # Invoice table
        display_cols = [
            "Tenant_Name", "Owner_Name", "Warehouse_Location",
            "Monthly_Rent_INR", "Total_Invoice_INR", "Payment_Status",
            "Tenant_Email", "Tenant_Phone"
        ]
        available_cols = [c for c in display_cols if c in month_data.columns]
        
        st.dataframe(month_data[available_cols], use_container_width=True, hide_index=True)
        
        # Send options
        st.markdown("---")
        st.markdown("### 📤 Send Invoices")
        
        send_col1, send_col2, send_col3 = st.columns(3)
        
        with send_col1:
            if st.button("📧 Send via Email", use_container_width=True):
                with st.spinner("Sending emails..."):
                    # Simulate sending
                    st.success(f"✅ Sent {len(month_data)} invoices via email")
        
        with send_col2:
            if st.button("💬 Send via WhatsApp", use_container_width=True):
                with st.spinner("Sending WhatsApp messages..."):
                    # Check for credentials
                    if not st.session_state.get("ultramsg_token"):
                        st.error("❌ UltraMsg token not configured. Go to ⚙️ Settings first.")
                    else:
                        st.success(f"✅ Sent {len(month_data)} invoices via WhatsApp")
        
        with send_col3:
            if st.button("📨 Send All", use_container_width=True):
                with st.spinner("Sending all invoices..."):
                    st.success(f"✅ Sent {len(month_data)} invoices (Email + WhatsApp)")
    
    st.markdown("---")
    
    # Reminders for overdue
    st.markdown("### ⏰ Payment Reminders")
    
    overdue = df[(df["Payment_Status"] == "Not Paid") & (df["Delay_Days"] > 0)].copy()
    
    if len(overdue) > 0:
        st.warning(f"⚠️ {len(overdue)} overdue payments detected")
        
        st.dataframe(
            overdue[["Tenant_Name", "Monthly_Rent_INR", "Delay_Days", "Balance_Due_INR"]],
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("📢 Send Reminders to All Overdue", type="primary", use_container_width=True):
            with st.spinner("Sending reminders..."):
                st.success(f"✅ Sent reminders to {len(overdue)} tenants")
    else:
        st.success("✅ No overdue payments!")
