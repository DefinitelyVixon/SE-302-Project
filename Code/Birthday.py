class Birthday:
    def __init__(self, day: int, month: int, year: int):
        self.day = day
        self.month = month
        self.year = year

    def date_to_string(self):
        return f"{self.day}/{self.month}/{self.year}"
