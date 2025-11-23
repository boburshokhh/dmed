#!/usr/bin/env python3
"""
Скрипт диагностики qrcode-styled на Ubuntu сервере
Запустите: python3 diagnose_qrcode_styled.py
"""

import sys
import os

print("=" * 70)
print("ДИАГНОСТИКА qrcode-styled")
print("=" * 70)
print()

# 1. Проверка версии Python
print("1. Версия Python:")
print(f"   {sys.version}")
print(f"   Путь к Python: {sys.executable}")
print()

# 2. Проверка установленных библиотек
print("2. Проверка установленных библиотек:")
try:
    import pkg_resources
    
    packages_to_check = ['qrcode-styled', 'Pillow', 'qrcode']
    for package in packages_to_check:
        try:
            dist = pkg_resources.get_distribution(package)
            print(f"   ✓ {package}: {dist.version}")
        except pkg_resources.DistributionNotFound:
            print(f"   ✗ {package}: НЕ УСТАНОВЛЕН")
except Exception as e:
    print(f"   Ошибка при проверке пакетов: {e}")
print()

# 3. Проверка импорта qrcode-styled
print("3. Проверка импорта qrcode-styled:")
try:
    import qrcode_styled
    print(f"   ✓ Импорт успешен")
    print(f"   Путь к модулю: {qrcode_styled.__file__}")
    try:
        print(f"   Версия: {qrcode_styled.__version__}")
    except:
        print(f"   Версия: не указана")
