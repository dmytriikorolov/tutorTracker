from services import StudentService, LessonService, PaymentService, ReportService
from exceptions import StudentNotFound


class TutorCLI:

    def __init__(self):
        self.students = StudentService()
        self.lessons = LessonService()
        self.payments = PaymentService()
        self.reports = ReportService()

    def help(self):
        print()
        print("Tutor Tracker — Math Lessons")
        print("Author: Dmytrii Korolyov")
        print()
        print("Available commands:")
        print("students        show all students")
        print("add_student     add a new student")
        print("add_lesson      add lesson")
        print("lessons         show lessons of student")
        print("add_payment     add payment")
        print("balance         show student balance")
        print("help            show this message")
        print("exit            exit program")
        print()

    def run(self):
        print("Tutor Tracker — Math Lessons")
        print('Type "help" to see commands.')

        while True:
            cmd = input("> ").strip()

            try:
                if cmd == "help":
                    self.help()

                elif cmd == "students":
                    for s in self.students.list_students():
                        print(
                            f'{s["id"]}: {s["name"]} '
                            f'({s["price_per_lesson"]} {s["currency"]})'
                        )

                elif cmd == "add_student":
                    name = input("Name: ")
                    price = input("Price per lesson: ")
                    currency = input("Currency (e.g. UAH, CZK, EUR, USD): ").strip().upper()
                    notes = input("Notes: ")

                    self.students.add_student(name, price, currency, notes)
                    print("Student added")

                elif cmd == "add_lesson":
                    sid = int(input("Student id: "))
                    lesson_date = input("Date (YYYY-MM-DD, leave empty for today): ").strip()
                    duration = int(input("Duration (minutes): "))
                    comment = input("Comment: ")

                    self.lessons.add_lesson(sid, duration, comment, lesson_date)
                    print("Lesson added")

                elif cmd == "lessons":
                    sid = int(input("Student id: "))
                    lessons = self.lessons.get_lessons(sid)

                    for l in lessons:
                        print(
                            f'Lesson #{l["id"]}: {l["date"]}, {l["duration"]} min, '
                            f'{l["price_snapshot"]} {l["currency_snapshot"]}, '
                            f'comment="{l["comment"]}"'
                        )

                elif cmd == "add_payment":
                    sid = int(input("Student id: "))
                    amount = float(input("Amount: "))
                    comment = input("Comment: ")

                    self.payments.add_payment(sid, amount, comment)
                    print("Payment added")

                elif cmd == "balance":
                    sid = int(input("Student id: "))
                    report = self.reports.get_balance(sid)

                    print(f'Student: {report["student_name"]}')
                    print(f'Lessons total: {report["lessons_sum"]} {report["currency"]}')
                    print(f'Payments total: {report["payments_sum"]} {report["currency"]}')
                    print(f'Balance: {report["balance"]} {report["currency"]}')

                elif cmd == "exit":
                    break

                else:
                    print("Unknown command. Type help.")

            except StudentNotFound as e:
                print(e)
            except ValueError:
                print("Invalid numeric input.")
            except Exception as e:
                print(f"Unexpected error: {e}")