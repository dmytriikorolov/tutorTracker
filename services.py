from collections import defaultdict
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from difflib import SequenceMatcher

from exceptions import (
    AmbiguousStudentMatch,
    InvalidInput,
    LessonNotFound,
    PaymentNotFound,
    StudentNotFound,
)
from models import Lesson, Payment, Student
from storage import load_data, save_data

MONEY_PRECISION = Decimal("0.01")
FUZZY_MATCH_THRESHOLD = 0.7
FUZZY_MATCH_MARGIN = 0.1


def validate_date_string(date_str: str, *, field_name: str, allow_empty: bool = False) -> str:
    cleaned = str(date_str).strip()
    if not cleaned:
        if allow_empty:
            return str(date.today())
        raise InvalidInput(f"{field_name} is required.")

    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
        return cleaned
    except ValueError as exc:
        raise InvalidInput(f"{field_name} must be in YYYY-MM-DD format.") from exc


def validate_positive_int(value, *, field_name: str) -> int:
    try:
        parsed = int(str(value).strip())
    except ValueError as exc:
        raise InvalidInput(f"{field_name} must be a whole number.") from exc

    if parsed <= 0:
        raise InvalidInput(f"{field_name} must be greater than zero.")

    return parsed


def validate_positive_amount(value, *, field_name: str) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise InvalidInput(f"{field_name} must be a number.") from exc

    if parsed <= Decimal("0"):
        raise InvalidInput(f"{field_name} must be greater than zero.")

    return quantize_money(parsed)


def parse_money(value) -> Decimal:
    try:
        return quantize_money(Decimal(str(value).strip()))
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise InvalidInput("Stored money value is invalid.") from exc


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_PRECISION)


def serialize_money(value: Decimal) -> str:
    return format(quantize_money(value), ".2f")


def format_money(value) -> str:
    return format(parse_money(value), ".2f")


def validate_currency(value: str) -> str:
    currency = str(value).strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise InvalidInput("Currency must be a 3-letter code such as USD, EUR, or CZK.")
    return currency


def validate_name(value: str) -> str:
    name = str(value).strip()
    if not name:
        raise InvalidInput("Student name cannot be empty.")
    return name


class StudentService:

    def list_students(self):
        return load_data()["students"]

    def search_students(self, query):
        search_query = str(query).strip().casefold()
        if not search_query:
            raise InvalidInput("Search query cannot be empty.")

        data = load_data()
        return [
            student for student in data["students"]
            if search_query in student["name"].casefold()
        ]

    def resolve_student(self, reference):
        lookup_value = str(reference).strip()
        if not lookup_value:
            raise InvalidInput("Student id or name is required.")

        data = load_data()
        students = data["students"]

        if lookup_value.isdigit():
            student_id = int(lookup_value)
            student = next((s for s in students if s["id"] == student_id), None)
            if not student:
                raise StudentNotFound(f"Student with id {student_id} not found.")
            return student

        normalized_lookup = lookup_value.casefold()
        exact_matches = [s for s in students if s["name"].casefold() == normalized_lookup]
        if len(exact_matches) == 1:
            return exact_matches[0]
        if len(exact_matches) > 1:
            raise AmbiguousStudentMatch(self.build_ambiguous_match_message(lookup_value, exact_matches))

        partial_matches = [s for s in students if normalized_lookup in s["name"].casefold()]
        if len(partial_matches) == 1:
            return partial_matches[0]
        if len(partial_matches) > 1:
            raise AmbiguousStudentMatch(self.build_ambiguous_match_message(lookup_value, partial_matches))

        fuzzy_matches = self.get_fuzzy_matches(lookup_value, students)
        if len(fuzzy_matches) == 1:
            return fuzzy_matches[0]
        if len(fuzzy_matches) > 1:
            raise AmbiguousStudentMatch(self.build_ambiguous_match_message(lookup_value, fuzzy_matches))
        raise StudentNotFound(f"No student found for '{lookup_value}'.")

    @staticmethod
    def build_ambiguous_match_message(lookup_value, matches):
        options = ", ".join(f'{student["id"]}: {student["name"]}' for student in matches)
        return f"Multiple students match '{lookup_value}': {options}. Please use the id."

    @staticmethod
    def get_fuzzy_matches(lookup_value, students):
        normalized_lookup = lookup_value.casefold()
        scored_matches = []

        for student in students:
            ratio = SequenceMatcher(None, normalized_lookup, student["name"].casefold()).ratio()
            if ratio >= FUZZY_MATCH_THRESHOLD:
                scored_matches.append((ratio, student))

        if not scored_matches:
            return []

        scored_matches.sort(key=lambda item: item[0], reverse=True)
        top_score = scored_matches[0][0]
        return [
            student for score, student in scored_matches
            if top_score - score <= FUZZY_MATCH_MARGIN
        ]

    def add_student(self, name, price, currency, notes=""):
        data = load_data()
        new_id = len(data["students"]) + 1

        student = Student(
            id=new_id,
            name=validate_name(name),
            price_per_lesson=serialize_money(
                validate_positive_amount(price, field_name="Price per lesson")
            ),
            currency=validate_currency(currency),
            notes=str(notes).strip(),
        )

        data["students"].append(student.__dict__)
        save_data(data)

    def get_student_by_id(self, student_id):
        data = load_data()
        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")
        return student


