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

-- Insert test data if it doesn’t already exist
INSERT OR IGNORE INTO panelpal (
    analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bam_file
) VALUES 
    ('6/11/24', 'John Doe', '01/01/01', '1234567890', 'R56', 'BRCA1,BRCA2', 'http://example.com/bamfile.bam');
