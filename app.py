import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

import constants as const
from data_processing import (
    process_transactions_df,
    calculate_current_month_expense,
    calculate_last_month_income,
)
from visualizations import (
    plot_monthly_breakdown,
    plot_expenses_by_month,
    plot_expenses_by_year,
    plot_top_categories,
    plot_income_vs_expense_trend,
    plot_yearly_income_vs_expense,
    plot_yearly_category_breakdown,
)

# --- CONFIGURATION ---
PAGE_TITLE = "Expnense and Income Tracker"

st.set_page_config(page_title=PAGE_TITLE, page_icon="💰")
st.title("💰 Expense and Income Tracker")

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

# calculate current date in central timezone
central = pytz.timezone("America/Chicago")
now_utc = datetime.now().replace(tzinfo=pytz.utc)
now_central = now_utc.astimezone(central)

st.sidebar.header("Add Expense")

with st.sidebar.form(key="expense_form", clear_on_submit=True):

    transaction_type = "Expense"
    selected_categories = const.categories[transaction_type]

    category = st.selectbox("Category", options=selected_categories, key=1, index=0)
    item = st.text_input("Description (e.g., 'Coffee')")
    amount = st.number_input("Amount", min_value=0.01, format="%.2f", key=2)
    date_input = st.date_input("Date", now_central.date(), key=3)

    submitted = st.form_submit_button("Save Expense Entry", key=4)

    if submitted:
        if item and amount > 0:
            save_data(date_input, category, item, amount, transaction_type)
            st.success("Entry saved!")
        else:
            st.error("Please enter a description and amount.")

st.sidebar.header("Add Income")
with st.sidebar.form(key="income_form", clear_on_submit=True):

    transaction_type = "Income"
    selected_categories = const.categories[transaction_type]

    category = st.selectbox("Category", options=selected_categories, key=5, index=0)

    item = st.text_input("Earner")
    amount = st.number_input("Amount", min_value=0.01, format="%.2f", key=6)
    date_input = st.date_input("Date", now_central.date(), key=7)

    submitted = st.form_submit_button("Save Income Entry", key=8)

    if submitted:
        if category and amount > 0:
            save_data(date_input, category, item, amount, transaction_type)
            st.success("Entry saved!")
        else:
            st.error("Please select Category and amount.")

# --- MAIN DASHBOARD ---

# 1. Load Data
df = load_data()

if not df.empty:

    # Process once per render and reuse everywhere below, instead of every
    # KPI/chart re-deriving numeric/date/year/month columns from scratch.
    processed_df = process_transactions_df(df.copy())

    # 2. KPIs
    last_month_income = calculate_last_month_income(processed_df)
    current_month_expense = calculate_current_month_expense(processed_df)
    savings = (
        round((last_month_income - current_month_expense), 2)
        if last_month_income > current_month_expense
        else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Last Month Income", f"${last_month_income:,.0f}")
    col2.metric("Current Month Expenses", f"${current_month_expense:,.0f}")
    col3.metric("Savings", f"${savings:,.0f}", delta_color="normal")

    # 4. Monthly Charts
    st.subheader("📊 Monthly Analysis")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Expenses by Category",
            "Expenses by Month",
            "Income by Category",
            "Top Categories",
            "Income vs Expense Trend",
        ]
    )

    with tab1:
        if not df.empty:
            # Group by Category
            plotly_fig_expense = plot_monthly_breakdown(processed_df, "Expense")
            st.plotly_chart(plotly_fig_expense)
        else:
            st.info("No expenses recorded yet.")

    with tab2:
        if not df.empty:
            categories = ["All"] + const.categories["Expense"]
            selected_category = st.selectbox(
                "Select category to visualize:",
                options=categories,
                key="select_category",
            )

            plotly_fig = plot_expenses_by_month(
                transactions_df=processed_df, category=selected_category
            )
            st.plotly_chart(plotly_fig)
        else:
            st.info("No expenses recorded yet.")

    with tab3:
        if not df.empty:
            # Group by Category
            plotly_fig_income = plot_monthly_breakdown(processed_df, "Income")
            st.plotly_chart(plotly_fig_income)
        else:
            st.info("No income recorded yet.")

    with tab4:
        top_expense_categories = plot_top_categories(processed_df, "Expense")
        if top_expense_categories is not None:
            st.plotly_chart(top_expense_categories)
        else:
            st.info("No expenses recorded yet this month.")

    with tab5:
        income_vs_expense_fig = plot_income_vs_expense_trend(processed_df)
        if income_vs_expense_fig is not None:
            st.plotly_chart(income_vs_expense_fig)
        else:
            st.info("No transactions recorded yet this year.")

    # 5. Recent Transactions Table
    st.subheader("📝 Recent Transactions")
    display_df = df.copy()
    display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce")
    st.dataframe(display_df.tail(10).iloc[::-1], width="stretch")  # Show last 10, reversed

    # 6. Yearly Charts
    st.subheader("📈 Yearly Analysis")

    year_tab1, year_tab2, year_tab3 = st.tabs(
        ["Total Expenses", "Income vs Expense", "Expenses by Category"]
    )

    with year_tab1:
        yearly_plotly_fig = plot_expenses_by_year(
            transactions_df=processed_df, years_to_plot=5
        )
        st.plotly_chart(yearly_plotly_fig)

    with year_tab2:
        yearly_income_vs_expense_fig = plot_yearly_income_vs_expense(
            processed_df, years_to_plot=5
        )
        if yearly_income_vs_expense_fig is not None:
            st.plotly_chart(yearly_income_vs_expense_fig)
        else:
            st.info("No transactions recorded yet.")

    with year_tab3:
        yearly_category_fig = plot_yearly_category_breakdown(
            processed_df, data_type="Expense", years_to_plot=5
        )
        if yearly_category_fig is not None:
            st.plotly_chart(yearly_category_fig)
        else:
            st.info("No expenses recorded yet.")

else:
    st.info("No data found. Use the sidebar to add your first expense!")
