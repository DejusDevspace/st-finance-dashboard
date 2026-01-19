from __future__ import annotations

import pandas as pd


def add_running_balance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        out["RunningBalance"] = pd.Series(dtype="float64")
        return out

    out["RunningBalance"] = out["SignedAmount"].cumsum()
    return out


def compute_kpis(df: pd.DataFrame) -> dict:
    income = float(df.loc[df["Type"] == "Income", "Amount"].sum())
    expense = float(df.loc[df["Type"] == "Expense", "Amount"].sum())
    net = income - expense
    savings_rate = (net / income) if income else 0.0

    return {
        "income": income,
        "expense": expense,
        "net": net,
        "savings_rate": savings_rate,
    }


def filter_by_date(df: pd.DataFrame, start_d, end_d) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    return df[(df["Date"].dt.date >= start_d) & (df["Date"].dt.date <= end_d)].copy()


def compare_period_kpis(df_all: pd.DataFrame, start_d, end_d) -> dict:
    current = filter_by_date(df_all, start_d=start_d, end_d=end_d)
    k_current = compute_kpis(current)

    days = (pd.Timestamp(end_d) - pd.Timestamp(start_d)).days + 1
    prev_end = (pd.Timestamp(start_d) - pd.Timedelta(days=1)).date()
    prev_start = (pd.Timestamp(prev_end) - pd.Timedelta(days=days - 1)).date()

    prev = filter_by_date(df_all, start_d=prev_start, end_d=prev_end)
    k_prev = compute_kpis(prev)

    return {
        "current": k_current,
        "previous": k_prev,
        "prev_range": (prev_start, prev_end),
    }


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame({"Month": [], "Income": [], "Expense": [], "Net": []})

    tmp = df.copy()
    tmp["Month"] = tmp["Date"].dt.to_period("M").dt.to_timestamp()

    grouped = (
        tmp.groupby(["Month", "Type"], as_index=False)["Amount"]
        .sum()
        .pivot(index="Month", columns="Type", values="Amount")
        .fillna(0.0)
        .reset_index()
    )

    if "Income" not in grouped.columns:
        grouped["Income"] = 0.0
    if "Expense" not in grouped.columns:
        grouped["Expense"] = 0.0

    grouped["Net"] = grouped["Income"] - grouped["Expense"]
    return grouped.sort_values("Month", ascending=True)


def expense_by_category(df: pd.DataFrame) -> pd.DataFrame:
    exp = df[df["Type"] == "Expense"].copy()
    if exp.empty:
        return pd.DataFrame({"Category": [], "Amount": []})

    return (
        exp.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )


def top_expenses(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    exp = df[df["Type"] == "Expense"].copy()
    if exp.empty:
        return exp

    return exp.sort_values("Amount", ascending=False).head(n)
