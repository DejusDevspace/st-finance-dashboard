from __future__ import annotations

import pandas as pd
import plotly.express as px


def line_income_expense(monthly: pd.DataFrame):
    if monthly.empty:
        monthly = pd.DataFrame({"Month": [], "Income": [], "Expense": []})

    long_df = monthly.melt(
        id_vars=["Month"],
        value_vars=["Income", "Expense"],
        var_name="Type",
        value_name="Amount",
    )

    fig = px.line(
        long_df,
        x="Month",
        y="Amount",
        color="Type",
        markers=True,
        title="Income vs Expense (Monthly)",
    )
    fig.update_layout(legend_title_text="")
    return fig


def bar_net_cashflow(monthly: pd.DataFrame):
    if monthly.empty:
        monthly = pd.DataFrame({"Month": [], "Net": []})

    fig = px.bar(
        monthly,
        x="Month",
        y="Net",
        title="Net Cashflow (Monthly)",
    )
    return fig


def donut_expense_by_category(cat: pd.DataFrame):
    if cat.empty:
        cat = pd.DataFrame({"Category": [], "Amount": []})

    fig = px.pie(
        cat,
        names="Category",
        values="Amount",
        hole=0.5,
        title="Expenses by Category",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def bar_expense_by_category(cat: pd.DataFrame):
    if cat.empty:
        cat = pd.DataFrame({"Category": [], "Amount": []})

    fig = px.bar(
        cat.sort_values("Amount", ascending=True),
        x="Amount",
        y="Category",
        orientation="h",
        title="Expenses by Category (Selected)",
    )
    fig.update_layout(yaxis_title="", xaxis_title="")
    return fig


def area_running_balance(df_with_balance: pd.DataFrame):
    if df_with_balance.empty:
        df_with_balance = pd.DataFrame({"Date": [], "RunningBalance": []})

    fig = px.area(
        df_with_balance,
        x="Date",
        y="RunningBalance",
        title="Running Balance",
    )
    return fig
