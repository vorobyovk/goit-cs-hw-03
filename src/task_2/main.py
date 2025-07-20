from cats_manager import (
    add_feature_to_cat,
    delete_all_cats,
    delete_cat_by_name,
    find_cat_by_name,
    insert_cat,
    show_all_cats,
    update_cat_age,
)
from colorama import init
from config import (
    COLLECTION_NAME,
    COLORS,
    DATABASE_NAME,
    MESSAGES,
    MONGO_URI,
    setup_logging,
)
from db_connection import get_db_connection
from pymongo.errors import ServerSelectionTimeoutError
from validators import validate_age, validate_features, validate_name

# Ініціалізація colorama
init()

# Налаштування логування
logger = setup_logging()


def format_error(message: str) -> str:
    """Форматує повідомлення про помилку"""
    return f"{COLORS['error']}{message}{COLORS['reset']}"


def handle_error(error: Exception) -> None:
    """Обробляє та логує помилки"""
    print(MESSAGES["db_error"](str(error)))
    logger.error(f"Помилка: {error}")


class CatManager:
    """Клас для управління операціями CRUD із котами в MongoDB."""

    def __init__(self, collection):
        self.collection = collection
        self.options = {
            "1": ("Показати всіх котів", self.show_cats),
            "2": ("Знайти кота за ім'ям", self.find_cat),
            "3": ("Оновити вік кота", self.update_cat),
            "4": ("Додати характеристику до кота", self.add_feature),
            "5": ("Видалити кота за ім'ям", self.delete_cat),
            "6": ("Видалити всіх котів", self.delete_all),
            "7": ("Додати нового кота", self.add_cat),
            "0": ("Вийти", None),
        }

    def _log_action(self, action: str, input_data: str, result: str):
        """Логує дії користувача та результати"""
        if "помилка валідації" in result.lower() or "не знайдено" in result.lower():
            logger.warning(
                f"Дія: {action} | Введені дані: {input_data} | Результат: {result}"
            )
        elif "помилка" in result.lower():
            logger.error(
                f"Дія: {action} | Введені дані: {input_data} | Результат: {result}"
            )
        elif "успішно" in result.lower():
            logger.success(
                f"Дія: {action} | Введені дані: {input_data} | Результат: {result}"
            )
        else:
            logger.info(
                f"Дія: {action} | Введені дані: {input_data} | Результат: {result}"
            )

    def show_cats(self):
        cats, error = show_all_cats(self.collection)
        if error:
            handle_error(error)
            return
        if not cats:
            print(MESSAGES["empty_db"])
            return

        print(MESSAGES["cat_list_header"])
        for cat in cats:
            print(f"\nІм'я: {cat['name']}")
            print(f"Вік: {cat['age']} років")
            print("Характеристики:")
            for feature in cat["features"]:
                print(f"  - {feature}")
        print(MESSAGES["cat_list_footer"])

    def find_cat(self):
        name = input("Введіть ім'я кота: ")
        self._log_action("Пошук кота", f"ім'я: {name}", "початок пошуку")

        is_valid, name_value, error = validate_name(name)
        if not is_valid:
            self._log_action(
                "Пошук кота", f"ім'я: {name}", f"помилка валідації: {error}"
            )
            print(format_error(error))
            return

        cat, error = find_cat_by_name(self.collection, name_value)
        if error:
            log_msg = (
                "помилка валідації" if "не знайдено" in error else f"помилка: {error}"
            )
            self._log_action("Пошук кота", f"ім'я: {name_value}", log_msg)
            print(
                MESSAGES["db_error"](error)
                if "не знайдено" not in error
                else MESSAGES["cat_not_found"](name_value)
            )
            return

        features = (
            ", ".join(cat.get("features", []))
            if cat.get("features")
            else "Немає характеристик"
        )
        self._log_action("Пошук кота", f"ім'я: {name_value}", "успішно знайдено")
        print(f"\nІм'я: {cat['name']}")
        print(f"Вік: {cat['age']} років")
        print(f"Характеристики: {features}")

    def update_cat(self):
        name = input("Введіть ім'я кота: ")
        age = input("Введіть новий вік кота: ")
        self._log_action("Оновлення віку", f"ім'я: {name}, вік: {age}", "початок")

        is_valid, age_value, error = validate_age(age)
        if not is_valid:
            self._log_action(
                "Оновлення віку",
                f"ім'я: {name}, вік: {age}",
                f"помилка валідації: {error}",
            )
            print(format_error(error))
            return

        success, error = update_cat_age(self.collection, name, age_value)
        if not success:
            self._log_action(
                "Оновлення віку", f"ім'я: {name}, вік: {age_value}", f"помилка: {error}"
            )
            print(format_error(error))
        else:
            self._log_action(
                "Оновлення віку", f"ім'я: {name}, вік: {age_value}", "успішно оновлено"
            )
            print(MESSAGES["cat_updated"](name))

    def add_feature(self):
        name = input("Введіть ім'я кота: ")
        feature = input("Введіть нову характеристику: ")
        self._log_action(
            "Додавання характеристики",
            f"ім'я: {name}, характеристика: {feature}",
            "початок",
        )

        success, error = add_feature_to_cat(self.collection, name, feature)
        result = "успішно" if success else f"помилка: {error}"
        self._log_action(
            "Додавання характеристики",
            f"ім'я: {name}, характеристика: {feature}",
            result,
        )

        if not success:
            print(format_error(error))
        else:
            print(MESSAGES["cat_updated"](name))

    def delete_cat(self):
        name = input("Введіть ім'я кота: ")
        self._log_action("Видалення кота", f"ім'я: {name}", "початок")

        is_valid, name_value, error = validate_name(name)
        if not is_valid:
            self._log_action(
                "Видалення кота", f"ім'я: {name}", f"помилка валідації: {error}"
            )
            print(format_error(error))
            return

        success = delete_cat_by_name(self.collection, name_value)
        if success:
            self._log_action(
                "Видалення кота", f"ім'я: {name_value}", "успішно видалено"
            )
            print(MESSAGES["cat_deleted"](name_value))
        else:
            self._log_action(
                "Видалення кота", f"ім'я: {name_value}", "кота не знайдено"
            )
            print(MESSAGES["cat_not_found"](name_value))

    def delete_all(self):
        confirm = input("Ви впевнені? (y/n): ")
        if confirm.lower() == "y":
            self._log_action("Видалення всіх котів", "", "початок")
            count = delete_all_cats(self.collection)
            if count > 0:
                self._log_action(
                    "Видалення всіх котів", "", f"успішно видалено {count} котів"
                )
                print(MESSAGES["cats_deleted"](count))
            else:
                self._log_action("Видалення всіх котів", "", "база даних порожня")
                print(MESSAGES["empty_db"])

    def add_cat(self):
        name = input("Введіть ім'я кота: ")
        self._log_action("Додавання кота", f"ім'я: {name}", "початок")

        is_valid, name_value, error = validate_name(name)
        if not is_valid:
            self._log_action(
                "Додавання кота", f"ім'я: {name}", f"помилка валідації: {error}"
            )
            print(format_error(error))
            return

        age = input("Введіть вік кота: ")
        is_valid, age_value, error = validate_age(age)
        if not is_valid:
            self._log_action(
                "Додавання кота",
                f"ім'я: {name_value}, вік: {age}",
                f"помилка валідації: {error}",
            )
            print(format_error(error))
            return

        features = input("Введіть характеристики (через кому): ")
        is_valid, features_list, error = validate_features(features)
        if not is_valid:
            self._log_action(
                "Додавання кота",
                f"ім'я: {name_value}, характеристики: {features}",
                f"помилка валідації: {error}",
            )
            print(format_error(error))
            return

        success = insert_cat(self.collection, name_value, age_value, features_list)
        if success:
            self._log_action(
                "Додавання кота",
                f"ім'я: {name_value}, вік: {age_value}, характеристики: {features}",
                "успішно додано",
            )
            print(MESSAGES["cat_added"](name_value))
        else:
            self._log_action(
                "Додавання кота", f"ім'я: {name_value}", "помилка додавання"
            )
            print(format_error("Помилка додавання кота"))


