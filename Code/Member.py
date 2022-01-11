from Birthday import Birthday


class Member:
    def __init__(self, name: str, surname: str, age: int, gender: str,
                 member_layer_level: int, day=0, month=0, year=0):
        self.name = name
        self.surname = surname
        self.age = age
        self.birthday = Birthday(day, month, year)
        self.gender = gender
        self.member_layer_level = member_layer_level

    def check_level(self):
        return self.member_layer_level

