# Быстрый старт - DMED Admin Frontend

## Шаг 1: Настройка базы данных

1. Выполните SQL миграцию:
```bash
psql -h 45.138.159.141 -U dmed_app -d dmed -f migrations/001_create_users_table.sql
```

2. Создайте первого super_admin:
```bash
python create_super_admin.py
```

## Шаг 2: Установка зависимостей фронтенда

```bash
cd front_generate
npm install
```

## Шаг 3: Настройка переменных окружения

Создайте файл `front_generate/.env.local`:
```env
API_URL=http://localhost:5000/api
```

## Шаг 4: Запуск фронтенда

```bash
cd front_generate
npm run dev
```

Откройте браузер: http://localhost:3000

## Шаг 5: Вход в систему

Используйте учетные данные, созданные через `create_super_admin.py`

## Структура ролей

### Super Admin может:
- ✅ Создавать и управлять администраторами
- ✅ Генерировать документы
- ✅ Просматривать статистику
- ✅ Менять пароли и логины админов

### Admin может:
- ✅ Генерировать документы
- ✅ Просматривать список документов

## API Endpoints (нужно реализовать на бэкенде)

См. `front_generate/README.md` для полного списка API endpoints.

