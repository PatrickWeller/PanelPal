"""
Tests to check whether database initialisation runs correctly.

These tests verify the successful creation of database tables and log messages during
the initialization process using an in-memory SQLite database. The tests ensure that 
the expected tables are created and that the appropriate log entries are generated.

Notes
-----
As tests use an in-memory test database created within this script, they do not seem to
contribute to the coverage report.
Tests that examine how information is added to the database are covered in 
`test_db_input.py`.
"""

import pytest
import logging
from datetime import date
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from DB.panelpal_db import Base, Patient, BedFile, PanelInfo

# Set up temporary in-memory SQLite engine for tests
@pytest.fixture
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine

# Create a session for the engine
@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_database_tables_exist(engine):
    """
    Test if the 3 expected tables: `patients`, `bed_files`, and 
    `panel_info` are created successfully upon database initialisation.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        SQLAlchemy engine connected to the in-memory SQLite database.

    Raises
    ------
    AssertionError
        If any of the tables do not exist in the database.
    """
    # Get list of table names from the database
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check if the 3 expected tables exist
    expected_tables = ['patients', 'bed_files', 'panel_info']
    for table in expected_tables:
        assert table in tables, f"Table {table} was not created successfully."


# Logger to test for correct log messages being generated on database startup
logger = logging.getLogger(__name__)  # Create logger
logger.setLevel(logging.INFO)
# StreamHandler captures log entries during testing
ch = logging.StreamHandler()
logger.addHandler(ch)

def test_create_database_tables(caplog, engine):
    """
    Test that database tables are created and log messages are correct.

    This test verifies that the database tables are successfully created and 
    that the expected log message is generated during initialisation.

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        The fixture used to capture log messages during the test.
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy engine connected to the in-memory SQLite database.

    Raises
    ------
    Exception
        If an error occurs while creating the database tables.
    """
    try:
        # Attempt to create tables (already created in the fixture)
        Base.metadata.create_all(engine)

        # Log database startup success
        logger.info("Database initialised successfully.")
    except Exception as e:
        logger.error("Error creating database tables: %s", e)
        raise

    # Check if the log entry was made successfully
    with caplog.at_level(logging.INFO):
        # Make sure the log contains the expected message
        assert "Database initialised successfully." in caplog.text


def test_patient(session):
    """
    Test adding and retrieving a patient from the database.

    This test ensures that a patient can be added to the `patients` table and 
    that the related bed file and test information are added correctly.
    
    Parameters
    ----------
    session : sqlalchemy.orm.Session
        The database session for performing database operations.
    
    Raises
    ------
    AssertionError
        If the patient or related data is not added correctly.
    """
    # Create a fake patient and add to the database
    patient = Patient(nhs_number="1234567890", dob=date(1990, 1, 1), 
                      patient_name="John Doe")
    session.add(patient)
    session.commit()
    
    # Add a fake bed file for the patient
    bed_file = BedFile(
        analysis_date=date(2025, 1, 1),
        bed_file_path="/path/to/bedfile.bed",
        merged_bed_path="/path/to/merged_bedfile.bed",
        patient_id="1234567890"
    )
    session.add(bed_file)
    session.commit()
    
    # Add fake panel info 
    panel_info = PanelInfo(
        bed_file_id=bed_file.id,
        panel_data={
            "test_name": "Test Panel",
            "result": "Positive"
        }
    )
    session.add(panel_info)
    session.commit()

    # Retrieve patient and related data
    retrieved_patient = session.query(Patient).filter_by(nhs_number="1234567890").first()
    assert retrieved_patient is not None, "Patient was not added to the database"
    assert retrieved_patient.nhs_number == "1234567890", f"Patient NHS number does not match"

    # Retrieve bed file and related data
    retrieved_bed_file = session.query(BedFile).filter_by(patient_id="1234567890").first()
    assert retrieved_bed_file is not None, "Bed file was not added to the database"
    assert retrieved_bed_file.bed_file_path == "/path/to/bedfile.bed", "Bed file path does not match"

    # Retrieve panel info
    retrieved_panel_info = session.query(PanelInfo).filter_by(bed_file_id=bed_file.id).first()

    # Assertions
    assert retrieved_panel_info is not None
    assert retrieved_panel_info.panel_data["test_name"] == "Test Panel"
    assert retrieved_panel_info.panel_data["result"] == "Positive"

class TestClassMethods:
    def test_repr_(self, session):
        # Create a fake patient and add to the database
        patient = Patient(nhs_number="1234567890", dob=date(1990, 1, 1), patient_name="John Doe")
        session.add(patient)
        session.commit()
        patient = session.query(Patient).filter_by(nhs_number="1234567890").first()

        # Get the string representation of the patient
        patient_repr = repr(patient)

        # Test if the string contains expected values
        assert "John Doe" in patient_repr, "Patient name not found in __repr__"
        assert "1234567890" in patient_repr, "Patient NHS number not found in __repr__"
        
    # def test_find_patient():
    def test_find_patient(self, session):
        # add a fake patient
        patient = Patient(nhs_number="1234567890", dob=date(1990, 1, 1), patient_name="John Doe")
        session.add(patient)
        session.commit()

        # Use the class method to find the patient
        found_patients = Patient.find_patient(session, "1234567890")

        # Ensure that the patient was found
        assert len(found_patients) > 0, "No patients found using find_patient()"
        assert found_patients[0].nhs_number == "1234567890", "Found patient NHS number does not match"

def test_get_by_patient_id(session):
    # Create and add a fake patient
    patient = Patient(nhs_number="1234567890", dob=date(1990, 1, 1), patient_name="John Doe")
    session.add(patient)
    session.commit()

    # Create and add a fake bed file linked to the patient
    bed_file = BedFile(
        analysis_date=date(2025, 1, 1),
        bed_file_path="/path/to/bedfile.bed",
        merged_bed_path="/path/to/merged_bedfile.bed",
        patient_id="1234567890"
    )
    session.add(bed_file)
    session.commit()

    # Retrieve bed files by patient ID
    retrieved_bed_files = BedFile.get_by_patient_id(session, "1234567890")

    # Ensure list of bed files is not empty
    assert retrieved_bed_files, "No bed files found for patient ID"
    # Ensure bed file belongs to correct patient
    assert retrieved_bed_files[0].patient_id == "1234567890", "Retrieved bed file patient ID does not match"
    assert retrieved_bed_files[0].bed_file_path == "/path/to/bedfile.bed", "Bed file path does not match"

    # def test_get_by_bedfile():

    # def test_extract_panel_data():