-- Миграция для создания таблицы пользователей с ролями
-- Роли: admin, super_admin

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'super_admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    last_login TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Создание первого super_admin пользователя (пароль: admin123)
-- Пароль должен быть захеширован с помощью bcrypt
-- Для примера: хеш для 'admin123' (нужно будет заменить на реальный хеш)
-- INSERT INTO users (username, email, password_hash, role, created_by) 
-- VALUES ('superadmin', 'admin@tamex.uz', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5q5', 'super_admin', NULL);

COMMENT ON TABLE users IS 'Таблица пользователей системы управления генерацией документов';
COMMENT ON COLUMN users.role IS 'Роль пользователя: admin или super_admin';
COMMENT ON COLUMN users.created_by IS 'ID пользователя, создавшего этого пользователя (для super_admin NULL)';