class LessonService:

    def add_lesson(self, student_id, duration, comment="", lesson_date=""):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        new_id = len(data["lessons"]) + 1
        lesson = Lesson(
            id=new_id,
            student_id=student_id,
            date=self.validate_date(lesson_date),
            duration=validate_positive_int(duration, field_name="Duration"),
            comment=str(comment).strip(),
            price_snapshot=serialize_money(parse_money(student["price_per_lesson"])),
            currency_snapshot=student["currency"],
        )

        data["lessons"].append(lesson.__dict__)
        save_data(data)

    def get_lessons(self, student_id):
        data = load_data()
        return [lesson for lesson in data["lessons"] if lesson["student_id"] == student_id]

    def update_lesson(self, lesson_id, *, lesson_date="", duration="", comment=None):
        data = load_data()
        lesson = next((item for item in data["lessons"] if item["id"] == lesson_id), None)
        if not lesson:
            raise LessonNotFound(f"Lesson with id {lesson_id} not found.")

        if lesson_date.strip():
            lesson["date"] = self.validate_date(lesson_date)
        if str(duration).strip():
            lesson["duration"] = validate_positive_int(duration, field_name="Duration")
        if comment is not None:
            lesson["comment"] = str(comment).strip()

        save_data(data)
        return lesson

    def delete_lesson(self, lesson_id):
        data = load_data()
        lesson = next((item for item in data["lessons"] if item["id"] == lesson_id), None)
        if not lesson:
            raise LessonNotFound(f"Lesson with id {lesson_id} not found.")

        data["lessons"] = [item for item in data["lessons"] if item["id"] != lesson_id]
        save_data(data)
        return lesson

    @staticmethod
    def validate_date(date_str: str) -> str:
        return validate_date_string(date_str, field_name="Date", allow_empty=True)


class PaymentService:

    def add_payment(self, student_id, amount, comment="", payment_date=""):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        new_id = len(data["payments"]) + 1
        payment = Payment(
            id=new_id,
            student_id=student_id,
            date=self.validate_date(payment_date),
            amount=serialize_money(validate_positive_amount(amount, field_name="Amount")),
            currency=student["currency"],
            comment=str(comment).strip(),
        )

        data["payments"].append(payment.__dict__)
        save_data(data)

    def get_payments(self, student_id):
        data = load_data()
        return [payment for payment in data["payments"] if payment["student_id"] == student_id]

    def update_payment(self, payment_id, *, payment_date="", amount="", comment=None):
        data = load_data()
        payment = next((item for item in data["payments"] if item["id"] == payment_id), None)
        if not payment:
            raise PaymentNotFound(f"Payment with id {payment_id} not found.")

        if payment_date.strip():
            payment["date"] = self.validate_date(payment_date)
        if str(amount).strip():
            payment["amount"] = serialize_money(validate_positive_amount(amount, field_name="Amount"))
        if comment is not None:
            payment["comment"] = str(comment).strip()

        save_data(data)
        return payment

    def delete_payment(self, payment_id):
        data = load_data()
        payment = next((item for item in data["payments"] if item["id"] == payment_id), None)
        if not payment:
            raise PaymentNotFound(f"Payment with id {payment_id} not found.")

        data["payments"] = [item for item in data["payments"] if item["id"] != payment_id]
        save_data(data)
        return payment

    @staticmethod
    def validate_date(date_str: str) -> str:
        return validate_date_string(date_str, field_name="Payment date", allow_empty=True)


