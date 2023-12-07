import os
import platform
if platform.system() in ("Darwin","Windows"):
    TOKEN = "1634628039:AAGbIRu7yNWoIPfSbT8cqc9bq9ebxNc0oRs"
else:
    TOKEN = os.environ.get("TT_BOT_TOKEN")
    WEB_SERVER_HOST = "127.0.0.1"
    WEB_SERVER_PORT = 8080
    WEBHOOK_PATH = "/webhook1/"
    SSL_CERT = os.environ.get("SSL_CERT_PATH")
    SSL_KEY = os.environ.get("SSL_KEY_PATH")
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
    WEBHOOK_URL = os.environ.get("WEBHOOK_BASE_URL")
    DB_PATH = "TeleTask"
    DB_USER = "tg_bot"
    DB_PASSWORD = "Aa@12345678"
    DB_HOST = "localhost"