
import csv
from collections import Counter
from pathlib import Path

file_path = Path("data/raw/FOIA_Sanchez_A50952_20210615_Year_2021.txt")

monthly_counts = Counter()
total_rows = 0
missing_dates = 0
invalid_dates = 0
problem_lines = []

with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file, delimiter="$", quotechar='"')

    for row in reader:
        total_rows += 1

        issue_date = row.get("Issue Date")

        # Skip rows with missing issue dates
        if not issue_date or not issue_date.strip():
            missing_dates += 1
            if len(problem_lines) < 5:
                problem_lines.append(reader.line_num)
            continue

        # Extract month and year
        try:
            date = issue_date.strip().split()[0]
            month, day, year = date.split("/")

            month_num = int(month)
            year_num = int(year)

            if not 1 <= month_num <= 12:
                raise ValueError("Invalid month")

            monthly_counts[f"{year_num}-{month_num:02d}"] += 1

        except (ValueError, IndexError):
            invalid_dates += 1
            if len(problem_lines) < 5:
                problem_lines.append(reader.line_num)

print("\nRecords by month:")
for month, count in sorted(monthly_counts.items()):
    print(f"{month}: {count:,}")

print("\nData Quality Summary:")
print(f"Total rows read: {total_rows:,}")
print(f"Valid dated rows: {sum(monthly_counts.values()):,}")
print(f"Missing issue dates: {missing_dates:,}")
print(f"Invalid issue dates: {invalid_dates:,}")
print(f"Example problematic line numbers: {problem_lines}")
