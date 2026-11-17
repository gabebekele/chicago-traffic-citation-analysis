
USE chicago_citations_jan2021;


-- Check table counts

SELECT 'Tickets' AS table_name, COUNT(*) AS records
FROM Tickets
UNION ALL
SELECT 'Violations', COUNT(*) FROM Violations
UNION ALL
SELECT 'Financials', COUNT(*) FROM Financials
UNION ALL
SELECT 'Notices', COUNT(*) FROM Notices
UNION ALL
SELECT 'Hearings', COUNT(*) FROM Hearings;


-- Check dataset coverage

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT Ticket_number) AS unique_tickets,
    MIN(Issue_date) AS earliest_record,
    MAX(Issue_date) AS latest_record,
    COUNT(DISTINCT DATE(Issue_date)) AS days_recorded
FROM Tickets;


-- Check citation status distribution

SELECT
    Ticket_Queue,
    COUNT(*) AS total_records
FROM Tickets
GROUP BY Ticket_Queue
ORDER BY total_records DESC;


-- Check financial totals

SELECT
    COUNT(*) AS total_records,
    ROUND(SUM(Total_Payments), 2) AS total_payments,
    ROUND(SUM(Current_Amount_Due), 2) AS net_balance,
    ROUND(SUM(CASE
        WHEN Current_Amount_Due > 0
            THEN Current_Amount_Due
        ELSE 0
    END), 2) AS positive_outstanding_balance,
    SUM(Current_Amount_Due < 0) AS negative_balance_records,
    SUM(Current_Amount_Due > 0) AS positive_balance_records,
    SUM(Current_Amount_Due IS NULL) AS missing_balances,
    SUM(Total_Payments IS NULL) AS missing_payments
FROM Financials;


-- Check for missing required relationships

SELECT
    SUM(v.Ticket_number IS NULL) AS missing_violations,
    SUM(f.Ticket_number IS NULL) AS missing_financials
FROM Tickets t
LEFT JOIN Violations v
    ON t.Ticket_number = v.Ticket_number
LEFT JOIN Financials f
    ON t.Ticket_number = f.Ticket_number;


-- Confirm analytical views contain all expected records

SELECT
    'Vehicle make' AS analysis,
    SUM(ticket_count) AS records
FROM tickets_by_vehicle_make

UNION ALL

SELECT
    'Daily activity',
    SUM(total_citations)
FROM daily_citation_activity

UNION ALL

SELECT
    'Hourly activity',
    SUM(total_citations)
FROM hourly_citation_activity

UNION ALL

SELECT
    'Weekday and weekend activity',
    SUM(total_citations)
FROM weekday_weekend_activity

UNION ALL

SELECT
    'Violation frequency',
    SUM(total_records)
FROM violation_frequency

UNION ALL

SELECT
    'Financial status',
    SUM(total_records)
FROM financial_summary_by_status

UNION ALL

SELECT
    'Violation financials',
    SUM(total_records)
FROM violation_financial_summary;


-- Reconcile financial results across views

SELECT
    'Financial summary by status' AS analysis,
    SUM(total_payments) AS total_payments,
    SUM(positive_outstanding_balance) AS positive_balances,
    SUM(net_balance) AS net_balance
FROM financial_summary_by_status

UNION ALL

SELECT
    'Financial summary by violation',
    SUM(total_payments),
    SUM(positive_outstanding_balance),
    SUM(net_balance)
FROM violation_financial_summary;
