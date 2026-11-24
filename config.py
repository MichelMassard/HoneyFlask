import os

from dotenv import load_dotenv

# Legge il file .env (se esiste) e mette i valori nelle variabili d'ambiente
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///honeypot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
