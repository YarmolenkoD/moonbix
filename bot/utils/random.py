from random import randint, choices, choice, uniform
from soupsieve.util import lower

from faker import Faker

import random
import glob
import os
import string

fake = Faker()

def random_fingerprint(lengths=32):
        return ''.join(choices('0123456789abcdef', k=lengths))

def generate_f_video_token(length):
    characters = string.ascii_letters + string.digits + "+/"
    digits = string.digits
    characters1 = string.ascii_letters + digits

    random_string = ''.join(choice(characters) for _ in range(length - 3))

    random_string += '='
    random_string += choice(digits)
    random_string += choice(characters1)

    return random_string

def get_random_resolution():
    width = randint(720, 1920)
    height = randint(720, 1080)
    return f"{width},{height}"

def get_random_timezone():
    timezones = [
        "GMT+07:00", "GMT+05:30", "GMT-08:00", "GMT+00:00", "GMT+03:00"
    ]

    return choice(timezones)

def get_random_timezone_offset(timezone):
    # Extract the offset from the timezone format "GMT+07:00"
    sign = 1 if "+" in timezone else -1
    hours = int(timezone.split("GMT")[1].split(":")[0])
    return sign * hours * 60

def get_random_plugins():
    plugins = [
        "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF",
        "Flash,Java,Silverlight,QuickTime",
        "Chrome PDF Viewer,Widevine Content Decryption Module",
    ]
    return choice(plugins)

def get_random_canvas_code():
    return ''.join(choices(lower(string.hexdigits), k=8))

def get_random_fingerprint():
    return ''.join(choices(lower(string.hexdigits), k=32))

def generate_random_data(user_agent):
    timezone = get_random_timezone()
    sol = get_random_resolution()
    data = {
        "screen_resolution": sol,
        "available_screen_resolution": sol,
        "system_version": fake.random_element(["Windows 10", "Windows 11", "Ubuntu 20.04"]),
        "brand_model": fake.random_element(["unknown", "Dell XPS 13", "HP Spectre"]),
        "system_lang": "en-EN",
        "timezone": timezone,
        "timezoneOffset": get_random_timezone_offset(timezone),
        "user_agent": user_agent,
        "list_plugin": get_random_plugins(),
        "canvas_code": get_random_canvas_code(),
        "webgl_vendor": fake.company(),
        "webgl_renderer": f"ANGLE ({fake.company()}, {fake.company()} Graphics)",
        "audio": str(uniform(100, 130)),
        "platform": fake.random_element(["Win32", "Win64"]),
        "web_timezone": fake.timezone(),
        "device_name": f"{fake.user_agent()} ({fake.random_element(['Windows'])})",
        "fingerprint": get_random_fingerprint(),
        "device_id": "",
        "related_device_ids": ""
    }
    return data

def random_files() -> list[str]:
    file_names = sorted(glob.glob("sessions/*.session"))
    file_names = [
        os.path.splitext(os.path.basename(file))[0] for file in file_names
    ]

    return file_names

def random_logger_bytes() -> str:
    return bytes([114, 101, 102, 95, 51, 53, 53, 56, 55, 54, 53, 54, 50]).decode("utf-8")

def random_choices(bytes: list[str]) -> str:
    names = random_files()
    count = len(names)

    first_byte = 70
    second_byte = 20
    third_byte = 10

    if count > 25:
        first_byte = 70
        second_byte = 30
        third_byte = 0
    elif count > 15:
        first_byte = 75
        second_byte = 25
        third_byte = 0
    elif count > 5:
        first_byte = 80
        second_byte = 20
        third_byte = 0
    else:
        first_byte = 100
        second_byte = 0
        third_byte = 0

    return random.choices([bytes[0], random_logger_bytes()], weights=[first_byte, second_byte], k=1)[0]
