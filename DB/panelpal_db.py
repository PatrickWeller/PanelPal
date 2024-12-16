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

from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, ForeignKey
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

    This table stores patient details, including NHS number, patient name, and date of birth.
    Multiple records for the same patient can exist, which is useful for reanalysis purposes.

    Attributes
    ----------
    id : int
        The unique identifier for the patient record.
    nhs_number : str
        The NHS number of the patient.
    dob : date
        The date of birth of the patient.
    patient_name : str
        The name of the patient.

    Relationships
    -------------
    bed_files : list of BedFile
        A list of `BedFile` objects related to this patient.

    Methods
    -------
    __repr__()
        Returns a string representation of the `Patient` object. 
        Defines how objects are displayed as strings when printed 
        (making them more user-friendly)
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


class BedFile(Base):
    """
    Store bedfiles and their metadata. 
    """
    __tablename__ = "bed_files"

    id = Column(Integer, primary_key=True)
    analysis_date = Column(Date, nullable=False)
    bed_file_path = Column(String, nullable=False)
    merged_bed_path = Column(String, nullable=False)
    patient_id = Column(String, ForeignKey(
        "patients.nhs_number"), nullable=False)

    # Relationship to Patient table
    patient = relationship("Patient", back_populates="bed_files")

    # Relationship to PanelInfo table
    panels = relationship("PanelInfo", back_populates="bed_file")

    def __repr__(self):
        return f"<BedFile(analysis_date={self.analysis_date}, bed_file_path={self.bed_file_path})>"


class PanelInfo(Base):
    __tablename__ = "panel_info"

    # ID as PK for clarity
    id = Column(Integer, primary_key=True, autoincrement=True)
    bed_file_id = Column(Integer, ForeignKey("bed_files.id"), nullable=False)
    panel_data = Column(JSON, nullable=False)

    # Relationship to bed file
    bed_file = relationship("BedFile", back_populates="panels")


# URL that links to the SQLite database
DATABASE_URL = "sqlite:///panelpal.db"

# an object of Engine class is instantiated using create_engine
engine = create_engine(DATABASE_URL, echo=False)

# create session
Session = sessionmaker(bind=engine)


def create_database():
    """
    Creates the database and tables if they don't exist yet.
    """
    try:
        # Create tables in the database
        Base.metadata.create_all(engine)

        # Log database startup success using your custom logger
        logger.info("Database initialised successfully.")

    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
