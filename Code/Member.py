from Code.Birthday import Birthday
import enum


class Gender(enum.Enum):
    Male = 1
    Female = 2
    NonBinary = 3


class Member:
    def __init__(self, name: str, surname: str, age: int, birthday=None, gender=None, member_id=0):
        self.member_id = member_id
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

    def to_dict(self):
        return {
            "id": self.member_id,
            "name": self.name,
            "surname": self.surname,
            "age": self.age,
            "birthday": str(self.birthday),
            "gender": self.gender
        }
