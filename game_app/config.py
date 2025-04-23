from os import getenv

from dotenv import load_dotenv

load_dotenv()

JWT_ALGORITHM = getenv('JWT_ALGORITHM')
JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
YANDEX_MUSIC_TOKEN = getenv('YANDEX_MUSIC_TOKEN')
