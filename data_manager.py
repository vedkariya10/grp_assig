"""
data_manager.py — Data Management & Persistence
"""

import json
import os
import pandas as pd
import streamlit as st

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

BUSINESS_FILE = os.path.join(DATA_DIR, "business.json")
OWNERS_FILE = os.path.join(DATA_DIR, "owners.json")
WAREHOUSES_FILE = os.path.join(DATA_DIR, "warehouses.json")
TENANTS_FILE = os.path.join(DATA_DIR, "tenants.json")
RENTALS_FILE = os.path.join(DATA_DIR, "rentals.json")


def load_json(filepath):
    """Load JSON file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def save_json(filepath, data):
    """Save data to JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def get_business():
    """Get business profile."""
    return load_json(BUSINESS_FILE)


def set_business(data):
    """Save business profile."""
    save_json(BUSINESS_FILE, data)


def get_owners():
    """Get all owners."""
    data = load_json(OWNERS_FILE)
    return data.get("owners", [])


def set_owners(owners):
    """Save owners list."""
    save_json(OWNERS_FILE, {"owners": owners})


def get_warehouses():
    """Get all warehouses."""
    data = load_json(WAREHOUSES_FILE)
    return data.get("warehouses", [])


def set_warehouses(warehouses):
    """Save warehouses list."""
    save_json(WAREHOUSES_FILE, {"warehouses": warehouses})


def get_tenants():
    """Get all tenants."""
    data = load_json(TENANTS_FILE)
    return data.get("tenants", [])


def set_tenants(tenants):
    """Save tenants list."""
    save_json(TENANTS_FILE, {"tenants": tenants})


def get_rentals():
    """Get all rentals."""
    data = load_json(RENTALS_FILE)
    return data.get("rentals", [])


def set_rentals(rentals):
    """Save rentals list."""
    save_json(RENTALS_FILE, {"rentals": rentals})


def get_transaction_df():
    """Load main transaction data from CSV or built data."""
    try:
        df = pd.read_csv("warehouse_data.csv")
        df["Month"] = pd.to_datetime(df["Month"], format="%d-%m-%Y")
        return df
    except:
        # Fallback: return empty DataFrame with structure
        return pd.DataFrame()
