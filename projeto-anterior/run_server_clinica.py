"""
Inicia o servidor local do Django (Clínica Agenda) na porta 8001 com banco SQLite local
já populado para os testes de desempenho (Locust) e funcionais (Selenium).
"""
import os
import sys
from pathlib import Path

_LOCAL_BACKEND = Path(__file__).resolve().parent / "backend"
DJANGO_DIR = _LOCAL_BACKEND if _LOCAL_BACKEND.exists() else (Path(__file__).resolve().parents[2] / "Teste-Tecnico_Backend-Django")
sys.path.insert(0, str(DJANGO_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")

import django
from django.conf import settings

if os.getenv("USE_SQLITE", "1") == "1":
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DJANGO_DIR / "db_teste_local.sqlite3"),
        "OPTIONS": {"timeout": 30},
    }

django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    porta = os.getenv("PORTA_CLINICA", "8001")
    execute_from_command_line(["manage.py", "runserver", f"127.0.0.1:{porta}", "--noreload"])
