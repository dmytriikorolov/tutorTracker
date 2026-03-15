from models import Student, Lesson, Payment
from storage import load_data, save_data
from exceptions import StudentNotFound
from datetime import date, datetime
from collections import defaultdict

class StudentService:

    def list_students(self):
        return load_data()["students"]

    def add_student(self, name, price, currency, notes=""):
        data = load_data()
        new_id = len(data["students"]) + 1

        student = Student(
            id=new_id,
            name=name,
            price_per_lesson=float(price),
            currency=currency.upper(),
            notes=notes
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
        actual_date = self.validate_date(lesson_date)

        lesson = Lesson(
            id=new_id,
            student_id=student_id,
            date=actual_date,
            duration=duration,
            comment=comment,
            price_snapshot=student["price_per_lesson"],
            currency_snapshot=student["currency"]
        )

        data["lessons"].append(lesson.__dict__)
        save_data(data)

    def get_lessons(self, student_id):
        data = load_data()
        return [l for l in data["lessons"] if l["student_id"] == student_id]

    @staticmethod
    def validate_date(date_str: str) -> str:
        if not date_str:
            return str(date.today())

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")


class PaymentService:

    def add_payment(self, student_id, amount, comment=""):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        new_id = len(data["payments"]) + 1

        payment = Payment(
            id=new_id,
            student_id=student_id,
            date=str(date.today()),
            amount=float(amount),
            currency=student["currency"],
            comment=comment
        )

        data["payments"].append(payment.__dict__)
        save_data(data)

    def get_payments(self, student_id):
        data = load_data()
        return [p for p in data["payments"] if p["student_id"] == student_id]



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

        lessons = [l for l in data["lessons"] if l["student_id"] == student_id]
        payments = [p for p in data["payments"] if p["student_id"] == student_id]

        lessons_sum = sum(l["price_snapshot"] for l in lessons)
        payments_sum = sum(p["amount"] for p in payments)
        balance = lessons_sum - payments_sum

        return {
            "student_name": student["name"],
            "currency": student["currency"],
            "lessons_sum": lessons_sum,
            "payments_sum": payments_sum,
            "balance": balance,
            "status": self.get_balance_status(balance),
        }

    def get_current_month_summary(self):
        data = load_data()
        today = date.today()
        current_month = today.strftime("%Y-%m")

        lessons_this_month = [
            l for l in data["lessons"]
            if l["date"].startswith(current_month)
        ]

        payments_this_month = [
            p for p in data["payments"]
            if p["date"].startswith(current_month)
        ]

        earned_by_currency = defaultdict(float)
        received_by_currency = defaultdict(float)
        lessons_per_student = defaultdict(int)
        earned_per_student = defaultdict(lambda: {"currency": None, "amount": 0.0})

        for lesson in lessons_this_month:
            currency = lesson["currency_snapshot"]
            earned_by_currency[currency] += lesson["price_snapshot"]
            lessons_per_student[lesson["student_id"]] += 1

            student = next((s for s in data["students"] if s["id"] == lesson["student_id"]), None)
            if student:
                earned_per_student[student["name"]]["currency"] = currency
                earned_per_student[student["name"]]["amount"] += lesson["price_snapshot"]

        for payment in payments_this_month:
            currency = payment["currency"]
            received_by_currency[currency] += payment["amount"]

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

        lessons_total_by_currency = defaultdict(float)
        payments_total_by_currency = defaultdict(float)
        balance_total_by_currency = defaultdict(float)

        for lesson in data["lessons"]:
            lessons_total_by_currency[lesson["currency_snapshot"]] += lesson["price_snapshot"]

        for payment in data["payments"]:
            payments_total_by_currency[payment["currency"]] += payment["amount"]

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