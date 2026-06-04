"""
utils.py — Machine Learning Models & Utilities
Warehouse Rental Management Analytics Platform
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, confusion_matrix, mean_squared_error, r2_score
)
from sklearn.cluster import KMeans
from mlxtend.frequent_patterns import apriori, association_rules
from scipy.stats import pearsonr
import json
import os

# ════════════════════════════════════════════════════════════════════════════
# COLOR & DISPLAY UTILITIES
# ════════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg_dark": "#0F1923",
    "bg_light": "#F8F9FA",
    "accent": "#2563EB",
    "success": "#1D8A5F",
    "danger": "#C0392B",
    "warning": "#D97706",
}

PALETTE = [
    "#2563EB", "#7C3AED", "#DB2777", "#EA580C",
    "#65A30D", "#0891B2", "#7C2D12", "#1E3A8A",
]

def inr_fmt(x):
    """Format numbers as Indian Rupees."""
    if pd.isna(x): return "₹0"
    if abs(x) >= 10_000_000:
        return f"₹{x/10_000_000:.1f}Cr"
    if abs(x) >= 100_000:
        return f"₹{x/100_000:.1f}L"
    return f"₹{x:,.0f}"


# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING & FILTERING
# ════════════════════════════════════════════════════════════════════════════
def load_data(filepath):
    """Load warehouse data with type conversions."""
    df = pd.read_csv(filepath)
    df["Month"] = pd.to_datetime(df["Month"], format="%d-%m-%Y")
    return df


def apply_filters(df, owner=None, location=None, wh_type=None, pay_status=None, year=None):
    """Apply global filters to dataset."""
    result = df.copy()
    if owner and owner != "All":
        result = result[result["Owner_Name"] == owner]
    if location and location != "All":
        result = result[result["Warehouse_Location"] == location]
    if wh_type and wh_type != "All":
        result = result[result["Warehouse_Type"] == wh_type]
    if pay_status and pay_status != "All":
        if pay_status == "Paid":
            result = result[result["Payment_Status"] == "Paid"]
        else:
            result = result[result["Payment_Status"] == "Not Paid"]
    if year and year != "All":
        result = result[result["Month"].dt.year == int(year)]
    return result


def compute_kpis(df):
    """Compute key performance indicators."""
    return {
        "total_revenue": df["Revenue_Collected_INR"].sum(),
        "avg_rent": df["Monthly_Rent_INR"].mean(),
        "num_tenants": df["Tenant_ID"].nunique(),
        "num_warehouses": df["WH_ID"].nunique(),
        "payment_rate": (df["Is_Paid_Binary"].sum() / len(df) * 100) if len(df) > 0 else 0,
        "avg_delay": df["Delay_Days"].mean(),
        "num_invoices": len(df),
    }


# ════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION: MULTIPLE ALGORITHMS WITH COMPARISON
# ════════════════════════════════════════════════════════════════════════════
def train_multi_classifiers(df, random_state=42):
    """
    Train multiple classification algorithms to predict payment status.
    Returns dictionary of models with performance metrics for each.
    """
    # Prepare data
    feature_cols = [
        "Monthly_Rent_INR", "Warehouse_Size", "Warehouse_Type",
        "Tenant_Type", "Industry_Type", "Payment_Behavior",
        "Customer_Tenure_Months", "Lease_Duration_Months", "Risk_Score"
    ]
    
    df_clean = df.dropna(subset=feature_cols + ["Is_Paid_Binary"])
    
    # Encode categorical features
    le_dict = {}
    df_encoded = df_clean.copy()
    
    for col in ["Warehouse_Size", "Warehouse_Type", "Tenant_Type", "Industry_Type", "Payment_Behavior"]:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded["Is_Paid_Binary"].copy()
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    # Define classifiers
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "SVM": SVC(kernel='rbf', probability=True, random_state=random_state),
        "Decision Tree": DecisionTreeClassifier(random_state=random_state),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=random_state),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes": GaussianNB(),
    }
    
    results = {}
    
    for name, clf in classifiers.items():
        # Train
        clf.fit(X_train, y_train)
        
        # Predict
        y_pred = clf.predict(X_test)
        y_pred_proba = clf.predict_proba(X_test)[:, 1]
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_pred_proba)
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            "model": clf,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": roc,
            "confusion_matrix": cm,
            "y_test": y_test,
            "y_pred": y_pred,
            "y_pred_proba": y_pred_proba,
        }
    
    return results, scaler, feature_cols, le_dict, X_test, y_test


def train_classifier(df, random_state=42):
    """Train Random Forest classifier for prospect scoring (original function)."""
    feature_cols = [
        "Monthly_Rent_INR", "Warehouse_Size", "Warehouse_Type",
        "Tenant_Type", "Industry_Type", "Payment_Behavior",
        "Customer_Tenure_Months", "Lease_Duration_Months", "Risk_Score"
    ]
    
    df_clean = df.dropna(subset=feature_cols + ["Is_Paid_Binary"])
    
    le_dict = {}
    df_encoded = df_clean.copy()
    
    for col in ["Warehouse_Size", "Warehouse_Type", "Tenant_Type", "Industry_Type", "Payment_Behavior"]:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded["Is_Paid_Binary"].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_pred_proba),
    }
    
    return model, scaler, metrics, feature_cols


# ════════════════════════════════════════════════════════════════════════════
# REGRESSION: LINEAR, RIDGE, LASSO
# ════════════════════════════════════════════════════════════════════════════
def train_rent_regressor(df, random_state=42):
    """Predict monthly rent based on warehouse characteristics."""
    feature_cols = [
        "Warehouse_Size", "Warehouse_Type", "Customer_Tenure_Months",
        "Lease_Duration_Months"
    ]
    
    df_clean = df.dropna(subset=feature_cols + ["Monthly_Rent_INR"])
    
    le_dict = {}
    df_encoded = df_clean.copy()
    
    for col in ["Warehouse_Size", "Warehouse_Type"]:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded["Monthly_Rent_INR"].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=random_state
    )
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Lasso Regression": Lasso(alpha=1.0),
    }
    
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        mae = np.mean(np.abs(y_test - y_pred))
        
        results[name] = {
            "model": model,
            "rmse": rmse,
            "r2_score": r2,
            "mae": mae,
            "y_test": y_test,
            "y_pred": y_pred,
        }
    
    return results, scaler, feature_cols


def train_delay_regressor(df, random_state=42):
    """Predict payment delay days."""
    feature_cols = [
        "Monthly_Rent_INR", "Warehouse_Size", "Warehouse_Type",
        "Tenant_Type", "Industry_Type", "Customer_Tenure_Months",
        "Lease_Duration_Months", "Risk_Score"
    ]
    
    df_clean = df[df["Delay_Days"] >= 0].dropna(subset=feature_cols + ["Delay_Days"])
    
    le_dict = {}
    df_encoded = df_clean.copy()
    
    for col in ["Warehouse_Size", "Warehouse_Type", "Tenant_Type", "Industry_Type"]:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded["Delay_Days"].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=random_state
    )
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Lasso Regression": Lasso(alpha=1.0),
    }
    
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        mae = np.mean(np.abs(y_test - y_pred))
        
        results[name] = {
            "model": model,
            "rmse": rmse,
            "r2_score": r2,
            "mae": mae,
            "y_test": y_test,
            "y_pred": y_pred,
        }
    
    return results, scaler, feature_cols


# ════════════════════════════════════════════════════════════════════════════
# CLUSTERING: K-MEANS WITH ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
def train_clustering(df, k=4, random_state=42):
    """Train K-Means clustering with elbow method."""
    feature_cols = [
        "Monthly_Rent_INR", "Customer_Tenure_Months",
        "Risk_Score", "Delay_Days"
    ]
    
    df_clean = df.dropna(subset=feature_cols)
    X = df_clean[feature_cols].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Elbow method
    inertias = []
    silhouette_scores = []
    K_range = range(2, 11)
    
    for k_val in K_range:
        km = KMeans(n_clusters=k_val, random_state=random_state, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
    
    # Train final model
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    clusters = model.fit_predict(X_scaled)
    
    df_clean["Cluster"] = clusters
    
    # Cluster profiles
    profiles = {}
    for cluster_id in range(k):
        cluster_data = df_clean[df_clean["Cluster"] == cluster_id]
        profiles[f"Cluster {cluster_id}"] = {
            "size": len(cluster_data),
            "avg_rent": cluster_data["Monthly_Rent_INR"].mean(),
            "avg_tenure": cluster_data["Customer_Tenure_Months"].mean(),
            "avg_risk": cluster_data["Risk_Score"].mean(),
            "avg_delay": cluster_data["Delay_Days"].mean(),
            "primary_tenant": cluster_data["Tenant_Type"].mode()[0] if len(cluster_data) > 0 else "N/A",
            "primary_industry": cluster_data["Industry_Type"].mode()[0] if len(cluster_data) > 0 else "N/A",
        }
    
    return {
        "model": model,
        "clusters": clusters,
        "profiles": profiles,
        "inertias": list(inertias),
        "k_range": list(K_range),
        "data": df_clean,
    }


# ════════════════════════════════════════════════════════════════════════════
# ASSOCIATION RULES: MARKET BASKET ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
def compute_association_rules(df, min_support=0.1):
    """
    Derive association rules: Which warehouse types are rented by which tenant types?
    Which tenant types prefer which industries?
    """
    # Create transaction matrix: Warehouse Type + Tenant Type + Industry Type
    transactions = df[["Warehouse_Type", "Tenant_Type", "Industry_Type"]].copy()
    transactions = transactions.drop_duplicates()
    
    # Create binary matrix (one-hot encoding)
    basket = pd.get_dummies(transactions, prefix=['WH', 'Tenant', 'Ind'])
    
    # Apply Apriori
    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    
    if len(frequent_itemsets) < 2:
        return {"rules": pd.DataFrame(), "itemsets": frequent_itemsets}
    
    # Generate rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
    
    if len(rules) > 0:
        rules = rules.sort_values("lift", ascending=False)
        rules["antecedent_str"] = rules["antecedents"].apply(
            lambda x: ", ".join(list(x))
        )
        rules["consequent_str"] = rules["consequents"].apply(
            lambda x: ", ".join(list(x))
        )
    
    return {
        "rules": rules,
        "itemsets": frequent_itemsets,
    }


# ════════════════════════════════════════════════════════════════════════════
# PROSPECT SCORING
# ════════════════════════════════════════════════════════════════════════════
PROSPECT_SCHEMA = {
    "Tenant_Name": str,
    "Tenant_Type": str,
    "Industry_Type": str,
    "Warehouse_Type": str,
    "Warehouse_Size": str,
    "Monthly_Rent_INR": float,
    "Customer_Tenure_Months": int,
    "Lease_Duration_Months": int,
}


def score_prospects(prospects_df, model, scaler, feature_cols):
    """Score new prospects using trained classifier."""
    df = prospects_df.copy()
    
    # Encode
    le_size = LabelEncoder()
    le_type = LabelEncoder()
    le_tenant = LabelEncoder()
    le_ind = LabelEncoder()
    le_behav = LabelEncoder()
    
    # Fit on sample values
    le_size.fit(["Small", "Medium", "Large"])
    le_type.fit(["Distribution Hub", "Cold Storage", "Dry Warehouse", "General"])
    le_tenant.fit(["Business", "Individual"])
    le_ind.fit(["Logistics", "Retail", "Textile", "Trading", "Food", "Manufacturing"])
    le_behav.fit(["On-time", "Delayed", "Defaulted"])
    
    df["Warehouse_Size"] = le_size.transform(df["Warehouse_Size"])
    df["Warehouse_Type"] = le_type.transform(df["Warehouse_Type"])
    df["Tenant_Type"] = le_tenant.transform(df["Tenant_Type"])
    df["Industry_Type"] = le_ind.transform(df["Industry_Type"])
    df["Payment_Behavior"] = "On-time"
    df["Payment_Behavior"] = le_behav.transform(df["Payment_Behavior"])
    df["Risk_Score"] = 30  # Default low risk
    
    X = df[feature_cols].copy()
    X_scaled = scaler.transform(X)
    
    y_pred = model.predict(X_scaled)
    y_pred_proba = model.predict_proba(X_scaled)[:, 1]
    
    df["Pay_Probability"] = y_pred_proba
    df["Predicted_Payment"] = y_pred
    df["Risk_Tier"] = df["Pay_Probability"].apply(
        lambda x: "High Risk" if x < 0.4 else ("Medium Risk" if x < 0.7 else "Low Risk")
    )
    df["Recommended_Action"] = df["Risk_Tier"].apply(
        lambda x: "Require deposit" if x == "High Risk" else ("Standard contract" if x == "Medium Risk" else "Approve")
    )
    
    return df


# ════════════════════════════════════════════════════════════════════════════
# CORRELATION & DIAGNOSTICS
# ════════════════════════════════════════════════════════════════════════════
def compute_correlations(df):
    """Compute Pearson correlation matrix for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr_matrix = df[numeric_cols].corr()
    return corr_matrix
