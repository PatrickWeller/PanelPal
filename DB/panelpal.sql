-- open connection to the DB
connect()

-- patients DB: store patient's basic details
CREATE TABLE patients (
    nhs_number TEXT PRIMARY KEY,
    dob DATE NOT NULL,
    patient_name TEXT NOT NULL
);

-- bed files DB: store bed file metadata
CREATE TABLE bed_files (
    id INTEGER PRIMARY KEY,
    analysis_date DATE NOT NULL,
    bed_file_path TEXT NOT NULL,
    patient_id INTEGER NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE gene_list (
    id INTEGER PRIMARY KEY,
    bed_file_id INTEGER NOT NULL,
    gene_symbol TEXT NOT NULL,
    gene_data JSON, -- To store hierarchical data
    FOREIGN KEY (bed_file_id) REFERENCES bed_files(id)
);

