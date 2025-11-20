'use client'

import { useEffect, useRef, useState } from 'react'

export default function QRCodeDisplay({ qrData, qrSize, logoSize, onQRCodeReady }) {
  const qrRef = useRef(null)
  const qrCodeRef = useRef(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || !qrRef.current || typeof window === 'undefined') return

    let isMounted = true

    // Динамический импорт для клиентской библиотеки
    import('qr-code-styling').then((module) => {
      if (!isMounted || !qrRef.current) return

      const QRCodeStyling = module.default

      // Создаем SVG логотип для центра QR-кода (звездочка в стиле Telegram)
      const logoSvg = `
        <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="starGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#0088cc;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#229ED9;stop-opacity:1" />
            </linearGradient>
          </defs>
          <path d="M50 10 L60 40 L90 40 L68 58 L78 88 L50 68 L22 88 L32 58 L10 40 L40 40 Z" 
                fill="url(#starGradient)" 
                stroke="#0088cc" 
                stroke-width="2"/>
        </svg>
      `
      
      // Конвертируем SVG в Data URL
      const logoDataUrl = `data:image/svg+xml;base64,${btoa(logoSvg)}`

      // Инициализируем QR-код
      const qrCode = new QRCodeStyling({
        width: qrSize,
        height: qrSize,
        data: qrData,
        image: logoDataUrl,
        dotsOptions: {
          color: '#000000',
          type: 'rounded' // Скругленные точки как в Telegram
        },
        backgroundOptions: {
          color: '#ffffff',
        },
        imageOptions: {
          crossOrigin: 'anonymous',
          margin: 8,
          imageSize: 0.3, // Размер логотипа относительно QR-кода
        },
        cornersSquareOptions: {
          color: '#000000',
          type: 'extra-rounded' // Скругленные углы
        },
        cornersDotOptions: {
          color: '#000000',
          type: 'dot' // Точки в углах
        },
      })

      qrCodeRef.current = qrCode

      // Передаем ссылку родительскому компоненту
      if (onQRCodeReady) {
        onQRCodeReady(qrCodeRef)
      }

      // Очищаем предыдущий QR-код
      if (qrRef.current) {
        qrRef.current.innerHTML = ''
        qrCode.append(qrRef.current)
      }
    })

    return () => {
      isMounted = false
      if (qrRef.current) {
        qrRef.current.innerHTML = ''
      }
    }
  }, [qrData, qrSize, logoSize, mounted, onQRCodeReady])

  // Компонент всегда рендерится одинаково, так как SSR отключен
  return (
    <div
      ref={qrRef}
      className="flex items-center justify-center"
      style={{ minHeight: `${qrSize}px` }}
    />
  )
}

