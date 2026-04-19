from constants import APP_TITLE, APP_AUTHOR, COMMAND_DESCRIPTIONS
from services import format_money


def print_welcome():
    print(APP_TITLE)
    print('Type "help" to see commands.')


def print_help():
    print()
    print(APP_TITLE)
    print(f"Author: {APP_AUTHOR}")
    print()
    print("Available commands:")

    for command, description in COMMAND_DESCRIPTIONS.items():
        print(f"{command:<15} {description}")

    print()


def print_students(students):
    if not students:
        print("No students found.")
        return

    for s in students:
        print(
            f'{s["id"]}: {s["name"]} | '
            f'price {format_money(s["price_per_lesson"])} {s["currency"]} | '
            f'lessons {s["total_lessons"]} | '
            f'last lesson {s["last_lesson_date"]} | '
            f'balance {format_money(s["balance"])} {s["currency"]} ({s["status"]})'
        )


def print_lessons(lessons):
    if not lessons:
        print("No lessons found.")
        return

    for lesson in lessons:
        print(
            f'Lesson #{lesson["id"]}: {lesson["date"]}, {lesson["duration"]} min, '
            f'{format_money(lesson["price_snapshot"])} {lesson["currency_snapshot"]}, '
            f'comment="{lesson["comment"]}"'
        )


def print_payments(payments):
    if not payments:
        print("No payments found.")
        return

    for payment in payments:
        print(
            f'Payment #{payment["id"]}: {payment["date"]}, '
            f'{format_money(payment["amount"])} {payment["currency"]}, '
            f'comment="{payment["comment"]}"'
        )


def print_balance(report):
    print(f'Student: {report["student_name"]} (id: {report["student_id"]})')
    print(f'Lessons total: {format_money(report["lessons_sum"])} {report["currency"]}')
    print(f'Payments total: {format_money(report["payments_sum"])} {report["currency"]}')
    print(f'Balance: {format_money(report["balance"])} {report["currency"]} ({report["status"]})')


def print_month_summary(summary):
    print(f'Current Month Summary — {summary["month"]}')
    print()
    print(f'Total lessons: {summary["total_lessons"]}')
    print()

    print("Earned from lessons:")
    if summary["earned_by_currency"]:
        for currency, amount in summary["earned_by_currency"].items():
            print(f'- {currency}: {format_money(amount)}')
    else:
        print("No lessons this month.")

    print()
    print("Payments received:")
    if summary["received_by_currency"]:
        for currency, amount in summary["received_by_currency"].items():
            print(f'- {currency}: {format_money(amount)}')
    else:
        print("No payments this month.")

    print()
    print("Per-student breakdown:")
    if summary["student_breakdown"]:
        for student_name, info in summary["student_breakdown"].items():
            print(
                f'- {student_name}: '
                f'{info["lessons"]} lessons, '
                f'{format_money(info["amount"])} {info["currency"]} earned'
            )
    else:
        print("No student activity this month.")


def print_overall_summary(summary, balance_status_getter):
    print("Overall Summary")
    print()
    print(f'Total students: {summary["total_students"]}')
    print(f'Total lessons: {summary["total_lessons"]}')
    print()

    print("Lessons total:")
    if summary["lessons_total_by_currency"]:
        for currency, amount in summary["lessons_total_by_currency"].items():
            print(f'- {currency}: {format_money(amount)}')
    else:
        print("No lessons recorded.")

    print()
    print("Payments total:")
    if summary["payments_total_by_currency"]:
        for currency, amount in summary["payments_total_by_currency"].items():
            print(f'- {currency}: {format_money(amount)}')
    else:
        print("No payments recorded.")

    print()
    print("Current balances:")
    if summary["balance_total_by_currency"]:
        for currency, amount in summary["balance_total_by_currency"].items():
            status = balance_status_getter(amount)
            print(f'- {currency}: {format_money(amount)} ({status})')
    else:
        print("No balances to show.")

def print_student_summary(summary):
    print("Student Summary")
    print()
    print(f'Student: {summary["student_name"]}')
    print(f'Price per lesson: {format_money(summary["price_per_lesson"])} {summary["currency"]}')
    print(f'Notes: {summary["notes"]}')
    print()
    print(f'Total lessons: {summary["total_lessons"]}')
    print(f'Total teaching time: {summary["total_minutes"]} minutes')
    print(f'Average lesson duration: {summary["average_duration"]:.1f} minutes')
    print(f'Total earned: {format_money(summary["total_earned"])} {summary["currency"]}')
    print(f'Total paid: {format_money(summary["total_paid"])} {summary["currency"]}')
    print(
        f'Current balance: {format_money(summary["balance"])} '
        f'{summary["currency"]} ({summary["status"]})'
    )
    print()
    print(f'First lesson: {summary["first_lesson_date"]}')
    print(f'Last lesson: {summary["last_lesson_date"]}')
