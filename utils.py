"""Утилиты для работы приложения"""
import random
import string
from datetime import datetime
import qrcode
from PIL import Image, ImageDraw
import io
import os
from config import DOC_NUMBER_PREFIX, DOC_NUMBER_FORMAT


def generate_document_number():
    """Генерирует уникальный номер документа в формате: № 01ВШ XXXXXXX"""
    max_attempts = 100
    
    # Префикс организации из конфига
    prefix = DOC_NUMBER_PREFIX
    
    for _ in range(max_attempts):
        # Генерируем 9-значный номер в зависимости от формата
        if DOC_NUMBER_FORMAT == 'date':
            # Формат: DDMMYY + 3 цифры порядкового номера (рекомендуется)
            now = datetime.now()
            date_part = f"{now.day:02d}{now.month:02d}{now.year % 100:02d}"
            serial_part = random.randint(100, 999)
            number_part = int(f"{date_part}{serial_part}")
        elif DOC_NUMBER_FORMAT == 'random':
            # Случайный 9-значный номер
            number_part = random.randint(100000000, 999999999)
        else:
            # Sequential или по умолчанию - timestamp
            number_part = int(datetime.now().timestamp()) % 1000000000
        
        # Формируем полный номер: № 01ВШ XXXXXXX
        doc_number = f"№ {prefix} {number_part:09d}"
        
        # Проверяем уникальность в БД (импортируем здесь чтобы избежать циклических импортов)
        try:
            from database import db_select
            result = db_select('documents', 'doc_number = %s', [doc_number], fetch_one=True)
        except ImportError:
            # Если database еще не импортирован, пропускаем проверку
            result = None
        if not result:
            return doc_number
    
    # Если не удалось найти уникальный номер, используем timestamp
    timestamp = int(datetime.now().timestamp())
    return f"№ {prefix} {timestamp % 1000000000:09d}"


def generate_pin_code():
    """Генерирует 4-значный PIN-код"""
    return ''.join(random.choices(string.digits, k=4))


def create_logo_image(size=100):
    """Создает изображение логотипа из SVG файла shoxahosh.svg"""
    # Путь к файлу shoxahosh.svg
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Директория где utils.py
    project_root = os.path.dirname(base_dir)  # Корень проекта (dmed)
    logo_svg_path = os.path.join(project_root, 'front', 'public', 'shoxahosh.svg')
    
    # Альтернативный путь
    if not os.path.exists(logo_svg_path):
        alt_path = os.path.join(base_dir, 'front', 'public', 'shoxahosh.svg')
        if os.path.exists(alt_path):
            logo_svg_path = alt_path
    
    # Пробуем использовать cairosvg (работает на Linux, требует системные библиотеки)
    if os.path.exists(logo_svg_path):
        try:
            import cairosvg
            with open(logo_svg_path, 'rb') as f:
                svg_data = f.read()
            
            # Конвертируем весь SVG файл в PNG
            # Сохраняем пропорции оригинального SVG (276x76)
            # Но делаем квадратным для QR-кода
            png_data = cairosvg.svg2png(
                bytestring=svg_data, 
                output_width=size, 
                output_height=size
            )
            img = Image.open(io.BytesIO(png_data))
            return img.convert('RGBA')
        except (ImportError, OSError):
            # cairosvg не работает на Windows без системных библиотек
            pass
        except Exception:
            # Другие ошибки - используем fallback
            pass
    
    # Fallback: Рисуем упрощенную версию символа ✱ через PIL
    # Это работает на всех платформах без дополнительных библиотек
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # Рисуем упрощенный символ ✱ - 8-конечная звезда
    star_outer_radius = int(size * 0.35)
    star_inner_radius = int(size * 0.15)
    
    import math
    points = []
    for i in range(16):
        angle = i * math.pi / 8
        if i % 2 == 0:
            r = star_outer_radius
        else:
            r = star_inner_radius
        x = center + int(r * math.cos(angle))
        y = center + int(r * math.sin(angle))
        points.append((x, y))
    
    if len(points) > 2:
        draw.polygon(points, fill="#0D34B4")
    
    return img


def generate_qr_code(url):
    """Генерирует QR-код с логотипом в центре согласно спецификации"""
    # Спецификация QR-кода:
    # - error_correction: "H" (High) - позволяет заменить до 30% данных
    # - quiet_zone_modules: 4 (отступы)
    # - logo size_ratio: 0.22 (22% от размера QR-кода)
    # - logo overprint: true (логотип поверх, без белого фона)
    
    ERROR_CORRECT_H = qrcode.constants.ERROR_CORRECT_H  # Уровень коррекции ошибок H (High)
    
    qr = qrcode.QRCode(
        version=None,  # Автоматический выбор версии
        error_correction=ERROR_CORRECT_H,  # Высокий уровень для вставки логотипа
        box_size=10,
        border=4,  # quiet_zone_modules: 4
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Создаем базовое изображение QR-кода
    # Стиль: черные модули на белом фоне, квадратные угловые маркеры
    img = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert('RGB')
    
    # Создаем логотип согласно спецификации
    # size_ratio: 0.22 (22% от размера QR-кода) - уменьшено в 2 раза от предыдущего
    qr_size = min(img.size)
    logo_size = int(qr_size * 0.22)  # Логотип занимает 22% размера QR-кода
    logo = create_logo_image(size=logo_size)
    
    if logo:
        # Вычисляем позицию для вставки логотипа (центр)
        img_width, img_height = img.size
        logo_width, logo_height = logo.size
        
        # Позиция для вставки (центр)
        pos = ((img_width - logo_width) // 2, (img_height - logo_height) // 2)
        
        # overprint: true - логотип вставляется поверх без белого фона
        # Конвертируем изображение QR-кода в RGBA для поддержки прозрачности
        img = img.convert('RGBA')
        
        # Вставляем логотип поверх QR-кода (overprint)
        img.paste(logo, pos, logo)
        
        # Конвертируем обратно в RGB
        img = img.convert('RGB')
    
    return img

