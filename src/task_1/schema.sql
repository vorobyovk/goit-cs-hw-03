BEGIN;

-- Видалення таблиць, якщо вони вже існують.
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Створення таблиці користувачів (users).
CREATE TABLE users (
    id SERIAL PRIMARY KEY,              -- Унікальний ідентифікатор користувача (автоінкремент).
    fullname VARCHAR(100) NOT NULL,     -- Повне ім'я користувача (обов'язкове поле).
    email VARCHAR(100) UNIQUE NOT NULL  -- Унікальна електронна адреса (обов'язково).
);

-- Створення таблиці статусів (status).
CREATE TABLE status (
    id SERIAL PRIMARY KEY,           -- Унікальний ідентифікатор статусу (автоінкремент).
    name VARCHAR(50) UNIQUE NOT NULL -- Унікальна назва статусу (обов'язково).
    -- Приклади: 'new', 'in progress', 'completed'.
);

-- Створення таблиці завдань (tasks).
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,           -- Унікальний ідентифікатор завдання (автоінкремент).
    title VARCHAR(100) NOT NULL,     -- Назва завдання (обов'язково).
    description TEXT,                -- Опис завдання (опційно).
    status_id INTEGER NOT NULL REFERENCES status (id),
    user_id INTEGER NOT NULL REFERENCES users (id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
