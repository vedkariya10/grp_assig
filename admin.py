"""
admin.py — Admin Panel & Data Management
"""

import streamlit as st
import pandas as pd
from data_manager import (
    get_business, set_business,
    get_owners, set_owners,
    get_warehouses, set_warehouses,
    get_tenants, set_tenants,
    get_rentals, set_rentals,
)


def render_admin_page():
    """Render admin panel."""
    st.markdown('<div class="section-header">🗂️ Admin Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Manage business data: owners, warehouses, tenants, rentals</div>', unsafe_allow_html=True)
    
    admin_tab = st.selectbox(
        "Select Section",
        ["Business Profile", "Owners", "Warehouses", "Tenants", "Rentals"]
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # BUSINESS PROFILE
    # ─────────────────────────────────────────────────────────────────────
    if admin_tab == "Business Profile":
        st.markdown("### 👤 Business Profile")
        
        biz = get_business()
        
        with st.form("biz_form"):
            name = st.text_input("Business Name", value=biz.get("name", ""))
            phone = st.text_input("Phone", value=biz.get("phone", ""))
            email = st.text_input("Email", value=biz.get("email", ""))
            bank = st.text_input("Bank Name", value=biz.get("bank_name", ""))
            acc = st.text_input("Account Number", value=biz.get("bank_account", ""))
            ifsc = st.text_input("IFSC", value=biz.get("ifsc", ""))
            gstin = st.text_input("GSTIN", value=biz.get("gstin", ""))
            
            if st.form_submit_button("Save Profile", type="primary"):
                set_business({
                    "name": name, "phone": phone, "email": email,
                    "bank_name": bank, "bank_account": acc,
                    "ifsc": ifsc, "gstin": gstin
                })
                st.success("✅ Profile saved!")
    
    # ─────────────────────────────────────────────────────────────────────
    # OWNERS
    # ─────────────────────────────────────────────────────────────────────
    elif admin_tab == "Owners":
        st.markdown("### 👥 Owners")
        
        owners = get_owners()
        
        with st.form("owner_form"):
            owner_name = st.text_input("Owner Name")
            owner_phone = st.text_input("Phone")
            owner_email = st.text_input("Email")
            
            if st.form_submit_button("Add Owner", type="primary"):
                owners.append({
                    "id": f"OWN-{len(owners)+1:03d}",
                    "name": owner_name,
                    "phone": owner_phone,
                    "email": owner_email,
                })
                set_owners(owners)
                st.success(f"✅ Added owner: {owner_name}")
                st.rerun()
        
        if owners:
            st.markdown("**Existing Owners**")
            for owner in owners:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{owner['name']}** ({owner['phone']})")
                with col2:
                    if st.button("🗑️", key=owner['id']):
                        owners.remove(owner)
                        set_owners(owners)
                        st.rerun()
    
    # ─────────────────────────────────────────────────────────────────────
    # WAREHOUSES
    # ─────────────────────────────────────────────────────────────────────
    elif admin_tab == "Warehouses":
        st.markdown("### 🏭 Warehouses")
        
        warehouses = get_warehouses()
        owners = get_owners()
        owner_names = [o['name'] for o in owners]
        
        with st.form("wh_form"):
            owner = st.selectbox("Owner", owner_names if owner_names else ["No owners"])
            location = st.text_input("Location")
            state = st.text_input("State")
            wh_type = st.selectbox("Type", ["Cold Storage", "Dry Warehouse", "Distribution Hub", "General"])
            size = st.selectbox("Size", ["Small", "Medium", "Large"])
            
            if st.form_submit_button("Add Warehouse", type="primary"):
                warehouses.append({
                    "id": f"WH-{len(warehouses)+1:03d}",
                    "owner": owner,
                    "location": location,
                    "state": state,
                    "type": wh_type,
                    "size": size,
                })
                set_warehouses(warehouses)
                st.success(f"✅ Added warehouse in {location}")
                st.rerun()
        
        if warehouses:
            st.markdown("**Existing Warehouses**")
            for wh in warehouses:
                st.write(f"**{wh['location']}** ({wh['type']}, {wh['size']}) - {wh['owner']}")
    
    # ─────────────────────────────────────────────────────────────────────
    # TENANTS
    # ─────────────────────────────────────────────────────────────────────
    elif admin_tab == "Tenants":
        st.markdown("### 👨‍💼 Tenants")
        
        tenants = get_tenants()
        
        with st.form("tenant_form"):
            name = st.text_input("Tenant Name")
            ttype = st.selectbox("Type", ["Business", "Individual"])
            industry = st.text_input("Industry")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            
            if st.form_submit_button("Add Tenant", type="primary"):
                tenants.append({
                    "id": f"TNT-{len(tenants)+1:03d}",
                    "name": name,
                    "type": ttype,
                    "industry": industry,
                    "phone": phone,
                    "email": email,
                })
                set_tenants(tenants)
                st.success(f"✅ Added tenant: {name}")
                st.rerun()
        
        if tenants:
            st.markdown("**Existing Tenants**")
            for tenant in tenants:
                st.write(f"**{tenant['name']}** ({tenant['type']}) - {tenant['industry']}")
    
    # ─────────────────────────────────────────────────────────────────────
    # RENTALS
    # ─────────────────────────────────────────────────────────────────────
    elif admin_tab == "Rentals":
        st.markdown("### 📋 Rentals")
        
        rentals = get_rentals()
        tenants = get_tenants()
        warehouses = get_warehouses()
        
        tenant_names = [t['name'] for t in tenants]
        wh_locations = [w['location'] for w in warehouses]
        
        with st.form("rental_form"):
            tenant = st.selectbox("Tenant", tenant_names if tenant_names else ["No tenants"])
            warehouse = st.selectbox("Warehouse", wh_locations if wh_locations else ["No warehouses"])
            rent = st.number_input("Monthly Rent (₹)", 5000, 500000, 50000)
            lease_months = st.slider("Lease Duration (months)", 6, 60, 12)
            start_date = st.date_input("Start Date")
            
            if st.form_submit_button("Add Rental", type="primary"):
                rentals.append({
                    "id": f"RNT-{len(rentals)+1:03d}",
                    "tenant": tenant,
                    "warehouse": warehouse,
                    "rent": rent,
                    "lease_months": lease_months,
                    "start_date": str(start_date),
                })
                set_rentals(rentals)
                st.success(f"✅ Added rental: {tenant} at {warehouse}")
                st.rerun()
        
        if rentals:
            st.markdown("**Active Rentals**")
            for rental in rentals:
                st.write(f"**{rental['tenant']}** @ {rental['warehouse']} - ₹{rental['rent']}/month")
