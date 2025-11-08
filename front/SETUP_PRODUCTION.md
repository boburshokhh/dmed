# ⚙️ Настройка для продакшна

## Переменная окружения NEXT_PUBLIC_API_URL

### Где установить:

#### Netlify:
1. Netlify Dashboard → Ваш проект
2. **Site settings** → **Environment variables**
3. Добавьте:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.com
   ```

#### Vercel:
1. Vercel Dashboard → Ваш проект
2. **Settings** → **Environment Variables**
3. Добавьте:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.com
   ```

### Примеры значений:

```env
# Локальная разработка
NEXT_PUBLIC_API_URL=http://localhost:5000

# Продакшн (примеры)
NEXT_PUBLIC_API_URL=https://api.dmed.uz
NEXT_PUBLIC_API_URL=https://dmed-backend.herokuapp.com
NEXT_PUBLIC_API_URL=https://backend.example.com
```

### ⚠️ Важные замечания:

1. **Без trailing slash:** Не добавляйте `/` в конце URL
   - ✅ Правильно: `https://api.example.com`
   - ❌ Неправильно: `https://api.example.com/`

2. **HTTPS обязателен:** В продакшне используйте только HTTPS
   - ✅ Правильно: `https://api.example.com`
   - ❌ Неправильно: `http://api.example.com`

3. **Пересборка:** После изменения переменных нужно пересобрать проект

## Проверка настройки

### После деплоя откройте консоль браузера (F12) и проверьте:

1. **Нет ошибок CORS:**
   ```
   Access to fetch at 'https://your-backend-url.com/api/...' from origin 'https://your-site.netlify.app' has been blocked by CORS policy
   ```
   Если видите эту ошибку → проверьте CORS на бэкенде

2. **API запросы идут на правильный URL:**
   - Откройте вкладку **Network** в DevTools
   - Проверьте что запросы идут на ваш продакшн URL, а не на localhost

3. **Данные загружаются:**
   - Проверьте что документы загружаются
   - Проверьте что PDF отображается

## Тестирование перед деплоем

### Локальное тестирование с продакшн API:

1. Создайте `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

2. Запустите:
   ```bash
   npm run build
   npm start
   ```

3. Откройте `http://localhost:3000` и протестируйте все функции

## Структура API запросов

Приложение делает следующие запросы:

1. **POST** `/api/access/{uuid}/verify-pin` - проверка PIN-кода
2. **GET** `/api/access/{uuid}` - получение данных документа
3. **GET** `/download-by-uuid/{uuid}` - загрузка PDF

Все эти запросы используют `NEXT_PUBLIC_API_URL` как базовый URL.

---

✅ **После настройки переменной окружения проект готов к работе!**

