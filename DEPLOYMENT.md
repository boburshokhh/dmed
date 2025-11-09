# Инструкция по развертыванию DMED на продакшн-сервере

## Требования

- Python 3.8+
- pip
- PostgreSQL (уже настроен)
- Доступ к серверу через SSH

## Установка системных зависимостей

```bash
# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем Python и необходимые пакеты
apt install -y python3 python3-venv python3-pip python3-full

# Устанавливаем PostgreSQL клиент (если нужен)
apt install -y postgresql-client
```

## Настройка проекта

### 1. Перейдите в директорию проекта

```bash
cd /var/www/dmed
```

### 2. Создайте виртуальное окружение и установите зависимости

```bash
# Делаем скрипт исполняемым
chmod +x setup_venv.sh

# Запускаем установку
bash setup_venv.sh
```

Или вручную:

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```bash
nano .env
```

Добавьте необходимые переменные:

```env
# База данных
DB_HOST=45.138.159.141
DB_PORT=5432
DB_NAME=dmed
DB_USER=dmed_app
DB_PASSWORD=ваш_пароль

# Flask
SECRET_KEY=ваш_секретный_ключ_для_production
DEBUG=False

# Другие настройки
UPLOAD_FOLDER=uploads/documents
FRONTEND_URL=https://coruscating-nasturtium-520c28.netlify.app
```

### 4. Создайте первого super_admin

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Создаем super_admin
python create_super_admin.py
```

## Запуск приложения

### Вариант 1: Прямой запуск (для тестирования)

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем приложение
python app.py
```

### Вариант 2: Использование скрипта

```bash
# Делаем скрипт исполняемым
chmod +x start.sh

# Запускаем
bash start.sh
```

### Вариант 3: Использование systemd (рекомендуется для продакшена)

Создайте файл `/etc/systemd/system/dmed.service`:

```ini
[Unit]
Description=DMED Flask Application
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dmed
Environment="PATH=/var/www/dmed/venv/bin"
ExecStart=/var/www/dmed/venv/bin/python /var/www/dmed/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable dmed

# Запускаем сервис
systemctl start dmed

# Проверяем статус
systemctl status dmed

# Просмотр логов
journalctl -u dmed -f
```

## Использование Gunicorn (рекомендуется для продакшена)

### 1. Установите Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### 2. Создайте файл `gunicorn_config.py`:

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

### 3. Запустите через Gunicorn:

```bash
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app
```

### 4. Обновите systemd service для использования Gunicorn:

```ini
[Unit]
Description=DMED Flask Application (Gunicorn)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dmed
Environment="PATH=/var/www/dmed/venv/bin"
ExecStart=/var/www/dmed/venv/bin/gunicorn -c /var/www/dmed/gunicorn_config.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Настройка Nginx (если используется)

Создайте конфигурацию `/etc/nginx/sites-available/dmed`:

```nginx
server {
    listen 80;
    server_name dmed.gubkin.uz;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте конфигурацию:

```bash
ln -s /etc/nginx/sites-available/dmed /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Обновление приложения

```bash
cd /var/www/dmed

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем код (через git или вручную)
git pull  # если используете git

# Обновляем зависимости (если requirements.txt изменился)
pip install -r requirements.txt --upgrade

# Перезапускаем сервис
systemctl restart dmed
```

## Проверка работоспособности

```bash
# Проверка API
curl http://localhost:5000/api/health

# Проверка логов
journalctl -u dmed -n 50
```

## Решение проблем

### Виртуальное окружение не активируется

```bash
# Убедитесь, что python3-venv установлен
apt install python3-venv python3-full

# Пересоздайте виртуальное окружение
rm -rf venv
python3 -m venv venv
```

### Ошибки при установке зависимостей

```bash
# Обновите pip
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Попробуйте установить зависимости снова
pip install -r requirements.txt
```

### Порт 5000 уже занят

Измените порт в `app.py` или используйте другой порт через переменную окружения.


