from Code.Member import Gender
from Code.Member import Member
from Code.Birthday import Birthday
from datetime import datetime
import enum
import re

class Filter(enum.Enum):
    Age = 1
    Gender = 2
    Birthday = 3

def FilterMember(member_list, filter_type, filter_args):
    filtered = []
    if(filter_type == Filter.Age):
        # x as age => x<32 || x>=15
        filtered = filter(lambda member: eval(filter_args.replace(
            "x", "member.age")), member_list)
        return list(filtered)
    elif(filter_type == Filter.Birthday):
        # x as birthday => x<(day.month.year)
        dates = re.findall('\((.*?)\)', filter_args)
        for date in dates:
            parts = date.replace("(", "").replace(")", "").split('.')
            filter_args = filter_args.replace(
                date, "Birthday("+parts[0]+","+parts[1]+","+parts[2]+")")

        filtered = filter(lambda member: eval(filter_args.replace(
            "x", "member.birthday")), member_list)
        return list(filtered)
    elif(filter_type == Filter.Gender):
        # x as gender => Gender.Male

        filtered = filter(lambda member: member.gender ==
                          eval(filter_args), member_list)
        return list(filtered)
    else:
        raise Exception