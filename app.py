import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, date
import pytz

import visualizations as viz

# --- CONFIGURATION ---
PAGE_TITLE = "My Expense Tracker"

st.set_page_config(page_title=PAGE_TITLE, page_icon="💰")
st.title("💰 Expense Tracker")

# --- DATA HANDLING (The Backend) ---
# We use st.connection to handle the Google Sheets API automatically


def load_data():
    """Loads the dataframe from Google Sheets."""
    # Create a connection object.
    # This looks for "connections.gsheets" in your .streamlit/secrets.toml
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
        # ttl=0 ensures we don't serve stale data from cache after an update
        df = conn.read(worksheet="Sheet1", ttl=0)

        # If the sheet is empty, return the structure we expect
        if df.empty:
            return pd.DataFrame(columns=["Date", "Category", "Item", "Amount", "Type"])

        # Ensure consistent data types (Sheet data often comes as strings)
        if "Amount" in df.columns:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)

        return df
    except Exception:
        # Fallback if table doesn't exist yet
        return pd.DataFrame(columns=["Date", "Category", "Item", "Amount", "Type"])


def save_data(date_val, category, item, amount, trans_type):
    """Appends a new row to the Google Sheet."""
    new_data = pd.DataFrame(
        {
            "Date": [str(date_val)],  # Convert date to string for Sheet compatibility
            "Category": [category],
            "Item": [item],
            "Amount": [float(amount)],
            "Type": [trans_type],
        }
    )

    # 1. Load current data
    current_df = load_data()

    # 2. Append new data
    updated_df = pd.concat([current_df, new_data], ignore_index=True)

    # 3. Update the sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet="Sheet1", data=updated_df)


# --- SIDEBAR: DATA ENTRY ---
st.sidebar.header("Add New Entry")

with st.sidebar.form("entry_form", clear_on_submit=True):
    transaction_type = st.selectbox("Type", ["Expense", "Income"])

    # Dynamic categories based on type
    if transaction_type == "Expense":
        categories = [
            "House",
            "Car",
            "Childcare",
            "Groceries",
            "Utilities",
            "Shopping",
            "Medical",
            "Family support",
            "Kids activities",
            "Restaurant",
            "Health & Fitness",
            "Entertainment",
            "Travel",
            "Gifts",
            "Taxes",
            "Other",
        ]
    else:
        categories = [
            "Paycheck",
            "Bonus",
            "Reimbursement",
            "Cashback",
            "Gift",
        ]

    category = st.selectbox("Category", categories)
    item = st.text_input("Description (e.g., 'Coffee')")
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")

    # calculate current date in central timezone
    central = pytz.timezone("America/Chicago")
    now_utc = datetime.now().replace(tzinfo=pytz.utc)
    now_central = now_utc.astimezone(central)
    date_input = st.date_input("Date", now_central.date())

    submitted = st.form_submit_button("Save Entry")

    if submitted:
        if item and amount > 0:
            save_data(date_input, category, item, amount, transaction_type)
            st.success("Entry saved!")
        else:
            st.error("Please enter a description and amount.")

# --- MAIN DASHBOARD ---

# 1. Load Data
df = load_data()

if not df.empty:
    # Ensure numeric column is actually numeric for math
    df["Amount"] = pd.to_numeric(df["Amount"])

    # 2. KPIs
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income:,.2f}")
    col2.metric("Total Expenses", f"${total_expense:,.2f}")
    col3.metric("Remaining Balance", f"${balance:,.2f}", delta_color="normal")

    # 3. Recent Transactions Table
    st.subheader("📝 Recent Transactions")
    st.dataframe(df.tail(5).iloc[::-1], width="stretch")  # Show last 5, reversed

    # 4. Simple Charts
    st.subheader("📊 Analysis")

    tab1, tab2 = st.tabs(["Expenses by Category", "Income vs Expense"])

    with tab1:
        expense_df = df[df["Type"] == "Expense"]
        if not expense_df.empty:
            # Group by Category
            plotly_fig = viz.plot_monthly_breakdown(expense_df)
            st.plotly_chart(plotly_fig)
            # category_group = expense_df.groupby("Category")["Amount"].sum()
            # st.bar_chart(category_group, horizontal=True)
        else:
            st.info("No expenses recorded yet.")

    with tab2:
        type_group = df.groupby("Type")["Amount"].sum()
        st.bar_chart(type_group)

else:
    st.info("No data found. Use the sidebar to add your first expense!")
