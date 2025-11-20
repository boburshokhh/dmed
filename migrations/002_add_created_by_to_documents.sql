-- Миграция для добавления поля created_by в таблицу documents
-- Это поле будет хранить ID пользователя, создавшего документ

-- Добавляем поле created_by с внешним ключом на таблицу users
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);

-- Создаем индекс для быстрого поиска документов по создателю
CREATE INDEX IF NOT EXISTS idx_documents_created_by ON documents(created_by);

-- Добавляем комментарий к полю
COMMENT ON COLUMN documents.created_by IS 'ID пользователя, создавшего документ';

