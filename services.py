
from models import Student, Lesson, Payment
from storage import load_data, save_data
from exceptions import StudentNotFound
from datetime import date

class StudentService:

    def list_students(self):
        return load_data()["students"]

    def add_student(self, name, price, notes=""):
        data = load_data()
        new_id = len(data["students"]) + 1
        student = Student(new_id, name, float(price), notes)
        data["students"].append(student.__dict__)
        save_data(data)

class LessonService:

    def add_lesson(self, student_id, duration, comment=""):
        data = load_data()

        student = next((s for s in data["students"] if s["id"] == student_id), None)
        if not student:
            raise StudentNotFound()

        new_id = len(data["lessons"]) + 1

        lesson = Lesson(
            id=new_id,
            student_id=student_id,
            date=str(date.today()),
            duration=duration,
            comment=comment,
            price_snapshot=student["price_per_lesson"]
        )

        data["lessons"].append(lesson.__dict__)
        save_data(data)

    def get_lessons(self, student_id):
        data = load_data()
        return [l for l in data["lessons"] if l["student_id"] == student_id]

class PaymentService:

    def add_payment(self, student_id, amount, comment=""):
        data = load_data()
        new_id = len(data["payments"]) + 1

        payment = Payment(
            id=new_id,
            student_id=student_id,
            date=str(date.today()),
            amount=float(amount),
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

        lessons = [l for l in data["lessons"] if l["student_id"] == student_id]
        payments = [p for p in data["payments"] if p["student_id"] == student_id]

        lessons_sum = sum(l["price_snapshot"] for l in lessons)
        payments_sum = sum(p["amount"] for p in payments)

        return lessons_sum - payments_sum
