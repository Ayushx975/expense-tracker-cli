# Expense Tracker CLI

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white) ![stdlib only](https://img.shields.io/badge/deps-stdlib_only-blue.svg) ![License MIT](https://img.shields.io/badge/License-MIT-green.svg)

A zero-dependency personal finance CLI in pure Python — track spends, set budgets, get month-end summaries.

Designed for daily terminal use: one command to log an expense, one to see where your money went. Data lives in a local JSON file — no accounts, no cloud, no dependencies.

## Features

- `add` — log an expense (amount, category, note, date defaults to today)
- `list` — filter by category / month / date range
- `summary` — totals per category with percentage bars + budget status
- `budget` — set/view monthly category budgets; warns on overspend
- `export` — dump to CSV for spreadsheets
- ISO-date parsing, safe float handling, friendly errors

## Quick Start

```bash
python tracker.py add 249 food "campus canteen"
python tracker.py add 1200 travel "bus pass" --date 2026-09-01
python tracker.py budget food 3000
python tracker.py list --month 2026-09
python tracker.py summary --month 2026-09
python tracker.py export --out expenses.csv
```

## Sample Output

```
$ python tracker.py summary --month 2026-09

September 2026 spend: Rs. 8,432.00

food        3,860  [############--------]  45.8%  over budget by Rs. 860!
travel      2,800  [########------------]  33.2%  within budget (Rs. 3,000)
misc        1,200  [#####---------------]  14.2%  no budget set
books         572  [###-----------------]   6.8%  no budget set
```

## Data

All expenses are stored in `expenses.json` next to the script:

```json
[{"id": 1, "amount": 249.0, "category": "food", "note": "campus canteen", "date": "2026-09-13"}]
```

## Tech

Python 3.11 | stdlib only (argparse, json, csv, datetime, pathlib)

## License

MIT
