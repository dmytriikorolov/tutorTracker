from dataclasses import dataclass

@dataclass
class Student:
    id: int
    name: str
    price_per_lesson: float
    currency: str
    notes: str = ""

@dataclass
class Lesson:
    id: int
    student_id: int
    date: str
    duration: int
    comment: str
    price_snapshot: float
    currency_snapshot: str

@dataclass
class Payment:
    id: int
    student_id: int
    date: str
    amount: float
    currency: str
    comment: str = ""