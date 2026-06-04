"""
app.py — Warehouse Rental Management Analytics Platform (Enhanced)
Data Analytics MGB Project | Family Business Use Case
Run: streamlit run app.py
"""

import io
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from notifications import render_notification_page
from settings import render_settings_page, init_settings
from admin import render_admin_page
from data_manager import get_transaction_df, get_business
from utils import (
    load_data, apply_filters, compute_kpis, inr_fmt,
    train_multi_classifiers, train_classifier, 
    train_rent_regressor, train_delay_regressor,
    train_clustering, compute_association_rules, score_prospects,
    COLORS, PALETTE, PROSPECT_SCHEMA, compute_correlations,
)
from charts import (
    # Original charts
    monthly_revenue_trend, owner_revenue_bar, owner_revenue_pie,
    location_bar, payment_status_donut, payment_behaviour_bar,
    quarterly_revenue, wh_type_revenue, automation_summary,
    correlation_heatmap, rent_vs_size, rent_vs_type,
    delay_by_industry, delay_by_tenant_type, risk_score_histogram,
    location_type_heatmap,
    roc_curve_chart, confusion_matrix_chart, feature_importance_chart,
    regression_actual_vs_predicted,
    elbow_chart, cluster_scatter, cluster_profile_radar,
    association_heatmap, association_bubble,
    prospect_gauge, prospect_risk_bar,
    # New classification charts
    classifier_comparison_metrics, classifier_accuracy_radar,
    confusion_matrix_heatmap, roc_curve_comparison,
    feature_importance_comparison,
    # Regression charts
    regression_comparison_metrics,
)

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="WareHub Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0F1923;
    border-right: 1px solid #1E2D3D;
}
[data-testid="stSidebar"] * { color: #C8D8E8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1, h2, h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #90A4AE !important; font-size: 12px; }

/* KPI cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E0D8;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(15,25,35,.07);
    transition: box-shadow .2s;
}
.kpi-card:hover { box-shadow: 0 4px 16px rgba(15,25,35,.12); }
.kpi-label { font-size: 11px; font-weight: 600; color: #64748B;
             text-transform: uppercase; letter-spacing: .07em; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #0F1923;
             letter-spacing: -.03em; line-height: 1; }
.kpi-footer { font-size: 11px; color: #94A3B8; margin-top: 6px; }
.kpi-tag { display: inline-block; font-size: 10px; font-weight: 600;
           padding: 2px 9px; border-radius: 10px; margin-top: 8px;
           text-transform: uppercase; letter-spacing: .04em; }
.tag-green  { background: #E8F6F0; color: #1D8A5F; }
.tag-red    { background: #FCEAEA; color: #C0392B; }
.tag-amber  { background: #FDF6E3; color: #D97706; }
.tag-blue   { background: #EBF2FA; color: #1A3C5E; }

/* Alert */
.alert-danger {
    background: #FCEAEA; border: 1px solid #F5C4C4;
    border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
    font-size: 13px; color: #C0392B;
}
.alert-info {
    background: #EBF2FA; border: 1px solid #BDD5EE;
    border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
    font-size: 13px; color: #1A3C5E;
}
.alert-success {
    background: #E8F6F0; border: 1px solid #A8DDD8;
    border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
    font-size: 13px; color: #1D8A5F;
}

/* Section header */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 22px; color: #0F1923;
    letter-spacing: -.02em; margin-bottom: 4px;
}
.section-sub { font-size: 13px; color: #64748B; margin-bottom: 20px; }

/* Divider */
.divider { border: none; border-top: 1px solid #E5E0D8; margin: 24px 0; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data
def get_data():
    return load_data("warehouse_data.csv")

df_main = get_transaction_df()
init_settings()

# Pre-fill WhatsApp number and email from business profile
biz = get_business()
if biz.get("phone") and not st.session_state.get("sender_phone_set"):
    import re as _re
    ph = _re.sub(r"\D","", biz["phone"])
    if not ph.startswith("91"): ph = "91" + ph
    st.session_state["sender_phone"] = ph
    st.session_state["sender_phone_set"] = True
if biz.get("email") and not st.session_state.get("gmail_user"):
    st.session_state["gmail_user_prefill"] = biz["email"]


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏭 WareHub Analytics")
    st.markdown("Warehouse Rental Management\nData Analytics MGB Project")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        options=[
            "📊 Overview",
            "💰 Revenue Analysis",
            "🔍 Diagnostic Analysis",
            "🤖 Classification (Multi-Algorithm)",
            "📈 Regression Analysis",
            "🎯 Clustering",
            "🔗 Association Rules",
            "🚀 Prospect Scoring",
            "📨 Invoice & Reminders",
            "📋 Data Explorer",
            "⚙️ Settings",
            "🗂️ Admin — Manage Data",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Global Filters**")

    owners    = ["All"] + sorted(df_main["Owner_Name"].dropna().unique().tolist())
    locations = ["All"] + sorted(df_main["Warehouse_Location"].dropna().unique().tolist())
    wh_types  = ["All"] + sorted(df_main["Warehouse_Type"].dropna().unique().tolist())
    years     = ["All"] + sorted(df_main["Month"].dt.year.dropna().unique().astype(str).tolist())

    sel_owner    = st.selectbox("Owner",    owners)
    sel_location = st.selectbox("Location", locations)
    sel_type     = st.selectbox("WH Type",  wh_types)
    sel_year     = st.selectbox("Year",     years)
    sel_pay      = st.selectbox("Payment",  ["All", "Paid", "Not Paid"])

    df = apply_filters(
        df_main,
        owner=sel_owner, location=sel_location,
        wh_type=sel_type, pay_status=sel_pay, year=sel_year,
    )

    st.markdown("---")
    n_filtered = len(df)
    st.caption(f"📌 Showing {n_filtered} of {len(df_main)} records")


# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════
def render_kpis(data):
    """Render KPI row."""
    kpis = compute_kpis(data)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">💰 Total Revenue</div>
            <div class="kpi-value">{inr_fmt(kpis['total_revenue'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">👥 Tenants</div>
            <div class="kpi-value">{kpis['num_tenants']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🏭 Warehouses</div>
            <div class="kpi-value">{kpis['num_warehouses']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✅ Payment Rate</div>
            <div class="kpi-value">{kpis['payment_rate']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📅 Avg Delay</div>
            <div class="kpi-value">{kpis['avg_delay']:.1f}d</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📋 Invoices</div>
            <div class="kpi-value">{kpis['num_invoices']}</div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown('<div class="section-header">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Key metrics, trends & snapshots</div>', unsafe_allow_html=True)
    
    render_kpis(df)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(monthly_revenue_trend(df), use_container_width=True)
    with col2:
        st.plotly_chart(payment_status_donut(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(owner_revenue_pie(df), use_container_width=True)
    with col2:
        st.plotly_chart(payment_behaviour_bar(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(location_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(wh_type_revenue(df), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: REVENUE ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
elif page == "💰 Revenue Analysis":
    st.markdown('<div class="section-header">💰 Revenue Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Descriptive analysis of revenue patterns</div>', unsafe_allow_html=True)
    
    render_kpis(df)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(quarterly_revenue(df), use_container_width=True)
    with col2:
        st.plotly_chart(owner_revenue_bar(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(location_type_heatmap(df), use_container_width=True)
    with col2:
        st.plotly_chart(automation_summary(df), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: DIAGNOSTIC ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Diagnostic Analysis":
    st.markdown('<div class="section-header">🔍 Diagnostic Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Correlations and relationships in the data (Pearson r)</div>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="alert-info">📊 <strong>Pearson Correlation:</strong> '
        'Measures linear relationship between two continuous variables. '
        'Range: -1 (perfect negative) to +1 (perfect positive). |r| > 0.7 = strong correlation.</div>',
        unsafe_allow_html=True,
    )
    
    corr = compute_correlations(df_main)
    st.plotly_chart(correlation_heatmap(corr), use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(rent_vs_size(df), use_container_width=True)
    with col2:
        st.plotly_chart(rent_vs_type(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(risk_score_histogram(df), use_container_width=True)
    with col2:
        st.plotly_chart(delay_by_tenant_type(df), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CLASSIFICATION (MULTI-ALGORITHM)
# ════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Classification (Multi-Algorithm)":
    st.markdown('<div class="section-header">🤖 Classification Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Compare 7 algorithms: Accuracy, Precision, Recall, F1, ROC-AUC</div>', unsafe_have_html=True)
    
    st.markdown(
        '<div class="alert-info">🎯 <strong>Target:</strong> Predict payment status (Paid/Not Paid)<br>'
        '<strong>Algorithms:</strong> Logistic Regression, Random Forest, SVM, Decision Tree, '
        'Gradient Boosting, K-NN, Naive Bayes<br>'
        '<strong>Metrics:</strong> Accuracy (overall correctness), Precision (true positives among positives), '
        'Recall (true positives found), F1-Score (harmonic mean), ROC-AUC (discrimination ability)</div>',
        unsafe_allow_html=True,
    )
    
    with st.spinner("Training 7 classification models..."):
        results, scaler, feature_cols, le_dict, X_test, y_test = train_multi_classifiers(df_main)
    
    # Metrics comparison
    st.markdown("### 📊 Performance Metrics Comparison")
    st.plotly_chart(classifier_comparison_metrics(results), use_container_width=True)
    
    # Radar chart
    st.markdown("### 📈 Radar Chart Comparison")
    st.plotly_chart(classifier_accuracy_radar(results), use_container_width=True)
    
    # ROC Curves
    st.markdown("### 🎯 ROC Curves")
    st.plotly_chart(roc_curve_comparison(results, y_test), use_container_width=True)
    
    # Feature importance
    st.markdown("### 🔑 Feature Importance (Tree Models)")
    st.plotly_chart(feature_importance_comparison(
        {k: v["model"] for k, v in results.items()},
        feature_cols
    ), use_container_width=True)
    
    # Detailed metrics table
    st.markdown("### 📋 Detailed Metrics Table")
    metrics_df = pd.DataFrame({
        "Algorithm": results.keys(),
        "Accuracy": [round(v["accuracy"], 4) for v in results.values()],
        "Precision": [round(v["precision"], 4) for v in results.values()],
        "Recall": [round(v["recall"], 4) for v in results.values()],
        "F1-Score": [round(v["f1_score"], 4) for v in results.values()],
        "ROC-AUC": [round(v["roc_auc"], 4) for v in results.values()],
    })
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Download results
    csv_buf = io.BytesIO()
    metrics_df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    st.download_button(
        "⬇️ Download Metrics CSV",
        data=csv_buf,
        file_name="classification_metrics.csv",
        mime="text/csv",
    )
    
    # Best model analysis
    st.markdown("### 🏆 Best Performing Model")
    best_algo = max(results.items(), key=lambda x: x[1]["f1_score"])
    st.success(f"**{best_algo[0]}** with F1-Score: {best_algo[1]['f1_score']:.4f}")
    
    # Confusion matrices
    st.markdown("### 🔴 Confusion Matrices (Top 3 by F1-Score)")
    top3 = sorted(results.items(), key=lambda x: x[1]["f1_score"], reverse=True)[:3]
    cols = st.columns(3)
    for i, (algo_name, metrics) in enumerate(top3):
        with cols[i]:
            st.plotly_chart(confusion_matrix_heatmap(metrics["confusion_matrix"], algo_name))


# ════════════════════════════════════════════════════════════════════════════
# PAGE: REGRESSION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📈 Regression Analysis":
    st.markdown('<div class="section-header">📈 Regression Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Predict rent and payment delay (Linear, Ridge, Lasso)</div>', unsafe_allow_html=True)
    
    reg_type = st.radio("Select Regression Target", ["Rent Prediction", "Delay Prediction"], horizontal=True)
    
    if reg_type == "Rent Prediction":
        st.markdown(
            '<div class="alert-info">🏪 <strong>Objective:</strong> Predict monthly rent based on warehouse characteristics.<br>'
            '<strong>Features:</strong> Warehouse Size, Type, Tenure, Lease Duration<br>'
            '<strong>Models:</strong> Linear Regression, Ridge (L2), Lasso (L1)</div>',
            unsafe_allow_html=True,
        )
        
        with st.spinner("Training regression models..."):
            results_rent, scaler_rent, feat_rent = train_rent_regressor(df_main)
        
        # Metrics comparison
        st.plotly_chart(regression_comparison_metrics(results_rent, "rmse"), use_container_width=True)
        
        # Metrics table
        metrics_table = pd.DataFrame({
            "Model": results_rent.keys(),
            "RMSE (₹)": [f"₹{v['rmse']:,.0f}" for v in results_rent.values()],
            "MAE (₹)": [f"₹{v['mae']:,.0f}" for v in results_rent.values()],
            "R² Score": [f"{v['r2_score']:.4f}" for v in results_rent.values()],
        })
        st.dataframe(metrics_table, use_container_width=True, hide_index=True)
        
        # Actual vs Predicted
        st.markdown("### 🎯 Actual vs Predicted (Top Model)")
        best_model_name = max(results_rent.items(), key=lambda x: x[1]["r2_score"])[0]
        st.plotly_chart(
            regression_actual_vs_predicted(
                results_rent[best_model_name]["y_test"],
                results_rent[best_model_name]["y_pred"],
                best_model_name
            ),
            use_container_width=True
        )
    
    else:  # Delay Prediction
        st.markdown(
            '<div class="alert-info">📅 <strong>Objective:</strong> Predict payment delay days.<br>'
            '<strong>Features:</strong> Rent, Warehouse characteristics, Risk Score, Tenure<br>'
            '<strong>Models:</strong> Linear Regression, Ridge (L2), Lasso (L1)</div>',
            unsafe_allow_html=True,
        )
        
        with st.spinner("Training delay prediction models..."):
            results_delay, scaler_delay, feat_delay = train_delay_regressor(df_main)
        
        st.plotly_chart(regression_comparison_metrics(results_delay, "rmse"), use_container_width=True)
        
        metrics_table = pd.DataFrame({
            "Model": results_delay.keys(),
            "RMSE (days)": [f"{v['rmse']:.2f}" for v in results_delay.values()],
            "MAE (days)": [f"{v['mae']:.2f}" for v in results_delay.values()],
            "R² Score": [f"{v['r2_score']:.4f}" for v in results_delay.values()],
        })
        st.dataframe(metrics_table, use_container_width=True, hide_index=True)
        
        st.markdown("### 🎯 Actual vs Predicted (Top Model)")
        best_model_name = max(results_delay.items(), key=lambda x: x[1]["r2_score"])[0]
        st.plotly_chart(
            regression_actual_vs_predicted(
                results_delay[best_model_name]["y_test"],
                results_delay[best_model_name]["y_pred"],
                best_model_name
            ),
            use_container_width=True
        )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CLUSTERING
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Clustering":
    st.markdown('<div class="section-header">🎯 Clustering Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">K-Means segmentation: rent, tenure, risk, delay</div>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="alert-info">🔀 <strong>K-Means Clustering:</strong> Groups tenants into K clusters based on behavior.<br>'
        '<strong>Features:</strong> Monthly Rent, Customer Tenure, Risk Score, Delay Days<br>'
        '<strong>Interpretation:</strong> Each cluster represents a tenant segment with similar characteristics.</div>',
        unsafe_allow_html=True,
    )
    
    with st.spinner("Training K-Means clustering..."):
        cluster_result = train_clustering(df_main, k=4)
    
    # Elbow chart
    st.markdown("### 📊 Elbow Method — Optimal K Selection")
    st.plotly_chart(elbow_chart(cluster_result["inertias"], cluster_result["k_range"]), use_container_width=True)
    
    # Cluster profiles
    st.markdown("### 👥 Cluster Profiles")
    profiles = cluster_result["profiles"]
    for cluster_name, profile in profiles.items():
        with st.expander(f"**{cluster_name}** — {profile['size']} members", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Rent", f"₹{profile['avg_rent']:,.0f}")
            with col2:
                st.metric("Avg Tenure (months)", f"{profile['avg_tenure']:.1f}")
            with col3:
                st.metric("Avg Risk Score", f"{profile['avg_risk']:.1f}")
            with col4:
                st.metric("Avg Delay (days)", f"{profile['avg_delay']:.1f}")
            
            st.markdown(f"**Primary Tenant Type:** {profile['primary_tenant']}")
            st.markdown(f"**Primary Industry:** {profile['primary_industry']}")
    
    # Cluster profiles radar
    st.markdown("### 📈 Cluster Comparison Radar")
    st.plotly_chart(cluster_profile_radar(profiles), use_container_width=True)
    
    # Scatter plots
    st.markdown("### 📍 Cluster Scatter Plots")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(cluster_scatter(cluster_result["data"], "Monthly_Rent_INR", "Customer_Tenure_Months"), use_container_width=True)
    with col2:
        st.plotly_chart(cluster_scatter(cluster_result["data"], "Risk_Score", "Delay_Days"), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ASSOCIATION RULES
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Association Rules":
    st.markdown('<div class="section-header">🔗 Association Rules Mining</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Which warehouse types are preferred by which tenant types?</div>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="alert-info">🔍 <strong>Association Rules:</strong> Discover relationships between categorical variables.<br>'
        '<strong>Metrics:</strong><br>'
        '• Support = P(A and B) — frequency of itemset<br>'
        '• Confidence = P(B|A) — if A, then B probability<br>'
        '• Lift = Confidence / Support(B) — strength of association (Lift > 1 = positive)</div>',
        unsafe_allow_html=True,
    )
    
    with st.spinner("Mining association rules..."):
        ar_result = compute_association_rules(df_main, min_support=0.05)
    
    rules = ar_result["rules"]
    
    if len(rules) > 0:
        # Heatmap
        st.markdown("### 📊 Support vs Confidence Heatmap")
        st.plotly_chart(association_heatmap(rules), use_container_width=True)
        
        # Bubble chart
        st.markdown("### 🫧 Top Rules Bubble Chart")
        st.plotly_chart(association_bubble(rules), use_container_width=True)
        
        # Detailed rules table
        st.markdown("### 📋 Association Rules Table")
        rules_display = rules.head(15).copy()
        rules_display = rules_display[[
            "antecedent_str", "consequent_str", "support", "confidence", "lift"
        ]].copy()
        rules_display.columns = ["If (Antecedent)", "Then (Consequent)", "Support", "Confidence", "Lift"]
        rules_display["Support"] = rules_display["Support"].round(3)
        rules_display["Confidence"] = rules_display["Confidence"].round(3)
        rules_display["Lift"] = rules_display["Lift"].round(3)
        
        st.dataframe(rules_display, use_container_width=True, hide_index=True)
        
        # Download
        csv_buf = io.BytesIO()
        rules_display.to_csv(csv_buf, index=False)
        csv_buf.seek(0)
        st.download_button(
            "⬇️ Download Rules CSV",
            data=csv_buf,
            file_name="association_rules.csv",
            mime="text/csv",
        )
    else:
        st.info("No significant association rules found. Try lowering the min_support threshold.")
    
    st.markdown(
        '<div class="alert-info">📌 <strong>Lift Interpretation:</strong> '
        'Lift > 1 = positive association (better than chance) | '
        'Lift = 1 = no association | Lift < 1 = negative association. '
        'Use high-lift rules to decide which tenant type to target for each warehouse type.</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: PROSPECT SCORING
# ════════════════════════════════════════════════════════════════════════════
elif page == "🚀 Prospect Scoring":
    st.markdown('<div class="section-header">🚀 Prospect Scoring & Lead Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload new prospect data and predict payment likelihood to prioritise your marketing strategy</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="alert-info">💡 <strong>How it works:</strong> Upload a CSV with prospect details. '
        'The trained Random Forest model scores each prospect on payment probability (0–100%), '
        'assigns a risk tier, and recommends a contract approach.</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading classification model..."):
        model_clf, scaler_clf, metrics_clf, feat_clf = train_classifier(df_main)

    # Template download
    template_df = pd.DataFrame([
        {"Tenant_Name": "ABC Logistics",   "Tenant_Type": "Business",   "Industry_Type": "Logistics",
         "Warehouse_Type": "Distribution Hub", "Warehouse_Size": "Large",  "Monthly_Rent_INR": 90000,
         "Customer_Tenure_Months": 0, "Lease_Duration_Months": 24},
        {"Tenant_Name": "Priya Textiles",  "Tenant_Type": "Business",   "Industry_Type": "Textile",
         "Warehouse_Type": "Dry Warehouse",   "Warehouse_Size": "Medium", "Monthly_Rent_INR": 35000,
         "Customer_Tenure_Months": 0, "Lease_Duration_Months": 12},
        {"Tenant_Name": "Ravi Kumar",      "Tenant_Type": "Individual",  "Industry_Type": "Trading",
         "Warehouse_Type": "General",         "Warehouse_Size": "Small",  "Monthly_Rent_INR": 18000,
         "Customer_Tenure_Months": 0, "Lease_Duration_Months": 6},
    ])

    buf = io.BytesIO()
    template_df.to_csv(buf, index=False)
    buf.seek(0)
    st.download_button(
        "⬇️ Download Prospect Template CSV",
        data=buf,
        file_name="prospect_template.csv",
        mime="text/csv",
    )

    st.markdown("---")
    uploaded = st.file_uploader(
        "Upload Prospect CSV",
        type=["csv"],
        help="Use the template above. Required columns: Tenant_Name, Tenant_Type, Industry_Type, "
             "Warehouse_Type, Warehouse_Size, Monthly_Rent_INR, Customer_Tenure_Months, Lease_Duration_Months",
    )

    # Manual entry fallback
    use_manual = st.checkbox("Or enter prospect details manually")

    prospects_df = None

    if uploaded is not None:
        try:
            prospects_df = pd.read_csv(uploaded)
            st.success(f"✅ Loaded {len(prospects_df)} prospects from file.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    elif use_manual:
        with st.form("manual_prospect"):
            st.markdown("**Enter Prospect Details**")
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                m_name   = st.text_input("Tenant Name", "New Prospect Ltd")
                m_ttype  = st.selectbox("Tenant Type",  ["Business", "Individual"])
                m_ind    = st.text_input("Industry",     "Logistics")
            with mc2:
                m_wtype  = st.selectbox("WH Type",  ["Distribution Hub", "Cold Storage", "Dry Warehouse", "General"])
                m_wsize  = st.selectbox("WH Size",  ["Large", "Medium", "Small"])
                m_rent   = st.number_input("Monthly Rent (₹)", 5000, 300000, 50000, step=1000)
            with mc3:
                m_tenure = st.slider("Est. Tenure (months)", 0, 60, 0)
                m_lease  = st.slider("Lease Duration (months)", 6, 36, 12)
            m_sub = st.form_submit_button("Score This Prospect", type="primary")
        if m_sub:
            prospects_df = pd.DataFrame([{
                "Tenant_Name": m_name, "Tenant_Type": m_ttype, "Industry_Type": m_ind,
                "Warehouse_Type": m_wtype, "Warehouse_Size": m_wsize, "Monthly_Rent_INR": m_rent,
                "Customer_Tenure_Months": m_tenure, "Lease_Duration_Months": m_lease,
            }])

    if prospects_df is not None and not prospects_df.empty:
        try:
            scored = score_prospects(prospects_df, model_clf, scaler_clf, feat_clf)
            st.markdown("### 🎯 Scoring Results")

            # Gauges for up to 3
            if len(scored) <= 3:
                gcols = st.columns(len(scored))
                for i, (_, row) in enumerate(scored.iterrows()):
                    with gcols[i]:
                        name = row.get("Tenant_Name", f"Prospect {i+1}")
                        st.plotly_chart(prospect_gauge(float(row["Pay_Probability"]), name), use_container_width=True)
            else:
                st.plotly_chart(prospect_risk_bar(scored), use_container_width=True)

            # Results table
            show_cols = ["Tenant_Name", "Tenant_Type", "Industry_Type",
                         "Warehouse_Type", "Warehouse_Size", "Monthly_Rent_INR",
                         "Pay_Probability", "Predicted_Payment", "Risk_Tier", "Recommended_Action"]
            out_df = scored[[c for c in show_cols if c in scored.columns]].copy()
            out_df["Pay_Probability"] = (out_df["Pay_Probability"] * 100).round(1).astype(str) + "%"
            st.dataframe(out_df, use_container_width=True, hide_index=True)

            # Download scored results
            scored_buf = io.BytesIO()
            scored.to_csv(scored_buf, index=False)
            scored_buf.seek(0)
            st.download_button(
                "⬇️ Download Scored Results CSV",
                data=scored_buf,
                file_name="prospect_scores.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Scoring error: {e}")
            st.info("Make sure your CSV has all required columns. Download the template above.")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: INVOICE & REMINDERS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📨 Invoice & Reminders":
    render_notification_page(df)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: DATA EXPLORER
# ════════════════════════════════════════════════════════════════════════════
elif page == "📋 Data Explorer":
    st.markdown('<div class="section-header">📋 Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Browse, filter, and download the full dataset</div>', unsafe_allow_html=True)

    render_kpis(df)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Column selector
    all_cols = df.columns.tolist()
    default_cols = [c for c in [
        "Row_ID", "Tenant_Name", "Owner_Name", "Warehouse_Location",
        "Warehouse_Type", "Warehouse_Size", "Month_Name", "Monthly_Rent_INR",
        "Total_Invoice_INR", "Payment_Status", "Payment_Behavior",
        "Delay_Days", "Balance_Due_INR", "Risk_Score", "Tenant_Segment",
    ] if c in all_cols]
    selected_cols = st.multiselect("Select columns to display", all_cols, default=default_cols)
    if not selected_cols:
        selected_cols = default_cols

    search = st.text_input("Search by tenant name", "")
    view   = df.copy()
    if search:
        mask = view.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        view = view[mask]

    st.dataframe(view[selected_cols], use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(view)} rows × {len(selected_cols)} columns")

    # Download
    dl_buf = io.BytesIO()
    view[selected_cols].to_csv(dl_buf, index=False)
    dl_buf.seek(0)
    st.download_button(
        "⬇️ Download Filtered Dataset (CSV)",
        data=dl_buf,
        file_name="warehouse_data_filtered.csv",
        mime="text/csv",
    )

    # Descriptive stats
    st.markdown("#### Descriptive Statistics")
    num_cols = view.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        st.dataframe(view[num_cols].describe().round(2), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    render_settings_page()


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ADMIN
# ════════════════════════════════════════════════════════════════════════════
elif page == "🗂️ Admin — Manage Data":
    render_admin_page()
