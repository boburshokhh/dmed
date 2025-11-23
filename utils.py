"""Утилиты для работы приложения"""
import random
import string
from datetime import datetime
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
        # Ярко-синий цвет звездочки как на фото (#0088cc или #229ED9)
        draw.polygon(points, fill="#0088cc")
    
    return img


def generate_qr_code(url):
    """Генерирует QR-код используя qrcode-styled для стиля Telegram"""
    try:
        from qrcode_styled import QRCodeStyled
        
        logo_img = create_logo_image(size=200)
        
        if logo_img and logo_img.mode != 'RGBA':
            try:
                logo_img = logo_img.convert('RGBA')
            except:
                pass
        
        qr = QRCodeStyled()
        
        try:
            try:
                img = qr.get_image(url, image=logo_img if logo_img else None)
            except TypeError:
                try:
                    img = qr.get_image(url)
                except Exception as e2:
                    print(f"[ERROR] Ошибка генерации QR-кода: {e2}")
                    raise
        except Exception as get_image_error:
            print(f"[ERROR] Ошибка при вызове qr.get_image(): {get_image_error}")
            import traceback
            print(traceback.format_exc())
            raise
        
        if img is None:
            raise Exception("qrcode-styled.get_image() вернул None")
        
        is_pil_image = isinstance(img, Image.Image) or (hasattr(img, 'save') and hasattr(img, 'size') and hasattr(img, 'mode'))
        
        if is_pil_image:
            if img.mode != 'RGBA':
                try:
                    img = img.convert('RGBA')
                except:
                    pass
        else:
            try:
                import io
                buffer = io.BytesIO()
                if hasattr(img, 'save'):
                    img.save(buffer, 'PNG')
                else:
                    raise Exception(f"Объект {type(img)} не имеет метода save()")
                buffer.seek(0)
                img = Image.open(buffer).convert('RGBA')
            except Exception as save_error:
                print(f"[ERROR] Не удалось обработать изображение: {save_error}")
                import traceback
                print(traceback.format_exc())
                raise Exception(f"Не удалось обработать изображение от qrcode-styled: {save_error}")
        
        if hasattr(img, '__class__') and 'PilStyledImage' in str(type(img)):
            try:
                import io
                buffer = io.BytesIO()
                img.save(buffer, 'PNG')
                buffer.seek(0)
                img = Image.open(buffer).convert('RGBA')
            except:
                pass
        
        if not isinstance(img, Image.Image) and not (hasattr(img, 'save') and hasattr(img, 'size') and hasattr(img, 'mode')):
            raise Exception(f"После обработки изображение все еще не PIL.Image, тип: {type(img)}")
        
        if not hasattr(img, 'size') or img.size[0] == 0 or img.size[1] == 0:
            raise Exception(f"Изображение имеет нулевой или неопределенный размер: {getattr(img, 'size', 'unknown')}")
        
        if hasattr(img, '__class__') and 'PilStyledImage' in str(type(img)):
            try:
                import io
                buffer = io.BytesIO()
                img.save(buffer, 'PNG')
                buffer.seek(0)
                img = Image.open(buffer).convert('RGBA')
            except:
                pass
        
        return img
        
    except ImportError as e:
        error_msg = f"qrcode-styled не установлен: {e}. Установите библиотеку: pip install qrcode-styled"
        print(f"[ERROR] {error_msg}")
        import traceback
        print(traceback.format_exc())
        raise ImportError(error_msg)
    except Exception as e:
        error_msg = f"Ошибка при генерации QR-кода: {e}"
        print(f"[ERROR] {error_msg}")
        import traceback
        print(traceback.format_exc())
        raise Exception(error_msg)