class ReportService:

    @staticmethod
    def get_balance_status(balance):
        if balance > 0:
            return "owed to you"
        if balance < 0:
            return "prepaid"
        return "settled"

    def get_balance(self, student_id):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        lessons = [lesson for lesson in data["lessons"] if lesson["student_id"] == student_id]
        payments = [payment for payment in data["payments"] if payment["student_id"] == student_id]

        lessons_sum = sum((parse_money(lesson["price_snapshot"]) for lesson in lessons), Decimal("0"))
        payments_sum = sum((parse_money(payment["amount"]) for payment in payments), Decimal("0"))
        balance = lessons_sum - payments_sum

        return {
            "student_id": student["id"],
            "student_name": student["name"],
            "currency": student["currency"],
            "lessons_sum": lessons_sum,
            "payments_sum": payments_sum,
            "balance": balance,
            "status": self.get_balance_status(balance),
        }

    def get_students_overview(self):
        data = load_data()
        return self.get_students_overview_for_students(data["students"])

    def get_students_overview_for_students(self, students):
        data = load_data()
        lessons_by_student = defaultdict(list)
        payments_by_student = defaultdict(list)

        for lesson in data["lessons"]:
            lessons_by_student[lesson["student_id"]].append(lesson)

        for payment in data["payments"]:
            payments_by_student[payment["student_id"]].append(payment)

        overview = []
        for student in students:
            lessons = lessons_by_student[student["id"]]
            payments = payments_by_student[student["id"]]
            lesson_dates = sorted(lesson["date"] for lesson in lessons)
            lessons_total = sum((parse_money(lesson["price_snapshot"]) for lesson in lessons), Decimal("0"))
            payments_total = sum((parse_money(payment["amount"]) for payment in payments), Decimal("0"))
            balance = lessons_total - payments_total

            overview.append({
                "id": student["id"],
                "name": student["name"],
                "price_per_lesson": student["price_per_lesson"],
                "currency": student["currency"],
                "total_lessons": len(lessons),
                "last_lesson_date": lesson_dates[-1] if lesson_dates else "—",
                "balance": balance,
                "status": self.get_balance_status(balance),
            })

        return overview

    def get_current_month_summary(self):
        data = load_data()
        current_month = date.today().strftime("%Y-%m")

        lessons_this_month = [
            lesson for lesson in data["lessons"]
            if lesson["date"].startswith(current_month)
        ]

        payments_this_month = [
            payment for payment in data["payments"]
            if payment["date"].startswith(current_month)
        ]

        earned_by_currency = defaultdict(lambda: Decimal("0"))
        received_by_currency = defaultdict(lambda: Decimal("0"))
        lessons_per_student = defaultdict(int)
        earned_per_student = defaultdict(lambda: {"currency": None, "amount": Decimal("0")})

        for lesson in lessons_this_month:
            currency = lesson["currency_snapshot"]
            earned_by_currency[currency] += parse_money(lesson["price_snapshot"])
            lessons_per_student[lesson["student_id"]] += 1

            student = next((s for s in data["students"] if s["id"] == lesson["student_id"]), None)
            if student:
                earned_per_student[student["name"]]["currency"] = currency
                earned_per_student[student["name"]]["amount"] += parse_money(lesson["price_snapshot"])

        for payment in payments_this_month:
            received_by_currency[payment["currency"]] += parse_money(payment["amount"])

        student_breakdown = {}
        for student in data["students"]:
            sid = student["id"]
            if sid in lessons_per_student:
                student_breakdown[student["name"]] = {
                    "lessons": lessons_per_student[sid],
                    "currency": earned_per_student[student["name"]]["currency"],
                    "amount": earned_per_student[student["name"]]["amount"],
                }

        return {
            "month": current_month,
            "total_lessons": len(lessons_this_month),
            "earned_by_currency": dict(earned_by_currency),
            "received_by_currency": dict(received_by_currency),
            "student_breakdown": student_breakdown,
        }

    def get_overall_summary(self):
        data = load_data()

        lessons_total_by_currency = defaultdict(lambda: Decimal("0"))
        payments_total_by_currency = defaultdict(lambda: Decimal("0"))
        balance_total_by_currency = defaultdict(lambda: Decimal("0"))

        for lesson in data["lessons"]:
            lessons_total_by_currency[lesson["currency_snapshot"]] += parse_money(lesson["price_snapshot"])

        for payment in data["payments"]:
            payments_total_by_currency[payment["currency"]] += parse_money(payment["amount"])

        for currency, amount in lessons_total_by_currency.items():
            balance_total_by_currency[currency] += amount

        for currency, amount in payments_total_by_currency.items():
            balance_total_by_currency[currency] -= amount

        return {
            "total_students": len(data["students"]),
            "total_lessons": len(data["lessons"]),
            "lessons_total_by_currency": dict(lessons_total_by_currency),
            "payments_total_by_currency": dict(payments_total_by_currency),
            "balance_total_by_currency": dict(balance_total_by_currency),
        }

    def get_student_summary(self, student_id):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        lessons = [lesson for lesson in data["lessons"] if lesson["student_id"] == student_id]
        payments = [payment for payment in data["payments"] if payment["student_id"] == student_id]

        total_earned = sum((parse_money(lesson["price_snapshot"]) for lesson in lessons), Decimal("0"))
        total_paid = sum((parse_money(payment["amount"]) for payment in payments), Decimal("0"))
        balance = total_earned - total_paid

        total_minutes = sum(lesson["duration"] for lesson in lessons)
        average_duration = total_minutes / len(lessons) if lessons else 0

        lesson_dates = sorted(lesson["date"] for lesson in lessons)
        first_lesson_date = lesson_dates[0] if lesson_dates else "—"
        last_lesson_date = lesson_dates[-1] if lesson_dates else "—"

        return {
            "student_name": student["name"],
            "price_per_lesson": student["price_per_lesson"],
            "currency": student["currency"],
            "notes": student.get("notes", ""),
            "total_lessons": len(lessons),
            "total_minutes": total_minutes,
            "average_duration": average_duration,
            "total_earned": total_earned,
            "total_paid": total_paid,
            "balance": balance,
            "status": self.get_balance_status(balance),
            "first_lesson_date": first_lesson_date,
            "last_lesson_date": last_lesson_date,
        }
