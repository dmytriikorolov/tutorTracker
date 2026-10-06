# Tutor Tracker

A lightweight terminal application for managing private tutoring sessions, payments, student balances, and lesson history.

The project started as a small personal tool and evolved into a more structured Python application with separated storage, services, CLI logic, validation, and tests.

## Features

- Manage students, lessons, and payments
- Track outstanding balances per student
- Monthly and overall summaries
- Search students by name or ID
- Edit and delete lessons and payments
- Command aliases and tab completion
- Persistent local JSON storage
- Atomic writes to reduce the risk of data corruption
- `Decimal`-based money calculations
- Backward compatibility with older stored numeric values
- Automated tests for core service logic

## Project Structure

```text
.
├── app.py
├── cli.py
├── cli_views.py
├── constants.py
├── exceptions.py
├── models.py
├── services.py
├── storage.py
└── tests/
```

The application is split into several layers:

- `cli.py` handles user interaction
- `services.py` contains business logic
- `storage.py` handles persistence
- `models.py` defines application data structures
- `tests/` contains automated tests

## Running the Application

Requires Python 3.

```bash
git clone https://github.com/dmytriikorolov/tutorTracker.git
cd tutorTracker
python app.py
```

On first launch, the application automatically creates a local:

```text
tracker_data.json
```

This file contains the user's private tutoring data and is intentionally excluded from Git.

## Example

```text
Tutor Tracker — Math Lessons
Type "help" to see commands.

> add_student
Student name: Alice
Price per lesson: 25
Currency: EUR
Notes:
Student added

> add_lesson
Student id or name: Alice
Matched student: 1 - Alice
Date (YYYY-MM-DD, leave empty for today):
Duration (minutes): 60
Comment: algebra
Lesson added

> balance
Student id or name: Alice
Matched student: 1 - Alice
Alice: 25.00 EUR owed to you
```

## Commands

Useful commands include:

```text
students
find_student
add_student

add_lesson
lessons
edit_lesson
delete_lesson

add_payment
payments
edit_payment
delete_payment

balance
student_summary
month_summary
summary
```

Run:

```text
help
```

inside the application to see the complete command list.

## Money Handling

All new monetary values are stored and calculated using Python's `Decimal` type instead of floating-point arithmetic.

This avoids common precision problems when working with money.

Older data containing numeric JSON values such as:

```json
500.0
```

is still supported.

## Data Safety

User data is stored locally in `tracker_data.json`.

The file is excluded from the repository through `.gitignore`.

Writes are atomic: the application first writes data to a temporary file and then replaces the existing database file. This reduces the risk of leaving corrupted JSON if the process is interrupted during a save.

## Tests

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

or:

```bash
pytest -q
```

## Motivation

I originally built Tutor Tracker to replace manual notes for tutoring sessions and payments with a small tool tailored to my own workflow.

The project also became an exercise in improving a simple script into a more maintainable application with clearer separation of concerns, validation, persistence, and testing.
