import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from constants import month_lst
from data_processing import (
    process_data_by_type,
    prepare_yearly_expense_data,
    prepare_yearly_income_expense,
    prepare_yearly_category_breakdown,
    prepare_current_month_category_totals,
    prepare_income_expense_trend,
)


def plot_monthly_breakdown(transactions_df: pd.DataFrame, data_type: str) -> px.bar:
    """Plot monthly expense breakdown using Plotly."""
    month_category = process_data_by_type(transactions_df, data_type).query(
        "year == @pd.Timestamp.now().year"
    )

    monthly_sum = (
        month_category.groupby("month")
        .agg(monthly_sum=("Amount", lambda x: x.sum().round()))
        .reset_index()
    )

    if data_type == "Expense":
        x_label = "Total Expenses ($)"
    else:
        x_label = "Total Income ($)"

    fig = px.bar(
        month_category,
        x="Amount",
        y="month",
        labels={"month": "Month", "Amount": x_label},
        color="Category",
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Safe,
        category_orders={"month": month_lst},
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_sum["monthly_sum"],
            y=monthly_sum["month"],
            mode="text",
            text=monthly_sum["monthly_sum"],
            textposition="middle right",
            showlegend=False,
        )
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_yaxes(autorange="reversed")

    if data_type == "Expense":
        fig.update_xaxes(range=[0, 12000])
        fig.add_vline(x=11166, line_dash="dash", line_color="red")
    elif data_type == "Income":
        fig.update_xaxes(range=[0, 21000])

    return fig


def plot_expenses_by_month(
    transactions_df: pd.DataFrame,
    category: str = None,
) -> px.line:
    """Plot expenses by month using Plotly."""
    expense_data = process_data_by_type(transactions_df, "Expense").query(
        "year == @pd.Timestamp.now().year"
    )

    if category == "All":
        expense_data = expense_data.groupby("month")["Amount"].sum().reset_index()
    else:
        expense_data = (
            expense_data.query("Category == @category")
            .groupby("month")["Amount"]
            .sum()
            .reset_index()
        )

    fig = px.line(
        expense_data,
        x="month",
        y="Amount",
        labels={"month": "Month", "Amount": "Expenses ($)"},
        markers=True,
        text="Amount",
        category_orders={"month": month_lst}
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_traces(
        line=dict(width=4), marker=dict(size=10), textposition="top center"
    )
    fig.update_xaxes(range=[-0.5, 12.5])

    return fig


def plot_expenses_by_year(
    transactions_df: pd.DataFrame,
    years_to_plot: int = 5,
) -> px.bar:
    """Plot expenses by year using Plotly."""

    yearly_expense = prepare_yearly_expense_data(
        transactions_df, years_to_plot=years_to_plot
    )

    fig = px.bar(
        yearly_expense,
        x="year",
        y="Amount",
        labels={"year": "Year", "Amount": "Total Expenses ($)"},
        text="Amount",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_xaxes(type="category")

    return fig


def plot_yearly_income_vs_expense(
    transactions_df: pd.DataFrame,
    years_to_plot: int = 5,
):
    """Plot yearly Income vs Expense totals as grouped bars.

    Returns None if there is no data in the lookback window.
    """
    yearly_data = prepare_yearly_income_expense(
        transactions_df, years_to_plot=years_to_plot
    )

    if yearly_data is None or yearly_data.empty:
        return None

    fig = px.bar(
        yearly_data,
        x="year",
        y="Amount",
        color="Type",
        barmode="group",
        text="Amount",
        labels={"year": "Year", "Amount": "Amount ($)", "Type": "Type"},
        color_discrete_map={
            "Income": px.colors.qualitative.Safe[0],
            "Expense": px.colors.qualitative.Safe[1],
        },
    )

    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_xaxes(type="category")

    return fig


def plot_yearly_category_breakdown(
    transactions_df: pd.DataFrame,
    data_type: str = "Expense",
    years_to_plot: int = 5,
):
    """Plot yearly totals by category as a stacked bar.

    Returns None if there is no data in the lookback window.
    """
    yearly_category = prepare_yearly_category_breakdown(
        transactions_df, data_type=data_type, years_to_plot=years_to_plot
    )

    if yearly_category is None or yearly_category.empty:
        return None

    yearly_sum = yearly_category.groupby("year")["Amount"].sum().round().reset_index()

    label = "Expenses" if data_type == "Expense" else "Income"

    fig = px.bar(
        yearly_category,
        x="year",
        y="Amount",
        color="Category",
        labels={"year": "Year", "Amount": f"Total {label} ($)"},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.add_trace(
        go.Scatter(
            x=yearly_sum["year"],
            y=yearly_sum["Amount"],
            mode="text",
            text=yearly_sum["Amount"],
            textposition="top center",
            showlegend=False,
        )
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_xaxes(type="category")

    return fig


def plot_top_categories(transactions_df: pd.DataFrame, data_type: str = "Expense"):
    """Plot categories ranked by total amount for the current month.

    Returns None if there is no data for the current month yet.
    """
    category_totals = prepare_current_month_category_totals(
        transactions_df, data_type
    )

    if category_totals is None or category_totals.empty:
        return None

    label = "Expenses" if data_type == "Expense" else "Income"

    fig = px.bar(
        category_totals,
        x="Amount",
        y="Category",
        orientation="h",
        text="Amount",
        labels={"Category": "Category", "Amount": f"{label} This Month ($)"},
        color="Amount",
        color_continuous_scale="Blues",
    )

    fig.update_yaxes(categoryorder="total ascending")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=14, color="black"),
        coloraxis_showscale=False,
    )

    return fig


def plot_income_vs_expense_trend(transactions_df: pd.DataFrame):
    """Plot Income vs Expense trend by month for the current year.

    Returns None if there is no data for the current year yet.
    """
    trend_data = prepare_income_expense_trend(transactions_df)

    if trend_data is None or trend_data.empty:
        return None

    fig = px.line(
        trend_data,
        x="month",
        y="Amount",
        color="Type",
        labels={"month": "Month", "Amount": "Amount ($)", "Type": "Type"},
        markers=True,
        category_orders={"month": month_lst},
        color_discrete_map={
            "Income": px.colors.qualitative.Safe[0],
            "Expense": px.colors.qualitative.Safe[1],
        },
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_traces(line=dict(width=4), marker=dict(size=10))
    fig.update_xaxes(range=[-0.5, 11.5])

    return fig
