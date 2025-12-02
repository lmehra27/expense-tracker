import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_monthly_breakdown(expense_df):
    """Plot monthly expense breakdown using Plotly."""
    if expense_df.empty:
        return None

    expense_df["Date"] = pd.to_datetime(expense_df["Date"])

    current_year_df = expense_df.assign(
        year=expense_df["Date"].dt.year,
        month=expense_df["Date"].dt.strftime("%b"),
    ).query("year == @pd.Timestamp.now().year")

    month_lst = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    current_year_df["month"] = pd.Categorical(
        current_year_df["month"], categories=month_lst, ordered=True
    )

    month_category = (
        current_year_df.groupby(["month", "Category"])["Amount"].sum().reset_index()
    )

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
