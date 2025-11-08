# 🚀 Инструкция по деплою на Ubuntu сервер

## Шаг 1: Git Push

### Если у вас еще нет удаленного репозитория:

1. **Создайте репозиторий на GitHub/GitLab/Bitbucket:**
   - Перейдите на GitHub.com (или другую платформу)
   - Создайте новый репозиторий (например: `dmed`)
   - **НЕ** инициализируйте его с README

2. **Добавьте remote и сделайте push:**
   ```bash
   git remote add origin https://github.com/ваш-username/dmed.git
   git push -u origin main
   ```

### Если репозиторий уже существует:

```bash
git remote add origin <URL_вашего_репозитория>
git push -u origin main
```

---

## Шаг 2: Подключение к Ubuntu серверу

```bash
ssh root@45.138.159.141
# или
ssh ваш_пользователь@45.138.159.141
```

---

## Шаг 3: Установка зависимостей на сервере

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install -y python3 python3-pip python3-venv

# Установка PostgreSQL клиента (если нужно)
sudo apt install -y postgresql-client

# Установка Git
sudo apt install -y git

# Установка Nginx (для reverse proxy)
sudo apt install -y nginx
```

---

## Шаг 4: Клонирование репозитория

```bash
# Создайте директорию для приложения
sudo mkdir -p /var/www/dmed
sudo chown $USER:$USER /var/www/dmed

# Клонируйте репозиторий
cd /var/www/dmed
git clone https://github.com/ваш-username/dmed.git .

# Или если репозиторий приватный, используйте SSH:
# git clone git@github.com:ваш-username/dmed.git .
```

---

## Шаг 5: Настройка виртуального окружения

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

---

## Шаг 6: Настройка .env файла

```bash
# Создайте .env файл
nano .env
```

Добавьте следующее содержимое:

```env
# PostgreSQL
DB_HOST=45.138.159.141
DB_PORT=5432
DB_NAME=dmed
DB_USER=dmed_app
DB_PASSWORD="ваш_пароль_здесь"
DB_SSLMODE=prefer

# Flask
SECRET_KEY=сгенерируйте-случайный-секретный-ключ
UPLOAD_FOLDER=static/generated_documents
DEBUG=False

# Настройки
DOC_NUMBER_PREFIX=01ВШ
DOC_NUMBER_FORMAT=date
DOCX_FONT_NAME=Times New Roman
```

**Важно:** Замените `ваш_пароль_здесь` на реальный пароль и сгенерируйте `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Шаг 7: Создание таблицы в БД

```bash
# Подключитесь к PostgreSQL
psql -h 45.138.159.141 -U dmed_app -d dmed

# Выполните SQL скрипт (сначала создайте файл create_table.sql на сервере)
# Или выполните SQL команды напрямую в psql
```

---

## Шаг 8: Настройка systemd service

```bash
# Создайте файл сервиса
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
ExecStart=/var/www/dmed/venv/bin/python3 app.py
Restart=always

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

---

## Шаг 9: Настройка Nginx

```bash
# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/dmed
```

Добавьте:

```nginx
server {
    listen 80;
    server_name ваш_домен.com или IP_адрес;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/dmed/static;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/dmed /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Шаг 10: Настройка SSL (опционально, но рекомендуется)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ваш_домен.com
```

---

## Полезные команды

```bash
# Проверка статуса приложения
sudo systemctl status dmed

# Просмотр логов
sudo journalctl -u dmed -f

# Перезапуск приложения
sudo systemctl restart dmed

# Обновление кода
cd /var/www/dmed
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dmed
```

---

## Проверка работы

Откройте в браузере: `http://ваш_IP_адрес` или `http://ваш_домен.com`

---

## Важные замечания

1. **Безопасность:**
   - Не коммитьте `.env` файл в git
   - Используйте сильный `SECRET_KEY`
   - Настройте firewall (ufw)

2. **Права доступа:**
   ```bash
   sudo chown -R www-data:www-data /var/www/dmed
   sudo chmod -R 755 /var/www/dmed
   ```

3. **Логи:**
   - Логи приложения: `sudo journalctl -u dmed -f`
   - Логи Nginx: `sudo tail -f /var/log/nginx/error.log`

