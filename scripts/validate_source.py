
import csv
from pathlib import Path
from decimal import Decimal

file_path = Path("data/raw/FOIA_Sanchez_A50952_20210615_Year_2021.txt")

count = 0
warnings = 0
positive_records = 0
negative_records = 0

total_payments = Decimal("0")
net_balance = Decimal("0")
positive_balance = Decimal("0")

with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file, delimiter="$")

    for row in reader:
        date = row.get("Issue Date") or ""

        # Only include January 2021
        if not date.startswith("01/") or "/2021" not in date:
            continue

        count += 1

        payments = Decimal(row["Total Payments"])
        balance = Decimal(row["Current Amount Due"])

        total_payments += payments
        net_balance += balance

        if balance > 0:
            positive_balance += balance
            positive_records += 1

        elif balance < 0:
            negative_records += 1

        if row["Ticket Queue"] == "Warning":
            warnings += 1

print(f"Total records: {count:,}")
print(f"Warnings: {warnings:,}")
print(f"Total payments: ${total_payments:,.2f}")
print(f"Net balance: ${net_balance:,.2f}")
print(f"Positive balances: ${positive_balance:,.2f}")
print(f"Positive balance records: {positive_records:,}")
print(f"Negative balance records: {negative_records:,}")
