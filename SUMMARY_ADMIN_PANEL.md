# Сводка: Админ-панель для генерации документов

## Что было сделано

### 1. База данных
- ✅ Создана миграция `migrations/001_create_users_table.sql` для таблицы `users`
- ✅ Две роли: `admin` и `super_admin`
- ✅ Скрипт `create_super_admin.py` для создания первого администратора

### 2. Backend API (Flask)

#### Авторизация (`auth_routes.py`)
- `POST /api/auth/login` - вход в систему
- `POST /api/auth/logout` - выход

#### Управление пользователями (`auth_routes.py`)
- `GET /api/admin/users` - список пользователей (super_admin)
- `POST /api/admin/users` - создание пользователя (super_admin)
- `PUT /api/admin/users/:id` - обновление пользователя (super_admin)
- `DELETE /api/admin/users/:id` - удаление пользователя (super_admin)
- `GET /api/admin/stats/users` - статистика пользователей
- `GET /api/admin/stats/documents` - статистика документов

#### Работа с документами (`document_routes.py`)
- `GET /api/documents` - список документов
- `POST /api/documents/generate` - генерация документа
- `GET /api/documents/:id/download` - скачивание документа

#### Работа с файлами (`app.py`)
- `GET /api/files` - список всех файлов в хранилище
- `GET /api/files/download/:filename` - скачивание файла
- `DELETE /api/files/delete/:filename` - удаление файла

### 3. Frontend (Next.js без TypeScript)

#### Структура приложения
```
front_generate/
├── app/
│   ├── login/page.js          # Страница входа
│   ├── dashboard/page.js      # Главная панель (super_admin)
│   ├── documents/page.js      # Генерация документов ✨ НОВОЕ
│   ├── files/page.js          # История файлов ✨ НОВОЕ
│   └── admin/users/page.js    # Управление админами
├── components/
│   ├── ui/                    # UI компоненты (shadcn/ui)
│   └── layout/
│       ├── sidebar.js         # Боковое меню
│       └── main-layout.js     # Основной макет
└── lib/
    ├── api.js                 # Axios клиент
    └── auth.js                # Функции авторизации
```

#### Страница генерации документов (`/documents`)
**Поля для заполнения:**

**Информация о пациенте:**
- ФИО пациента * (обязательное)
- ПИНФЛ (JSHSHIR)
- Пол * (Erkak/Ayol)
- Возраст *
- Адрес
- Прикрепленное медучреждение

**Диагноз:**
- Первичный диагноз *
- Код МКБ-10
- Заключительный диагноз
- Код МКБ-10 (заключительный)

**Период освобождения:**
- Освобожден с (дата)
- Освобожден по (дата)

**Информация об организации и враче:**
- Организация *
- Дата выдачи *
- ФИО врача *
- Должность врача *
- Заведующий отделением

**Функции:**
- ✅ Генерация документов с полным набором полей
- ✅ Автоматическое создание PDF и DOCX
- ✅ Генерация уникального номера и PIN-кода
- ✅ Список всех созданных документов
- ✅ Поиск по номеру или имени пациента
- ✅ Скачивание документов

#### Страница истории файлов (`/files`)
**Функции:**
- ✅ Список всех файлов из хранилища (MinIO/локально)
- ✅ Фильтры:
  - По типу (PDF/DOCX)
  - Поиск по имени, UUID, пациенту
  - По дате создания (от/до)
- ✅ Статистика:
  - Всего файлов
  - PDF документы
  - DOCX документы
  - Общий размер
- ✅ Скачивание файлов
- ✅ Удаление файлов (только super_admin)

#### Страница управления админами (`/admin/users`)
**Функции (только super_admin):**
- ✅ Список всех администраторов
- ✅ Создание новых админов
- ✅ Редактирование (логин, пароль, роль)
- ✅ Удаление админов
- ✅ Активация/деактивация

### 4. Безопасность
- ✅ JWT токены для авторизации
- ✅ Bcrypt для хеширования паролей
- ✅ Проверка ролей на уровне API
- ✅ Защита маршрутов на фронтенде
- ✅ CORS настроен для localhost:3000

## Как запустить

### 1. Настройка базы данных
```bash
# Выполнить миграцию
psql -h 45.138.159.141 -U dmed_app -d dmed -f migrations/001_create_users_table.sql

# Создать первого super_admin
python create_super_admin.py
```

### 2. Установить зависимости
```bash
# Backend
pip install PyJWT bcrypt

# Frontend
cd front_generate
npm install
```

### 3. Запустить приложения
```bash
# Backend (Flask)
python app.py

# Frontend (Next.js) в другом терминале
cd front_generate
npm run dev
```

### 4. Открыть в браузере
```
http://localhost:3000
```

## Учетные записи

### Super Admin
- Создается через `create_super_admin.py`
- Может:
  - Создавать/редактировать/удалять админов
  - Генерировать документы
  - Просматривать историю файлов
  - Удалять файлы
  - Просматривать статистику

### Admin
- Создается super_admin через веб-интерфейс
- Может:
  - Генерировать документы
  - Просматривать историю файлов
  - Скачивать документы

## API Endpoints

### Авторизация
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Админы (super_admin)
- `GET /api/admin/users`
- `POST /api/admin/users`
- `PUT /api/admin/users/:id`
- `DELETE /api/admin/users/:id`
- `GET /api/admin/stats/users`
- `GET /api/admin/stats/documents`

### Документы (admin, super_admin)
- `GET /api/documents`
- `POST /api/documents/generate`
- `GET /api/documents/:id/download`

### Файлы (admin, super_admin)
- `GET /api/files`
- `GET /api/files/download/:filename`
- `DELETE /api/files/delete/:filename` (super_admin)

## Файлы

### Backend
- `auth_routes.py` - авторизация и управление пользователями
- `document_routes.py` - работа с документами
- `create_super_admin.py` - создание первого администратора
- `migrations/001_create_users_table.sql` - миграция БД

### Frontend
- `front_generate/app/login/page.js` - вход
- `front_generate/app/dashboard/page.js` - главная
- `front_generate/app/documents/page.js` - генерация документов ✨
- `front_generate/app/files/page.js` - история файлов ✨
- `front_generate/app/admin/users/page.js` - управление админами

## Документация
- `QUICKSTART.md` - быстрый старт
- `CORS_FIX.md` - решение CORS проблемы
- `front_generate/README.md` - документация фронтенда
- `migrations/README.md` - документация миграций

## Следующие шаги
1. ✅ Запустить Flask сервер
2. ✅ Создать super_admin
3. ✅ Запустить Next.js фронтенд
4. ✅ Войти в систему
5. ✅ Создать первые документы

