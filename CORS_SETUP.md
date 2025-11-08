# Настройка CORS для работы с PDF документами

## Что было настроено

### 1. **CORS для API endpoints**
```python
r"/api/*": {
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Range"],
    "expose_headers": ["Content-Range", "Accept-Ranges", "Content-Length"],
}
```

**Зачем нужны эти заголовки:**
- `Range` - для поддержки частичной загрузки больших PDF файлов
- `Content-Range` - информация о диапазоне загруженных данных
- `Accept-Ranges` - сервер поддерживает частичную загрузку
- `Content-Length` - размер файла для отображения прогресса

### 2. **CORS для скачивания PDF**
```python
r"/download/*": {
    "methods": ["GET", "OPTIONS"],
    "expose_headers": ["Content-Range", "Accept-Ranges", "Content-Length", "Content-Disposition"],
}
```

```python
r"/download-by-uuid/*": {
    "methods": ["GET", "OPTIONS"],
    "expose_headers": ["Content-Range", "Accept-Ranges", "Content-Length", "Content-Disposition"],
}
```

**Зачем:**
- `Content-Disposition` - позволяет браузеру правильно обработать скачивание файла
- Поддержка прогрессивной загрузки PDF

### 3. **Разрешенные источники**
```python
"origins": [
    "http://localhost:3000",           # Локальная разработка
    "http://localhost:3001",           # Альтернативный порт
    "http://127.0.0.1:3000",           # IP адрес localhost
    "http://127.0.0.1:3001",
    "https://dmed.netlify.app",        # Продакшн сайт
    "https://*.netlify.app"            # Preview deployments
]
```

## Улучшения фронтенда

### 1. **Индикатор загрузки документа**

#### При загрузке данных документа:
```javascript
<div className="relative">
  <div className="w-16 h-16 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>
  <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin"></div>
</div>
<div className="text-xl font-medium text-gray-700 animate-pulse">
  Загрузка документа...
</div>
```

**Эффект:** Двойной спиннер с плавной анимацией

#### При загрузке PDF:
```javascript
<div className="relative">
  <div className="w-16 h-16 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>
  <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin" style={{ animationDuration: '1.5s' }}></div>
</div>
<div className="text-lg font-medium text-gray-700 animate-pulse">
  Загрузка PDF документа...
</div>
```

#### При загрузке каждой страницы PDF:
```javascript
<div className="flex items-center justify-center py-10 bg-gray-50">
  <div className="flex flex-col items-center gap-3">
    <div className="w-10 h-10 border-3 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
    <div className="text-sm text-gray-500">Загрузка страницы {index + 1}...</div>
  </div>
</div>
```

### 2. **Адаптивность**
- Отступы: `px-2 sm:px-4` (адаптируются под размер экрана)
- Центрирование: `flex justify-center` (PDF всегда по центру)
- Тени: `shadow-lg` (красивый эффект глубины)

### 3. **Обработка ошибок**
```javascript
<div className="text-center max-w-md">
  <div className="text-lg font-semibold text-red-600 mb-4">
    Ошибка при загрузке PDF
  </div>
  <p className="text-gray-600 mb-4">
    Не удалось загрузить документ. Попробуйте открыть его в новой вкладке.
  </p>
  <a href={pdfUrl} target="_blank" className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg">
    Открыть в новой вкладке
  </a>
</div>
```

## Как это работает

### Поток загрузки документа:

```
1. Пользователь переходит на: /el-docs/{uuid}
   ↓ [Показывается спиннер: "Загрузка документа..."]
   ↓
2. Запрос к API: GET /api/access/{uuid}
   ↓
3. Получение данных документа (включая pdf_url_by_uuid)
   ↓ [Показывается спиннер: "Загрузка PDF документа..."]
   ↓
4. React-PDF загружает PDF: GET /download-by-uuid/{uuid}
   ↓ [CORS заголовки разрешают запрос]
   ↓
5. Для каждой страницы PDF:
   ↓ [Показывается спиннер: "Загрузка страницы N..."]
   ↓
6. Отображение PDF документа с прокруткой
   ↓
7. Кнопка печати в правом нижнем углу
```

## Особенности CORS настройки

### Почему важны `expose_headers`?

**Проблема:**
По умолчанию браузер блокирует доступ JavaScript к большинству HTTP заголовков в cross-origin запросах.

**Решение:**
```python
"expose_headers": ["Content-Range", "Accept-Ranges", "Content-Length", "Content-Disposition"]
```

Это позволяет React-PDF:
- Узнать размер файла (`Content-Length`)
- Использовать частичную загрузку (`Accept-Ranges`, `Content-Range`)
- Правильно обработать файл (`Content-Disposition`)

### Почему важны `allow_headers`?

**Проблема:**
React-PDF может отправлять запросы с заголовком `Range` для частичной загрузки больших PDF.

**Решение:**
```python
"allow_headers": ["Content-Type", "Authorization", "Range"]
```

Это разрешает браузеру отправлять эти заголовки в cross-origin запросах.

## Тестирование

### Проверка CORS:
```bash
# Проверка OPTIONS preflight запроса
curl -X OPTIONS http://localhost:5000/api/access/test-uuid \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"

# Проверка GET запроса
curl http://localhost:5000/api/access/test-uuid \
  -H "Origin: http://localhost:3000"
```

### Ожидаемые заголовки в ответе:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Expose-Headers: Content-Range, Accept-Ranges, Content-Length
```

## Возможные проблемы

### 1. **PDF не загружается**
**Симптомы:** Спиннер крутится бесконечно

**Решение:**
- Проверьте консоль браузера на CORS ошибки
- Убедитесь что Flask CORS правильно настроен
- Проверьте что endpoint `/download-by-uuid/{uuid}` возвращает корректный PDF

### 2. **Медленная загрузка**
**Симптомы:** PDF загружается очень долго

**Решение:**
- Используйте `Range` запросы для больших файлов
- Проверьте размер PDF файлов (оптимизируйте если больше 5MB)
- Используйте CDN для статических файлов

### 3. **Ошибка CORS в продакшене**
**Симптомы:** Работает локально, но не на `dmed.netlify.app`

**Решение:**
- Убедитесь что `https://dmed.netlify.app` в списке `origins`
- Проверьте что backend развернут и доступен
- Проверьте настройку `NEXT_PUBLIC_API_URL` в переменных окружения

## Переменные окружения

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Backend (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=1
```

## Безопасность

### ⚠️ Важно!
В продакшене ограничьте список `origins` только вашими доменами:

```python
"origins": [
    "https://dmed.netlify.app",  # Только продакшн домен
]
```

Не используйте `"*"` (разрешить все источники) в продакшене!

---

✅ **CORS настроен и готов к работе!**

