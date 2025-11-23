#!/bin/bash
# Скрипт для исправления проблемы с виртуальным окружением gunicorn

echo "=========================================="
echo "ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С VENV GUNICORN"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /var/www/dmed || exit 1

echo -e "${BLUE}Проблема найдена:${NC}"
echo "Gunicorn использует: .venv"
echo "Библиотеки установлены в: venv"
echo ""

# Проверяем, какое окружение использует gunicorn
GUNICORN_VENV=$(ps aux | grep gunicorn | grep -oP '/var/www/dmed/\.?venv' | head -1)
echo -e "${YELLOW}Gunicorn использует: $GUNICORN_VENV${NC}"
echo ""

# Вариант 1: Установить библиотеки в .venv
echo -e "${BLUE}Вариант 1: Установка библиотек в .venv (РЕКОМЕНДУЕТСЯ)${NC}"
echo "----------------------------------------"

if [ -d ".venv" ]; then
    echo "Активируем .venv..."
    source .venv/bin/activate
    
    echo "Проверяем установленные библиотеки:"
    pip list | grep -E "(qrcode|Pillow)" || echo "Библиотеки не найдены"
    echo ""
    
    echo "Устанавливаем библиотеки..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo ""
    echo "Проверяем установку:"
    python3 -c "import qrcode_styled; from PIL import Image; print('✓ Библиотеки установлены')" 2>&1
    
    deactivate
    echo -e "${GREEN}✓ Библиотеки установлены в .venv${NC}"
else
    echo -e "${RED}✗ .venv не найден${NC}"
fi

echo ""

# Вариант 2: Проверка конфигурации systemd
echo -e "${BLUE}Вариант 2: Проверка конфигурации systemd${NC}"
echo "----------------------------------------"

if [ -f "/etc/systemd/system/dmed.service" ]; then
    echo "Файл конфигурации найден:"
    echo ""
    cat /etc/systemd/system/dmed.service | grep -E "(venv|WorkingDirectory|ExecStart)" || echo "Конфигурация не найдена"
    echo ""
    echo -e "${YELLOW}Если в конфигурации указан .venv, но библиотеки в venv,${NC}"
    echo -e "${YELLOW}нужно либо установить библиотеки в .venv (Вариант 1),${NC}"
    echo -e "${YELLOW}либо изменить конфигурацию на использование venv${NC}"
else
    echo "Файл конфигурации systemd не найден"
fi

echo ""

# Вариант 3: Создать симлинк или скопировать библиотеки
echo -e "${BLUE}Вариант 3: Проверка обоих окружений${NC}"
echo "----------------------------------------"

if [ -d "venv" ] && [ -d ".venv" ]; then
    echo "Оба окружения существуют:"
    echo "  venv: $(ls -d venv 2>/dev/null | wc -l) директория"
    echo "  .venv: $(ls -d .venv 2>/dev/null | wc -l) директория"
    echo ""
    echo -e "${YELLOW}Рекомендация: Использовать одно окружение${NC}"
    echo "  - Либо установить библиотеки в .venv (Вариант 1)"
    echo "  - Либо изменить конфигурацию gunicorn на venv"
fi

echo ""
echo "=========================================="
echo "СЛЕДУЮЩИЕ ШАГИ:"
echo "=========================================="
echo ""
echo "1. После установки библиотек в .venv перезапустите сервис:"
echo "   sudo systemctl restart dmed"
echo ""
echo "2. Проверьте логи:"
echo "   sudo journalctl -u dmed -f"
echo ""
echo "3. Создайте тестовый документ и проверьте QR-код"
echo ""

