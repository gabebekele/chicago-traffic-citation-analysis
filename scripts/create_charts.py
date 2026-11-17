
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.ticker import FuncFormatter
from pathlib import Path
from getpass import getpass
from textwrap import fill


output_dir = Path(__file__).resolve().parents[1] / "reports" / "figures"
output_dir.mkdir(parents=True, exist_ok=True)


# Save and close a completed chart
def save_chart(filename):
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300)
    plt.close()

    print(f"Saved: {filename}")


# Format financial values in millions
def format_money(value, position):
    return f"${value / 1000000:.1f}M"


# Chart 1: Daily citation activity
def daily_activity(cursor):

    cursor.execute("""
        SELECT citation_date, total_citations, warnings
        FROM daily_citation_activity
        ORDER BY citation_date
    """)

    rows = cursor.fetchall()

    dates = []
    totals = []
    warnings = []

    for row in rows:
        dates.append(row[0])
        totals.append(int(row[1]))
        warnings.append(int(row[2]))

    plt.figure(figsize=(12, 6))

    plt.plot(dates, totals, marker="o", label="Total records")
    plt.plot(dates, warnings, marker="o", label="Warnings")

    plt.title("Daily Traffic Citation Activity - January 2021")
    plt.xlabel("Date")
    plt.ylabel("Number of Records")

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    plt.xticks(rotation=45)
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid(axis="y", alpha=0.2)

    save_chart("daily_activity.png")


# Chart 2: Hourly citation activity
def hourly_activity(cursor):

    cursor.execute("""
        SELECT hour_of_day, non_warnings, warnings, unknown_status
        FROM hourly_citation_activity
        ORDER BY hour_of_day
    """)

    rows = cursor.fetchall()

    hours = []
    non_warnings = []
    warnings = []
    unknown = []

    for row in rows:
        hours.append(row[0])
        non_warnings.append(int(row[1]))
        warnings.append(int(row[2]))
        unknown.append(int(row[3]))

    plt.figure(figsize=(12, 6))

    plt.bar(hours, non_warnings, label="Non-warning records")

    plt.bar(
        hours,
        warnings,
        bottom=non_warnings,
        label="Warnings"
    )

    if any(unknown):
        bottom = []

        for i in range(len(hours)):
            bottom.append(non_warnings[i] + warnings[i])

        plt.bar(
            hours,
            unknown,
            bottom=bottom,
            label="Unknown status"
        )

    plt.title("Hourly Traffic Citation Activity - January 2021")
    plt.xlabel("Hour of Day (24-Hour Format)")
    plt.ylabel("Number of Records")

    plt.xticks(range(24))
    plt.legend()
    plt.grid(axis="y", alpha=0.2)

    save_chart("hourly_activity.png")


# Chart 3: Weekday vs. weekend activity
def weekday_weekend(cursor):

    cursor.execute("""
        SELECT day_type, avg_daily_citations
        FROM weekday_weekend_activity
        ORDER BY day_type
    """)

    rows = cursor.fetchall()

    day_types = []
    averages = []

    for row in rows:
        day_types.append(row[0])
        averages.append(float(row[1]))

    plt.figure(figsize=(8, 6))

    bars = plt.bar(day_types, averages, width=0.5)

    labels = []

    for value in averages:
        labels.append(f"{value:,.0f}")

    plt.bar_label(bars, labels=labels, padding=5)

    plt.title("Average Daily Citations: Weekdays vs. Weekends")
    plt.xlabel("Day Type")
    plt.ylabel("Average Daily Records")

    plt.ylim(0, max(averages) * 1.15)
    plt.grid(axis="y", alpha=0.2)

    save_chart("weekday_weekend.png")


