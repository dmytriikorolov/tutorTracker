Tutor Tracker — Math Lessons
Author: Dmytrii Korolyov

Terminal application to track tutoring students, lessons, payments, and balances.

## Run

```bash
python app.py
```

The app stores data in `tracker_data.json` in the project directory.

## Current Features

- Add students with lesson price, currency, and notes
- Find students by name with `find_student`
- Use student name or student ID in the main student-specific flows
- Add lessons with optional custom date
- List, edit, and delete lessons
- Add payments with optional custom date
- List, edit, and delete payments
- Show student balances
- Show per-student summary
- Show current month summary
- Show overall summary
- Use `Decimal`-based money calculations for correct financial totals
- Safely read older JSON data that still contains numeric money values

## Commands

- `help` : show all commands
- `students` : show all students with price, lesson count, last lesson date, and balance
- `find_student` : search students by partial name
- `add_student` : add a new student
- `add_lesson` : add a lesson for a student
- `lessons` : list lessons for a student
- `edit_lesson` : edit a lesson by lesson ID
- `delete_lesson` : delete a lesson by lesson ID
- `add_payment` : add a payment for a student
- `payments` : list payments for a student
- `edit_payment` : edit a payment by payment ID
- `delete_payment` : delete a payment by payment ID
- `balance` : show balance for one student
- `student_summary` : show detailed summary for one student
- `month_summary` : show current month activity
- `summary` : show overall totals
- `exit` or `quit` : leave the program

## Student Lookup

For these commands, you can type either the student ID or the student name:

- `add_lesson`
- `lessons`
- `add_payment`
- `payments`
- `balance`
- `student_summary`

Lookup behavior:

- Exact name match is preferred
- Partial name match works if it identifies one student uniquely
- If multiple students match, the app asks you to use the ID
- If no exact or partial match is found, the app may suggest close names

Example:

```text
> add_lesson
Student id or name: Alice
Matched student: 1 - Alice
Date (YYYY-MM-DD, leave empty for today): 2026-04-10
Duration (minutes): 60
Comment: geometry
Lesson added
```

## Editing Records

When editing lessons or payments:

- Press `Enter` on a field to keep the current value
- Type `-` for the comment field to clear the comment

Delete commands require typing `DELETE` as confirmation.

## Money Handling

- New and updated money values are saved as strings like `"25.00"`
- Calculations use `Decimal`, not `float`
- Existing JSON files with older numeric values such as `25.0` are still supported

## Data Safety

Saves are atomic:

- Data is written to a temporary file first
- The temporary file is then moved into place

This reduces the risk of corrupting `tracker_data.json` if the app stops during a save.

## Tests

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

Or with pytest:

```bash
pytest -q tests/test_services.py -p no:cacheprovider
```
