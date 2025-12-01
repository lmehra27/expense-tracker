import pandas as pd
import plotly.express as px


def plot_monthly_breakdown(expense_df):
    """Plot monthly expense breakdown using Plotly."""
    if expense_df.empty:
        return None

    expense_df["Date"] = pd.to_datetime(expense_df["Date"])

    current_year_df = (
        expense_df
        .assign(
            year=expense_df["Date"].dt.year,
            month=expense_df["Date"].dt.strftime("%b"),
            )
        .query("year == @pd.Timestamp.now().year")
    )

    month_lst = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_year_df["month"] = pd.Categorical(
        current_year_df["month"], categories=month_lst, ordered=True
    )

    month_category = (
        current_year_df.groupby(
            ["month", "Category"]
        )["Amount"]
        .sum()
        .reset_index()
    )

    monthly_sum = month_category.groupby("month").agg(
        monthly_sum=("Amount", "sum")   
    ).reset_index()

    month_category = month_category.merge(
        monthly_sum, on="month", how="left"
    )    

    fig = px.bar(  
        month_category,
        x="Amount",
        y="month",
        labels={"month": "Month", "Amount": "Total Expense"},
        color="Category",
        orientation="h",
        text="monthly_sum",)
    
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    return fig
