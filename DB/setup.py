import sqlite3
import logging

### LOGGING
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("DBsetup.log"), # sends logs here
        logging.StreamHandler()
    ]
)

### CREATE DB
def connect():

    try:
        # connect to SQLite
        conn = sqlite3.connect('panelpal.db')
        logger.debug("Establishing database connection...")
        logger.info("Connection established")
        return conn
    except sqlite3.Error as e:
        logger.error(f"failed to connect: {e}")

def fetch_patients():
    try:
        conn = connect()
        cursor = conn.cursor()
        logger.debug("Fetching patient info...")
        cursor.execute("select * from panelpal")
        results = cursor.fetchall()
        logger.debug(f"Fetched {len(results)} patients from database")
        return results
    
    except sqlite3.Error as e:
        logger.error(f"Error fetching patients: {e}")
        raise

    finally:
        if conn:
            conn.close()
            logger.info("Connection to database closed")


if __name__ == "__main__":
    fetch_patients()
