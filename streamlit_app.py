from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.analytics import (
    add_running_balance,
    compare_period_kpis,
    compute_kpis,
    expense_by_category,
    filter_by_date,
    monthly_summary,
    top_expenses,
)
from src.charts import (
    area_running_balance,
    bar_expense_by_category,
    bar_net_cashflow,
    donut_expense_by_category,
    line_income_expense,
)
from src.cleaning import clean_transactions
from src.sheets import load_public_sheet_as_df


APP_TZ = ZoneInfo("Africa/Lagos")


def _format_ngn(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"₦{value:,.2f}"


@st.cache_data(ttl=60)
def load_data(sheet_url: str, tab_name: str) -> pd.DataFrame:
    raw = load_public_sheet_as_df(sheet_url=sheet_url, tab_name=tab_name)
    return clean_transactions(raw)


def main() -> None:
    st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

    st.title("Personal Finance Dashboard")

    with st.sidebar:
        st.header("Data")
        sheet_url = st.text_input(
            "Google Sheets URL",
            value="https://docs.google.com/spreadsheets/d/1nTnLC8MPAxJASRhnYFqWL-sIYlfcrc71Y0MNmtvuRAg/edit?usp=sharing",
        )
        tab_name = st.text_input("Tab name", value="Sheet1")

        if st.button("Refresh data"):
            st.cache_data.clear()

        st.caption(
            "Cache TTL: 60s (auto refresh after expiry). Use 'Refresh data' for instant reload."
        )

    try:
        df_all = load_data(sheet_url=sheet_url, tab_name=tab_name)
    except Exception as e:
        st.error(str(e))
        st.stop()

    if df_all.empty:
        st.warning(
            "No transactions found in the sheet. Add rows to your Google Sheet and refresh."
        )
        st.stop()

    df_all = add_running_balance(df_all)

    st.caption(
        f"Loaded {len(df_all):,} transactions • Last refreshed: {datetime.now(APP_TZ).strftime('%d-%m-%Y %H:%M:%S')}"
    )

    with st.sidebar:
        st.header("Filters")

        min_d = df_all["Date"].min().date()
        max_d = df_all["Date"].max().date()

        today = datetime.now(APP_TZ).date()
        this_month_start = today.replace(day=1)

        preset = st.selectbox(
            "Date range",
            options=["This month", "Last 3 months", "Year to date", "All", "Custom"],
            index=0,
        )

        if preset == "This month":
            start_d, end_d = this_month_start, today
        elif preset == "Last 3 months":
            start_d = (pd.Timestamp(today) - pd.DateOffset(months=3)).date()
            end_d = today
        elif preset == "Year to date":
            start_d, end_d = today.replace(month=1, day=1), today
        elif preset == "All":
            start_d, end_d = min_d, max_d
        else:
            picked = st.date_input("Pick dates", value=(min_d, max_d))
            if isinstance(picked, tuple) and len(picked) == 2:
                start_d, end_d = picked
            else:
                start_d, end_d = min_d, max_d

        type_filter = st.multiselect(
            "Type",
            options=["Income", "Expense"],
            default=["Income", "Expense"],
        )

        categories = sorted(df_all["Category"].dropna().unique().tolist())
        category_filter = st.multiselect("Category", options=categories, default=[])

        search_text = st.text_input("Search description")

    df = df_all.copy()
    df = df[df["Type"].isin(type_filter)]
    df = filter_by_date(df, start_d=start_d, end_d=end_d)

    if category_filter:
        df = df[df["Category"].isin(category_filter)]

    if search_text.strip():
        df = df[df["Description"].str.contains(search_text.strip(), case=False, na=False)]

    if df.empty:
        st.info(
            "No transactions match your filters. Adjust filters (date, category, type) to see results."
        )

    current_balance = float(df_all["RunningBalance"].iloc[-1]) if not df_all.empty else 0.0

    kpis_filtered = compute_kpis(df)
    kpis_all = compute_kpis(df_all)

    comparison = compare_period_kpis(df_all, start_d=start_d, end_d=end_d)
    k_prev = comparison["previous"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current balance (all time)", _format_ngn(current_balance))
    c2.metric(
        "Income (selected)",
        _format_ngn(kpis_filtered["income"]),
        delta=_format_ngn(kpis_filtered["income"] - k_prev["income"]),
    )
    c3.metric(
        "Expense (selected)",
        _format_ngn(kpis_filtered["expense"]),
        delta=_format_ngn(kpis_filtered["expense"] - k_prev["expense"]),
    )
    c4.metric(
        "Net (selected)",
        _format_ngn(kpis_filtered["net"]),
        delta=_format_ngn(kpis_filtered["net"] - k_prev["net"]),
    )
    c5.metric("Savings rate (selected)", f"{kpis_filtered['savings_rate']*100:,.1f}%")

    st.divider()

    tab_overview, tab_categories, tab_transactions = st.tabs(
        ["Overview", "Categories", "Transactions"]
    )

    monthly = monthly_summary(df)
    cat = expense_by_category(df)

    with tab_overview:
        left, right = st.columns([2, 1])
        with left:
            st.plotly_chart(line_income_expense(monthly), use_container_width=True)
            st.plotly_chart(bar_net_cashflow(monthly), use_container_width=True)
        with right:
            st.metric("Income (all time)", _format_ngn(kpis_all["income"]))
            st.metric("Expense (all time)", _format_ngn(kpis_all["expense"]))
            st.plotly_chart(area_running_balance(df_all), use_container_width=True)

    with tab_categories:
        left, right = st.columns([1, 1])
        with left:
            st.plotly_chart(donut_expense_by_category(cat), use_container_width=True)
        with right:
            st.plotly_chart(bar_expense_by_category(cat), use_container_width=True)

        st.subheader("Expense totals by category (selected)")
        cat_table = cat.copy()
        if not cat_table.empty:
            cat_table["Amount"] = cat_table["Amount"].map(_format_ngn)
        st.dataframe(cat_table, use_container_width=True, hide_index=True)

    with tab_transactions:
        st.subheader("Transactions")

        display = df.copy()
        if not display.empty:
            display["Amount"] = display["Amount"].map(_format_ngn)
            display["SignedAmount"] = display["SignedAmount"].map(_format_ngn)
            display["RunningBalance"] = display["RunningBalance"].map(_format_ngn)

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Top expenses (selected)")
        top = top_expenses(df, n=10).copy()
        if top.empty:
            st.info("No expenses in the selected filters.")
        else:
            top["Amount"] = top["Amount"].map(_format_ngn)
            st.dataframe(top, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download selected data (CSV)",
            data=csv,
            file_name="transactions_selected.csv",
        )


if __name__ == "__main__":
    main()
