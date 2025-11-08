# DMED Frontend

Фронтенд приложение для проверки документов по PIN-коду.

## Технологии

- Next.js 14
- React 18
- Tailwind CSS 3

## Установка

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3000

## Сборка для продакшена

```bash
npm run build
npm start
```

## Настройка API

По умолчанию приложение настроено на работу с Flask бэкендом на `http://localhost:5000`.

Если ваш бэкенд работает на другом адресе, измените настройки в `next.config.js`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://your-backend-url:port/:path*',
    },
  ]
}
```

## Структура проекта

```
front/
├── app/
│   ├── page.js              # Главная страница с формой PIN
│   ├── layout.js            # Основной layout
│   ├── globals.css          # Глобальные стили
│   └── document/
│       └── [docNumber]/
│           └── page.js      # Страница просмотра документа
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── next.config.js
```

## Функциональность

- Ввод PIN-кода (4 цифры)
- Переключение языков (RU/UZ/EN)
- Проверка PIN через API
- Просмотр документа после успешной проверки
- Адаптивный дизайн для мобильных устройств

