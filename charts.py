"""
charts.py — Plotly Visualizations
Warehouse Rental Management Analytics Platform
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import roc_curve
import json


# ════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION ALGORITHM COMPARISON CHARTS
# ════════════════════════════════════════════════════════════════════════════
def classifier_comparison_metrics(results_dict):
    """
    Create grouped bar chart comparing accuracy, precision, recall, f1, ROC-AUC
    across all classifiers.
    """
    metrics_data = []
    
    for algo_name, metrics in results_dict.items():
        metrics_data.append({
            "Algorithm": algo_name,
            "Accuracy": metrics["accuracy"],
            "Precision": metrics["precision"],
            "Recall": metrics["recall"],
            "F1-Score": metrics["f1_score"],
            "ROC-AUC": metrics["roc_auc"],
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Melt for grouped bar
    df_melted = df_metrics.melt(
        id_vars=["Algorithm"],
        var_name="Metric",
        value_name="Score"
    )
    
    fig = px.bar(
        df_melted,
        x="Algorithm",
        y="Score",
        color="Metric",
        barmode="group",
        title="Classification Algorithm Performance Comparison",
        labels={"Score": "Score (0-1)", "Algorithm": "Algorithm"},
        height=500,
        template="plotly_white",
        color_discrete_sequence=[
            "#2563EB", "#7C3AED", "#DB2777", "#EA580C", "#65A30D"
        ]
    )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_tickangle=-45,
        font=dict(size=11),
        margin=dict(b=100)
    )
    
    return fig


def classifier_accuracy_radar(results_dict):
    """Radar chart comparing 5 metrics across all algorithms."""
    metrics_data = []
    algorithms = []
    
    for algo_name, metrics in results_dict.items():
        algorithms.append(algo_name)
        metrics_data.append([
            metrics["accuracy"],
            metrics["precision"],
            metrics["recall"],
            metrics["f1_score"],
            metrics["roc_auc"],
        ])
    
    categories = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
    
    fig = go.Figure()
    
    colors = [
        "#2563EB", "#7C3AED", "#DB2777", "#EA580C",
        "#65A30D", "#0891B2", "#7C2D12"
    ]
    
    for i, (algo, values) in enumerate(zip(algorithms, metrics_data)):
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=algo,
            line=dict(color=colors[i % len(colors)]),
            hovertemplate="<b>%{name}</b><br>%{theta}: %{r:.3f}<extra></extra>",
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickformat=".2f",
            )
        ),
        showlegend=True,
        height=600,
        title="Algorithm Performance Radar Comparison",
        font=dict(size=11),
        hovermode="closest",
    )
    
    return fig


def confusion_matrix_heatmap(cm, algorithm_name):
    """Heatmap of confusion matrix for a single classifier."""
    labels = ["Not Paid", "Paid"]
    
    # Normalize for display
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    
    fig = go.Figure(data=go.Heatmap(
        z=cm_norm,
        x=["Predicted Not Paid", "Predicted Paid"],
        y=["Actual Not Paid", "Actual Paid"],
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 14},
        colorscale="Blues",
        hovertemplate="<b>%{y} → %{x}</b><br>Count: %{text}<br>Proportion: %{z:.1%}<extra></extra>",
    ))
    
    fig.update_layout(
        title=f"Confusion Matrix — {algorithm_name}",
        xaxis_title="Predicted Label",
        yaxis_title="Actual Label",
        height=450,
        width=500,
    )
    
    return fig


def roc_curve_comparison(results_dict, y_test):
    """ROC curves for all classifiers overlaid."""
    fig = go.Figure()
    
    colors = [
        "#2563EB", "#7C3AED", "#DB2777", "#EA580C",
        "#65A30D", "#0891B2", "#7C2D12"
    ]
    
    for i, (algo_name, metrics) in enumerate(results_dict.items()):
        fpr, tpr, _ = roc_curve(y_test, metrics["y_pred_proba"])
        auc = metrics["roc_auc"]
        
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            name=f"{algo_name} (AUC={auc:.3f})",
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate="FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>",
        ))
    
    # Diagonal (random classifier)
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random (AUC=0.5)',
        line=dict(color='#999999', dash='dash', width=2),
        hoverinfo='skip',
    ))
    
    fig.update_layout(
        title="ROC Curves — Algorithm Comparison",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=600,
        template="plotly_white",
        hovermode="closest",
        font=dict(size=11),
    )
    
    fig.update_xaxes(range=[0, 1])
    fig.update_yaxes(range=[0, 1])
    
    return fig


def feature_importance_comparison(models_dict, feature_names):
    """Feature importance for tree-based models (RF, GB, DT)."""
    fi_data = []
    
    tree_models = {
        "Random Forest": models_dict.get("Random Forest"),
        "Gradient Boosting": models_dict.get("Gradient Boosting"),
        "Decision Tree": models_dict.get("Decision Tree"),
    }
    
    for model_name, model_info in tree_models.items():
        if model_info is None:
            continue
        
        model = model_info["model"]
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            for feat, imp in zip(feature_names, importances):
                fi_data.append({
                    "Feature": feat,
                    "Importance": imp,
                    "Model": model_name
                })
    
    if not fi_data:
        return go.Figure().add_annotation(text="No feature importance data available")
    
    df_fi = pd.DataFrame(fi_data)
    
    fig = px.bar(
        df_fi,
        x="Importance",
        y="Feature",
        color="Model",
        barmode="group",
        orientation="h",
        title="Feature Importance (Tree-Based Models)",
        height=500,
        template="plotly_white",
        color_discrete_sequence=["#2563EB", "#7C3AED", "#DB2777"]
    )
    
    fig.update_layout(
        hovermode="closest",
        font=dict(size=11),
        xaxis_title="Importance Score",
        yaxis_title="Feature",
    )
    
    return fig


# ════════════════════════════════════════════════════════════════════════════
# REGRESSION VISUALIZATIONS
# ════════════════════════════════════════════════════════════════════════════
def regression_comparison_metrics(results_dict, metric_name="rmse"):
    """Compare regression models: RMSE, MAE, R²."""
    metrics_data = []
    
    for model_name, metrics in results_dict.items():
        metrics_data.append({
            "Model": model_name,
            "RMSE": metrics.get("rmse", 0),
            "MAE": metrics.get("mae", 0),
            "R² Score": metrics.get("r2_score", 0),
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_metrics["Model"],
        y=df_metrics["RMSE"],
        name="RMSE",
        marker_color="#2563EB",
        hovertemplate="<b>%{x}</b><br>RMSE: ₹%{y:,.0f}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=df_metrics["Model"],
        y=df_metrics["MAE"],
        name="MAE",
        marker_color="#7C3AED",
        hovertemplate="<b>%{x}</b><br>MAE: ₹%{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Regression Model Comparison (Rent Prediction)",
        xaxis_title="Model",
        yaxis_title="Error (₹)",
        barmode="group",
        height=500,
        template="plotly_white",
        hovermode="x unified",
        font=dict(size=11),
    )
    
    return fig


def regression_actual_vs_predicted(y_test, y_pred, model_name):
    """Scatter plot: actual vs predicted values."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=y_test,
        y=y_pred,
        mode='markers',
        name='Predictions',
        marker=dict(size=6, color='#2563EB', opacity=0.6),
        hovertemplate="Actual: ₹%{x:,.0f}<br>Predicted: ₹%{y:,.0f}<extra></extra>"
    ))
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='#65A30D', dash='dash', width=2),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=f"Actual vs Predicted — {model_name}",
        xaxis_title="Actual Rent (₹)",
        yaxis_title="Predicted Rent (₹)",
        height=500,
        template="plotly_white",
        hovermode="closest",
        font=dict(size=11),
    )
    
    return fig


