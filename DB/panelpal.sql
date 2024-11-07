-- DATABASE: "panelpal.sql"
-- run after connection has been established to sqlite

-- Create the table if it doesn't already exist
CREATE TABLE IF NOT EXISTS panelpal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_date TEXT NOT NULL,
    patient_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    nhs_number TEXT UNIQUE NOT NULL,
    r_code TEXT NOT NULL,
    gene_list TEXT NOT NULL,
    bam_file TEXT NOT NULL
);

