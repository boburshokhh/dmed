"""Функции для работы с базой данных PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE

# Создаем пул подключений (отложенная инициализация)
db_pool = None


def get_db_connection():
    """Создает подключение к PostgreSQL"""
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD не установлен. Проверьте файл .env")
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=DB_SSLMODE
    )


def init_db_pool():
    """Инициализирует пул подключений к БД"""
    global db_pool
    if db_pool is None:
        try:
            from psycopg2 import pool as psycopg2_pool
            if not DB_PASSWORD:
                print("WARNING: DB_PASSWORD не установлен. Проверьте файл .env")
                return None
            
            db_pool = psycopg2_pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                sslmode=DB_SSLMODE
            )
            print("OK: Подключение к PostgreSQL установлено")
            return db_pool
        except Exception as e:
            print(f"ERROR: Ошибка подключения к PostgreSQL: {e}")
            db_pool = None
            return None
    return db_pool


def db_query(query, params=None, fetch_one=False, fetch_all=False):
    """Выполняет SQL запрос к БД"""
    conn = None
    try:
        # Инициализируем пул при первом использовании
        pool = init_db_pool()
        if pool:
            conn = pool.getconn()
        else:
            conn = get_db_connection()
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
            conn.commit()
        elif fetch_all:
            result = cursor.fetchall()
            conn.commit()
        else:
            conn.commit()
            result = cursor.rowcount
        
        cursor.close()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Ошибка БД: {e}")
        raise e
    finally:
        if conn:
            pool = init_db_pool()
            if pool:
                pool.putconn(conn)
            else:
                conn.close()


def db_insert(table, data):
    """Вставляет запись в таблицу и возвращает созданную запись"""
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    values = list(data.values())
    
    query = f"""
        INSERT INTO {table} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    print(f"DEBUG db_insert: query = {query[:200]}...")
    print(f"DEBUG db_insert: values count = {len(values)}")
    
    try:
        result = db_query(query, values, fetch_one=True)
        print(f"DEBUG db_insert: result = {result}")
        if result:
            result_dict = dict(result)
            print(f"DEBUG db_insert: result_dict keys = {list(result_dict.keys())}")
            return result_dict
        else:
            print("WARNING: db_insert вернул None")
            return None
    except Exception as e:
        print(f"ERROR db_insert: {e}")
        import traceback
        print(traceback.format_exc())
        raise


def db_select(table, where_clause=None, params=None, fetch_one=False):
    """Выбирает записи из таблицы"""
    query = f"SELECT * FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    
    if fetch_one:
        result = db_query(query, params, fetch_one=True)
        if result:
            return dict(result)
        return None
    else:
        results = db_query(query, params, fetch_all=True)
        if results:
            return [dict(row) for row in results]
        return []


def db_update(table, data, where_clause, where_params):
    """Обновляет запись в таблице"""
    set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
    values = list(data.values()) + list(where_params)
    
    query = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE {where_clause}
    """
    
    db_query(query, values)

