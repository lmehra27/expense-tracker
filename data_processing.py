from datetime import datetime
import pandas as pd

from constants import month_lst


def process_transactions_df(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Process transactions data."""
    if transactions_df.empty:
        return None

    transactions_df["Amount"] = pd.to_numeric(transactions_df["Amount"])
    transactions_df["Date"] = pd.to_datetime(transactions_df["Date"])

    transactions_df = transactions_df.assign(
        year=transactions_df["Date"].dt.year,
        month=transactions_df["Date"].dt.strftime("%b"),
    )

    transactions_df["month"] = pd.Categorical(
        transactions_df["month"], categories=month_lst, ordered=True
    )

    return transactions_df


def calculate_last_month_income(transactions_df: pd.DataFrame) -> float:
    """Calculate total income for the last month."""
    processed_transactions_df = process_transactions_df(transactions_df)

    current_year = datetime.now().year
    current_month = datetime.now().strftime("%b")

    if current_month == "Jan":
        last_month = ("Dec",)
        year = current_year - 1
    else:
        first_day_this_month = datetime.now().replace(day=1)
        last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
        last_month = last_day_prev_month.strftime("%b")
        year = current_year

    last_month_income = (
        processed_transactions_df[
            (processed_transactions_df["Type"] == "Income")
            & (processed_transactions_df["year"] == year)
            & (processed_transactions_df["month"] == last_month)
        ]["Amount"]
        .sum()
        .round()
    )

    return last_month_income


def calculate_current_month_expense(transactions_df: pd.DataFrame) -> float:
    """Calculate total expense for the current month."""
    processed_transactions_df = process_transactions_df(transactions_df)
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%b")
    current_month_expense = (
        processed_transactions_df[
            (processed_transactions_df["Type"] == "Expense")
            & (processed_transactions_df["year"] == current_year)
            & (processed_transactions_df["month"] == current_month)
        ]["Amount"]
        .sum()
        .round()
    )

    return current_month_expense
