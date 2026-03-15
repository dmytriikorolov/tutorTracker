from models import Student, Lesson, Payment
from storage import load_data, save_data
from exceptions import StudentNotFound
from datetime import date


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

    def add_lesson(self, student_id, duration, comment=""):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound(f"Student with id {student_id} not found.")

        new_id = len(data["lessons"]) + 1

        lesson = Lesson(
            id=new_id,
            student_id=student_id,
            date=str(date.today()),
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
        }