# ════════════════════════════════════════════════════════════════════════════
# CLUSTERING VISUALIZATIONS
# ════════════════════════════════════════════════════════════════════════════
def elbow_chart(inertias, k_range):
    """Elbow method chart for optimal K selection."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(k_range),
        y=inertias,
        mode='lines+markers',
        name='Inertia',
        line=dict(color='#2563EB', width=3),
        marker=dict(size=8),
        hovertemplate="K=%{x}<br>Inertia: %{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Elbow Method — Optimal K Selection",
        xaxis_title="Number of Clusters (K)",
        yaxis_title="Inertia (Within-cluster sum of squares)",
        height=500,
        template="plotly_white",
        hovermode="x unified",
        font=dict(size=11),
    )
    
    return fig


def cluster_scatter(df_clustered, x_col, y_col, cluster_col="Cluster"):
    """2D scatter plot of clusters."""
    fig = px.scatter(
        df_clustered,
        x=x_col,
        y=y_col,
        color=cluster_col,
        title=f"Cluster Distribution: {x_col} vs {y_col}",
        labels={x_col: x_col, y_col: y_col},
        height=550,
        template="plotly_white",
        color_discrete_sequence=["#2563EB", "#7C3AED", "#DB2777", "#EA580C"],
    )
    
    fig.update_traces(marker=dict(size=8, opacity=0.6))
    fig.update_layout(
        hovermode="closest",
        font=dict(size=11),
    )
    
    return fig


def cluster_profile_radar(profiles):
    """Radar chart comparing cluster profiles."""
    if not profiles:
        return go.Figure()
    
    fig = go.Figure()
    
    # Normalize metrics to 0-1 scale for comparison
    max_rent = max([p.get("avg_rent", 0) for p in profiles.values()]) or 1
    max_tenure = max([p.get("avg_tenure", 0) for p in profiles.values()]) or 1
    max_risk = max([p.get("avg_risk", 0) for p in profiles.values()]) or 1
    max_delay = max([p.get("avg_delay", 0) for p in profiles.values()]) or 1
    
    colors = ["#2563EB", "#7C3AED", "#DB2777", "#EA580C"]
    
    for i, (cluster_name, profile) in enumerate(profiles.items()):
        fig.add_trace(go.Scatterpolar(
            r=[
                profile.get("avg_rent", 0) / max_rent,
                profile.get("avg_tenure", 0) / max_tenure,
                profile.get("avg_risk", 0) / max_risk,
                profile.get("avg_delay", 0) / max_delay,
                profile.get("size", 0) / max([p.get("size", 0) for p in profiles.values()]),
            ],
            theta=["Avg Rent", "Avg Tenure", "Avg Risk", "Avg Delay", "Cluster Size"],
            fill='toself',
            name=cluster_name,
            line=dict(color=colors[i % len(colors)]),
            hovertemplate="<b>%{name}</b><br>%{theta}: %{r:.2f}<extra></extra>",
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
        height=600,
        title="Cluster Profiles Comparison",
        font=dict(size=11),
        hovermode="closest",
    )
    
    return fig


# ════════════════════════════════════════════════════════════════════════════
# ASSOCIATION RULES VISUALIZATIONS
# ════════════════════════════════════════════════════════════════════════════
def association_heatmap(rules):
    """Heatmap: Support vs Confidence with Lift as color."""
    if rules.empty:
        return go.Figure().add_annotation(text="No association rules found")
    
    # Create rule labels
    rules_display = rules.head(15).copy()
    rules_display["Rule"] = rules_display["antecedent_str"] + " → " + rules_display["consequent_str"]
    rules_display["Rule"] = rules_display["Rule"].str.slice(0, 50)  # Truncate
    
    fig = px.scatter(
        rules_display,
        x="support",
        y="confidence",
        size="lift",
        color="lift",
        hover_data={"support": ":.3f", "confidence": ":.3f", "lift": ":.3f"},
        title="Association Rules: Support vs Confidence (size/color = Lift)",
        labels={
            "support": "Support",
            "confidence": "Confidence",
            "lift": "Lift",
        },
        height=550,
        template="plotly_white",
        color_continuous_scale="Viridis",
    )
    
    fig.update_layout(
        hovermode="closest",
        font=dict(size=10),
        xaxis_title="Support (Frequency of itemset)",
        yaxis_title="Confidence (P(Consequent|Antecedent))",
    )
    
    return fig


def association_bubble(rules):
    """Bubble chart: Antecedent vs Consequent with Lift bubble size."""
    if rules.empty:
        return go.Figure().add_annotation(text="No rules")
    
    rules_top = rules.head(10).copy()
    rules_top["Index"] = range(len(rules_top))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rules_top["antecedent_str"],
        y=rules_top["consequent_str"],
        mode='markers',
        marker=dict(
            size=rules_top["lift"] * 20,
            color=rules_top["confidence"],
            colorscale="Plasma",
            showscale=True,
            colorbar=dict(title="Confidence"),
            line=dict(width=1, color='white'),
        ),
        text=[f"<b>Lift: {l:.2f}</b><br>Support: {s:.3f}<br>Confidence: {c:.3f}" 
              for l, s, c in zip(rules_top["lift"], rules_top["support"], rules_top["confidence"])],
        hovertemplate="%{text}<extra></extra>",
    ))
    
    fig.update_layout(
        title="Top Association Rules (Bubble = Lift magnitude)",
        xaxis_title="Antecedent (If)",
        yaxis_title="Consequent (Then)",
        height=600,
        template="plotly_white",
        hovermode="closest",
        font=dict(size=10),
        xaxis_tickangle=-45,
    )
    
    return fig


# ════════════════════════════════════════════════════════════════════════════
# ORIGINAL CHARTS (kept for compatibility)
# ════════════════════════════════════════════════════════════════════════════
def monthly_revenue_trend(df):
    """Line chart of monthly revenue."""
    monthly = df.groupby("Month_Name")["Revenue_Collected_INR"].sum().reset_index()
    monthly["Month_Name"] = pd.Categorical(
        monthly["Month_Name"],
        categories=["Jan-23", "Feb-23", "Mar-23", "Apr-23", "May-23", "Jun-23",
                   "Jul-23", "Aug-23", "Sep-23", "Oct-23", "Nov-23", "Dec-23",
                   "Jan-24", "Feb-24", "Mar-24", "Apr-24", "May-24", "Jun-24"],
        ordered=True
    )
    monthly = monthly.sort_values("Month_Name")
    
    fig = px.line(
        monthly,
        x="Month_Name",
        y="Revenue_Collected_INR",
        markers=True,
        title="📈 Monthly Revenue Trend",
        labels={"Month_Name": "Month", "Revenue_Collected_INR": "Revenue (₹)"},
        height=400,
        template="plotly_white",
    )
    
    fig.update_traces(
        line=dict(color="#2563EB", width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
    )
    
    fig.update_layout(font=dict(size=11), hovermode="x unified")
    return fig


def owner_revenue_bar(df):
    """Bar chart of revenue by owner."""
    owner_rev = df.groupby("Owner_Name")["Revenue_Collected_INR"].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=owner_rev.values,
        y=owner_rev.index,
        orientation='h',
        title="💰 Revenue by Owner (Top 10)",
        labels={"x": "Revenue (₹)", "y": "Owner"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(
        marker_color="#2563EB",
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
    )
    
    fig.update_layout(font=dict(size=11), hovermode="closest")
    return fig


def owner_revenue_pie(df):
    """Pie chart of revenue distribution by owner."""
    owner_rev = df.groupby("Owner_Name")["Revenue_Collected_INR"].sum().sort_values(ascending=False).head(8)
    
    fig = px.pie(
        values=owner_rev.values,
        names=owner_rev.index,
        title="Revenue Share by Owner (Top 8)",
        height=450,
    )
    
    fig.update_traces(hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>")
    return fig


def location_bar(df):
    """Bar chart of warehouses by location."""
    loc = df.groupby("Warehouse_Location").size().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=loc.values,
        y=loc.index,
        orientation='h',
        title="🏢 Warehouses by Location (Top 10)",
        labels={"x": "Count", "y": "Location"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#7C3AED")
    fig.update_layout(font=dict(size=11))
    return fig


def payment_status_donut(df):
    """Donut chart of payment status."""
    status = df["Payment_Status"].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=status.index,
        values=status.values,
        hole=0.4,
        textposition='inside',
        textinfo='label+percent',
    )])
    
    fig.update_layout(
        title="Payment Status Distribution",
        height=400,
    )
    
    return fig


def payment_behaviour_bar(df):
    """Bar chart of payment behavior."""
    behaviour = df["Payment_Behavior"].value_counts().sort_values(ascending=False)
    
    fig = px.bar(
        x=behaviour.index,
        y=behaviour.values,
        title="Payment Behavior Distribution",
        labels={"x": "Behavior", "y": "Count"},
        template="plotly_white",
        height=400,
    )
    
    colors_map = {
        "On-time": "#1D8A5F",
        "Delayed": "#D97706",
        "Defaulted": "#C0392B"
    }
    fig.update_traces(marker_color=[colors_map.get(b, "#2563EB") for b in behaviour.index])
    
    fig.update_layout(font=dict(size=11))
    return fig


def quarterly_revenue(df):
    """Quarterly revenue trend."""
    quarterly = df.groupby("Quarter")["Revenue_Collected_INR"].sum().reset_index()
    
    fig = px.bar(
        quarterly,
        x="Quarter",
        y="Revenue_Collected_INR",
        title="Quarterly Revenue",
        labels={"Quarter": "Quarter", "Revenue_Collected_INR": "Revenue (₹)"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#2563EB")
    fig.update_layout(font=dict(size=11))
    return fig


def wh_type_revenue(df):
    """Revenue by warehouse type."""
    wh_rev = df.groupby("Warehouse_Type")["Revenue_Collected_INR"].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=wh_rev.index,
        y=wh_rev.values,
        title="Revenue by Warehouse Type",
        labels={"x": "Type", "y": "Revenue (₹)"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#EA580C")
    fig.update_layout(font=dict(size=11))
    return fig


def automation_summary(df):
    """Summary of invoice automation."""
    summary = pd.DataFrame({
        "Channel": ["Email Sent", "WhatsApp Sent", "Invoice Sent"],
        "Count": [
            df["Email_Sent"].sum(),
            df["WhatsApp_Sent"].sum(),
            df["Invoice_Sent"].sum(),
        ]
    })
    
    fig = px.bar(
        summary,
        x="Channel",
        y="Count",
        title="Invoice Automation Summary",
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#0891B2")
    fig.update_layout(font=dict(size=11))
    return fig


def correlation_heatmap(corr_matrix):
    """Correlation heatmap of numerical columns."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale="RdBu",
        zmid=0,
        zmin=-1,
        zmax=1,
    ))
    
    fig.update_layout(
        title="Correlation Matrix — Numerical Variables",
        height=650,
        width=800,
    )
    
    return fig