except ImportError as e:
    print(f"   ✗ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"   ✗ Другая ошибка: {e}")
    import traceback
    traceback.print_exc()
print()

# 4. Проверка QRCodeStyled класса
print("4. Проверка класса QRCodeStyled:")
try:
    from qrcode_styled import QRCodeStyled
    print(f"   ✓ Класс QRCodeStyled импортирован")
    
    # Проверяем методы
    import inspect
    methods = [m for m in dir(QRCodeStyled) if not m.startswith('_')]
    print(f"   Доступные методы: {', '.join(methods[:5])}...")
    
    # Проверяем сигнатуру get_image
    try:
        sig = inspect.signature(QRCodeStyled.get_image)
        print(f"   Сигнатура get_image: {sig}")
    except Exception as e:
        print(f"   Не удалось получить сигнатуру: {e}")
        
except Exception as e:
    print(f"   ✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
print()

# 5. Проверка PIL/Pillow
print("5. Проверка PIL/Pillow:")
try:
    from PIL import Image
    print(f"   ✓ PIL импортирован")
    print(f"   Версия Pillow: {Image.__version__}")
    print(f"   Режимы изображений: {Image.MODES}")
except ImportError as e:
    print(f"   ✗ Ошибка импорта PIL: {e}")
except Exception as e:
    print(f"   ✗ Другая ошибка: {e}")
print()

# 6. Попытка создать экземпляр QRCodeStyled
print("6. Создание экземпляра QRCodeStyled:")
try:
    from qrcode_styled import QRCodeStyled
    qr = QRCodeStyled()
    print(f"   ✓ Экземпляр создан: {type(qr)}")
except Exception as e:
    print(f"   ✗ Ошибка создания экземпляра: {e}")
    import traceback
    traceback.print_exc()
print()

# 7. Попытка создать простой QR-код
print("7. Попытка создать простой QR-код (без логотипа):")
try:
    from qrcode_styled import QRCodeStyled
    from PIL import Image
    
    qr = QRCodeStyled()
    print("   Вызываем qr.get_image('test')...")
    img = qr.get_image('test')
    
    print(f"   ✓ QR-код создан!")
    print(f"   Тип результата: {type(img)}")
    
    # Проверяем, является ли это PIL Image
    if isinstance(img, Image.Image):
        print(f"   ✓ Это PIL.Image")
        print(f"   Размер: {img.size}")
        print(f"   Режим: {img.mode}")
    else:
        print(f"   ⚠ Это НЕ PIL.Image, тип: {type(img)}")
        # Проверяем, есть ли метод save
        if hasattr(img, 'save'):
            print(f"   ✓ Есть метод save()")
            # Пробуем сохранить
            import io
            buffer = io.BytesIO()
            img.save(buffer, 'PNG')
            buffer.seek(0)
            pil_img = Image.open(buffer)
            print(f"   ✓ Конвертировано в PIL.Image, размер: {pil_img.size}")
        else:
            print(f"   ✗ Нет метода save()")
            
except Exception as e:
    print(f"   ✗ Ошибка при создании QR-кода: {e}")
    import traceback
    traceback.print_exc()
print()

# 8. Попытка создать QR-код с логотипом
print("8. Попытка создать QR-код с логотипом:")
try:
    from qrcode_styled import QRCodeStyled
    from PIL import Image
    
    # Создаем простой логотип
    logo = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
    print(f"   Логотип создан: {logo.size}, {logo.mode}")
    
    qr = QRCodeStyled()
    print("   Вызываем qr.get_image('test', image=logo)...")
    img = qr.get_image('test', image=logo)
    
    print(f"   ✓ QR-код с логотипом создан!")
    print(f"   Тип результата: {type(img)}")
    
    if isinstance(img, Image.Image):
        print(f"   ✓ Это PIL.Image, размер: {img.size}, режим: {img.mode}")
    else:
        print(f"   ⚠ Это НЕ PIL.Image, тип: {type(img)}")
        
except Exception as e:
    print(f"   ✗ Ошибка при создании QR-кода с логотипом: {e}")
    import traceback
    traceback.print_exc()
print()

# 9. Проверка зависимостей qrcode-styled
print("9. Проверка зависимостей qrcode-styled:")
try:
    import pkg_resources
    dist = pkg_resources.get_distribution('qrcode-styled')
    print(f"   Установленные зависимости:")
    for req in dist.requires():
        print(f"     - {req}")
except Exception as e:
    print(f"   Не удалось получить зависимости: {e}")
print()

# 10. Проверка путей Python
print("10. Пути Python (sys.path):")
for i, path in enumerate(sys.path[:5]):  # Показываем первые 5
    print(f"   {i+1}. {path}")
if len(sys.path) > 5:
    print(f"   ... и еще {len(sys.path) - 5} путей")
print()

# 11. Проверка версий библиотек (детально)
print("11. Детальная информация о версиях:")
try:
    import pkg_resources
    
    critical_packages = {
        'qrcode-styled': '>=0.2.0',
        'Pillow': '>=9.0.0',
    }
    
    for package, min_version in critical_packages.items():
        try:
            dist = pkg_resources.get_distribution(package)
            installed_version = dist.version
            print(f"   {package}:")
            print(f"     Установлено: {installed_version}")
            print(f"     Требуется: {min_version}")
            
            # Простая проверка совместимости
            if package == 'Pillow':
                try:
                    from PIL import Image
                    print(f"     PIL работает: ✓")
                except:
                    print(f"     PIL работает: ✗")
                    
        except pkg_resources.DistributionNotFound:
            print(f"   {package}: НЕ УСТАНОВЛЕН")
except Exception as e:
    print(f"   Ошибка: {e}")
print()

# 12. Финальный тест - полная симуляция функции generate_qr_code
print("12. Финальный тест - симуляция generate_qr_code:")
try:
    from qrcode_styled import QRCodeStyled
    from PIL import Image
    
    # Создаем логотип как в реальном коде
    logo = Image.new('RGBA', (200, 200), (0, 136, 204, 255))
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')
    
    qr = QRCodeStyled()
    img = qr.get_image('https://test.example.com', image=logo)
    
    if isinstance(img, Image.Image):
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        print(f"   ✓ ФИНАЛЬНЫЙ ТЕСТ ПРОЙДЕН!")
        print(f"   Размер: {img.size}, Режим: {img.mode}")
    else:
        import io
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        img = Image.open(buffer).convert('RGBA')
        print(f"   ✓ ФИНАЛЬНЫЙ ТЕСТ ПРОЙДЕН (после конвертации)!")
        print(f"   Размер: {img.size}, Режим: {img.mode}")
        
except Exception as e:
    print(f"   ✗ ФИНАЛЬНЫЙ ТЕСТ НЕ ПРОЙДЕН: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 70)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 70)
print()
print("Отправьте весь вывод этого скрипта для анализа проблемы.")

