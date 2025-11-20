# Инструкция по деплою на Netlify

## Проблема с MissingBlobsEnvironmentError

Если при деплое возникает ошибка `MissingBlobsEnvironmentError`, это означает, что Netlify CLI пытается использовать Blobs без правильной конфигурации.

## Решения

### Вариант 1: Локальная сборка без деплоя (рекомендуется для тестирования)

```powershell
cd front
npm run build
```

Это создаст сборку в папке `.next` без попытки загрузить blobs.

### Вариант 2: Деплой через Netlify CLI с правильными параметрами

```powershell
cd front
netlify deploy --build --prod
```

Или для preview деплоя:

```powershell
cd front
netlify deploy --build
```

### Вариант 3: Деплой через Git (автоматический)

1. Закоммитьте изменения:
```powershell
git add .
git commit -m "Update print styles"
git push
```

2. Netlify автоматически задеплоит при push в основную ветку (если настроен автодеплой)

### Вариант 4: Использование переменных окружения для Blobs

Если нужно использовать Blobs, добавьте переменные окружения:

```powershell
$env:NETLIFY_SITE_ID = "e27b845d-0f97-4e57-8ea4-51ba9daaa39b"
$env:NETLIFY_AUTH_TOKEN = "your-token-here"
netlify deploy --build
```

Токен можно получить через: `netlify auth:token`

## Рекомендация

Для большинства случаев используйте **Вариант 3** (деплой через Git) - это самый надежный способ, так как Netlify автоматически настроит все необходимые переменные окружения.

