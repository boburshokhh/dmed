# 🚀 Деплой на Ubuntu сервер (без Docker)

## Быстрый старт

### 1. Подключитесь к серверу

```bash
ssh root@45.138.159.141
# или
ssh ваш_пользователь@45.138.159.141
```

### 2. Запустите скрипт деплоя

```bash
# Скачайте скрипт на сервер
wget https://raw.githubusercontent.com/ваш-репозиторий/deploy_ubuntu.sh
# или скопируйте файл deploy_ubuntu.sh на сервер

# Сделайте его исполняемым
chmod +x deploy_ubuntu.sh

# Запустите
sudo ./deploy_ubuntu.sh
```

---

## Ручной деплой (пошагово)

### Шаг 1: Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### Шаг 2: Установка зависимостей

```bash
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql-client
```

### Шаг 3: Клонирование репозитория

```bash
# Создайте директорию
sudo mkdir -p /var/www/dmed
sudo chown -R $USER:$USER /var/www/dmed

# Клонируйте репозиторий
cd /var/www/dmed
git clone https://github.com/ваш-username/dmed.git .

# Или если репозиторий приватный:
# git clone git@github.com:ваш-username/dmed.git .
```

### Шаг 4: Настройка виртуального окружения

```bash
cd /var/www/dmed

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 5: Создание .env файла

```bash
nano .env
```

Добавьте следующее содержимое (замените значения на свои):

```env
# PostgreSQL
DB_HOST=45.138.159.141
DB_PORT=5432
DB_NAME=dmed
DB_USER=dmed_app
DB_PASSWORD="ваш_пароль_здесь"
DB_SSLMODE=prefer

# Flask
SECRET_KEY=сгенерируйте-случайный-ключ-здесь
UPLOAD_FOLDER=static/generated_documents
DEBUG=False

# Настройки
DOC_NUMBER_PREFIX=01ВШ
DOC_NUMBER_FORMAT=date
DOCX_FONT_NAME=Times New Roman
```

**Генерация SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Шаг 6: Создание таблицы в БД

```bash
# Подключитесь к PostgreSQL
psql -h 45.138.159.141 -U dmed_app -d dmed

# Выполните SQL (создайте файл create_table.sql на сервере или выполните SQL напрямую)
```

### Шаг 7: Создание systemd service

```bash
sudo nano /etc/systemd/system/dmed.service
```

Добавьте:

```ini
[Unit]
Description=DMED Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dmed
Environment="PATH=/var/www/dmed/venv/bin"
ExecStart=/var/www/dmed/venv/bin/python3 /var/www/dmed/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dmed
sudo systemctl start dmed
sudo systemctl status dmed
```

### Шаг 8: Настройка Nginx

```bash
sudo nano /etc/nginx/sites-available/dmed
```

Добавьте:

```nginx
server {
    listen 80;
    server_name _;  # Замените на ваш домен, если есть

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/dmed/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/dmed /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Удалите дефолтную конфигурацию
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx
```

### Шаг 9: Настройка прав доступа

```bash
sudo chown -R www-data:www-data /var/www/dmed
sudo chmod -R 755 /var/www/dmed
```

### Шаг 10: Настройка Firewall (опционально)

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (если настроите SSL)
sudo ufw enable
```

---

## Полезные команды

### Управление приложением

```bash
# Статус
sudo systemctl status dmed

# Запуск
sudo systemctl start dmed

# Остановка
sudo systemctl stop dmed

# Перезапуск
sudo systemctl restart dmed

# Просмотр логов
sudo journalctl -u dmed -f
```

### Обновление кода

```bash
cd /var/www/dmed
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dmed
```

### Проверка работы

```bash
# Проверка приложения
curl http://localhost:5000

# Проверка Nginx
curl http://localhost

# Проверка портов
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :80
```

---

## Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата (замените на ваш домен)
sudo certbot --nginx -d ваш-домен.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

---

## Устранение проблем

### Приложение не запускается

```bash
# Проверьте логи
sudo journalctl -u dmed -n 50

# Проверьте .env файл
cat /var/www/dmed/.env

# Проверьте подключение к БД
psql -h 45.138.159.141 -U dmed_app -d dmed
```

### Nginx не работает

```bash
# Проверьте конфигурацию
sudo nginx -t

# Проверьте логи
sudo tail -f /var/log/nginx/error.log

# Проверьте статус
sudo systemctl status nginx
```

### Порт 5000 занят

```bash
# Найдите процесс
sudo lsof -i :5000

# Убейте процесс
sudo kill -9 <PID>
```

---

## Структура файлов на сервере

```
/var/www/dmed/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── venv/
├── static/
│   ├── css/
│   ├── js/
│   └── generated_documents/
└── templates/
```

---

## Безопасность

1. **Не коммитьте .env файл** в git
2. **Используйте сильный SECRET_KEY**
3. **Настройте firewall** (ufw)
4. **Используйте SSL** для HTTPS
5. **Регулярно обновляйте систему**: `sudo apt update && sudo apt upgrade`

---

## Готово! 🎉

Ваше приложение должно быть доступно по адресу:
- `http://45.138.159.141` (или ваш домен)