def main_menu(collection):
    manager = CatManager(collection)
    while True:
        print(f"\n{MESSAGES['menu_header']}")
        for key, (text, _) in manager.options.items():
            # Особливе форматування для пункту "Вийти"
            if key == "0":
                print(f"{key}. {COLORS['error']}{text}{COLORS['reset']}")
            else:
                print(f"{key}. {COLORS['menu']}{text}{COLORS['reset']}")

        try:
            choice = input(f"{COLORS['success']}Оберіть опцію: {COLORS['reset']}")
            if choice not in manager.options:
                logger.warning(f"Введено неправильну опцію: {choice}")
                print(MESSAGES["invalid_choice"])
                continue

            action_text, action_name = manager.options[choice]
            logger.info(f"Обрано опцію {choice}: {action_text}")

            if choice == "0":
                logger.success("Завершення роботи програми")
                print(MESSAGES["exit"])
                break

            action = manager.options[choice][1]
            if action:
                action()

        except Exception as e:
            logger.error(
                f"Помилка при виконанні опції {choice} ({manager.options[choice][0]}): {e}"
            )
            handle_error(e)


if __name__ == "__main__":
    try:
        collection = get_db_connection(MONGO_URI, DATABASE_NAME, COLLECTION_NAME)
        main_menu(collection)
    except ServerSelectionTimeoutError:
        print(
            f"{COLORS['error']}Не вдалося підключитися до бази даних. Програму завершено.{COLORS['reset']}"
        )
        logger.error("Помилка підключення до MongoDB")
    except Exception as e:
        print(f"{COLORS['error']}Неочікувана помилка: {e}{COLORS['reset']}")
        logger.error(f"Неочікувана помилка: {e}")
