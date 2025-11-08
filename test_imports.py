"""
Тест импорта всех модулей
"""
print("Проверка импорта модулей...")

try:
    from auth_routes import auth_bp, admin_bp
    print("✓ auth_routes импортирован успешно")
except Exception as e:
    print(f"✗ auth_routes: {e}")

try:
    from document_routes import documents_bp
    print("✓ document_routes импортирован успешно")
except Exception as e:
    print(f"✗ document_routes: {e}")

try:
    import app
    print("✓ app.py импортирован успешно")
except Exception as e:
    print(f"✗ app.py: {e}")

print("\n✅ Все проверки завершены!")

