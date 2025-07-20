import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from colorama import Fore, Style, init

# Ініціалізація colorama
init()

# Отримання шляху до директорії скрипта
SCRIPT_DIR = Path(__file__).parent.absolute()

# MongoDB налаштування
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "cats_database")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "cats")
MONGO_TIMEOUT = 5000  # мілісекунди

# Custom log levels
logging.SUCCESS = 25  # Between INFO and WARNING
logging.addLevelName(logging.SUCCESS, "SUCCESS")

# Налаштування логування
LOG_DIR = SCRIPT_DIR / "logs"
LOG_FORMAT = "%(asctime)s - %(levelname)-8s - %(message)s"
LOG_LEVEL = logging.INFO


class CustomLogger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.SUCCESS):
            self._log(logging.SUCCESS, msg, args, **kwargs)


# Кольорові схеми для повідомлень
COLORS = {
    "success": Fore.GREEN,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "header": Fore.CYAN,
    "menu": Fore.BLUE,
    "reset": Style.RESET_ALL,
}

# Шаблони повідомлень
MESSAGES = {
    "menu_header": f"{COLORS['header']}=== МЕНЮ УПРАВЛІННЯ КОТЯЧОЮ БАЗОЮ ==={COLORS['reset']}",
    "cat_list_header": f"{COLORS['header']}=== Список усіх котів ==={COLORS['reset']}",
    "cat_list_footer": f"{COLORS['header']}=== Кінець списку ==={COLORS['reset']}",
    "empty_db": f"{COLORS['warning']}База даних порожня. Котів не знайдено.{COLORS['reset']}",
    "invalid_choice": f"{COLORS['warning']}Неправильний вибір. Спробуйте знову.{COLORS['reset']}",
    "exit": f"{COLORS['warning']}Вихід.{COLORS['reset']}",
}

MESSAGES.update(
    {
        "cat_not_found": lambda name: f"{COLORS['warning']}Кота з ім'ям '{name}' не знайдено.{COLORS['reset']}",
        "cat_updated": lambda name: f"{COLORS['success']}Дані кота {name} оновлено.{COLORS['reset']}",
        "cat_added": lambda name: f"{COLORS['success']}Додано нового кота з ім'ям {name}.{COLORS['reset']}",
        "cat_deleted": lambda name: f"{COLORS['success']}Кота з ім'ям {name} видалено.{COLORS['reset']}",
        "db_error": lambda e: f"{COLORS['error']}Помилка бази даних: {e}{COLORS['reset']}",
        "cats_deleted": lambda count: f"{COLORS['success']}Видалено {count} котів.{COLORS['reset']}",
    }
)

MENU_OPTIONS = {
    "1": ("Показати всіх котів", "show_cats"),
    "2": ("Знайти кота за ім'ям", "find_cat"),
    "3": ("Оновити вік кота", "update_cat"),
    "4": ("Додати характеристику до кота", "add_feature"),
    "5": ("Видалити кота за ім'ям", "delete_cat"),
    "6": ("Видалити всіх котів", "delete_all"),
    "7": ("Додати нового кота", "add_cat"),
    "0": ("Вийти", "exit"),
}


def get_log_file():
    """Генерує шлях до файлу логу з часовою міткою"""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return LOG_DIR / f"cats_app_{timestamp}.log"


def setup_logging():
    """Налаштування системи логування"""
    logging.setLoggerClass(CustomLogger)
    logging.basicConfig(filename=get_log_file(), level=LOG_LEVEL, format=LOG_FORMAT)
    logger = logging.getLogger(__name__)
    return logger


def validate_config():
    """Валідація конфігурації"""
    try:
        result = urlparse(MONGO_URI)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Неправильний формат MONGO_URI")

        if not all([DATABASE_NAME, COLLECTION_NAME]):
            raise ValueError(
                "DATABASE_NAME та COLLECTION_NAME не можуть бути порожніми"
            )
    except Exception as e:
        raise ValueError(f"Помилка конфігурації: {e}")


# Валідація конфігурації при імпорті
validate_config()
