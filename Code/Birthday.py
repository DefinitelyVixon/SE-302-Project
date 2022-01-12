class Birthday:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            args = args[0].split("/")
        self.day = args[0]
        self.month = args[1]
        self.year = args[2]

    def date_to_string(self):
        return f"{self.day}/{self.month}/{self.year}"

    def __str__(self):
        return self.date_to_string()
