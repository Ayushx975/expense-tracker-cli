"""Expense Tracker CLI - pure stdlib personal finance tracker."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB = Path(__file__).parent / "expenses.json"


def load() -> list[dict]:
    if not DB.exists():
        return []
    with open(DB, encoding="utf-8") as f:
        return json.load(f)


def save(rows: list[dict]) -> None:
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def next_id(rows: list[dict]) -> int:
    return max((r["id"] for r in rows), default=0) + 1


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def cmd_add(args) -> None:
    rows = load()
    try:
        amount = round(float(args.amount), 2)
    except ValueError:
        sys.exit("error: amount must be a number, e.g. 249.50")
    if amount <= 0:
        sys.exit("error: amount must be positive")
    d = parse_date(args.date) if args.date else date.today()
    rows.append({
        "id": next_id(rows),
        "amount": amount,
        "category": args.category.strip().lower() or "misc",
        "note": args.note or "",
        "date": d.isoformat(),
    })
    save(rows)
    print(f"added Rs. {amount:.2f} to '{rows[-1]['category']}' on {d.isoformat()}")


def in_month(r: dict, month: str) -> bool:
    return r["date"].startswith(month)


def cmd_list(args) -> None:
    rows = load()
    if args.category:
        rows = [r for r in rows if r["category"] == args.category.strip().lower()]
    if args.month:
        rows = [r for r in rows if in_month(r, args.month)]
    if not rows:
        print("no expenses found (adjust filters?)")
        return
    total = 0.0
    print(f"{'ID':>4}  {'Date':<11}{'Category':<12}{'Amount':>10}  Note")
    for r in rows:
        total += r["amount"]
        print(f"{r['id']:>4}  {r['date']:<11}{r['category']:<12}{r['amount']:>10.2f}  {r['note']}")
    print(f"\n{len(rows)} expenses, total Rs. {total:.2f}")


def cmd_summary(args) -> None:
    rows = load()
    if args.month:
        rows = [r for r in rows if in_month(r, args.month)]
        label = args.month
    else:
        label = "all time"
    if not rows:
        print(f"no expenses for {label}")
        return

    budgets = load_budgets()
    totals: dict[str, float] = {}
    for r in rows:
        totals[r["category"]] = totals.get(r["category"], 0.0) + r["amount"]

    grand = sum(totals.values())
    print(f"\n{label} spend: Rs. {grand:,.2f}\n")
    for cat, amt in sorted(totals.items(), key=lambda kv: -kv[1]):
        pct = amt / grand
        bar = "#" * int(pct * 20)
        bud = budgets.get(cat)
        if bud is None:
            status = "no budget set"
        elif amt > bud:
            status = f"over budget by Rs. {amt - bud:,.2f}!"
        else:
            status = f"within budget (Rs. {bud:,.2f})"
        print(f"{cat:<12}{amt:>9,.2f}  [{bar:<20}] {pct:5.1%}  {status}")


BUDGETS = Path(__file__).parent / "budgets.json"


def load_budgets() -> dict[str, float]:
    if not BUDGETS.exists():
        return {}
    with open(BUDGETS, encoding="utf-8") as f:
        return json.load(f)


def cmd_budget(args) -> None:
    budgets = load_budgets()
    if not args.category:
        if not budgets:
            print("no budgets set. usage: budget food 3000")
            return
        for cat, amt in sorted(budgets.items()):
            print(f"{cat:<12}Rs. {amt:,.2f}")
        return
    cat = args.category.strip().lower()
    if args.amount is None:
        print(f"{cat:<12}Rs. {budgets.get(cat, 0):,.2f}")
        return
    try:
        amt = round(float(args.amount), 2)
    except ValueError:
        sys.exit("error: budget must be a number")
    if amt <= 0:
        sys.exit("error: budget must be positive")
    budgets[cat] = amt
    with open(BUDGETS, "w", encoding="utf-8") as f:
        json.dump(budgets, f, indent=2)
    print(f"budget for '{cat}' set to Rs. {amt:,.2f}")


def cmd_export(args) -> None:
    rows = load()
    if not rows:
        sys.exit("nothing to export")
    out = Path(args.out)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"exported {len(rows)} expenses to {out}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="tracker", description="zero-dependency expense tracker")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="log an expense")
    p.add_argument("amount")
    p.add_argument("category")
    p.add_argument("note", nargs="?")
    p.add_argument("--date", help="YYYY-MM-DD (default today)")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("list", help="list expenses")
    p.add_argument("--category")
    p.add_argument("--month", help="YYYY-MM")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("summary", help="category totals + budget status")
    p.add_argument("--month", help="YYYY-MM")
    p.set_defaults(fn=cmd_summary)

    p = sub.add_parser("budget", help="set or view budgets")
    p.add_argument("category", nargs="?")
    p.add_argument("amount", nargs="?")
    p.set_defaults(fn=cmd_budget)

    p = sub.add_parser("export", help="export to CSV")
    p.add_argument("--out", default="expenses.csv")
    p.set_defaults(fn=cmd_export)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
