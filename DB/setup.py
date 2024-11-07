import sqlite3
import logging

### LOGGING - configure settings

logging.basicConfig(
    level=logging.DEBUG, 
    # format debugging messages (timestamp, name of logger, level of log message, actual message.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logging/DBsetup.log"), # store logs here
        logging.StreamHandler() # print to stdout as well
    ]
)

# initialise logger
logger = logging.getLogger(__name__)


########## CREATE DB ############

def connect():
    """
    Connect to the SQLite database;
    return a database connection object
    """

    try:
        # connect to SQLite database "panelpal.db"
        conn = sqlite3.connect('panelpal.db')

        # log the connection attempt
        logger.debug("Establishing database connection...")
        logger.info("Connection established")
        
        # return the connection object
        return conn
    
    # log any errors that occur
    except sqlite3.Error as e:
        logger.error(f"failed to connect: {e}")


def fetch_patients():
    """
    fetches the patient records from panelpal input into the SQLite database.
    Returns list of patient records. 
    """
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
        logger.debug(f"Fetched {len(results)} patients from database")
        
        # return fetched records as a list
        return results 
    
    # log and raise exceptions
    except sqlite3.Error as e:
        logger.error(f"Error fetching patients: {e}")
        raise 

    finally:
        # close database connection if it connected
        if conn:
            conn.close()
            logger.info("Connection to database closed")



##### RUN FUNCTION ######

if __name__ == "__main__":
    fetch_patients()
