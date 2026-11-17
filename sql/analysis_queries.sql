
USE chicago_citations_jan2021;


-- =====================================================
-- Query 1: Citations by vehicle manufacturer
-- =====================================================

CREATE OR REPLACE VIEW tickets_by_vehicle_make AS
SELECT
    Vehicle_Make AS vehicle_make,
    COUNT(*) AS ticket_count
FROM Tickets
GROUP BY Vehicle_Make;

SELECT *
FROM tickets_by_vehicle_make
ORDER BY ticket_count DESC, vehicle_make;

-- Check vehicle data quality
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT Vehicle_Make) AS unique_vehicle_makes,
    SUM(Vehicle_Make = 'OTHR') AS other_vehicle_records,
    SUM(Vehicle_Make IS NULL OR Vehicle_Make = '')
        AS missing_vehicle_records
FROM Tickets;


-- =====================================================
-- Query 2: Daily citation activity
-- =====================================================

CREATE OR REPLACE VIEW daily_citation_activity AS
SELECT
    DATE(Issue_date) AS citation_date,
    COUNT(*) AS total_citations,
    SUM(CASE
        WHEN Ticket_Queue = 'Warning' THEN 1
        ELSE 0
    END) AS warnings,
    SUM(CASE
        WHEN Ticket_Queue <> 'Warning'
            AND Ticket_Queue <> '' THEN 1
        ELSE 0
    END) AS non_warnings,
    SUM(CASE
        WHEN Ticket_Queue IS NULL
            OR Ticket_Queue = '' THEN 1
        ELSE 0
    END) AS unknown_status
FROM Tickets
GROUP BY DATE(Issue_date);

SELECT *
FROM daily_citation_activity
ORDER BY citation_date;


-- =====================================================
-- Query 3: Hourly citation activity
-- =====================================================

CREATE OR REPLACE VIEW hourly_citation_activity AS
SELECT
    HOUR(Issue_date) AS hour_of_day,
    COUNT(*) AS total_citations,
    SUM(CASE
        WHEN Ticket_Queue = 'Warning' THEN 1
        ELSE 0
    END) AS warnings,
    SUM(CASE
        WHEN Ticket_Queue <> 'Warning'
            AND Ticket_Queue <> '' THEN 1
        ELSE 0
    END) AS non_warnings,
    SUM(CASE
        WHEN Ticket_Queue IS NULL
            OR Ticket_Queue = '' THEN 1
        ELSE 0
    END) AS unknown_status
FROM Tickets
GROUP BY HOUR(Issue_date);

SELECT *
FROM hourly_citation_activity
ORDER BY hour_of_day;


-- =====================================================
-- Query 4: Weekday vs. weekend activity
-- =====================================================

CREATE OR REPLACE VIEW weekday_weekend_activity AS
SELECT
    CASE
        WHEN WEEKDAY(citation_date) IN (5, 6)
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS days_recorded,
    SUM(total_citations) AS total_citations,
    ROUND(AVG(total_citations), 2) AS avg_daily_citations,
    SUM(warnings) AS total_warnings,
    ROUND(AVG(warnings), 2) AS avg_daily_warnings
FROM daily_citation_activity
GROUP BY day_type;

SELECT *
FROM weekday_weekend_activity;


-- =====================================================
-- Query 5: Most frequent violations
-- =====================================================

CREATE OR REPLACE VIEW violation_frequency AS
SELECT
    v.Violation_Code AS violation_code,
    v.Violation_description AS violation_description,
    COUNT(*) AS total_records,
    SUM(CASE
        WHEN t.Ticket_Queue = 'Warning' THEN 1
        ELSE 0
    END) AS warnings,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM Tickets), 2
    ) AS percentage_of_records
FROM Violations v
JOIN Tickets t
    ON v.Ticket_number = t.Ticket_number
GROUP BY
    v.Violation_Code,
    v.Violation_description;

SELECT *
FROM violation_frequency
ORDER BY total_records DESC;


-- =====================================================
-- Query 6: Citation activity by ZIP code
-- =====================================================

CREATE OR REPLACE VIEW citations_by_zip_code AS
SELECT
    LEFT(TRIM(Zip_code), 5) AS zip_code,
    COUNT(*) AS total_citations,
    SUM(CASE
        WHEN Ticket_Queue = 'Warning' THEN 1
        ELSE 0
    END) AS warnings
FROM Tickets
WHERE TRIM(Zip_code) REGEXP '^[0-9]{5}(-?[0-9]{4})?$'
    AND LEFT(TRIM(Zip_code), 5) <> '00000'
GROUP BY LEFT(TRIM(Zip_code), 5);

