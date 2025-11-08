"""
Скрипт для создания первого super_admin пользователя
Использование: python create_super_admin.py
"""
import bcrypt
import getpass
from database import db_insert, db_select

def create_super_admin():
    """Создает первого super_admin пользователя"""
    
    # Проверяем, есть ли уже super_admin
    existing = db_select('users', where_clause="role = 'super_admin'", fetch_one=True)
    if existing:
        print(f"⚠️  Super admin уже существует: {existing['username']}")
        response = input("Создать еще одного? (y/n): ")
        if response.lower() != 'y':
            return
    
    print("Создание нового Super Admin пользователя")
    print("-" * 50)
    
    username = input("Имя пользователя: ").strip()
    if not username:
        print("❌ Имя пользователя не может быть пустым")
        return
    
    # Проверяем, существует ли пользователь
    existing_user = db_select('users', where_clause="username = %s", params=[username], fetch_one=True)
    if existing_user:
        print(f"❌ Пользователь {username} уже существует")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email не может быть пустым")
        return
    
    # Проверяем, существует ли email
    existing_email = db_select('users', where_clause="email = %s", params=[email], fetch_one=True)
    if existing_email:
        print(f"❌ Email {email} уже используется")
        return
    
    password = getpass.getpass("Пароль: ")
    if len(password) < 6:
        print("❌ Пароль должен быть не менее 6 символов")
        return
    
    password_confirm = getpass.getpass("Подтвердите пароль: ")
    if password != password_confirm:
        print("❌ Пароли не совпадают")
        return
    
    # Хешируем пароль
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        # Создаем пользователя
        user = db_insert('users', {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': 'super_admin',
            'is_active': True,
            'created_by': None
        })
        
        if user:
            print("\n✅ Super Admin успешно создан!")
            print(f"   ID: {user['id']}")
            print(f"   Имя пользователя: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Роль: {user['role']}")
        else:
            print("❌ Ошибка при создании пользователя")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    try:
        create_super_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

