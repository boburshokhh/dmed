#!/bin/bash

# Скрипт для деплоя Flask приложения на Ubuntu сервер
# Использование: ./deploy_ubuntu.sh

set -e  # Остановка при ошибке

echo "=========================================="
echo "Деплой DMED приложения на Ubuntu сервер"
echo "=========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переменные
APP_DIR="/var/www/dmed"
APP_USER="www-data"
APP_NAME="dmed"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
NGINX_CONFIG="/etc/nginx/sites-available/${APP_NAME}"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ошибка: Запустите скрипт с правами root (sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}Шаг 1: Обновление системы...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}Шаг 2: Установка зависимостей...${NC}"
apt install -y python3 python3-pip python3-venv git nginx postgresql-client

echo -e "${GREEN}Шаг 3: Создание директории приложения...${NC}"
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

echo -e "${YELLOW}ВНИМАНИЕ: Убедитесь, что вы уже клонировали репозиторий в $APP_DIR${NC}"
echo -e "${YELLOW}Выполните: git clone <ваш_repo_url> $APP_DIR${NC}"
read -p "Нажмите Enter после клонирования репозитория..."

echo -e "${GREEN}Шаг 4: Настройка виртуального окружения...${NC}"
cd $APP_DIR
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER ./venv/bin/pip install --upgrade pip
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt

echo -e "${GREEN}Шаг 5: Создание .env файла...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}Создайте .env файл вручную:${NC}"
    echo "nano $APP_DIR/.env"
    echo ""
    echo "Добавьте следующее содержимое:"
    echo "DB_HOST=45.138.159.141"
    echo "DB_PORT=5432"
    echo "DB_NAME=dmed"
    echo "DB_USER=dmed_app"
    echo "DB_PASSWORD=\"ваш_пароль\""
    echo "DB_SSLMODE=prefer"
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
    echo "UPLOAD_FOLDER=static/generated_documents"
    echo "DEBUG=False"
    echo "DOC_NUMBER_PREFIX=01ВШ"
    echo "DOC_NUMBER_FORMAT=date"
    echo "DOCX_FONT_NAME=Times New Roman"
    echo ""
    read -p "Нажмите Enter после создания .env файла..."
else
    echo -e "${GREEN}.env файл уже существует${NC}"
fi

echo -e "${GREEN}Шаг 6: Создание systemd service...${NC}"
cat > $SERVICE_FILE << EOF
[Unit]
Description=DMED Flask Application
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Шаг 7: Активация systemd service...${NC}"
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME
systemctl status $APP_NAME --no-pager

echo -e "${GREEN}Шаг 8: Настройка Nginx...${NC}"
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Активируем конфигурацию
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Проверяем конфигурацию Nginx
nginx -t

echo -e "${GREEN}Шаг 9: Перезапуск Nginx...${NC}"
systemctl restart nginx

echo ""
echo -e "${GREEN}=========================================="
echo "Деплой завершен успешно!"
echo "==========================================${NC}"
echo ""
echo "Проверка статуса:"
echo "  sudo systemctl status $APP_NAME"
echo ""
echo "Просмотр логов:"
echo "  sudo journalctl -u $APP_NAME -f"
echo ""
echo "Перезапуск приложения:"
echo "  sudo systemctl restart $APP_NAME"
echo ""
echo "Приложение доступно по адресу:"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""

