import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2
import sqlparse
from colorama import Fore, Style, init
from config import DB_CONFIG, FILE_CONFIG, LOG_CONFIG

# Ініціалізація colorama та логування
init(autoreset=True)
logging.basicConfig(**LOG_CONFIG)
logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Кастомний JSON енкодер для обробки datetime об'єктів"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class SQLValidator:
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, Optional[str]]:
        """Перевіряє синтаксис SQL запиту"""
        try:
            parsed = sqlparse.parse(query)
            if not parsed:
                return False, "Порожній запит"
            return True, None
        except Exception as e:
            return False, f"Помилка валідації SQL: {str(e)}"


def get_operation_message(query: str, affected: int) -> str:
    """Повертає детальне повідомлення про результат операції"""
    query_type = query.strip().upper().split()[0]

    messages = {
        "SELECT": f"Отримано {affected} записів",
        "INSERT": f"Створено {affected} записів",
        "UPDATE": f"Оновлено {affected} записів",
        "DELETE": f"Видалено {affected} записів",
    }
    return messages.get(query_type, f"Оброблено {affected} записів")


class ResultWriter:
    """Клас для роботи з файлами результатів"""

    def __init__(self):
        self.success_file = FILE_CONFIG["success_file"]
        self.error_file = FILE_CONFIG["error_file"]
        self.success_results = []
        self.error_results = []

    def append_result(self, result: Dict, is_success: bool):
        """Додає результат у відповідний список та зберігає у файл"""
        if is_success:
            self.success_results.append(result)
            self._save_results(self.success_file, self.success_results)
        else:
            self.error_results.append(result)
            if self.error_results:  # Зберігаємо файл помилок, тільки якщо є помилки
                self._save_results(self.error_file, self.error_results)

    def _save_results(self, file_path: Path, results: List[Dict]):
        """Зберігає результати у файл"""
        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

            # Розширене логування
            log_msg = [
                f"{'='*50}",
                f"Оновлено файл: {file_path}",
                f"Кількість записів: {len(results)}",
                f"{'='*50}",
            ]
            logger.info("\n".join(log_msg))
        except Exception as e:
            logger.error(f"Помилка збереження у файл {file_path}: {e}")

    def cleanup(self):
        """Видаляє порожній файл з помилками"""
        if not self.error_results and self.error_file.exists():
            self.error_file.unlink()
            logger.info(f"Видалено порожній файл помилок: {self.error_file}")


def print_colored(text: str, color: Fore, bold: bool = False) -> None:
    """Виводить текст з кольором"""
    if bold:
        print(f"{Style.BRIGHT}{color}{text}{Style.RESET_ALL}")
    else:
        print(f"{color}{text}{Style.RESET_ALL}")


def execute_query(
    cursor: psycopg2.extensions.cursor,
    query: str,
    description: str,
    writer: ResultWriter,
) -> Dict:
    """Виконує запит і повертає результат"""
    logger.info(f"\nВиконання запиту:\n{query}")

    try:
        is_valid, error = SQLValidator.validate_query(query)
        if not is_valid:
            raise ValueError(error)

        start_time = datetime.now()
        cursor.execute(query)
        execution_time = (datetime.now() - start_time).total_seconds()

        is_select = query.strip().upper().startswith("SELECT")
        result = cursor.fetchall() if is_select else None
        affected = len(result) if is_select else cursor.rowcount

        message = get_operation_message(query, affected)

        response = {
            "description": description,
            "query": query,
            "status": "success",
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "affected_rows": affected,
            "message": message,
            "execution_time": execution_time,
            "result": result,
        }

        writer.append_result(response, True)
        return response

    except Exception as e:
        error_response = {
            "description": description,
            "query": query,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "affected_rows": 0,
            "result": None,
        }
        writer.append_result(error_response, False)
        return error_response


def parse_sql_file() -> List[Tuple[str, str]]:
    """Читає та валідує SQL файл"""
    sql_file = FILE_CONFIG["sql_file"]
    if not sql_file.exists():
        raise FileNotFoundError(f"Файл {sql_file} не знайдено")

    content = sql_file.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("SQL файл порожній")

    queries = []
    invalid_queries = []
    blocks = [block.strip() for block in content.split("--") if block.strip()]

    for i, block in enumerate(blocks, 1):
        parts = block.split("\n", 1)
        if len(parts) != 2:
            invalid_queries.append((i, "Неправильний формат блоку"))
            continue

        description = f"--{parts[0].strip()}"
        query = parts[1].strip()

        if not query:
            invalid_queries.append((i, "Порожній запит"))
            continue

        # Валідація запиту
        is_valid, error = SQLValidator.validate_query(query)
        if is_valid:
            queries.append((description, query))
        else:
            invalid_queries.append((i, f"Помилка валідації: {error}"))

    # Виведення результатів валідації
    print_colored("\nРезультати перевірки SQL запитів:", Fore.CYAN, bold=True)
    print_colored(
        f"Знайдено {len(queries)} валідних запитів з {len(blocks)} загалом",
        Fore.GREEN if len(queries) == len(blocks) else Fore.YELLOW,
    )

    if invalid_queries:
        print_colored("\nВиявлено невалідні запити:", Fore.YELLOW)
        for block_num, error in invalid_queries:
            print_colored(f"Блок #{block_num}: {error}", Fore.RED)
        print()  # Порожній рядок (для кращої читабельності)

    if not queries:
        raise ValueError("Не знайдено валідних SQL запитів")

    return queries


def main():
    """Основна функція програми"""
    start_time = datetime.now()
    logger.info(f"Початок виконання скрипту: {start_time.isoformat()}")

    try:
        # Спочатку валідуємо всі запити
        queries = parse_sql_file()

        writer = ResultWriter()
        with psycopg2.connect(**DB_CONFIG) as conn, conn.cursor() as cur:
            for i, (description, query) in enumerate(queries, 1):
                print_colored(f"\nЗапит {i}/{len(queries)}:", Fore.CYAN, bold=True)
                print_colored("Опис:", Fore.GREEN)
                print(description)
                print_colored("SQL:", Fore.GREEN)
                print(query)

                if input(
                    f"\n{Fore.YELLOW}Виконати цей запит? (N/n для відміни, 'Enter'/Y/y для підтвердження): {Style.RESET_ALL}"
                ).lower() in ("n", "no"):
                    logger.info(f"Запит #{i} пропущено користувачем")
                    print_colored("Запит пропущено", Fore.YELLOW)
                    continue

                result = execute_query(cur, query, description, writer)
                print_colored("\nРезультат:", Fore.GREEN, bold=True)
                print(
                    json.dumps(
                        result, ensure_ascii=False, indent=2, cls=DateTimeEncoder
                    )
                )

                if result["status"] == "success":
                    conn.commit()
                    print_colored(f"\n{result['message']}", Fore.GREEN)
                else:
                    conn.rollback()
                    print_colored(f"\nПомилка: {result['error']}", Fore.RED)

        # Очищення в кінці роботи
        writer.cleanup()
        logger.info("Скрипт завершено успішно")
        print_colored("\nОбробка всіх запитів завершена!", Fore.GREEN, bold=True)

    except Exception as e:
        logger.error(f"Критична помилка: {e}")
        print_colored(f"Помилка: {e}", Fore.RED)
    finally:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Загальний час виконання: {execution_time:.3f} сек.")


if __name__ == "__main__":
    main()