def rent_vs_size(df):
    """Scatter: Rent vs Warehouse Size."""
    fig = px.scatter(
        df,
        x="Warehouse_Size",
        y="Monthly_Rent_INR",
        color="Warehouse_Type",
        title="Rent vs Warehouse Size",
        template="plotly_white",
        height=450,
    )
    
    fig.update_layout(font=dict(size=11))
    return fig


def rent_vs_type(df):
    """Box plot: Rent distribution by Warehouse Type."""
    fig = px.box(
        df,
        x="Warehouse_Type",
        y="Monthly_Rent_INR",
        title="Rent Distribution by Warehouse Type",
        template="plotly_white",
        height=450,
    )
    
    fig.update_layout(font=dict(size=11))
    return fig


def delay_by_industry(df):
    """Delay days by industry type."""
    delay = df.groupby("Industry_Type")["Delay_Days"].mean().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=delay.values,
        y=delay.index,
        orientation='h',
        title="Avg Payment Delay by Industry (Top 10)",
        labels={"x": "Avg Delay (days)", "y": "Industry"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#D97706")
    fig.update_layout(font=dict(size=11))
    return fig


def delay_by_tenant_type(df):
    """Delay days by tenant type."""
    delay = df.groupby("Tenant_Type")["Delay_Days"].mean()
    
    fig = px.bar(
        x=delay.index,
        y=delay.values,
        title="Avg Payment Delay by Tenant Type",
        labels={"x": "Tenant Type", "y": "Avg Delay (days)"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#DB2777")
    fig.update_layout(font=dict(size=11))
    return fig


def risk_score_histogram(df):
    """Histogram of risk scores."""
    fig = px.histogram(
        df,
        x="Risk_Score",
        nbins=30,
        title="Risk Score Distribution",
        labels={"Risk_Score": "Risk Score", "count": "Frequency"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#EA580C")
    fig.update_layout(font=dict(size=11))
    return fig


def location_type_heatmap(df):
    """Heatmap: Location × Type revenue."""
    pivot = df.pivot_table(
        values="Revenue_Collected_INR",
        index="Warehouse_Location",
        columns="Warehouse_Type",
        aggfunc="sum"
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="Viridis",
    ))
    
    fig.update_layout(
        title="Revenue Heatmap: Location × Type",
        height=600,
    )
    
    return fig


def roc_curve_chart(y_test, y_pred_proba):
    """ROC curve for single model."""
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    auc = np.trapz(tpr, fpr)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines',
        name=f'ROC Curve (AUC={auc:.3f})',
        line=dict(color='#2563EB', width=2),
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='#999', dash='dash'),
    ))
    
    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=500,
        template="plotly_white",
    )
    
    return fig


