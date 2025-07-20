-- (1) Отримати всі завдання певного користувача (наприклад `user_id = 1`):
SELECT * FROM tasks WHERE user_id = 1;

-- (2) Вибрати завдання зі статусом 'new':
SELECT * FROM tasks 
WHERE status_id = (SELECT id FROM status WHERE name = 'new');

-- (3) Оновити статус конкретного завдання (наприклад завдання з id=10):
UPDATE tasks SET status_id = (SELECT id FROM status WHERE name='in progress') WHERE id=10;

-- (4) Отримати список користувачів, які не мають жодного завдання:
SELECT * FROM users 
WHERE id NOT IN (SELECT user_id FROM tasks);

-- (5) Додати нове завдання для конкретного користувача (наприклад user_id=2, статус 'new'):
INSERT INTO tasks (title, description, status_id, user_id)
VALUES ('Задонать 2 гривні Стерненку', 'Наша русофобія недостатня!', (SELECT id FROM status WHERE name='new'), 2);

-- (6) Отримати всі завдання, які ще не завершено (статус != 'completed'):
SELECT * FROM tasks 
WHERE status_id <> (SELECT id FROM status WHERE name='completed');

-- (7) Видалити конкретне завдання (наприклад id=5):
DELETE FROM tasks WHERE id=5;

-- (8) Знайти користувачів з певною електронною поштою (наприклад, містить 'gmail'):
SELECT * FROM users WHERE email LIKE '%gmail%';

-- (9) Оновити ім'я користувача (наприклад, для user_id=3):
UPDATE users SET fullname='Степан Андрійович' WHERE id=3;

-- (10) Отримати кількість завдань для кожного статусу:
SELECT s.name, COUNT(t.id) AS task_count
FROM status s
LEFT JOIN tasks t ON s.id = t.status_id
GROUP BY s.name;
 
-- (11) Отримати завдання для користувачів з певним доменом email (наприклад '@example.com'):
SELECT t.*
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE u.email LIKE '%@example.com';
 
-- (12) Отримати список завдань, що не мають опису:
SELECT * FROM tasks WHERE description IS NULL OR description = '';
 
-- (13) Користувачі та їхні завдання у статусі 'in progress':
SELECT u.fullname, u.email, t.title, t.description
FROM users u
INNER JOIN tasks t ON u.id = t.user_id
WHERE t.status_id = (SELECT id FROM status WHERE name='in progress');
 
-- (14) Отримати користувачів та кількість їхніх завдань:
SELECT u.id, u.fullname, COUNT(t.id) AS task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.fullname;
