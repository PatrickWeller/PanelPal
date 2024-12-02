"""
Unit tests for the PanelPal database.

This module uses the unittest package to test:
- Database connection
- Ability to fetch patient records from the database
- Ability to check that each NHS number is unique, 
    safeguarding against duplicates/mistakes in records.

The tests are ran on a temporary in-memory SQLite database to ensure
isolation of the test data.
"""

import unittest
import sqlite3
from DB.setup import connect, fetch_patients


class TestDatabase(unittest.TestCase):
    """
    Test suite for the PanelPal database operations.
    """

    def setUp(self):
        """
        Set up a temporary in-memory database for testing.
        'setUp' is a special method that runs before each test to ensure a clean database state.
        """
        # connection function to setup + use in-memory DB
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # create the table for tests
        self.cursor.execute(
            """
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
            """
        )
        self.conn.commit()  # sends commit statement to SQL server, committing the transaction

    # teardown = special method that runs immediately after calling tests
    def tearDown(self):
        """
        Close database connection after each test.
        'tearDown' is a special method that runs immediately after calling tests.
        """
        self.conn.close()

    def test_connection(self):
        """
        Test that the connection to the DB has been established.
        """
        conn = connect()
        self.assertIsNotNone(
            conn
        )  # check the connection was successful (i.e. is not none)
        conn.close()

    def test_fetch_patients(self):
        """
        Test that patient records can be inserted into the database and received from it.
        """
        # insert test data
        self.cursor.execute(
            """
            INSERT INTO panelpal (
                analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bed_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "6/11/24",
                "John Doe",
                "01/01/01",
                "1234567890",
                "R56",
                "BRCA1,BRCA2",
                "http://example.com/bedfile.bed",
            ),
        )
        self.conn.commit()

        # check the values were added to the table
        self.cursor.execute("select * from panelpal")
        result = self.cursor.fetchall()

        # check that exactly 1 record was retrieved
        self.assertEqual(len(result), 1)

        # expected data (for an assert equal operation)
        expected = (
            1,
            "6/11/24",
            "John Doe",
            "01/01/01",
            "1234567890",
            "R56",
            "BRCA1,BRCA2",
            "http://example.com/bedfile.bed",
        )

        row = result[0]
        self.assertEqual(row, expected)  # check the data is what we expected

    def test_unique_nhs_id(self):
        """
        Test that inserting a duplicate NHS number raises an integrity error.
        """
        # insert patient
        self.cursor.execute(
            """
            INSERT INTO panelpal (
                analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bed_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "6/11/24",
                "John Doe",
                "01/01/01",
                "1234567890",
                "R56",
                "BRCA1,BRCA2",
                "http://example.com/bedfile.bed",
            ),
        )
        self.conn.commit()

        # Attempt to insert a duplicate NHS number
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                """
                INSERT INTO panelpal (
                    analysis_date, patient_name, dob, nhs_number, r_code, gene_list, bed_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    "7/11/24",
                    "Jane Doe",
                    "02/02/02",
                    "1234567890",
                    "R78",
                    "TP53",
                    "http://example.com/anotherfile.bed",
                ),
            )
            self.conn.commit()


if __name__ == "__main__":
    unittest.main()
