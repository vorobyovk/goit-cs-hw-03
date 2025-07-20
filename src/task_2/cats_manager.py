import logging

from pymongo.errors import PyMongoError
from validators import validate_features, validate_name

logger = logging.getLogger(__name__)


def validate_cat_exists(collection, name: str) -> tuple[bool, str]:
    """Перевіряє чи існує кіт з таким іменем"""
    try:
        if collection.find_one({"name": name}):
            return True, ""
        return (
            False,
            f"Кота з ім'ям '{name}' не знайдено",
        )  # This will be logged as WARNING
    except PyMongoError as e:
        logger.error(
            f"Помилка перевірки існування кота: {e}"
        )  # This will be logged as ERROR
        return False, str(e)


def show_all_cats(collection):
    """Показує всіх котів"""
    try:
        cats = list(collection.find())
        return cats, None
    except PyMongoError as e:
        logger.error(f"Помилка при отриманні списку котів: {e}")
        return None, str(e)


def find_cat_by_name(collection, name: str):
    """Знаходить кота за ім'ям"""
    is_valid, name_value, error = validate_name(name)
    if not is_valid:
        return None, error

    try:
        cat = collection.find_one({"name": name_value})
        if not cat:
            return None, f"Кота з ім'ям '{name_value}' не знайдено"
        # Safe handling of features
        cat["features"] = cat.get("features", [])
        return cat, None
    except PyMongoError as e:
        logger.error(f"Помилка пошуку кота: {e}")
        return None, str(e)


def update_cat_age(collection, name: str, age: int):
    """Оновлює вік кота"""
    is_valid, name_value, error = validate_name(name)
    if not is_valid:
        return False, error

    exists, error = validate_cat_exists(collection, name_value)
    if not exists:
        return False, error

    try:
        result = collection.update_one({"name": name_value}, {"$set": {"age": age}})
        if result.matched_count == 0:
            return False, f"Кота з ім'ям '{name_value}' не знайдено"
        if result.modified_count == 0:
            return False, "Вік не було оновлено (можливо, вказано той самий вік)"
        return True, None
    except PyMongoError as e:
        logger.error(f"Помилка оновлення віку: {e}")
        return False, str(e)


def add_feature_to_cat(collection, name: str, feature: str):
    """Додає характеристику до кота"""
    is_valid, name_value, error = validate_name(name)
    if not is_valid:
        return False, error

    exists, error = validate_cat_exists(collection, name_value)
    if not exists:
        return False, error

    is_valid, features_list, error = validate_features(feature)
    if not is_valid or not features_list:
        return False, error or "Характеристика не може бути порожньою"

    try:
        result = collection.update_one(
            {"name": name_value}, {"$addToSet": {"features": features_list[0]}}
        )
        if result.matched_count == 0:
            return False, f"Кота з ім'ям '{name_value}' не знайдено"
        if result.modified_count == 0:
            return False, "Ця характеристика вже існує"
        return True, None
    except PyMongoError as e:
        logger.error(f"Помилка додавання характеристики: {e}")
        return False, str(e)


def delete_cat_by_name(collection, name: str):
    """Видаляє кота за ім'ям"""
    try:
        result = collection.delete_one({"name": name})
        return result.deleted_count > 0
    except PyMongoError as e:
        logger.error(f"Помилка видалення кота: {e}")
        return False


def delete_all_cats(collection):
    """Видаляє всіх котів"""
    try:
        result = collection.delete_many({})
        return result.deleted_count
    except PyMongoError as e:
        logger.error(f"Помилка видалення всіх котів: {e}")
        return 0


def insert_cat(collection, name: str, age: int, features: list):
    """Додає нового кота"""
    try:
        # Check if cat with this name already exists
        existing_cat = collection.find_one({"name": name})
        if existing_cat:
            logger.warning(f"Кіт з ім'ям '{name}' вже існує")
            return False, "Кіт з таким ім'ям вже існує"

        cat_doc = {"name": name, "age": age, "features": features}
        result = collection.insert_one(cat_doc)
        return bool(result.inserted_id), None
    except PyMongoError as e:
        logger.error(f"Помилка додавання кота: {e}")
        return False, str(e)