# Chart 4: Most frequent violations
def top_violations(cursor):

    cursor.execute("""
        SELECT violation_description, total_records
        FROM violation_frequency
        ORDER BY total_records DESC, violation_code
        LIMIT 10
    """)

    rows = cursor.fetchall()

    violations = []
    counts = []

    for row in rows:
        violations.append(fill(row[0] or "Unknown", 35))
        counts.append(int(row[1]))

    plt.figure(figsize=(12, 8))

    bars = plt.barh(range(len(violations)), counts)

    plt.yticks(range(len(violations)), violations)
    plt.gca().invert_yaxis()

    labels = []

    for count in counts:
        labels.append(f"{count:,}")

    plt.bar_label(bars, labels=labels, padding=5)

    plt.title("Top 10 Traffic Violation Categories - January 2021")
    plt.xlabel("Number of Records")

    plt.xlim(0, max(counts) * 1.2)
    plt.grid(axis="x", alpha=0.2)

    save_chart("top_violations.png")


# Chart 5: Outstanding balances by violation
def outstanding_balances(cursor):

    cursor.execute("""
        SELECT
            violation_description,
            positive_outstanding_balance
        FROM violation_financial_summary
        ORDER BY positive_outstanding_balance DESC, violation_code
        LIMIT 10
    """)

    rows = cursor.fetchall()

    violations = []
    balances = []

    for row in rows:
        violations.append(fill(row[0] or "Unknown", 35))
        balances.append(float(row[1]))

    plt.figure(figsize=(12, 8))

    bars = plt.barh(range(len(violations)), balances)

    plt.yticks(range(len(violations)), violations)
    plt.gca().invert_yaxis()

    labels = []

    for balance in balances:
        labels.append(f"${balance:,.0f}")

    plt.bar_label(bars, labels=labels, padding=5)

    plt.title("Highest Outstanding Balances by Violation")
    plt.xlabel("Positive Outstanding Balance (USD)")

    plt.gca().xaxis.set_major_formatter(
        FuncFormatter(format_money)
    )

    plt.xlim(0, max(balances) * 1.3)
    plt.grid(axis="x", alpha=0.2)

    save_chart("outstanding_by_violation.png")


# Chart 6: Payments and outstanding balances by status
def financial_activity(cursor):

    cursor.execute("""
        SELECT
            ticket_status,
            total_payments,
            positive_outstanding_balance
        FROM financial_summary_by_status
        ORDER BY total_records DESC
    """)

    rows = cursor.fetchall()

    statuses = []
    payments = []
    balances = []

    for row in rows:
        statuses.append(row[0] or "Unknown")
        payments.append(float(row[1]))
        balances.append(float(row[2]))

    width = 0.35

    positions = []
    payment_positions = []
    balance_positions = []

    for i in range(len(statuses)):
        positions.append(i)
        payment_positions.append(i - width / 2)
        balance_positions.append(i + width / 2)

    plt.figure(figsize=(12, 6))

    plt.bar(
        payment_positions,
        payments,
        width=width,
        label="Total Payments"
    )

    plt.bar(
        balance_positions,
        balances,
        width=width,
        label="Positive Outstanding Balances"
    )

    plt.title("Payments and Outstanding Balances by Ticket Status")
    plt.xlabel("Ticket Status")
    plt.ylabel("Amount (USD)")

    plt.xticks(positions, statuses, rotation=30)

    plt.gca().yaxis.set_major_formatter(
        FuncFormatter(format_money)
    )

    plt.legend()
    plt.grid(axis="y", alpha=0.2)

    save_chart("financial_activity.png")


# Connect to MySQL and generate all six charts
def main():

    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="chicago_loader",
        password=getpass("MySQL password: "),
        database="chicago_citations_jan2021"
    )

    cursor = connection.cursor()

    try:
        daily_activity(cursor)
        hourly_activity(cursor)
        weekday_weekend(cursor)
        top_violations(cursor)
        outstanding_balances(cursor)
        financial_activity(cursor)

        print("\nAll charts generated successfully!")
        print(f"Output directory: {output_dir}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
