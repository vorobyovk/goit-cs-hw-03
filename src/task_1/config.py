from datetime import datetime
from pathlib import Path

# Налаштування бази даних
DB_CONFIG = {
    "dbname": "task_management",
    "user": "postgres",
    "password": "goit",
    "host": "localhost",
    "port": 5432,
}

# Базова директорія
BASE_DIR = Path(__file__).parent

# Часова мітка для файлів
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Налаштування файлів
FILE_CONFIG = {
    "sql_file": BASE_DIR / "requests.sql",
    "success_file": BASE_DIR / f"requests_results_success_{TIMESTAMP}.json",
    "error_file": BASE_DIR / f"requests_results_error_{TIMESTAMP}.json",
    "log_file": BASE_DIR / f"process_requests_{TIMESTAMP}.log",
}

# Налаштування логування
LOG_CONFIG = {
    "filename": FILE_CONFIG["log_file"],
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "encoding": "utf-8",
}
