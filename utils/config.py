import logging
import dotenv
import json
import os


DATABASE_PATH = "data/database.json"
FORMAT = '%(asctime)s - %(levelname)s (%(name)s) - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

path = dotenv.find_dotenv()
if path == "":
    token = input("Write bot's token (https://botfather.t.me): ")
    dotenv.set_key(".env", "TOKEN", token)

TOKEN: str = dotenv.get_key(".env", "TOKEN")

dir_exists = os.path.isdir('data')

if not dir_exists:
    os.mkdir("data")

try:
    with open(DATABASE_PATH, encoding="utf-8") as file:
        json.load(file)
except (json.JSONDecodeError, FileNotFoundError):
    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        file.write('{}')

