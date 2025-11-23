# Диагностика qrcode-styled на Ubuntu сервере

## Шаг 1: Загрузите скрипт диагностики на сервер

Скопируйте файл `diagnose_qrcode_styled.py` на ваш Ubuntu сервер.

## Шаг 2: Запустите диагностику

На Ubuntu сервере выполните:

```bash
# Активируйте виртуальное окружение (если используется)
source venv/bin/activate  # или путь к вашему venv

# Запустите диагностику

1. Версия Python:
   3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]
   Путь к Python: /usr/bin/python3

2. Проверка установленных библиотек:
/var/www/dmed/diagnose_qrcode_styled.py:24: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  import pkg_resources
   ✗ qrcode-styled: НЕ УСТАНОВЛЕН
   ✗ Pillow: НЕ УСТАНОВЛЕН
   ✗ qrcode: НЕ УСТАНОВЛЕН

3. Проверка импорта qrcode-styled:
   ✗ Ошибка импорта: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 40, in <module>
    import qrcode_styled
ModuleNotFoundError: No module named 'qrcode_styled'

4. Проверка класса QRCodeStyled:
   ✗ Ошибка: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 60, in <module>
    from qrcode_styled import QRCodeStyled
ModuleNotFoundError: No module named 'qrcode_styled'

5. Проверка PIL/Pillow:
   ✗ Ошибка импорта PIL: No module named 'PIL'

6. Создание экземпляра QRCodeStyled:
   ✗ Ошибка создания экземпляра: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 97, in <module>
    from qrcode_styled import QRCodeStyled
ModuleNotFoundError: No module named 'qrcode_styled'

7. Попытка создать простой QR-код (без логотипа):
   ✗ Ошибка при создании QR-кода: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 109, in <module>
    from qrcode_styled import QRCodeStyled
ModuleNotFoundError: No module named 'qrcode_styled'

8. Попытка создать QR-код с логотипом:
   ✗ Ошибка при создании QR-кода с логотипом: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 148, in <module>
    from qrcode_styled import QRCodeStyled
ModuleNotFoundError: No module named 'qrcode_styled'

9. Проверка зависимостей qrcode-styled:
   Не удалось получить зависимости: The 'qrcode-styled' distribution was not found and is required by the application

10. Пути Python (sys.path):
   1. /var/www/dmed
   2. /usr/lib/python312.zip
   3. /usr/lib/python3.12
   4. /usr/lib/python3.12/lib-dynload
   5. /usr/local/lib/python3.12/dist-packages
   ... и еще 1 путей

11. Детальная информация о версиях:
   qrcode-styled: НЕ УСТАНОВЛЕН
   Pillow: НЕ УСТАНОВЛЕН

12. Финальный тест - симуляция generate_qr_code:
   ✗ ФИНАЛЬНЫЙ ТЕСТ НЕ ПРОЙДЕН: No module named 'qrcode_styled'
Traceback (most recent call last):
  File "/var/www/dmed/diagnose_qrcode_styled.py", line 228, in <module>
    from qrcode_styled import QRCodeStyled
ModuleNotFoundError: No module named 'qrcode_styled'

======================================================================
ДИАГНОСТИКА ЗАВЕРШЕНА
======================================================================

Отправьте весь вывод этого скрипта для анализа проблемы.
root@vps06248:/var/www/dmed# 
```

## Шаг 3: Отправьте результаты

Скопируйте **весь вывод** скрипта и отправьте для анализа.

---

## Альтернатива: Быстрая проверка вручную

Если не можете запустить скрипт, выполните эти команды по порядку:

### 1. Проверка установки
```bash
source venv/bin/activate  # если используете venv
pip3 list | grep -i qrcode
pip3 list | grep -i pillow
```

### 2. Проверка импорта
```bash
python3 -c "import qrcode_styled; print('OK:', qrcode_styled.__file__)"
```

### 3. Проверка версий
```bash
python3 -c "
import qrcode_styled
from PIL import Image
print('qrcode-styled:', getattr(qrcode_styled, '__version__', 'unknown'))
print('Pillow:', Image.__version__)
"
```

### 4. Тест создания QR-кода
```bash
python3 -c "
from qrcode_styled import QRCodeStyled
from PIL import Image

qr = QRCodeStyled()
img = qr.get_image('test')
print('Тип:', type(img))
print('PIL Image:', isinstance(img, Image.Image))
if isinstance(img, Image.Image):
    print('Размер:', img.size)
    print('Режим:', img.mode)
else:
    print('НЕ PIL Image!')
"
```

### 5. Проверка логов приложения
```bash
# Если используете systemd
sudo journalctl -u dmed -n 100 | grep -i qr

# Или если запускаете напрямую
# просто скопируйте последние логи с ошибками
```

---

## Возможные проблемы и решения

### Проблема 1: qrcode-styled не установлен
**Решение:**
```bash
source venv/bin/activate
pip3 install qrcode-styled>=0.2.0
```

### Проблема 2: Несовместимость версий Pillow
**Решение:**
```bash
source venv/bin/activate
pip3 install --upgrade Pillow>=10.0.0
```

### Проблема 3: qrcode-styled возвращает не PIL.Image
**Решение:** Это известная проблема некоторых версий. Нужно обновить код для обработки.

### Проблема 4: Ошибка импорта
**Решение:**
```bash
source venv/bin/activate
pip3 uninstall qrcode-styled
pip3 install qrcode-styled>=0.2.0
```

---

## После диагностики

Отправьте результаты, и я:
1. Определю точную причину проблемы
2. Предложу конкретное решение
3. Обновлю код при необходимости

