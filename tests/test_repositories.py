"""Simple repository tests: valid, missing and failure cases.

Run from the project root:  python -m unittest tests.test_repositories -v
Each test uses its own temporary SQLite database, so real data is never touched.
"""
import os
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.data.complaint_repository import ComplaintRepository
from src.data.customer_repository import CustomerRepository
from src.data.database_manager import DatabaseConfig, DatabaseManager
from src.data.errors import DataIntegrityError, QueryError
from src.data.models import Complaint, Customer

SCHEMA = (Path(__file__).parent / "schema_test.sql").read_text()


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        # fresh empty database for every test
        self.folder = tempfile.TemporaryDirectory()
        path = os.path.join(self.folder.name, "test.db")
        raw = sqlite3.connect(path)
        raw.executescript(SCHEMA)
        raw.close()
        self.db = DatabaseManager(DatabaseConfig(backend="sqlite", sqlite_path=path))
        self.customers = CustomerRepository(self.db)
        self.complaints = ComplaintRepository(self.db)
        self.customers.add(Customer("C1", "Ada Lovelace"))

    def tearDown(self):
        self.folder.cleanup()

    def make_complaint(self, complaint_id="CP1", customer_id="C1"):
        return Complaint(complaint_id, customer_id, "Fees", "Open", date(2026, 1, 5))

    # ---- valid cases
    def test_add_then_get_returns_same_customer(self):
        self.assertEqual(self.customers.get_by_id("C1"), Customer("C1", "Ada Lovelace"))

    def test_add_then_get_returns_same_complaint(self):
        c = self.make_complaint()
        self.complaints.add(c)
        self.assertEqual(self.complaints.get_by_id("CP1"), c)

    def test_count_by_status(self):
        self.complaints.add(self.make_complaint("CP1"))
        self.complaints.add(self.make_complaint("CP2"))
        self.assertEqual(self.complaints.count_by_status(), {"Open": 2})

    # ---- missing cases
    def test_get_unknown_id_returns_none(self):
        self.assertIsNone(self.customers.get_by_id("NOPE"))

    def test_list_with_no_matches_returns_empty_list(self):
        self.assertEqual(self.complaints.list_by_customer("C1"), [])

    # ---- failure cases
    def test_duplicate_id_raises_error(self):
        with self.assertRaises(DataIntegrityError):
            self.customers.add(Customer("C1", "Someone Else"))

    def test_unknown_customer_raises_error(self):
        with self.assertRaises(DataIntegrityError):
            self.complaints.add(self.make_complaint(customer_id="NOPE"))

    def test_sql_error_raises_query_error(self):
        with self.assertRaises(QueryError):
            with self.db.transaction() as tx:
                tx.fetch_all("SELECT * FROM table_that_does_not_exist")

    # ---- resources close after error, and changes roll back
    def test_connection_closed_and_changes_rolled_back_after_error(self):
        saved = {}
        with self.assertRaises(RuntimeError):
            with self.db.transaction() as tx:
                saved["conn"] = tx._conn
                self.customers.add(Customer("C2", "New Person"), tx=tx)
                raise RuntimeError("something went wrong")
        self.assertIsNone(self.customers.get_by_id("C2"))      # rolled back
        with self.assertRaises(sqlite3.ProgrammingError):      # connection is closed
            saved["conn"].execute("SELECT 1")


if __name__ == "__main__":
    unittest.main()