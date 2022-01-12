from Birthday import Birthday


class Member:
    def __init__(self, name: str, surname: str, age: int, birthday=None, gender=None):
        # member_layer_level: int,
        self.name = name
        self.surname = surname
        self.age = age
        if birthday is None or isinstance(birthday, Birthday):
            self.birthday = birthday
        elif isinstance(birthday, str):
            self.birthday = Birthday(birthday)
        self.gender = gender
        # self.member_layer_level = member_layer_level

    # def check_level(self):
    #     return self.member_layer_level

    def full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.full_name()
