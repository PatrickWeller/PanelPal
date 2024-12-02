"""
Module for connecting to a SQLite database and retrieving patient records.

This module contains functions that establish a connection to a SQLite database, "panelpal.db",
fetching patient data from it. Operations are logged and errors are raised if they arise.

Functions:
    - Establish connection to SQLite database.
    - Fetch patient records from the "panelpal" table, which includes fields: 
        patient ID, analysis date, name, date of birth, NHS number, test R code, genes, 
        BAM file link.
    - Logs of all operations and any errors that arise during database interactions. 

Example usage:
    To fetch paitent records from the database, call `fetch_patients()`. 
    All logs will be written to both the console and specified log file. 
"""

import sqlite3
import logging

### LOGGING - configure settings

logging.basicConfig(
    level=logging.DEBUG,
    # format debugging messages (timestamp, name of logger, level of log message, actual message)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../logging/DBsetup.log"),  # store logs here
        logging.StreamHandler(),  # print to stdout as well
    ],
)

# initialise logger
logger = logging.getLogger(__name__)


########## CREATE DB ############


def connect():
    """
    This function connects to the SQLite database and returns a database connection object.

    First, it attempts to establish a connection to the SQLite database, titled "panelpal.db".
    It logs the connection attempt and any errors that occur.

    Returns:
        sqlite3.Connection: a connection object to interact with the database.

    Raises:
        sqlite3.Error: an exception is raised and logged if the connection fails.
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
    Fetches the patient records from panelpal input into the SQLite database.

    This function retrieves all patient records from the "panelpal" table within the
    SQLite database, logging the retrieval process and number of patients fetched.

    Returns: a list of patient records, including the fields:
        patient ID, analysis date, patient name, DOB, NHS number,
        test R code, list of genes included in the test, link to BAM file.

    Raises:
        sqlite3.Error: if fetching data from the database fails, an exception is raised.
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


##### RUN FUNCTION ######

if __name__ == "__main__":
    fetch_patients()
