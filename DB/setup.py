"""
Module for connecting to a SQLite database and retrieving patient records.

This module provides functionality for establishing a connection to a SQLite database
("panelpal.db") and fetching patient records from the "panelpal" table. All database
operations are logged, and any errors that occur during the operations are raised.

Functions
---------
- connect
    Establishes a connection to the SQLite database "panelpal.db".

- fetch_patients
    Fetches patient records from the "panelpal" table in the database. Each patient record
    includes the following fields:
    - patient ID
    - analysis date
    - name
    - date of birth
    - NHS number
    - test R code
    - genes
    - bed file link

Dependencies
------------
- sqlite3 : For interacting with the SQLite database to establish connections and execute queries.
- logging : For logging the progress of operations and any errors that arise.

Example Usage
-------------
>>> conn = connect()
>>> patients = fetch_patients()

"""

import sqlite3
from PanelPal.settings import get_logger

# Initialise logger
logger = get_logger(__name__)

def connect():
    """
    Connects to the SQLite database and returns a database connection object.

    This function attempts to establish a connection to the SQLite database, titled "panelpal.db". 
    It logs the connection attempt and any errors that occur.

    Returns
    -------
    sqlite3.Connection
        A connection object to interact with the database.

    Raises
    ------
    sqlite3.Error
        An exception raised and logged if the connection fails.
    """
    try:
        # connect to SQLite database "panelpal.db"
        conn = sqlite3.connect("panelpal.db")

        # log the connection attempt
        logger.debug("Establishing database connection...")
        logger.info("Connection established")

        # return the connection object
        return conn

    # log any errors that occur
    except sqlite3.Error as e:
        logger.error("Failed to connect: %s", e)
        return None  # return None if the connection fails


def fetch_patients():
    """
    Fetches patient records from the "panelpal" table in the SQLite database.

    This function connects to the SQLite database, retrieves all records from the 
    "panelpal" table, and logs the retrieval process, including the number of 
    patient records fetched. The database connection is safely closed after use.

    Returns
    -------
    results: list of tuple
        A list of tuples, where each tuple contains a patient record with the following fields:
        - patient ID
        - analysis date
        - name
        - date of birth
        - NHS number
        - test R code
        - genes
        - bed file link

    Raises
    ------
    sqlite3.Error
        Raised if there is an issue fetching data from the database.

    Notes
    -----
    - This function assumes the "panelpal" table exists in the connected SQLite database.
    """
    # initialise the connection variable
    conn = None
    try:
        # connect to panelpal.db (the above function)
        conn = connect()

        # create cursor object that executes SQL commands
        cursor = conn.cursor()

        # log retrieval of patient information
        logger.debug("Fetching patient info...")
        cursor.execute("select * from panelpal")

        # fetch all the results
        results = cursor.fetchall()

        # log the number of patient records
        logger.debug("Fetched %d patients from database", len(results))

        # return fetched records as a list
        return results

    # log and raise exceptions
    except sqlite3.Error as e:
        logger.error("Error fetching patients: %s", e)
        raise

    finally:
        # close database connection if it connected
        if conn:
            conn.close()
            logger.info("Connection to database closed")


if __name__ == "__main__":
    fetch_patients()
