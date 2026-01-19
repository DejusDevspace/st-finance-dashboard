from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = ["Date", "Type", "Category", "Description", "Amount"]


def _norm_col(col: object) -> str:
    return str(col).strip().lower()


def clean_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed", na=False)].copy()

    norm_to_original: dict[str, str] = {}
    for c in df.columns:
        key = _norm_col(c)
        if key not in norm_to_original:
            norm_to_original[key] = c

    selected_original_cols: list[str] = []
    rename_map: dict[str, str] = {}
    missing: list[str] = []
    for req in REQUIRED_COLUMNS:
        key = _norm_col(req)
        if key in norm_to_original:
            orig = norm_to_original[key]
            selected_original_cols.append(orig)
            rename_map[orig] = req
        else:
            missing.append(req)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
            + ". Found columns: "
            + ", ".join([str(c) for c in raw.columns])
        )

    df = df[selected_original_cols].rename(columns=rename_map).copy()

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all", subset=REQUIRED_COLUMNS).copy()

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    if df["Date"].isna().any():
        bad_rows = df[df["Date"].isna()].head(5)
        raise ValueError(
            "Some dates could not be parsed with DD-MM-YYYY. Example rows: "
            + bad_rows.to_json(orient="records")
        )

    df["Type"] = df["Type"].fillna("").astype(str).str.strip().str.lower()
    df["Category"] = df["Category"].fillna("").astype(str).str.strip()
    df["Description"] = df["Description"].fillna("").astype(str).str.strip()

    amt = df["Amount"].astype(str).str.replace("₦", "", regex=False).str.replace(",", "", regex=False).str.strip()
    df["Amount"] = pd.to_numeric(amt, errors="coerce")
    if df["Amount"].isna().any():
        bad_rows = df[df["Amount"].isna()].head(5)
        raise ValueError(
            "Some amounts could not be parsed as numbers. Example rows: "
            + bad_rows.to_json(orient="records")
        )

    df["Type"] = df["Type"].replace(
        {
            "income": "Income",
            "expense": "Expense",
        }
    )

    valid_types = {"Income", "Expense"}
    invalid = sorted(set(df["Type"]) - valid_types)
    if invalid:
        raise ValueError(
            "Invalid Type values found: "
            + ", ".join(invalid)
            + ". Expected 'Income' or 'Expense'."
        )

    df["SignedAmount"] = df["Amount"].where(df["Type"] == "Income", -df["Amount"])

    df = df.sort_values("Date", ascending=True).reset_index(drop=True)
    return df
