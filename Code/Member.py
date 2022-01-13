from Code.Birthday import Birthday
import enum

class Gender(enum.Enum):
    Male = 1
    Female = 2
    NonBinary = 3

class Member:
    def __init__(self, name: str, surname: str, age: int, birthday=None, gender=None):
        self.name = name
        self.surname = surname
        self.age = age
        if birthday is None or isinstance(birthday, Birthday):
            self.birthday = birthday
        elif isinstance(birthday, str):
            self.birthday = Birthday(birthday)
        self.gender = gender

    def full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.full_name()
