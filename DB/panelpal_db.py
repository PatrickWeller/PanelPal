"""
SQLalchemy object-relational configuration.

This script defines ORM (Object-Relational Mapping) classes using SQLAlchemy for managing
a database with tables for patient information, BED file metadata, and panel information.

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
- Ensure that `PanelPal.settings` contains a valid `get_logger` function.
- The database URL defaults to an SQLite database named `panelpal.db`.
- SQLAlchemy's echo mode is enabled for debugging.
"""

import sqlalchemy

from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from PanelPal.settings import get_logger

# Initialise logger
logger = get_logger(__name__)

# base class defined here. This allows all ORM classes below to inherit its methods.
Base = declarative_base()


# patient information table. NHS number used as primary key
class Patient(Base):
    __tablename__ = "patients"

    nhs_number = Column(String, primary_key=True)
    dob = Column(Date, nullable=False)
    patient_name = Column(String, nullable=False)

    # Relationship to BedFiles
    bed_files = relationship("BedFile", back_populates="patient")

    def __repr__(self):
        return (
            f"<Patient(nhs_number={self.nhs_number}, "
            f"patient_name={self.patient_name}, "
            f"dob={self.dob})>"
        )


# Bedfiles and metadata
class BedFile(Base):
    __tablename__ = "bed_files"

    id = Column(Integer, primary_key=True)
    analysis_date = Column(Date, nullable=False)
    bed_file_path = Column(String, nullable=False)
    patient_id = Column(String, ForeignKey("patients.nhs_number"), nullable=False)

    # Relationship to Patient
    patient = relationship("Patient", back_populates="bed_files")

    # Relationship to GeneList
    gene_lists = relationship("GeneList", back_populates="bed_file")

    def __repr__(self):
        return f"<BedFile(analysis_date={self.analysis_date}, bed_file_path={self.bed_file_path})>"


# Panel information. Foreign key to bed file
class PanelInfo(Base):
    __tablename__ = "gene_list"

    id = Column(Integer, primary_key=True)
    bed_file_id = Column(Integer, ForeignKey("bed_files.id"), nullable=False)
    panel_data = Column(JSON, nullable=False)  # store data in JSON format

    # Relationship to bed file
    bed_file = relationship("BedFile", back_populates="gene_lists")

    def __repr__(self):
        return (
            f"<GeneList(bed_file_id={self.bed_file_id}, panel_data={self.panel_data})>"
        )


# create engine that links to the SQLite DB
DATABASE_URL = "sqlite:///panelpal.db"
# an object of Engine class is instantiated using create_engine
engine = create_engine(DATABASE_URL, echo=True)

# create session
Session = sessionmaker(bind=engine)
