import psycopg2
from config.config import Config

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="Chatbot.user.db",
        user="postgres",
        password=Config.POSTGRES_DB_PASSWORD

    )