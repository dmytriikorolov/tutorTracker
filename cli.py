from services import StudentService, LessonService, PaymentService, ReportService
from exceptions import StudentNotFound
from constants import (
    CMD_HELP,
    CMD_STUDENTS,
    CMD_ADD_STUDENT,
    CMD_ADD_LESSON,
    CMD_LESSONS,
    CMD_ADD_PAYMENT,
    CMD_BALANCE,
    CMD_MONTH_SUMMARY,
    CMD_SUMMARY,
    CMD_STUDENT_SUMMARY,
    EXIT_COMMANDS,
    PROMPT,
)
from cli_views import (
    print_welcome,
    print_help,
    print_students,
    print_lessons,
    print_balance,
    print_month_summary,
    print_overall_summary,
    print_student_summary,
)


class TutorCLI:

    def __init__(self):
        self.students = StudentService()
        self.lessons = LessonService()
        self.payments = PaymentService()
        self.reports = ReportService()

        self.commands = {
            CMD_HELP: self.handle_help,
            CMD_STUDENTS: self.handle_students,
            CMD_ADD_STUDENT: self.handle_add_student,
            CMD_ADD_LESSON: self.handle_add_lesson,
            CMD_LESSONS: self.handle_lessons,
            CMD_ADD_PAYMENT: self.handle_add_payment,
            CMD_BALANCE: self.handle_balance,
            CMD_MONTH_SUMMARY: self.handle_month_summary,
            CMD_SUMMARY: self.handle_summary,
            CMD_STUDENT_SUMMARY: self.handle_student_summary,
        }

    def run(self):
        print_welcome()

        while True:
            cmd = input(PROMPT).strip()

            if cmd in EXIT_COMMANDS:
                break

            try:
                handler = self.commands.get(cmd)
                if handler is None:
                    print("Unknown command. Type help.")
                    continue

                handler()

            except StudentNotFound as e:
                print(e)
            except ValueError:
                print("Invalid numeric input.")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def handle_help(self):
        print_help()

    def handle_students(self):
        students = self.students.list_students()
        print_students(students)

    def handle_add_student(self):
        name = input("Name: ")
        price = input("Price per lesson: ")
        currency = input("Currency (e.g. UAH, CZK, EUR, USD): ").strip().upper()
        notes = input("Notes: ")

        self.students.add_student(name, price, currency, notes)
        print("Student added")

    def handle_add_lesson(self):
        sid = int(input("Student id: "))
        lesson_date = input("Date (YYYY-MM-DD, leave empty for today): ").strip()
        duration = int(input("Duration (minutes): "))
        comment = input("Comment: ")

        self.lessons.add_lesson(sid, duration, comment, lesson_date)
        print("Lesson added")

    def handle_lessons(self):
        sid = int(input("Student id: "))
        lessons = self.lessons.get_lessons(sid)
        print_lessons(lessons)

    def handle_add_payment(self):
        sid = int(input("Student id: "))
        amount = float(input("Amount: "))
        comment = input("Comment: ")

        self.payments.add_payment(sid, amount, comment)
        print("Payment added")

    def handle_balance(self):
        sid = int(input("Student id: "))
        report = self.reports.get_balance(sid)
        print_balance(report)

    def handle_month_summary(self):
        summary = self.reports.get_current_month_summary()
        print_month_summary(summary)

    def handle_summary(self):
        summary = self.reports.get_overall_summary()
        print_overall_summary(summary, self.reports.get_balance_status)

    def handle_student_summary(self):
        sid = int(input("Student id: "))
        summary = self.reports.get_student_summary(sid)
        print_student_summary(summary)