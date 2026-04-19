from pathlib import Path

try:
    import readline
except ImportError:  # pragma: no cover - platform-specific fallback
    readline = None

from constants import (
    ALIASES_FILE,
    BUILT_IN_ALIASES,
    CMD_ADD_LESSON,
    CMD_ADD_PAYMENT,
    CMD_ADD_STUDENT,
    CMD_BALANCE,
    CMD_DELETE_LESSON,
    CMD_DELETE_PAYMENT,
    CMD_EDIT_LESSON,
    CMD_EDIT_PAYMENT,
    CMD_FIND_STUDENT,
    CMD_HELP,
    CMD_LESSONS,
    CMD_MONTH_SUMMARY,
    CMD_PAYMENTS,
    CMD_STUDENTS,
    CMD_STUDENT_SUMMARY,
    CMD_SUMMARY,
    EXIT_COMMANDS,
    HISTORY_FILE,
    PROMPT,
)
from cli_views import (
    print_balance,
    print_help,
    print_lessons,
    print_month_summary,
    print_overall_summary,
    print_payments,
    print_student_summary,
    print_students,
    print_welcome,
)
from exceptions import (
    AmbiguousStudentMatch,
    InvalidInput,
    LessonNotFound,
    PaymentNotFound,
    StudentNotFound,
)
from services import LessonService, PaymentService, ReportService, StudentService, validate_positive_int


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
            CMD_EDIT_LESSON: self.handle_edit_lesson,
            CMD_DELETE_LESSON: self.handle_delete_lesson,
            CMD_ADD_PAYMENT: self.handle_add_payment,
            CMD_PAYMENTS: self.handle_payments,
            CMD_EDIT_PAYMENT: self.handle_edit_payment,
            CMD_DELETE_PAYMENT: self.handle_delete_payment,
            CMD_FIND_STUDENT: self.handle_find_student,
            CMD_BALANCE: self.handle_balance,
            CMD_MONTH_SUMMARY: self.handle_month_summary,
            CMD_SUMMARY: self.handle_summary,
            CMD_STUDENT_SUMMARY: self.handle_student_summary,
        }
        self.aliases = self.load_aliases()
        self.history_path = Path(HISTORY_FILE)
        self.configure_readline()

    def run(self):
        print_welcome()

        while True:
            raw_cmd = input(PROMPT).strip()
            cmd = self.resolve_command(raw_cmd)

            if cmd in EXIT_COMMANDS:
                break

            try:
                handler = self.commands.get(cmd)
                if handler is None:
                    print("Unknown command. Type help.")
                    continue

                handler()

            except StudentNotFound as exc:
                print(exc)
            except LessonNotFound as exc:
                print(exc)
            except PaymentNotFound as exc:
                print(exc)
            except AmbiguousStudentMatch as exc:
                print(exc)
            except InvalidInput as exc:
                print(exc)
            except Exception as exc:
                print(f"Unexpected error: {exc}")

        self.save_history()

    def load_aliases(self):
        aliases = dict(BUILT_IN_ALIASES)
        alias_path = Path(ALIASES_FILE)
        if not alias_path.exists():
            return aliases

        with open(alias_path, "r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                alias_name, target = self.parse_alias_line(line, line_number)
                aliases[alias_name] = target

        return aliases

    @staticmethod
    def parse_alias_line(line, line_number):
        if "=" in line:
            alias_name, target = (part.strip() for part in line.split("=", 1))
        else:
            parts = line.split()
            if len(parts) == 3 and parts[0] == "alias":
                _, alias_name, target = parts
            elif len(parts) == 2:
                alias_name, target = parts
            else:
                raise InvalidInput(
                    f"Invalid alias config on line {line_number}. "
                    "Use 'alias short full_command', 'short full_command', or 'short=full_command'."
                )

        if not alias_name or not target:
            raise InvalidInput(f"Invalid alias config on line {line_number}.")
        if alias_name == "alias":
            raise InvalidInput(
                f"Invalid alias config on line {line_number}. "
                "The 'alias' keyword must be followed by both alias name and target."
            )

        return alias_name, target

    def resolve_command(self, raw_cmd):
        if not raw_cmd:
            return raw_cmd

        visited = set()
        resolved = raw_cmd

        while resolved in self.aliases:
            if resolved in visited:
                raise InvalidInput(f"Alias loop detected for '{raw_cmd}'.")
            visited.add(resolved)
            resolved = self.aliases[resolved]

        return resolved

    def completer(self, text, state):
        options = sorted({
            *self.commands.keys(),
            *EXIT_COMMANDS,
            *self.aliases.keys(),
        })
        matches = [option for option in options if option.startswith(text)]
        if state < len(matches):
            return matches[state]
        return None

    def configure_readline(self):
        if readline is None:
            return

        readline.set_completer(self.completer)
        doc = (getattr(readline, "__doc__", "") or "").lower()
        if "libedit" in doc:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
        readline.set_history_length(1000)
        try:
            readline.read_history_file(self.history_path)
        except FileNotFoundError:
            pass

    def save_history(self):
        if readline is None:
            return

        try:
            readline.write_history_file(self.history_path)
        except OSError:
            pass

    def prompt_student(self):
        reference = input("Student id or name: ").strip()
        student = self.students.resolve_student(reference)
        print(f'Matched student: {student["id"]} - {student["name"]}')
        return student

    @staticmethod
    def prompt_record_id(label):
        raw_value = input(f"{label} id: ").strip()
        return validate_positive_int(raw_value, field_name=f"{label} id")

    @staticmethod
    def prompt_optional_comment(label):
        value = input(f"{label} comment (blank keeps current, '-' clears): ")
        if value == "":
            return None
        if value.strip() == "-":
            return ""
        return value

    def handle_help(self):
        print_help()

    def handle_students(self):
        students = self.reports.get_students_overview()
        print_students(students)

    def handle_find_student(self):
        query = input("Search student by name: ").strip()
        matching_students = self.students.search_students(query)
        students = self.reports.get_students_overview_for_students(matching_students)
        print_students(students)

    def handle_add_student(self):
        name = input("Name: ")
        price = input("Price per lesson: ")
        currency = input("Currency (e.g. UAH, CZK, EUR, USD): ")
        notes = input("Notes: ")

        self.students.add_student(name, price, currency, notes)
        print("Student added")

    def handle_add_lesson(self):
        student = self.prompt_student()
        lesson_date = input("Date (YYYY-MM-DD, leave empty for today): ").strip()
        duration = input("Duration (minutes): ")
        comment = input("Comment: ")

        self.lessons.add_lesson(student["id"], duration, comment, lesson_date)
        print("Lesson added")

    def handle_lessons(self):
        student = self.prompt_student()
        lessons = self.lessons.get_lessons(student["id"])
        print_lessons(lessons)

    def handle_edit_lesson(self):
        lesson_id = self.prompt_record_id("Lesson")
        lesson = self.lessons.update_lesson(
            lesson_id,
            lesson_date=input("New date (YYYY-MM-DD, blank to keep current): ").strip(),
            duration=input("New duration in minutes (blank to keep current): ").strip(),
            comment=self.prompt_optional_comment("New"),
        )
        print(f'Lesson updated: #{lesson["id"]}')

    def handle_delete_lesson(self):
        lesson_id = self.prompt_record_id("Lesson")
        confirmation = input("Type DELETE to confirm lesson deletion: ").strip()
        if confirmation != "DELETE":
            print("Deletion cancelled.")
            return

        lesson = self.lessons.delete_lesson(lesson_id)
        print(f'Lesson deleted: #{lesson["id"]}')

    def handle_add_payment(self):
        student = self.prompt_student()
        payment_date = input("Payment date (YYYY-MM-DD, leave empty for today): ").strip()
        amount = input("Amount: ")
        comment = input("Comment: ")

        self.payments.add_payment(student["id"], amount, comment, payment_date)
        print("Payment added")

    def handle_payments(self):
        student = self.prompt_student()
        payments = self.payments.get_payments(student["id"])
        print_payments(payments)

    def handle_edit_payment(self):
        payment_id = self.prompt_record_id("Payment")
        payment = self.payments.update_payment(
            payment_id,
            payment_date=input("New payment date (YYYY-MM-DD, blank to keep current): ").strip(),
            amount=input("New amount (blank to keep current): ").strip(),
            comment=self.prompt_optional_comment("New"),
        )
        print(f'Payment updated: #{payment["id"]}')

    def handle_delete_payment(self):
        payment_id = self.prompt_record_id("Payment")
        confirmation = input("Type DELETE to confirm payment deletion: ").strip()
        if confirmation != "DELETE":
            print("Deletion cancelled.")
            return

        payment = self.payments.delete_payment(payment_id)
        print(f'Payment deleted: #{payment["id"]}')

    def handle_balance(self):
        student = self.prompt_student()
        report = self.reports.get_balance(student["id"])
        print_balance(report)

    def handle_month_summary(self):
        summary = self.reports.get_current_month_summary()
        print_month_summary(summary)

    def handle_summary(self):
        summary = self.reports.get_overall_summary()
        print_overall_summary(summary, self.reports.get_balance_status)

    def handle_student_summary(self):
        student = self.prompt_student()
        summary = self.reports.get_student_summary(student["id"])
        print_student_summary(summary)
