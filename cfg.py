import os
import platform
if platform.system() in ("Darwin","Windows"):
    TOKEN = "1634628039:AAGbIRu7yNWoIPfSbT8cqc9bq9ebxNc0oRs"
    DB_USER = "tg_bot"
    DB_PASSWORD = "Aa@12345678"
else:
    TOKEN = os.environ.get("TELETASK_TOKEN")
    WEB_SERVER_HOST = "127.0.0.2"
    WEB_SERVER_PORT = 8080
    WEBHOOK_PATH = "/teletask_bot/"
    WEBHOOK_SECRET = os.environ.get("TELETASK_SECRET")
    WEBHOOK_URL = os.environ.get("BASE_URL")
    SSL_CERT = os.environ.get("SSL_CERT")
    SSL_KEY = os.environ.get("SSL_CERT_KEY")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

DB_HOST = "localhost"
DB_PATH = "TeleTask"
