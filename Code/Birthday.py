import datetime

class Birthday:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            args = args[0].split("/")
        self.day = args[0]
        self.month = args[1]
        self.year = args[2]

    def date_to_string(self):
        return f"{self.day}/{self.month}/{self.year}"

    def as_date_time(self):
        return datetime.datetime(self.year, self.month, self.day)
 
    def __str__(self):
        return self.date_to_string()

    def __lt__(self, other):
        if(self.as_date_time() < other.as_date_time()):
            return True
        return False

    def __le__(self, other):
        if(self.as_date_time() <= other.as_date_time()):
            return True
        return False

    def __gt__(self, other):
        if(self.as_date_time() > other.as_date_time()):
            return True
        return False

    def __ge__(self, other):
        if(self.as_date_time() >= other.as_date_time()):
            return True
        return False

    def __eq__(self, other):
        if(self.as_date_time() == other.as_date_time()):
            return True
        return False

    def __ne__(self, other):
        if(self.as_date_time() != other.as_date_time()):
            return True
        return False