SELECT *
FROM citations_by_zip_code
ORDER BY total_citations DESC;

-- Check ZIP code coverage
SELECT
    COUNT(*) AS total_records,
    SUM(CASE
        WHEN Zip_code IS NULL OR TRIM(Zip_code) = ''
            THEN 1
        ELSE 0
    END) AS missing_zip_codes,
    SUM(CASE
        WHEN TRIM(Zip_code) REGEXP '^[0-9]{5}(-?[0-9]{4})?$'
            AND LEFT(TRIM(Zip_code), 5) <> '00000'
            THEN 1
        ELSE 0
    END) AS usable_zip_codes
FROM Tickets;


-- =====================================================
-- Query 7: Financial summary by ticket status
-- =====================================================

CREATE OR REPLACE VIEW financial_summary_by_status AS
SELECT
    t.Ticket_Queue AS ticket_status,
    COUNT(*) AS total_records,
    ROUND(SUM(f.Total_Payments), 2) AS total_payments,
    ROUND(SUM(CASE
        WHEN f.Current_Amount_Due > 0
            THEN f.Current_Amount_Due
        ELSE 0
    END), 2) AS positive_outstanding_balance,
    ROUND(SUM(f.Current_Amount_Due), 2) AS net_balance,
    ROUND(AVG(f.Total_Payments), 2) AS average_payment
FROM Tickets t
JOIN Financials f
    ON t.Ticket_number = f.Ticket_number
GROUP BY t.Ticket_Queue;

SELECT *
FROM financial_summary_by_status
ORDER BY total_records DESC;


-- =====================================================
-- Query 8: Financial impact by violation
-- =====================================================

CREATE OR REPLACE VIEW violation_financial_summary AS
SELECT
    v.Violation_Code AS violation_code,
    v.Violation_description AS violation_description,
    COUNT(*) AS total_records,
    ROUND(SUM(f.Total_Payments), 2) AS total_payments,
    ROUND(SUM(CASE
        WHEN f.Current_Amount_Due > 0
            THEN f.Current_Amount_Due
        ELSE 0
    END), 2) AS positive_outstanding_balance,
    ROUND(SUM(f.Current_Amount_Due), 2) AS net_balance,
    ROUND(AVG(f.Current_Amount_Due), 2) AS average_net_balance
FROM Violations v
JOIN Financials f
    ON v.Ticket_number = f.Ticket_number
GROUP BY
    v.Violation_Code,
    v.Violation_description;

SELECT *
FROM violation_financial_summary
ORDER BY positive_outstanding_balance DESC;


-- =====================================================
-- Query 9: Payment collection indicators by violation
-- Excludes records currently classified as warnings.
-- =====================================================

CREATE OR REPLACE VIEW payment_collection_rates AS
SELECT
    v.Violation_Code AS violation_code,
    v.Violation_description AS violation_description,
    COUNT(*) AS total_non_warning_records,

    SUM(CASE
        WHEN f.Total_Payments > 0 THEN 1
        ELSE 0
    END) AS records_with_payment,

    SUM(CASE
        WHEN t.Ticket_Queue = 'Paid' THEN 1
        ELSE 0
    END) AS paid_records,

    ROUND(
        100.0 * SUM(CASE
            WHEN f.Total_Payments > 0 THEN 1
            ELSE 0
        END) / COUNT(*), 2
    ) AS payment_record_percentage,

    ROUND(
        100.0 * SUM(CASE
            WHEN t.Ticket_Queue = 'Paid' THEN 1
            ELSE 0
        END) / COUNT(*), 2
    ) AS paid_status_percentage,

    ROUND(SUM(f.Total_Payments), 2) AS total_payments

FROM Tickets t
JOIN Financials f
    ON t.Ticket_number = f.Ticket_number
JOIN Violations v
    ON t.Ticket_number = v.Ticket_number
WHERE t.Ticket_Queue <> 'Warning'
    AND t.Ticket_Queue <> ''
GROUP BY
    v.Violation_Code,
    v.Violation_description;

SELECT *
FROM payment_collection_rates
ORDER BY total_non_warning_records DESC;


-- =====================================================
-- Query 10: Hearing outcomes
-- =====================================================

CREATE OR REPLACE VIEW hearing_outcomes AS
SELECT
    COALESCE(
        NULLIF(TRIM(Hearing_Dispo), ''),
        'Unknown'
    ) AS hearing_disposition,

    COUNT(*) AS total_hearing_records,

    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM Hearings), 2
    ) AS percentage_of_hearing_records

FROM Hearings
GROUP BY hearing_disposition;

SELECT *
FROM hearing_outcomes
ORDER BY total_hearing_records DESC;

