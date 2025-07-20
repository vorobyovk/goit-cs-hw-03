import logging
import random
from datetime import datetime

import psycopg2
from config import DB_CONFIG, FILE_CONFIG, LOG_CONFIG
from faker import Faker

# Налаштування логування
logging.basicConfig(**LOG_CONFIG)
logger = logging.getLogger(__name__)

# Ініціалізація Faker
faker = Faker("uk_UA")


def create_connection():
    """
    Створює підключення до бази даних PostgreSQL.
    :return: об'єкт з'єднання (conn)
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Підключення до бази даних встановлено успішно.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Помилка підключення до бази даних: {e}")
        return None


def seed_statuses(conn):
    """
    Заповнює таблицю status попередньо визначеними значеннями.
    :param conn: об'єкт з'єднання до бази даних
    """
    statuses = ["new", "in progress", "completed"]
    try:
        with conn.cursor() as cursor:
            for status in statuses:
                cursor.execute(
                    """
                    INSERT INTO status (name) VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (status,),
                )
            conn.commit()
            logger.info("Таблиця 'status' заповнена успішно.")
    except psycopg2.Error as e:
        logger.error(f"Помилка при заповненні таблиці 'status': {e}")
        conn.rollback()


def seed_users(conn, count=10):
    """
    Заповнює таблицю users випадковими даними.
    :param conn: об'єкт з'єднання до бази даних
    :param count: кількість користувачів для створення
    """
    users = [(faker.name(), faker.unique.email()) for _ in range(count)]
    try:
        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO users (fullname, email) VALUES (%s, %s)
                ON CONFLICT (email) DO NOTHING
                """,
                users,
            )
            conn.commit()
            logger.info(f"Таблиця 'users' заповнена успішно ({count} користувачів).")
    except psycopg2.Error as e:
        logger.error(f"Помилка при заповненні таблиці 'users': {e}")
        conn.rollback()


def seed_tasks(conn, count=50):
    """
    Заповнює таблицю tasks випадковими даними.
    :param conn: об'єкт з'єднання до бази даних
    :param count: кількість завдань для створення
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, s.id 
                FROM users u CROSS JOIN status s
                """
            )
            combinations = cursor.fetchall()

            if not combinations:
                logger.warning("Немає даних для створення завдань")
                return

            tasks = [
                (
                    faker.sentence(nb_words=4),
                    faker.text(max_nb_chars=200),
                    random.choice([s_id for _, s_id in combinations]),
                    random.choice([u_id for u_id, _ in combinations]),
                )
                for _ in range(count)
            ]

            cursor.executemany(
                """
                INSERT INTO tasks (title, description, status_id, user_id)
                VALUES (%s, %s, %s, %s)
                """,
                tasks,
            )

            conn.commit()
            logger.info(f"Додано {count} завдань успішно")

    except Exception as e:
        logger.error(f"Помилка при додаванні завдань: {e}")
        conn.rollback()


def main():
    """
    Основна функція для запуску скрипта.
    """
    conn = create_connection()
    if conn:
        try:
            seed_statuses(conn)
            seed_users(conn, count=10)
            seed_tasks(conn, count=50)
        finally:
            conn.close()
            logger.info("З'єднання з базою даних закрито.")


if __name__ == "__main__":
    main()
