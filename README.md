# Personal Finance Dashboard (Streamlit)

This project is a Streamlit dashboard that loads your transactions from a **public Google Sheet** (real-time) and visualizes income, expenses, categories, and running balance.

## Expected Google Sheet columns

- `Date` (DD-MM-YYYY)
- `Type` (`Income` or `Expense`)
- `Category`
- `Description`
- `Amount` (number; commas are allowed)

## Run locally

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Start the app

```bash
streamlit run streamlit_app.py
```

## Notes

- Data is cached for 60 seconds for speed. Use the **Refresh data** button in the sidebar to reload instantly.
- If you later want private-sheet access (recommended for personal finances), we can switch to Google Sheets API + service account.
