
CREATE DATABASE IF NOT EXISTS chicago_citations_jan2021;

USE chicago_citations_jan2021;

-- 1. Main citation information
CREATE TABLE Tickets (
    Ticket_number BIGINT PRIMARY KEY,
    Issue_date DATETIME NOT NULL,
    Zip_code VARCHAR(20),
    Ticket_Queue VARCHAR(45),
    Ticket_Queue_Date DATE,
    Officer VARCHAR(45),
    Unit VARCHAR(45),
    Unit_description VARCHAR(60),
    Vehicle_Make VARCHAR(45),
    License_Plate_Type VARCHAR(45)
);

-- 2. Violation information
CREATE TABLE Violations (
    Ticket_number BIGINT PRIMARY KEY,
    Violation_Code VARCHAR(20),
    Violation_description VARCHAR(150),
    Violation_Location VARCHAR(150),

    FOREIGN KEY (Ticket_number)
        REFERENCES Tickets(Ticket_number)
);

-- 3. Financial information
CREATE TABLE Financials (
    Ticket_number BIGINT PRIMARY KEY,
    Fine_Level_1_Amount DECIMAL(12,2),
    Fine_Level_2_Amount DECIMAL(12,2),
    Current_Amount_Due DECIMAL(12,2),
    Total_Payments DECIMAL(12,2),

    FOREIGN KEY (Ticket_number)
        REFERENCES Tickets(Ticket_number)
);

-- 4. Notice information
CREATE TABLE Notices (
    Ticket_number BIGINT PRIMARY KEY,
    Notice_Number VARCHAR(30),
    Notice_Level VARCHAR(45),

    FOREIGN KEY (Ticket_number)
        REFERENCES Tickets(Ticket_number)
);

-- 5. Hearing information
CREATE TABLE Hearings (
    Ticket_number BIGINT PRIMARY KEY,
    Hearing_Dispo VARCHAR(45),
    Hearing_Reason VARCHAR(150),

    FOREIGN KEY (Ticket_number)
        REFERENCES Tickets(Ticket_number)
);
