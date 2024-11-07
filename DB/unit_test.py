import unittest
import sqlite3
from setup import connect, fetch_patients


class TestDatabase(unittest.TestCase):

    # setUp = special function called immediately before calling the test methods 
    def setUp(self):
        """
        Set up a new, temporary in-memory DB for testing purposes.
        This function runs before each test to ensure a clean database state.
        """
        # override connection function to use in-memory DB
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        # create the table for tests
        self.cursor.execute('''
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
            ''')
        self.conn.commit() # sends commit statement to SQL server, committing the transaction

    # teardown = special method that runs immediately after calling tests
    def tearDown(self):
        """
        Close database connection after each test.
        """
        self.conn.close()

    def test_connection(self):
        """
        Test that the connection to the DB has been established.
        """
        conn = connect()
        self.assertIsNotNone(conn) # check the connection was successful (i.e. is not none)
        conn.close()

    def test_fetch_patients(self):
        """
        Insert and retrieve patient records.
        """
        # insert test data
        self.cursor.execute('''
            INSERT INTO panelpal (
                analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bam_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('6/11/24', 'John Doe', '01/01/01', '1234567890', 'R56', 'BRCA1,BRCA2', 'http://example.com/bamfile.bam'))
        self.conn.commit()

        # check the values were added to the table
        self.cursor.execute("select * from panelpal")
        result = self.cursor.fetchall()

        # check that exactly 1 record was retrieved
        self.assertEqual(len(result),1)
   
        # expected data (for an assert equal operation)
        expected = (1, '6/11/24', 'John Doe', '01/01/01', '1234567890', 'R56', 'BRCA1,BRCA2', 'http://example.com/bamfile.bam')

        row = result[0]
        self.assertEqual(row, expected) # check the data is what we expected

    
    def test_unique_nhs_id(self):
        """
        Test that inserting a duplicate NHS number raises an error.
        """
        # insert patient
        self.cursor.execute('''
            INSERT INTO panelpal (
                analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bam_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('6/11/24', 'John Doe', '01/01/01', '1234567890', 'R56', 'BRCA1,BRCA2', 'http://example.com/bamfile.bam'))
        self.conn.commit()

        # Attempt to insert a duplicate NHS number
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute('''
                INSERT INTO panelpal (
                    analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bam_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('7/11/24', 'Jane Doe', '02/02/02', '1234567890', 'R78', 'TP53', 'http://example.com/anotherfile.bam'))
            self.conn.commit()

if __name__ == '__main__':
    unittest.main()