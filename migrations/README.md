# Миграции базы данных

## Выполнение миграций

### Миграция 001: Создание таблицы пользователей

Эта миграция создает таблицу `users` для системы управления пользователями с ролями.

**Выполнение:**

```bash
psql -h 45.138.159.141 -U dmed_app -d dmed -f migrations/001_create_users_table.sql
```

Или через Python:

```python
from database import db_query

with open('migrations/001_create_users_table.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    db_query(sql)
```

## Структура таблицы users

- `id` - SERIAL PRIMARY KEY
- `username` - VARCHAR(100) UNIQUE NOT NULL
- `email` - VARCHAR(255) UNIQUE NOT NULL
- `password_hash` - VARCHAR(255) NOT NULL
- `role` - VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'super_admin'))
- `is_active` - BOOLEAN DEFAULT TRUE
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `created_by` - INTEGER REFERENCES users(id)
- `last_login` - TIMESTAMP

## Создание первого super_admin

После выполнения миграции создайте первого супер-администратора через Python скрипт или напрямую в БД:

```python
import bcrypt
from database import db_insert

password = 'your_secure_password'
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

db_insert('users', {
    'username': 'superadmin',
    'email': 'admin@tamex.uz',
    'password_hash': password_hash,
    'role': 'super_admin',
    'is_active': True,
    'created_by': None
})
```

### Миграция 002: Добавление поля created_by в таблицу documents

Эта миграция добавляет поле `created_by` в таблицу `documents` для отслеживания, кто создал документ.

**Выполнение:**

```bash
psql -h 45.138.159.141 -U dmed_app -d dmed -f migrations/002_add_created_by_to_documents.sql
```

Или через Python:

```python
from database import db_query

with open('migrations/002_add_created_by_to_documents.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    db_query(sql)
```

**Что делает миграция:**
- Добавляет поле `created_by INTEGER REFERENCES users(id)` в таблицу `documents`
- Создает индекс `idx_documents_created_by` для быстрого поиска документов по создателю
- Добавляет комментарий к полю

**После миграции:**
- При создании документа через API (`/api/documents/generate`) автоматически сохраняется ID пользователя, создавшего документ
- При получении списка документов (`/api/documents`) возвращается информация о создателе (username и email)

