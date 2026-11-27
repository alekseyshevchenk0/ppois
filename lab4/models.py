from dataclasses import dataclass


@dataclass
class Student:
    name: str
    grade: float

    def __lt__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.grade < other.grade

    def __le__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.grade <= other.grade

    def __gt__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.grade > other.grade

    def __ge__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.grade >= other.grade

    def __str__(self):
        return f"{self.name}: {self.grade:g}"
