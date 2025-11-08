import './globals.css'

export const metadata = {
  title: 'DMED',
  description: 'Введите PIN-код для просмотра документа',
  icons: {
    icon: 'https://docs.dmed.uz/favicon.ico',
    shortcut: 'https://docs.dmed.uz/favicon.ico',
    apple: 'https://docs.dmed.uz/favicon.ico',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <head>
        <link rel="icon" href="https://docs.dmed.uz/favicon.ico" />
        <link rel="shortcut icon" href="https://docs.dmed.uz/favicon.ico" />
        <link rel="apple-touch-icon" href="https://docs.dmed.uz/favicon.ico" />
      </head>
      <body>{children}</body>
    </html>
  )
}

