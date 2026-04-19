from dataclasses import dataclass

@dataclass
class Student:
    id: int
    name: str
    price_per_lesson: str
    currency: str
    notes: str = ""

@dataclass
class Lesson:
    id: int
    student_id: int
    date: str
    duration: int
    comment: str
    price_snapshot: str
    currency_snapshot: str

@dataclass
class Payment:
    id: int
    student_id: int
    date: str
    amount: str
    currency: str
    comment: str = ""
