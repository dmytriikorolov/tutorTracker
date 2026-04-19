APP_TITLE = "Tutor Tracker — Math Lessons"
APP_AUTHOR = "Dmytrii Korolov"
PROMPT = "> "

CMD_HELP = "help"
CMD_STUDENTS = "students"
CMD_ADD_STUDENT = "add_student"
CMD_ADD_LESSON = "add_lesson"
CMD_LESSONS = "lessons"
CMD_EDIT_LESSON = "edit_lesson"
CMD_DELETE_LESSON = "delete_lesson"
CMD_ADD_PAYMENT = "add_payment"
CMD_PAYMENTS = "payments"
CMD_EDIT_PAYMENT = "edit_payment"
CMD_DELETE_PAYMENT = "delete_payment"
CMD_FIND_STUDENT = "find_student"
CMD_STUDENT_SUMMARY = "student_summary"
CMD_BALANCE = "balance"
CMD_MONTH_SUMMARY = "month_summary"
CMD_SUMMARY = "summary"
CMD_EXIT = "exit"
CMD_QUIT = "quit"

EXIT_COMMANDS = {CMD_EXIT, CMD_QUIT}

COMMAND_DESCRIPTIONS = {
    CMD_STUDENTS: "show all students",
    CMD_ADD_STUDENT: "add a new student",
    CMD_ADD_LESSON: "add lesson",
    CMD_LESSONS: "show lessons of student",
    CMD_EDIT_LESSON: "edit a lesson by id",
    CMD_DELETE_LESSON: "delete a lesson by id",
    CMD_ADD_PAYMENT: "add payment",
    CMD_PAYMENTS: "show payments of student",
    CMD_EDIT_PAYMENT: "edit a payment by id",
    CMD_DELETE_PAYMENT: "delete a payment by id",
    CMD_FIND_STUDENT: "find students by name",
    CMD_STUDENT_SUMMARY: "show summary for one student",
    CMD_BALANCE: "show student balance",
    CMD_MONTH_SUMMARY: "show current month summary",
    CMD_SUMMARY: "show overall summary statistics",
    CMD_HELP: "show this message",
    CMD_EXIT: "exit program",
    CMD_QUIT: "exit program",
}
