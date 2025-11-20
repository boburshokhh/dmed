"""Тестовый скрипт для проверки генерации QR-кода в документе"""
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import generate_qr_code
from PIL import Image

def test_qr_in_document():
    """Тестирует генерацию QR-кода для использования в документе"""
    print("=" * 60)
    print("Тест генерации QR-кода для документа")
    print("=" * 60)
    
    # Тестовый URL
    test_url = "https://docs.dmed.uz/access/test-uuid-12345"
    test_pin = "1234"
    
    try:
        print(f"\n1. Генерируем QR-код для URL: {test_url}")
        qr_img = generate_qr_code(test_url)
        
        print(f"2. Тип объекта: {type(qr_img)}")
        print(f"3. Размер изображения: {qr_img.size}")
        print(f"4. Режим изображения: {qr_img.mode}")
        
        # Проверяем что это PIL Image
        if not isinstance(qr_img, Image.Image):
            print("[ERROR] Объект не является PIL Image!")
            return False
        
        # Проверяем что можно сохранить в PNG (как в document_generator.py)
        upload_folder = 'static/generated_documents'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        
        qr_temp_path = os.path.join(upload_folder, f'qr_temp_{test_pin}.png')
        
        print(f"\n5. Сохраняем QR-код в файл (как в document_generator): {qr_temp_path}")
        with open(qr_temp_path, 'wb') as f:
            qr_img.save(f, 'PNG')
        
        # Проверяем что файл создан
        if os.path.exists(qr_temp_path):
            file_size = os.path.getsize(qr_temp_path)
            print(f"6. Размер файла: {file_size} байт")
            
            # Проверяем что файл можно открыть как изображение
            test_img = Image.open(qr_temp_path)
            print(f"7. Файл открыт успешно, размер: {test_img.size}, режим: {test_img.mode}")
            
            # Удаляем тестовый файл
            os.remove(qr_temp_path)
            print(f"8. Тестовый файл удален")
            
            print("\n[OK] Все тесты пройдены успешно! QR-код готов для использования в документе.")
            return True
        else:
            print("\n[ERROR] Ошибка: Файл не был создан!")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Ошибка при тестировании: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_qr_in_document()
    sys.exit(0 if success else 1)

