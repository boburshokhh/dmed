# Инструкция по деплою на Linux сервер

## Проблема с конвертацией DOCX в PDF

После деплоя на Linux сервер конвертация DOCX в PDF может не работать из-за отсутствия инструментов конвертации.

## Решение (РЕКОМЕНДУЕТСЯ LibreOffice)

### Для Ubuntu/Debian (ЛУЧШИЙ ВАРИАНТ):

**Установите LibreOffice:**
```bash
sudo apt-get update
sudo apt-get install -y libreoffice libreoffice-writer
```

**Проверьте установку:**
```bash
libreoffice --version
```

LibreOffice автоматически будет использоваться как основной метод конвертации.

### Для CentOS/RHEL:

```bash
sudo yum install -y libreoffice libreoffice-writer
```

---

## Альтернативный вариант (если LibreOffice не подходит)

### Ubuntu/Debian с weasyprint:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

pip install --upgrade weasyprint
```

---

## Методы конвертации (в порядке приоритета)

Приложение автоматически использует следующие методы (в этом порядке):

1. **LibreOffice** ✓ РЕКОМЕНДУЕТСЯ
   - Самый надежный и быстрый метод
   - Лучше всего работает на Linux
   - Требует: `sudo apt-get install libreoffice libreoffice-writer`

2. **mammoth + weasyprint**
   - Альтернативный метод для Linux
   - Требует системные библиотеки Pango/Harfbuzz

3. **docx2pdf**
   - Только для Windows
   - Требует установленный Microsoft Word

---

## Проверка установки

### 1. Проверьте статус методов конвертации

```bash
cd /var/www/dmed
source .venv/bin/activate

cat > check.py << 'EOF'
from converter import LIBREOFFICE_AVAILABLE, MAMMOTH_AVAILABLE, WEASYPRINT_AVAILABLE, DOCX2PDF_AVAILABLE
print(f"LibreOffice: {'✓' if LIBREOFFICE_AVAILABLE else '✗'}")
print(f"Mammoth: {'✓' if MAMMOTH_AVAILABLE else '✗'}")
print(f"Weasyprint: {'✓' if WEASYPRINT_AVAILABLE else '✗'}")
print(f"Docx2pdf: {'✓' if DOCX2PDF_AVAILABLE else '✗'}")
EOF

python3 check.py
```

### 2. Проверьте скорость конвертации

```bash
cd /var/www/dmed
source .venv/bin/activate

cat > test_speed.py << 'EOF'
import time
import sys
sys.path.insert(0, '.')
from converter import convert_docx_to_pdf_from_docx
from document_generator import create_default_docx_template
import os

# Создаем тестовый DOCX
doc = create_default_docx_template()
test_docx = "/tmp/test_template.docx"
doc.save(test_docx)

# Конвертируем
test_data = {'uuid': 'test123', 'doc_number': 'TEST001', 'pin_code': '1234'}

start = time.time()
pdf_path = convert_docx_to_pdf_from_docx(test_docx, test_data)
elapsed = time.time() - start

print(f"Время конвертации: {elapsed:.2f} сек")
if pdf_path:
    print(f"✓ Конвертация работает! PDF создан: {pdf_path}")
else:
    print("✗ Ошибка конвертации")

# Очищаем
if os.path.exists(test_docx):
    os.remove(test_docx)
EOF

python3 test_speed.py
```

---

## Перезапуск приложения

После установки зависимостей перезапустите приложение:

```bash
sudo systemctl restart dmed

# Проверьте статус
sudo systemctl status dmed

# Смотрите логи
sudo journalctl -u dmed -f
```

---

## Оптимизация для продакшена

### Уменьшить использование памяти LibreOffice

Отредактируйте `/etc/systemd/system/dmed.service`:

```bash
sudo nano /etc/systemd/system/dmed.service
```

Найдите строку `Environment=` и добавьте:

```ini
Environment="SAL_NO_FONT_SUBSTITUTION=1"
Environment="SAL_NOUI=1"
```

После редактирования:
```bash
sudo systemctl daemon-reload
sudo systemctl restart dmed
```

### Установите шрифты (опционально)

```bash
sudo apt-get install -y fonts-liberation fonts-dejavu
```

---

## Устранение неполадок

### LibreOffice не найден

```bash
which libreoffice
sudo apt-get install -y libreoffice libreoffice-writer
```

### Ошибка "could not convert document"

```bash
# Проверьте логи
sudo journalctl -u dmed | grep -i error

# Убедитесь, что входной DOCX корректен
libreoffice --headless --convert-to pdf /path/to/test.docx
```

### Медленная конвертация

Уменьшите использование памяти или установите дополнительные библиотеки:

```bash
sudo apt-get install -y libcairo2 fontconfig
```

---

## Примечания

- **LibreOffice требует X11/дисплей?** Нет, параметр `--headless` позволяет использовать его без графического интерфейса
- **Может ли несколько процессов конвертировать одновременно?** Да, но ограничьте количество рабочих процессов Gunicorn на 4-8
- **Какой метод самый быстрый?** LibreOffice (250-500мс), Mammoth+Weasyprint (500-1500мс)
