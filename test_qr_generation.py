"""Тестовый скрипт для проверки генерации QR-кода"""
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import generate_qr_code

def test_qr_generation():
    """Тестирует генерацию QR-кода"""
    print("=" * 50)
    print("Тест генерации QR-кода")
    print("=" * 50)
    
    # Тестовый URL
    test_url = "https://docs.dmed.uz/access/test-uuid-12345"
    
    try:
        print(f"\n1. Генерируем QR-код для URL: {test_url}")
        qr_img = generate_qr_code(test_url)
        
        print(f"2. Тип объекта: {type(qr_img)}")
        print(f"3. Размер изображения: {qr_img.size}")
        print(f"4. Режим изображения: {qr_img.mode}")
        
        # Сохраняем тестовое изображение
        test_output = "test_qr_code.png"
        qr_img.save(test_output, 'PNG')
        print(f"5. QR-код сохранен в файл: {test_output}")
        
        # Проверяем что файл существует
        if os.path.exists(test_output):
            file_size = os.path.getsize(test_output)
            print(f"6. Размер файла: {file_size} байт")
            print("\n[OK] Тест пройден успешно! QR-код сгенерирован и сохранен.")
            return True
        else:
            print("\n[ERROR] Ошибка: Файл не был создан!")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Ошибка при генерации QR-кода: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_qr_generation()
    sys.exit(0 if success else 1)

