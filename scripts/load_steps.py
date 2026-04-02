"""Load and display daily steps totals from Fitbit exported CSV files."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

FITBIT_DIR = Path(__file__).parent.parent / "Fitbit" / "Physical Activity_GoogleData"


def load_daily_steps() -> list[dict]:
    totals: dict[str, int] = defaultdict(int)
    for csv_file in sorted(FITBIT_DIR.glob("steps_*.csv")):
        with csv_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row["timestamp"][:10]  # extract YYYY-MM-DD
                totals[date] += int(row["steps"])

    return [{"date": date, "steps": steps} for date, steps in sorted(totals.items())]


if __name__ == "__main__":
    daily = load_daily_steps()

    if not daily:
        print("No steps data found.")
    else:
        print(f"{'Date':<12} {'Steps':>6}")
        print("-" * 20)
        for row in daily:
            print(f"{row['date']:<12} {row['steps']:>6}")
