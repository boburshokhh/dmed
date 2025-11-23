#!/bin/bash
# Скрипт для исправления проблемы с qrcode-styled на Ubuntu сервере

echo "=========================================="
echo "ИСПРАВЛЕНИЕ qrcode-styled на Ubuntu"
echo "=========================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверяем, запущен ли скрипт от root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Предупреждение: Скрипт запущен не от root${NC}"
fi

# Переходим в директорию проекта
cd /var/www/dmed || {
    echo -e "${RED}Ошибка: Не могу перейти в /var/www/dmed${NC}"
    exit 1
}

echo "Текущая директория: $(pwd)"
echo ""

# Шаг 1: Проверяем наличие виртуального окружения
echo "Шаг 1: Проверка виртуального окружения..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Виртуальное окружение найдено: venv${NC}"
    VENV_PATH="venv"
elif [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Виртуальное окружение найдено: .venv${NC}"
    VENV_PATH=".venv"
elif [ -d "env" ]; then
    echo -e "${GREEN}✓ Виртуальное окружение найдено: env${NC}"
    VENV_PATH="env"
else
    echo -e "${YELLOW}⚠ Виртуальное окружение не найдено. Создаём новое...${NC}"
    python3 -m venv venv
    VENV_PATH="venv"
    echo -e "${GREEN}✓ Виртуальное окружение создано: venv${NC}"
fi

# Активируем виртуальное окружение
source "$VENV_PATH/bin/activate" || {
    echo -e "${RED}Ошибка: Не могу активировать виртуальное окружение${NC}"
    exit 1
}

echo -e "${GREEN}✓ Виртуальное окружение активировано${NC}"
echo "Python путь: $(which python3)"
echo ""

# Шаг 2: Обновляем pip
echo "Шаг 2: Обновление pip..."
python3 -m pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip обновлён${NC}"
echo ""

# Шаг 3: Устанавливаем системные зависимости (если нужно)
echo "Шаг 3: Проверка системных зависимостей..."
if ! dpkg -l | grep -q python3-dev; then
    echo -e "${YELLOW}Устанавливаем python3-dev...${NC}"
    apt-get update -qq && apt-get install -y python3-dev python3-pip libjpeg-dev zlib1g-dev > /dev/null 2>&1
fi
echo -e "${GREEN}✓ Системные зависимости проверены${NC}"
echo ""

# Шаг 4: Устанавливаем библиотеки из requirements.txt
echo "Шаг 4: Установка библиотек из requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "Устанавливаем все зависимости..."
    python3 -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Все библиотеки установлены из requirements.txt${NC}"
    else
        echo -e "${RED}✗ Ошибка при установке из requirements.txt${NC}"
    fi
else
    echo -e "${YELLOW}⚠ requirements.txt не найден, устанавливаем вручную...${NC}"
    python3 -m pip install qrcode-styled>=0.2.0 Pillow>=10.0.0
fi
echo ""

# Шаг 5: Проверяем установку
echo "Шаг 5: Проверка установки..."
echo ""

# Проверка qrcode-styled
python3 -c "import qrcode_styled; print('✓ qrcode-styled:', getattr(qrcode_styled, '__version__', 'установлен'))" 2>/dev/null && \
    echo -e "${GREEN}✓ qrcode-styled установлен${NC}" || \
    echo -e "${RED}✗ qrcode-styled НЕ установлен${NC}"

# Проверка Pillow
python3 -c "from PIL import Image; print('✓ Pillow:', Image.__version__)" 2>/dev/null && \
    echo -e "${GREEN}✓ Pillow установлен${NC}" || \
    echo -e "${RED}✗ Pillow НЕ установлен${NC}"

echo ""

# Шаг 6: Тест создания QR-кода
echo "Шаг 6: Тест создания QR-кода..."
python3 << 'PYTHON_TEST'
try:
    from qrcode_styled import QRCodeStyled
    from PIL import Image
    
    qr = QRCodeStyled()
    img = qr.get_image('test')
    
    if isinstance(img, Image.Image):
        print(f"✓ QR-код создан успешно!")
        print(f"  Размер: {img.size}, Режим: {img.mode}")
    else:
        print(f"⚠ QR-код создан, но тип: {type(img)}")
        print("  (Это может быть нормально для некоторых версий)")
        
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST

echo ""

# Шаг 7: Показываем установленные версии
echo "Шаг 7: Установленные версии библиотек:"
python3 -m pip list | grep -E "(qrcode|Pillow)" || echo "Библиотеки не найдены в списке"
echo ""

# Шаг 8: Инструкции по перезапуску
echo "=========================================="
echo "УСТАНОВКА ЗАВЕРШЕНА"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Если используете systemd, перезапустите сервис:"
echo "   sudo systemctl restart dmed"
echo ""
echo "2. Если запускаете вручную, убедитесь что используете виртуальное окружение:"
echo "   source $VENV_PATH/bin/activate"
echo "   python3 app.py"
echo ""
echo "3. Проверьте логи:"
echo "   sudo journalctl -u dmed -f"
echo ""

# Деактивируем виртуальное окружение
deactivate 2>/dev/null

echo -e "${GREEN}Готово!${NC}"

