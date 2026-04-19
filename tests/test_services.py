import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import storage
from exceptions import AmbiguousStudentMatch, LessonNotFound, PaymentNotFound
from services import LessonService, PaymentService, ReportService, StudentService


class BaseServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tracker_data.json"
        self.original_data_file = storage.DATA_FILE
        storage.DATA_FILE = str(self.data_file)

        self.students = StudentService()
        self.lessons = LessonService()
        self.payments = PaymentService()
        self.reports = ReportService()

    def tearDown(self):
        storage.DATA_FILE = self.original_data_file
        self.temp_dir.cleanup()

    def load_raw_data(self):
        with open(self.data_file, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def seed_basic_student_data(self):
        self.students.add_student("Alice", 25, "EUR", "weekly")
        self.students.add_student("Bob", 30, "USD", "")

        data = storage.load_data()
        data["lessons"] = [
            {
                "id": 1,
                "student_id": 1,
                "date": "2026-04-05",
                "duration": 60,
                "comment": "algebra",
                "price_snapshot": 25.0,
                "currency_snapshot": "EUR",
            },
            {
                "id": 2,
                "student_id": 1,
                "date": "2026-04-12",
                "duration": 90,
                "comment": "geometry",
                "price_snapshot": 25.0,
                "currency_snapshot": "EUR",
            },
            {
                "id": 3,
                "student_id": 2,
                "date": "2026-04-10",
                "duration": 45,
                "comment": "fractions",
                "price_snapshot": 30.0,
                "currency_snapshot": "USD",
            },
        ]
        data["payments"] = [
            {
                "id": 1,
                "student_id": 1,
                "date": "2026-04-07",
                "amount": 20.0,
                "currency": "EUR",
                "comment": "partial",
            },
            {
                "id": 2,
                "student_id": 1,
                "date": "2026-04-20",
                "amount": 30.0,
                "currency": "EUR",
                "comment": "top-up",
            },
            {
                "id": 3,
                "student_id": 2,
                "date": "2026-04-11",
                "amount": 10.0,
                "currency": "USD",
                "comment": "advance",
            },
        ]
        storage.save_data(data)


class ReportServiceTests(BaseServiceTestCase):

    def test_get_balance_returns_expected_totals_and_status(self):
        self.seed_basic_student_data()

        report = self.reports.get_balance(1)

        self.assertEqual(report["student_id"], 1)
        self.assertEqual(report["student_name"], "Alice")
        self.assertEqual(report["currency"], "EUR")
        self.assertEqual(report["lessons_sum"], Decimal("50.00"))
        self.assertEqual(report["payments_sum"], Decimal("50.00"))
        self.assertEqual(report["balance"], Decimal("0.00"))
        self.assertEqual(report["status"], "settled")

    def test_get_student_summary_includes_aggregates_and_dates(self):
        self.seed_basic_student_data()

        summary = self.reports.get_student_summary(1)

        self.assertEqual(summary["student_name"], "Alice")
        self.assertEqual(summary["total_lessons"], 2)
        self.assertEqual(summary["total_minutes"], 150)
        self.assertEqual(summary["average_duration"], 75.0)
        self.assertEqual(summary["total_earned"], Decimal("50.00"))
        self.assertEqual(summary["total_paid"], Decimal("50.00"))
        self.assertEqual(summary["first_lesson_date"], "2026-04-05")
        self.assertEqual(summary["last_lesson_date"], "2026-04-12")

    def test_get_students_overview_includes_balance_and_last_lesson(self):
        self.seed_basic_student_data()

        overview = self.reports.get_students_overview()

        self.assertEqual(len(overview), 2)
        self.assertEqual(
            overview[0],
            {
                "id": 1,
                "name": "Alice",
                "price_per_lesson": "25.00",
                "currency": "EUR",
                "total_lessons": 2,
                "last_lesson_date": "2026-04-12",
                "balance": Decimal("0.00"),
                "status": "settled",
            },
        )
        self.assertEqual(
            overview[1],
            {
                "id": 2,
                "name": "Bob",
                "price_per_lesson": "30.00",
                "currency": "USD",
                "total_lessons": 1,
                "last_lesson_date": "2026-04-10",
                "balance": Decimal("20.00"),
                "status": "owed to you",
            },
        )

    def test_get_overall_summary_groups_by_currency(self):
        self.seed_basic_student_data()

        summary = self.reports.get_overall_summary()

        self.assertEqual(summary["total_students"], 2)
        self.assertEqual(summary["total_lessons"], 3)
        self.assertEqual(
            summary["lessons_total_by_currency"],
            {"EUR": Decimal("50.00"), "USD": Decimal("30.00")},
        )
        self.assertEqual(
            summary["payments_total_by_currency"],
            {"EUR": Decimal("50.00"), "USD": Decimal("10.00")},
        )
        self.assertEqual(
            summary["balance_total_by_currency"],
            {"EUR": Decimal("0.00"), "USD": Decimal("20.00")},
        )

    def test_reports_support_existing_numeric_json_values(self):
        self.students.add_student("Legacy Student", 25, "EUR", "")
        data = storage.load_data()
        data["students"][0]["price_per_lesson"] = 25.0
        data["lessons"] = [
            {
                "id": 1,
                "student_id": 1,
                "date": "2026-04-05",
                "duration": 60,
                "comment": "legacy lesson",
                "price_snapshot": 25.0,
                "currency_snapshot": "EUR",
            }
        ]
        data["payments"] = [
            {
                "id": 1,
                "student_id": 1,
                "date": "2026-04-07",
                "amount": 10.0,
                "currency": "EUR",
                "comment": "legacy payment",
            }
        ]
        storage.save_data(data)

        report = self.reports.get_balance(1)

        self.assertEqual(report["lessons_sum"], Decimal("25.00"))
        self.assertEqual(report["payments_sum"], Decimal("10.00"))
        self.assertEqual(report["balance"], Decimal("15.00"))


class LessonServiceTests(BaseServiceTestCase):

    def test_update_lesson_changes_only_supplied_fields(self):
        self.students.add_student("Alice", 25, "EUR", "")
        self.lessons.add_lesson(1, 60, "algebra", "2026-04-10")

        updated = self.lessons.update_lesson(
            1,
            lesson_date="2026-04-11",
            duration="75",
            comment=None,
        )

        self.assertEqual(updated["date"], "2026-04-11")
        self.assertEqual(updated["duration"], 75)
        self.assertEqual(updated["comment"], "algebra")
        self.assertEqual(self.load_raw_data()["lessons"][0]["duration"], 75)

    def test_delete_lesson_removes_record(self):
        self.students.add_student("Alice", 25, "EUR", "")
        self.lessons.add_lesson(1, 60, "algebra", "2026-04-10")

        deleted = self.lessons.delete_lesson(1)

        self.assertEqual(deleted["id"], 1)
        self.assertEqual(self.load_raw_data()["lessons"], [])

    def test_delete_missing_lesson_raises(self):
        with self.assertRaises(LessonNotFound):
            self.lessons.delete_lesson(999)


class PaymentServiceTests(BaseServiceTestCase):

    def test_update_payment_changes_only_supplied_fields(self):
        self.students.add_student("Alice", 25, "EUR", "")
        self.payments.add_payment(1, 25, "paid", "2026-04-10")

        updated = self.payments.update_payment(
            1,
            payment_date="2026-04-15",
            amount="30",
            comment="",
        )

        self.assertEqual(updated["date"], "2026-04-15")
        self.assertEqual(updated["amount"], "30.00")
        self.assertEqual(updated["comment"], "")
        self.assertEqual(self.load_raw_data()["payments"][0]["amount"], "30.00")

    def test_delete_payment_removes_record(self):
        self.students.add_student("Alice", 25, "EUR", "")
        self.payments.add_payment(1, 25, "paid", "2026-04-10")

        deleted = self.payments.delete_payment(1)

        self.assertEqual(deleted["id"], 1)
        self.assertEqual(self.load_raw_data()["payments"], [])

    def test_update_missing_payment_raises(self):
        with self.assertRaises(PaymentNotFound):
            self.payments.update_payment(999, amount="10")

    def test_new_records_persist_money_as_strings(self):
        self.students.add_student("Alice", 25, "EUR", "")
        self.lessons.add_lesson(1, 60, "algebra", "2026-04-10")
        self.payments.add_payment(1, 25, "paid", "2026-04-10")

        data = self.load_raw_data()

        self.assertEqual(data["students"][0]["price_per_lesson"], "25.00")
        self.assertEqual(data["lessons"][0]["price_snapshot"], "25.00")
        self.assertEqual(data["payments"][0]["amount"], "25.00")


class StudentLookupTests(BaseServiceTestCase):

    def test_resolve_student_accepts_single_strong_fuzzy_match(self):
        self.students.add_student("Matvey", 25, "EUR", "")

        student = self.students.resolve_student("matvei")

        self.assertEqual(student["name"], "Matvey")

    def test_resolve_student_rejects_ambiguous_fuzzy_matches(self):
        self.students.add_student("Matvey", 25, "EUR", "")
        self.students.add_student("Matey", 25, "EUR", "")

        with self.assertRaises(AmbiguousStudentMatch):
            self.students.resolve_student("matei")


if __name__ == "__main__":
    unittest.main()
