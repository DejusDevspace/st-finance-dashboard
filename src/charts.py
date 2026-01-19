from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
        color_discrete_map={"Income": "green", "Expense": "red"},
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
        color="Net",
        color_continuous_scale="aggrnyl"
    )
    return fig


def donut_expense_by_category(cat: pd.DataFrame):
    if cat.empty:
        cat = pd.DataFrame({"Category": [], "Amount": []})

    fig = px.pie(
        cat,
        names="Category",
        values="Amount",
        hole=0.35,
        title="Expenses by Category",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Vivid
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
        color="Amount",
        color_continuous_scale="aggrnyl",
        title="Expenses by Category (Selected)",
    )
    fig.update_layout(yaxis_title="", xaxis_title="")
    return fig


def area_running_balance(df_with_balance: pd.DataFrame):
    if df_with_balance.empty:
        df_with_balance = pd.DataFrame({"Date": [], "RunningBalance": []})

    tmp = df_with_balance.copy()
    tmp["RunningBalance"] = pd.to_numeric(tmp["RunningBalance"], errors="coerce").fillna(0.0)

    y_pos = tmp["RunningBalance"].clip(lower=0)
    y_neg = tmp["RunningBalance"].clip(upper=0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=tmp["Date"],
            y=y_pos,
            mode="lines",
            line=dict(color="green"),
            fill="tozeroy",
            fillcolor="rgba(0,128,0,0.25)",
            name="Balance (positive)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=tmp["Date"],
            y=y_neg,
            mode="lines",
            line=dict(color="red"),
            fill="tozeroy",
            fillcolor="rgba(220,0,0,0.25)",
            name="Balance (negative)",
        )
    )

    fig.update_layout(title="Running Balance", legend_title_text="")
    fig.update_yaxes(zeroline=True, zerolinecolor="rgba(0,0,0,0.25)")
    return fig
