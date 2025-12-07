import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import constants as const
from data_processing import process_expense_data


def plot_monthly_expense_breakdown(transactions_df: pd.DataFrame) -> px.bar:
    """Plot monthly expense breakdown using Plotly."""
    month_category = process_expense_data(transactions_df)

    monthly_sum = (
        month_category.groupby("month")
        .agg(monthly_sum=("Amount", lambda x: x.sum().round()))
        .reset_index()
    )

    fig = px.bar(
        month_category,
        x="Amount",
        y="month",
        labels={"month": "Month", "Amount": "Total Expense"},
        color="Category",
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Safe,
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

    fig.update_xaxes(range=[0, 12000])
    fig.add_vline(x=11166, line_dash="dash", line_color="red")

    return fig


def plot_expenses_by_month(
    transactions_df: pd.DataFrame,
    category: str = None,
) -> px.line:
    """Plot expenses by month using Plotly."""
    expense_data = process_expense_data(transactions_df)

    if category:
        expense_data = expense_data[expense_data["Category"] == category]
    else:
        expense_data = expense_data.groupby("month")["Amount"].sum().reset_index()

    fig = px.line(
        expense_data,
        x="month",
        y="Amount",
        labels={"month": "Month", "Amount": "Expense"},
        markers=True,
        text="Amount",
    )

    fig.update_layout(font=dict(family="Arial, sans-serif", size=14, color="black"))
    fig.update_traces(
        line=dict(width=4), marker=dict(size=10), textposition="top center"
    )
    fig.update_xaxes(range=[-0.5, 12.5])

    return fig
