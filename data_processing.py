from datetime import datetime
import pandas as pd

from constants import month_lst


def process_transactions_df(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Process raw transactions data into numeric amounts, parsed dates, and year/month columns.

    Call this once per data load; downstream helpers expect an already-processed
    dataframe rather than re-deriving it themselves.
    """
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


def process_data_by_type(processed_df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """Group already-processed transactions by year/month/category for one type."""
    if processed_df is None or processed_df.empty:
        return None

    data_df = processed_df[processed_df["Type"] == data_type]

    month_category_df = (
        data_df.groupby(["year", "month", "Category"])["Amount"]
        .sum()
        .round()
        .reset_index()
    )

    return month_category_df


def prepare_yearly_expense_data(
    processed_df: pd.DataFrame,
    years_to_plot: int = 5,
) -> pd.DataFrame:
    """Prepare yearly expense data for visualization."""
    if processed_df is None or processed_df.empty:
        return None

    expense_df = processed_df[processed_df["Type"] == "Expense"]

    current_year = pd.Timestamp.now().year
    loockback_year = current_year - years_to_plot + 1
    filtered_expense_df = expense_df.query("year >= @loockback_year")
    yearly_expense = (
        filtered_expense_df.groupby("year")["Amount"].sum().round().reset_index()
    )

    return yearly_expense


def prepare_yearly_income_expense(
    processed_df: pd.DataFrame,
    years_to_plot: int = 5,
) -> pd.DataFrame:
    """Prepare yearly Income vs Expense totals."""
    if processed_df is None or processed_df.empty:
        return None

    current_year = pd.Timestamp.now().year
    loockback_year = current_year - years_to_plot + 1
    filtered_df = processed_df.query("year >= @loockback_year")

    return (
        filtered_df.groupby(["year", "Type"])["Amount"]
        .sum()
        .round()
        .reset_index()
    )


def prepare_yearly_category_breakdown(
    processed_df: pd.DataFrame,
    data_type: str = "Expense",
    years_to_plot: int = 5,
) -> pd.DataFrame:
    """Prepare yearly totals by category for a given transaction type."""
    if processed_df is None or processed_df.empty:
        return None

    current_year = pd.Timestamp.now().year
    loockback_year = current_year - years_to_plot + 1
    type_df = processed_df[processed_df["Type"] == data_type].query(
        "year >= @loockback_year"
    )

    return (
        type_df.groupby(["year", "Category"])["Amount"]
        .sum()
        .round()
        .reset_index()
    )


def prepare_current_month_category_totals(
    processed_df: pd.DataFrame,
    data_type: str = "Expense",
) -> pd.DataFrame:
    """Rank categories by total amount for the current month."""
    if processed_df is None or processed_df.empty:
        return None

    current_year = pd.Timestamp.now().year
    current_month = pd.Timestamp.now().strftime("%b")

    month_df = processed_df.query(
        "Type == @data_type and year == @current_year and month == @current_month"
    )

    return (
        month_df.groupby("Category")["Amount"]
        .sum()
        .round()
        .reset_index()
    )


def prepare_income_expense_trend(processed_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare monthly Income vs Expense totals for the current year."""
    if processed_df is None or processed_df.empty:
        return None

    current_year = pd.Timestamp.now().year
    year_df = processed_df.query("year == @current_year")

    return (
        year_df.groupby(["month", "Type"])["Amount"]
        .sum()
        .round()
        .reset_index()
    )


def calculate_last_month_income(processed_df: pd.DataFrame) -> float:
    """Calculate total income for the last month."""
    processed_income_df = process_data_by_type(processed_df, "Income")

    current_year = datetime.now().year
    current_month = datetime.now().strftime("%b")

    if current_month == "Jan":
        last_month = "Dec"
        year = current_year - 1
    else:
        first_day_this_month = datetime.now().replace(day=1)
        last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
        last_month = last_day_prev_month.strftime("%b")
        year = current_year

    last_month_income = (
        processed_income_df[
            (processed_income_df["year"] == year)
            & (processed_income_df["month"] == last_month)
        ]["Amount"]
        .sum()
        .round()
    )

    return last_month_income


def calculate_current_month_expense(processed_df: pd.DataFrame) -> float:
    """Calculate total expense for the current month."""
    processed_expense_df = process_data_by_type(processed_df, "Expense")
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%b")
    current_month_expense = (
        processed_expense_df[
            (processed_expense_df["year"] == current_year)
            & (processed_expense_df["month"] == current_month)
        ]["Amount"]
        .sum()
        .round()
    )

    return current_month_expense
