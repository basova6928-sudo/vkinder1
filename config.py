from dotenv import load_dotenv
import os

load_dotenv()

GROUP_TOKEN = os.getenv("GROUP_TOKEN")
USER_TOKEN = os.getenv("USER_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
