#!/bin/bash
# Скрипт для проверки логов и диагностики проблемы с QR-кодом на Ubuntu

echo "=========================================="
echo "ПРОВЕРКА ЛОГОВ И ДИАГНОСТИКА QR-КОДА"
echo "=========================================="
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /var/www/dmed || exit 1

echo -e "${BLUE}1. Проверка последних логов приложения (systemd):${NC}"
echo "----------------------------------------"
if systemctl is-active --quiet dmed 2>/dev/null; then
    echo -e "${GREEN}✓ Сервис dmed активен${NC}"
    echo ""
    echo "Последние 100 строк логов с QR-кодом:"
    sudo journalctl -u dmed -n 100 --no-pager | grep -i -E "(qr|QR|error|ERROR|exception|Exception)" | tail -30
else
    echo -e "${YELLOW}⚠ Сервис dmed не активен или не найден${NC}"
fi
echo ""

echo -e "${BLUE}2. Проверка логов приложения (если запущено вручную):${NC}"
echo "----------------------------------------"
if [ -f "app.log" ]; then
    echo "Последние 50 строк из app.log:"
    tail -50 app.log | grep -i -E "(qr|QR|error|ERROR|exception|Exception)" || echo "Нет записей о QR-коде"
else
    echo "Файл app.log не найден"
fi
echo ""

echo -e "${BLUE}3. Тест генерации QR-кода напрямую:${NC}"
echo "----------------------------------------"
source venv/bin/activate 2>/dev/null || {
    echo -e "${RED}✗ Не могу активировать venv${NC}"
    exit 1
}

python3 << 'PYTHON_TEST'
import sys
import traceback

print("Тест 1: Проверка импорта библиотек...")
try:
    from qrcode_styled import QRCodeStyled
    print("  ✓ qrcode-styled импортирован")
except Exception as e:
    print(f"  ✗ Ошибка импорта qrcode-styled: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print("  ✓ PIL импортирован")
except Exception as e:
    print(f"  ✗ Ошибка импорта PIL: {e}")
    sys.exit(1)

print("\nТест 2: Создание простого QR-кода...")
try:
    qr = QRCodeStyled()
    img = qr.get_image('test')
    print(f"  ✓ QR-код создан, тип: {type(img)}")
    print(f"  Размер: {img.size if hasattr(img, 'size') else 'N/A'}")
    print(f"  Режим: {img.mode if hasattr(img, 'mode') else 'N/A'}")
except Exception as e:
    print(f"  ✗ Ошибка создания QR-кода: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nТест 3: Импорт функции generate_qr_code...")
try:
    from utils import generate_qr_code
    print("  ✓ Функция generate_qr_code импортирована")
except Exception as e:
    print(f"  ✗ Ошибка импорта generate_qr_code: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nТест 4: Вызов generate_qr_code...")
try:
    img = generate_qr_code('https://test.example.com')
    print(f"  ✓ generate_qr_code выполнен успешно")
    print(f"  Тип результата: {type(img)}")
    print(f"  Размер: {img.size}")
    print(f"  Режим: {img.mode}")
except Exception as e:
    print(f"  ✗ Ошибка в generate_qr_code: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
PYTHON_TEST

TEST_RESULT=$?
echo ""

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Библиотеки работают корректно${NC}"
else
    echo -e "${RED}✗ Обнаружена ошибка в библиотеках${NC}"
fi
echo ""

echo -e "${BLUE}4. Проверка последних ошибок в логах:${NC}"
echo "----------------------------------------"
if systemctl is-active --quiet dmed 2>/dev/null; then
    echo "Последние ошибки:"
    sudo journalctl -u dmed -n 200 --no-pager | grep -i -E "(error|ERROR|exception|Exception|traceback|Traceback)" | tail -20
else
    echo "Сервис не активен, проверьте логи вручную"
fi
echo ""

echo -e "${BLUE}5. Проверка процесса приложения:${NC}"
echo "----------------------------------------"
ps aux | grep -E "(python|app.py|gunicorn|uwsgi)" | grep -v grep || echo "Процессы не найдены"
echo ""

echo -e "${BLUE}6. Проверка файлов проекта:${NC}"
echo "----------------------------------------"
echo "utils.py существует: $([ -f utils.py ] && echo '✓' || echo '✗')"
echo "app.py существует: $([ -f app.py ] && echo '✓' || echo '✗')"
echo "document_generator.py существует: $([ -f document_generator.py ] && echo '✓' || echo '✗')"
echo ""

echo -e "${BLUE}7. Проверка версий библиотек:${NC}"
echo "----------------------------------------"
source venv/bin/activate
python3 -c "
try:
    import qrcode_styled
    from PIL import Image
    print(f'qrcode-styled: {getattr(qrcode_styled, \"__version__\", \"unknown\")}')
    print(f'Pillow: {Image.__version__}')
except Exception as e:
    print(f'Ошибка: {e}')
"
echo ""

echo "=========================================="
echo "ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "=========================================="
echo ""
echo "Скопируйте весь вывод выше для анализа."

