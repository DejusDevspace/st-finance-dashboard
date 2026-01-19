import re
from io import StringIO

import pandas as pd
import requests


def _extract_sheet_id(sheet_url: str) -> str:
    match = re.search(r"/spreadsheets/d/([^/]+)", sheet_url)
    if not match:
        raise ValueError("Could not extract spreadsheet id from URL")
    return match.group(1)


def build_public_csv_url(sheet_url: str, tab_name: str) -> str:
    sheet_id = _extract_sheet_id(sheet_url)
    return (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={requests.utils.quote(tab_name)}"
    )


def load_public_sheet_as_df(sheet_url: str, tab_name: str) -> pd.DataFrame:
    csv_url = build_public_csv_url(sheet_url=sheet_url, tab_name=tab_name)
    resp = requests.get(csv_url, timeout=30)
    resp.raise_for_status()
    # print("\n\n--------------- RESPONSE ---------------\n\n", resp.text)
    # print("\n\n--------------- DF VALUES ---------------\n\n", pd.read_csv(StringIO(resp.text)).values)[:, 5:]
    return pd.read_csv(StringIO(resp.text))
