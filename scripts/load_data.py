
import csv
import mysql.connector
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from getpass import getpass

file_path = Path("data/raw/FOIA_Sanchez_A50952_20210615_Year_2021.txt")
BATCH_SIZE = 1000


def save_batch(cursor, connection, tickets, violations,
               financials, notices, hearings):

    # Insert the main tickets first
    cursor.executemany("""
        INSERT INTO Tickets (
            Ticket_number, Issue_date, Zip_code,
            Ticket_Queue, Ticket_Queue_Date,
            Officer, Unit, Unit_description,
            Vehicle_Make, License_Plate_Type
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tickets)

    cursor.executemany("""
        INSERT INTO Violations (
            Ticket_number, Violation_Code,
            Violation_description, Violation_Location
        )
        VALUES (%s, %s, %s, %s)
    """, violations)

    cursor.executemany("""
        INSERT INTO Financials (
            Ticket_number, Fine_Level_1_Amount,
            Fine_Level_2_Amount, Current_Amount_Due,
            Total_Payments
        )
        VALUES (%s, %s, %s, %s, %s)
    """, financials)

    if notices:
        cursor.executemany("""
            INSERT INTO Notices (
                Ticket_number, Notice_Number, Notice_Level
            )
            VALUES (%s, %s, %s)
        """, notices)

    if hearings:
        cursor.executemany("""
            INSERT INTO Hearings (
                Ticket_number, Hearing_Dispo, Hearing_Reason
            )
            VALUES (%s, %s, %s)
        """, hearings)

    connection.commit()


def load_data():

    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="chicago_loader",
        password=getpass("MySQL password: "),
        database="chicago_citations_jan2021"
    )

    cursor = connection.cursor()

    tickets = []
    violations = []
    financials = []
    notices = []
    hearings = []

    count = 0

    try:
        cursor.execute("SELECT COUNT(*) FROM Tickets")

        if cursor.fetchone()[0] > 0:
            raise ValueError("Tickets table must be empty before importing.")

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter="$")

            for row in reader:
                date = row.get("Issue Date") or ""

                # Keep January 2021 records
                if not date.startswith("01/") or "/2021" not in date:
                    continue

                ticket_number = int(row["Ticket Number"])

                issue_date = datetime.strptime(
                    date, "%m/%d/%Y %I:%M %p"
                )

                queue_date = None
                if row["Ticket Queue Date"]:
                    queue_date = datetime.strptime(
                        row["Ticket Queue Date"], "%m/%d/%Y"
                    ).date()

                # Ticket information
                tickets.append((
                    ticket_number,
                    issue_date,
                    row["Zip Code"] or None,
                    row["Ticket Queue"],
                    queue_date,
                    row["Officer"],
                    row["Unit"],
                    row["Unit Description"],
                    row["Vehicle Make"],
                    row["License Plate Type"]
                ))

                # Violation information
                violations.append((
                    ticket_number,
                    row["Violation Code"],
                    row["Violation Description"],
                    row["Violation Location"]
                ))

                # Financial information
                financials.append((
                    ticket_number,
                    Decimal(row["Fine Level 1 Amount"]),
                    Decimal(row["Fine Level 2 Amount"]),
                    Decimal(row["Current Amount Due"]),
                    Decimal(row["Total Payments"])
                ))

                # Notice information
                notice_number = (row["Notice Number"] or "").strip()
                notice_level = (row["Notice Level"] or "").strip()

                if notice_number and notice_number != "0":
                    notices.append((
                        ticket_number,
                        notice_number,
                        notice_level or None
                    ))

                # Hearing information
                hearing_dispo = (row["Hearing Dispo"] or "").strip()
                hearing_reason = (row["Hearing Reason"] or "").strip()

                if hearing_dispo or hearing_reason:
                    hearings.append((
                        ticket_number,
                        hearing_dispo or None,
                        hearing_reason or None
                    ))

                count += 1

                # Insert every 1,000 tickets
                if len(tickets) == BATCH_SIZE:
                    save_batch(cursor, connection, tickets,
                               violations, financials, notices, hearings)

                    print(f"Inserted {count:,} tickets")

                    tickets.clear()
                    violations.clear()
                    financials.clear()
                    notices.clear()
                    hearings.clear()

        # Insert any remaining records
        if tickets:
            save_batch(cursor, connection, tickets,
                       violations, financials, notices, hearings)

        print(f"\nFinished! Total tickets inserted: {count:,}")

    except Exception:
        connection.rollback()
        print(f"Import stopped after processing {count:,} records.")
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_data()