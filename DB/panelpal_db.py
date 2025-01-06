"""
SQLalchemy object-relational configuration.

This script defines the database schema using ORM (Object-Relational Mapping) classes 
in SQLAlchemy for managing a database with three tables for patient information, 
BED file metadata, and panel information.

The script uses `declarative_base()` to create a base class from which all ORM classes
inherit, enabling the declaration of tables and their relationships in Python class format.

Classes:
--------
Patient : ORM class representing the "patients" table.
    Stores patient information such as NHS number, date of birth, and name.
    Includes a relationship to the `BedFile` class.

BedFile : ORM class representing the "bed_files" table.
    Stores BED file metadata, including file path and analysis date.
    Has a foreign key relationship to the `Patient` class and a relationship 
    to the `PanelInfo` class.

PanelInfo : ORM class representing the "gene_list" table.
    Stores panel data in JSON format and links to the `BedFile` class.

Variables:
----------
logger : logging.Logger
    Logger for this module.
Base : sqlalchemy.ext.declarative.api.DeclarativeMeta
    Base class for ORM definitions.
DATABASE_URL : str
    URL for the SQLite database.
engine : sqlalchemy.engine.base.Engine
    SQLAlchemy engine connected to the SQLite database.
Session : sqlalchemy.orm.session.sessionmaker
    Factory for creating new SQLAlchemy session objects.

Notes:
------
- The database URL defaults to an SQLite database named `panelpal.db`.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Date, JSON, ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from PanelPal.settings import get_logger

# Initialise logger
logger = get_logger(__name__)

# Define base class - this allows all ORM classes below to inherit its methods.
Base = declarative_base()

# Define the tables within the database (patient, bedfile and panelinfo):


class Patient(Base):
    """
    Patient information table.

    This table stores the details of patients, including their NHS number, 
    date of birth, and name. Multiple records for the same patient can exist,
    which is useful for reanalysis purposes.

    Attributes
    ----------
    id : int
        The unique identifier for the patient record. Automatically incremented.
    nhs_number : str
        The NHS number of the patient, which is a 10-digit unique identifier.
    dob : date
        The date of birth of the patient.
    patient_name : str
        The name of the patient.

    Relationships
    -------------
    bed_files : list of BedFile
        A list of `BedFile` objects associated with the patient. This represents 
        the patient's associated BED file data.

    Methods
    -------
    __repr__()
        Returns a string representation of the `Patient` object, displaying 
        key patient information (NHS number, name, date of birth).

    Notes
    -----
    - `id` is the primary key and automatically generated.
    - `nhs_number` is a unique identifier for patients, but multiple records 
      for the same NHS number can exist.
    - `bed_files` holds a relationship to the `BedFile` table.
    """

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nhs_number = Column(String(10), nullable=False)
    dob = Column(Date, nullable=False)
    patient_name = Column(String, nullable=False)

    # Relationship to BedFiles table
    bed_files = relationship("BedFile", back_populates="patient")

    # string representation method
    def __repr__(self):
        return (
            f"<Patient(nhs_number={self.nhs_number}, "
            f"patient_name={self.patient_name}, "
            f"dob={self.dob})>"
        )

    @classmethod
    def find_patient(cls, session, nhs_number):
        """
        Retrieve all patient records with the same NHS number.

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The database session to use for the query.
        nhs_number : str
            The NHS number to filter patient records by.

        Returns
        -------
        list of Patient
            A list of Patient instances that have the given NHS number.

        Example usage
        -------------
            patients_with_same_nhs = Patient.find_patient(session, "1234567890")
        """
        return session.query(cls).filter_by(nhs_number=nhs_number).all()



class BedFile(Base):
    """
    Bed files table.


    This table stores metadata about BED files and their associated information, 
    including analysis dates, file paths, and relationships to patients and panels.

    Attributes
    ----------
    __tablename__ : str
        The name of the table in the database (`bed_files`).
    id : sqlalchemy.Column
        The primary key for the table, an auto-incrementing integer.
    analysis_date : sqlalchemy.Column
        The date when the analysis was conducted, stored as a `Date`.
    bed_file_path : sqlalchemy.Column
        The file path to the BED file, stored as a string.
    merged_bed_path : sqlalchemy.Column
        The file path to the merged BED file, stored as a string.
    patient_id : sqlalchemy.Column
        A foreign key referencing the `nhs_number` column in the `patients` table.
    patient : sqlalchemy.orm.relationship
        Defines a relationship to the `Patient` model, linking each BED file to a patient.
    panels : sqlalchemy.orm.relationship
        Defines a relationship to the `PanelInfo` model, linking each BED file to related panels.

    Methods
    -------
    __repr__()
        Returns a string representation of the BedFile instance, 
        showing the `analysis_date` and `bed_file_path`.

    Notes
    -----
    - The `id` is the primary key, and it is auto-incremented.
    - The `patient_id` field is a foreign key referencing the `nhs_number` from the
      `patients` table.
    - The `panels` attribute holds a relationship to the `PanelInfo` table, 
    linking bed files to panel data.
    - The class has a composite unique constraint on the combination of `patient_id` 
    and `id` to ensure uniqueness
      within the scope of a patient's records.
    """

    __tablename__ = "bed_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    bed_file_path = Column(String, nullable=False)
    merged_bed_path = Column(String, nullable=False)
    patient_id = Column(String, ForeignKey(
        "patients.nhs_number"), nullable=False)

    # Relationship to Patient table
    patient = relationship("Patient", back_populates="bed_files")

    # Relationship to PanelInfo table
    panels = relationship("PanelInfo", back_populates="bed_file")

    # Composite unique constraint on patient_id and id
    __table_args__ = (
        UniqueConstraint('patient_id', 'id', name='uq_patient_id_id'),
    )

    def __repr__(self):
        return (
            f"<BedFile(analysis_date={self.analysis_date}, "
            f"bed_file_path={self.bed_file_path})>"
        )

    @classmethod
    def get_by_patient_id(cls, session, patient_id):
        """
        Retrieve all BedFiles for a given patient ID.

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The database session.
        patient_id : str
            The patient ID to filter BedFiles by.

        Returns
        -------
        list of BedFile
            A list of BedFile instances associated with the given patient ID.
        """
        return session.query(cls).filter_by(patient_id=patient_id).all()


class PanelInfo(Base):
    """
    Panel information table.

    This table stores information about genetic panels, including the 
    associated BED file and panel data. 

    Attributes
    ----------
    __tablename__ : str
        The name of the table in the database (`panel_info`).
    id : sqlalchemy.Column
        The primary key for the table, an auto-incrementing integer.
    bed_file_id : sqlalchemy.Column
        A foreign key referencing the `id` column in the `bed_files` table.
    panel_data : sqlalchemy.Column
        A JSON column storing panel information as a structured JSON object.
    bed_file : sqlalchemy.orm.relationship
        Defines a relationship to the `BedFile` model, enabling navigation
        between related records in the `bed_files` table.

    Notes
    -----
    - The `id` column is the primary key for this table.
    - A `bed_file_id` is required to link each panel to a specific BED file.
    - Panel data is stored in JSON format to allow for flexible storage of
      structured data.
    """

    __tablename__ = "panel_info"

    # ID as PK for clarity
    id = Column(Integer, primary_key=True, autoincrement=True)
    bed_file_id = Column(Integer, ForeignKey("bed_files.id"), nullable=False)
    panel_data = Column(JSON, nullable=False)

    # Relationship to bed file
    bed_file = relationship("BedFile", back_populates="panels")

    @classmethod
    def get_by_bed_file_id(cls, session, bed_file_id):
        """
        Retrieve PanelInfo associated with a specific BedFile ID.

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The database session.
        bed_file_id : int
            The ID of the BedFile.

        Returns
        -------
        PanelInfo
            The PanelInfo instance associated with the given BedFile ID, or None if not found.
        """
        return session.query(cls).filter_by(bed_file_id=bed_file_id).first()

    def extract_panel_data(self):
        """
        Extracts the panel_data JSON as a list of key-value pairs.

        Returns
        -------
        list of tuple
            A list of key-value pairs (tuples) extracted from the panel_data JSON.
        
        Example Usage
        -------------
            panel_data_list = panel_info_instance.extract_panel_data()
        """

        if isinstance(self.panel_data, dict):
            return list(self.panel_data.items())
        return []



# URL that links to the SQLite database
DATABASE_URL = "sqlite:///panelpal.db"

# an object of Engine class is instantiated using create_engine
engine = create_engine(DATABASE_URL, echo=False)

# create session
Session = sessionmaker(bind=engine)


def create_database():
    """
    Create the database and initialize tables if they do not already exist.

    This function uses SQLAlchemy's `Base.metadata.create_all` to create
    all tables defined in the database schema. If the tables already exist,
    no changes are made. 

    Returns
    -------
    None

    Raises
    ------
    Exception
        If an error occurs during the creation of database tables, the exception
        is logged and re-raised for further handling.

    Notes
    -----
    - This function assumes that the `engine` object and `Base` metadata
      are properly configured before calling it.
    - A custom logger is used to log database initialization status.

    Examples
    --------
    >>> create_database()
    Database initialised successfully.
    """

    try:
        # Create tables in the database
        Base.metadata.create_all(engine)

        # Log database startup success using your custom logger
        logger.info("Database initialised successfully.")

    except Exception as e:
        logger.error("Error creating database tables: %s", e)
        raise
