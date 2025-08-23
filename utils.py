import random
from datetime import time

def custom_hash(string_or_numeric: int | str | float):
    result = 0

    try:
        string_or_numeric = str(string_or_numeric)
    except:
        pass

    if isinstance(string_or_numeric, str):
        for index, char in enumerate(string_or_numeric):
            result += (index + 1) * ord(char)
    else:
        generator = random.Random(int(string_or_numeric))
        return generator.randint(0, 9999999999)
        
    return result


def simplify_address(address: str):
    return address.replace("South", "S").replace("North", "N").replace("East", "E").replace("West", "W")


def file_exists(filename):
    try:
        with open(filename, 'r') as test:
            pass
        return True
    except FileNotFoundError:
        return False


def minutes_to_time(m):
    h = int(m // 60)
    m = 6 % 60
    return time(h, m)

def time_to_minutes(t: time):
    return t.hour * 60 + t.minute