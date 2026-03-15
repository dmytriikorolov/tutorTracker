from constants import APP_TITLE, APP_AUTHOR, COMMAND_DESCRIPTIONS


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
        print(f'{s["id"]}: {s["name"]} ({s["price_per_lesson"]} {s["currency"]})')


def print_lessons(lessons):
    if not lessons:
        print("No lessons found.")
        return

    for lesson in lessons:
        print(
            f'Lesson #{lesson["id"]}: {lesson["date"]}, {lesson["duration"]} min, '
            f'{lesson["price_snapshot"]} {lesson["currency_snapshot"]}, '
            f'comment="{lesson["comment"]}"'
        )


def print_balance(report):
    print(f'Student: {report["student_name"]}')
    print(f'Lessons total: {report["lessons_sum"]} {report["currency"]}')
    print(f'Payments total: {report["payments_sum"]} {report["currency"]}')
    print(f'Balance: {report["balance"]} {report["currency"]} ({report["status"]})')


def print_month_summary(summary):
    print(f'Current Month Summary — {summary["month"]}')
    print()
    print(f'Total lessons: {summary["total_lessons"]}')
    print()

    print("Earned from lessons:")
    if summary["earned_by_currency"]:
        for currency, amount in summary["earned_by_currency"].items():
            print(f'- {currency}: {amount}')
    else:
        print("No lessons this month.")

    print()
    print("Payments received:")
    if summary["received_by_currency"]:
        for currency, amount in summary["received_by_currency"].items():
            print(f'- {currency}: {amount}')
    else:
        print("No payments this month.")

    print()
    print("Per-student breakdown:")
    if summary["student_breakdown"]:
        for student_name, info in summary["student_breakdown"].items():
            print(
                f'- {student_name}: '
                f'{info["lessons"]} lessons, '
                f'{info["amount"]} {info["currency"]} earned'
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
            print(f'- {currency}: {amount}')
    else:
        print("No lessons recorded.")

    print()
    print("Payments total:")
    if summary["payments_total_by_currency"]:
        for currency, amount in summary["payments_total_by_currency"].items():
            print(f'- {currency}: {amount}')
    else:
        print("No payments recorded.")

    print()
    print("Current balances:")
    if summary["balance_total_by_currency"]:
        for currency, amount in summary["balance_total_by_currency"].items():
            status = balance_status_getter(amount)
            print(f'- {currency}: {amount} ({status})')
    else:
        print("No balances to show.")