def confusion_matrix_chart(cm):
    """Simple confusion matrix."""
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=["Not Paid", "Paid"],
        y=["Not Paid", "Paid"],
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 14},
        colorscale="Blues",
    ))
    
    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        height=450,
        width=500,
    )
    
    return fig


def feature_importance_chart(model, feature_names):
    """Feature importance from tree model."""
    if not hasattr(model, "feature_importances_"):
        return go.Figure()
    
    fi = model.feature_importances_
    fi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": fi
    }).sort_values("Importance", ascending=True)
    
    fig = px.barh(
        fi_df,
        x="Importance",
        y="Feature",
        title="Feature Importance",
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color="#2563EB")
    fig.update_layout(font=dict(size=11))
    return fig


def prospect_gauge(prob, name):
    """Gauge chart for prospect payment probability."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=prob * 100,
        title={'text': f"{name}"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2563EB"},
            'steps': [
                {'range': [0, 33], 'color': "#FCEAEA"},
                {'range': [33, 67], 'color': "#FDF6E3"},
                {'range': [67, 100], 'color': "#E8F6F0"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=350, font=dict(size=12))
    return fig


def prospect_risk_bar(scored_df):
    """Bar chart of prospect risk tiers."""
    risk_counts = scored_df["Risk_Tier"].value_counts()
    colors_map = {
        "Low Risk": "#1D8A5F",
        "Medium Risk": "#D97706",
        "High Risk": "#C0392B"
    }
    
    fig = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        title="Prospect Risk Tier Distribution",
        labels={"x": "Risk Tier", "y": "Count"},
        template="plotly_white",
        height=400,
    )
    
    fig.update_traces(marker_color=[colors_map.get(t, "#2563EB") for t in risk_counts.index])
    fig.update_layout(font=dict(size=11))
    return fig
