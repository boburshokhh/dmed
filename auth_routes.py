"""
API маршруты для авторизации и управления пользователями
"""
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
from database import db_select, db_insert, db_update
from config import SECRET_KEY

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Время жизни токена (7 дней)
TOKEN_EXPIRATION_DAYS = 7


def generate_token(user_id, username, role):
    """Генерирует JWT токен"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=TOKEN_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def verify_token(token):
    """Проверяет JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Неверный формат токена'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Токен отсутствует'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Недействительный или истекший токен'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def require_super_admin(f):
    """Декоратор для проверки прав super_admin"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.current_user.get('role') != 'super_admin':
            return jsonify({'success': False, 'message': 'Недостаточно прав'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== АВТОРИЗАЦИЯ ====================

@auth_bp.route('/login', methods=['POST'])
def login():
    """Вход в систему"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Имя пользователя и пароль обязательны'}), 400
        
        # Ищем пользователя
        user = db_select('users', where_clause='username = %s', params=[username], fetch_one=True)
        
        if not user:
            return jsonify({'success': False, 'message': 'Неверное имя пользователя или пароль'}), 401
        
        if not user.get('is_active'):
            return jsonify({'success': False, 'message': 'Учетная запись деактивирована'}), 403
        
        # Проверяем пароль
        password_hash = user.get('password_hash')
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({'success': False, 'message': 'Неверное имя пользователя или пароль'}), 401
        
        # Обновляем время последнего входа
        try:
            db_update('users', {'last_login': datetime.now()}, 'id = %s', [user['id']])
        except:
            pass
        
        # Генерируем токен
        token = generate_token(user['id'], user['username'], user['role'])
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'is_active': user['is_active']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка входа: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Выход из системы"""
    return jsonify({'success': True, 'message': 'Выход выполнен успешно'})


# ==================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (SUPER_ADMIN) ====================

@admin_bp.route('/users', methods=['GET'])
@require_super_admin
def list_users():
    """Список всех пользователей"""
    try:
        users = db_select('users')
        # Убираем пароли из ответа
        for user in users:
            user.pop('password_hash', None)
        return jsonify(users)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка получения списка пользователей: {str(e)}'}), 500


@admin_bp.route('/users', methods=['POST'])
@require_super_admin
def create_user():
    """Создание нового пользователя"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'admin')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'Имя пользователя, email и пароль обязательны'}), 400
        
        if role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': 'Неверная роль'}), 400
        
        # Проверяем, существует ли пользователь
        existing_user = db_select('users', where_clause='username = %s', params=[username], fetch_one=True)
        if existing_user:
            return jsonify({'success': False, 'message': 'Пользователь с таким именем уже существует'}), 400
        
        existing_email = db_select('users', where_clause='email = %s', params=[email], fetch_one=True)
        if existing_email:
            return jsonify({'success': False, 'message': 'Пользователь с таким email уже существует'}), 400
        
        # Хешируем пароль
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Создаем пользователя
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'created_by': request.current_user.get('user_id')
        }
        
        new_user = db_insert('users', user_data)
        new_user.pop('password_hash', None)
        
        return jsonify(new_user), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка создания пользователя: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_super_admin
def update_user(user_id):
    """Обновление пользователя"""
    try:
        data = request.get_json()
        
        # Проверяем, существует ли пользователь
        user = db_select('users', where_clause='id = %s', params=[user_id], fetch_one=True)
        if not user:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
        
        # Не позволяем изменять самого себя (защита от случайной блокировки)
        if user_id == request.current_user.get('user_id'):
            if data.get('is_active') == False:
                return jsonify({'success': False, 'message': 'Нельзя деактивировать самого себя'}), 400
        
        update_data = {}
        
        if 'username' in data:
            # Проверяем уникальность username
            existing = db_select('users', where_clause='username = %s AND id != %s', params=[data['username'], user_id], fetch_one=True)
            if existing:
                return jsonify({'success': False, 'message': 'Пользователь с таким именем уже существует'}), 400
            update_data['username'] = data['username']
        
        if 'email' in data:
            # Проверяем уникальность email
            existing = db_select('users', where_clause='email = %s AND id != %s', params=[data['email'], user_id], fetch_one=True)
            if existing:
                return jsonify({'success': False, 'message': 'Пользователь с таким email уже существует'}), 400
            update_data['email'] = data['email']
        
        if 'password' in data and data['password']:
            # Хешируем новый пароль
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_data['password_hash'] = password_hash
        
        if 'role' in data:
            if data['role'] not in ['admin', 'super_admin']:
                return jsonify({'success': False, 'message': 'Неверная роль'}), 400
            # Не позволяем изменять роль самого себя
            if user_id == request.current_user.get('user_id'):
                return jsonify({'success': False, 'message': 'Нельзя изменить свою роль'}), 400
            update_data['role'] = data['role']
        
        if 'is_active' in data:
            update_data['is_active'] = data['is_active']
        
        if update_data:
            db_update('users', update_data, 'id = %s', [user_id])
        
        # Возвращаем обновленного пользователя
        updated_user = db_select('users', where_clause='id = %s', params=[user_id], fetch_one=True)
        updated_user.pop('password_hash', None)
        
        return jsonify(updated_user)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка обновления пользователя: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_super_admin
def delete_user(user_id):
    """Удаление пользователя"""
    try:
        # Проверяем, существует ли пользователь
        user = db_select('users', where_clause='id = %s', params=[user_id], fetch_one=True)
        if not user:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
        
        # Не позволяем удалить самого себя
        if user_id == request.current_user.get('user_id'):
            return jsonify({'success': False, 'message': 'Нельзя удалить самого себя'}), 400
        
        # Не позволяем удалить super_admin
        if user.get('role') == 'super_admin':
            return jsonify({'success': False, 'message': 'Нельзя удалить super_admin'}), 400
        
        # Удаляем пользователя
        from database import db_query
        db_query('DELETE FROM users WHERE id = %s', [user_id])
        
        return jsonify({'success': True, 'message': 'Пользователь удален'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка удаления пользователя: {str(e)}'}), 500


@admin_bp.route('/stats/users', methods=['GET'])
@require_super_admin
def stats_users():
    """Статистика пользователей"""
    try:
        from database import db_query
        
        total = db_query('SELECT COUNT(*) as count FROM users', fetch_one=True)
        active = db_query('SELECT COUNT(*) as count FROM users WHERE is_active = TRUE', fetch_one=True)
        
        return jsonify({
            'total': total.get('count', 0) if total else 0,
            'active': active.get('count', 0) if active else 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка получения статистики: {str(e)}'}), 500


@admin_bp.route('/stats/documents', methods=['GET'])
@require_super_admin
def stats_documents():
    """Статистика документов"""
    try:
        from database import db_query
        
        result = db_query('SELECT COUNT(*) as count FROM documents', fetch_one=True)
        
        return jsonify({
            'total': result.get('count', 0) if result else 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка получения статистики: {str(e)}'}), 500

