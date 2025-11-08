'use client'

import { useState, useRef, useEffect } from 'react'
import RU from 'country-flag-icons/react/3x2/RU'
import UZ from 'country-flag-icons/react/3x2/UZ'
import GB from 'country-flag-icons/react/3x2/GB'

const translations = {
  ru: {
    title: 'Введите PIN-код для просмотра документа',
    open: 'Открыть',
    hint: 'PIN-код размещается рядом с QR-кодом документа',
    error: 'Документ с таким PIN-кодом не найден',
    loading: 'Проверка...',
  },
  uz: {
    title: 'Hujjatni ko\'rish uchun PIN-kodni kiriting',
    open: 'Ochish',
    hint: 'PIN-kod hujjatning QR-kodi yonida joylashgan',
    error: 'Bunday PIN-kodli hujjat topilmadi',
    loading: 'Tekshirilmoqda...',
  },
  en: {
    title: 'Enter PIN code to view document',
    open: 'Open',
    hint: 'PIN code is located next to the document QR code',
    error: 'Document with this PIN code not found',
    loading: 'Checking...',
  },
}

export default function Home() {
  const [language, setLanguage] = useState('ru')
  const [pin, setPin] = useState(['', '', '', ''])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showLanguageMenu, setShowLanguageMenu] = useState(false)
  const inputRefs = useRef([])
  const languageMenuRef = useRef(null)

  const t = translations[language]

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (languageMenuRef.current && !languageMenuRef.current.contains(event.target)) {
        setShowLanguageMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handlePinChange = (index, value) => {
    if (!/^\d*$/.test(value)) return

    const newPin = [...pin]
    newPin[index] = value.slice(-1)
    setPin(newPin)
    setError('')

    if (value && index < 3) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !pin[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').slice(0, 4)
    if (/^\d+$/.test(pastedData)) {
      const newPin = pastedData.split('').concat(['', '', '', '']).slice(0, 4)
      setPin(newPin)
      const nextIndex = Math.min(pastedData.length, 3)
      inputRefs.current[nextIndex]?.focus()
    }
  }

  const handleVerify = async () => {
    const pinCode = pin.join('')
    
    if (pinCode.length !== 4) {
      setError(t.error)
      return
    }

    setLoading(true)
    setError('')

    try {
      // Используем полный URL для бэкенда или относительный путь
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/verify-pin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pin_code: pinCode }),
      })

      const result = await response.json()

      if (result.success) {
        window.location.href = `/document/${result.document.doc_number}?data=${encodeURIComponent(JSON.stringify(result.document))}`
      } else {
        setError(result.error || t.error)
      }
    } catch (error) {
      setError('Ошибка при проверке документа: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const isPinComplete = pin.every(digit => digit !== '')

  return (
    <div className="min-h-screen bg-background font-sans text-textPrimary">
      {/* Header */}
      <header className="max-w-containerSm md:max-w-containerMd lg:max-w-containerLg mx-auto px-4 pt-6 md:pt-8 lg:pt-8 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <img 
            src="/logo.svg" 
            alt="DMED" 
            className="h-logoHSm md:h-logoHMd lg:h-logoHLg w-auto"
          />
          <div className="relative" ref={languageMenuRef}>
            <button
              onClick={() => setShowLanguageMenu(!showLanguageMenu)}
              className="h-langChip px-4 inline-flex items-center gap-2 bg-chipBg rounded-full border border-inputBorder shadow-sm text-base lg:text-lg font-medium transition-colors hover:border-inputBorderFocus"
            >
              {language === 'ru' && (
                <>
                  <RU className="w-5 h-4" />
                  <span>Русский</span>
                </>
              )}
              {language === 'uz' && (
                <>
                  <UZ className="w-5 h-4" />
                  <span>O'zbekcha</span>
                </>
              )}
              {language === 'en' && (
                <>
                  <GB className="w-5 h-4" />
                  <span>English</span>
                </>
              )}
            </button>
            {showLanguageMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-md border border-inputBorder py-2 z-50">
                <button
                  onClick={() => {
                    setLanguage('ru')
                    setShowLanguageMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-chipBg flex items-center gap-2"
                >
                  <RU className="w-5 h-4" />
                  <span className={`text-base ${language === 'ru' ? 'text-textSecondary' : 'text-textPrimary'}`}>
                    Русский
                  </span>
                </button>
                <button
                  onClick={() => {
                    setLanguage('uz')
                    setShowLanguageMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-chipBg flex items-center gap-2"
                >
                  <UZ className="w-5 h-4" />
                  <span className={`text-base ${language === 'uz' ? 'text-textSecondary' : 'text-textPrimary'}`}>
                    O'zbekcha
                  </span>
                </button>
                <button
                  onClick={() => {
                    setLanguage('en')
                    setShowLanguageMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-chipBg flex items-center gap-2"
                >
                  <GB className="w-5 h-4" />
                  <span className={`text-base ${language === 'en' ? 'text-textSecondary' : 'text-textPrimary'}`}>
                    English
                  </span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-containerSm md:max-w-containerMd lg:max-w-containerLg mx-auto px-4 pt-8 md:pt-12 lg:pt-16 lg:px-8 pb-12 md:pb-12 lg:pb-16 text-center">
        <h1 className="text-3xl md:text-4xl lg:text-4xl leading-tight md:leading-snug lg:leading-snug font-bold tracking-tight mb-8 md:mb-10 lg:mb-10 text-textPrimary">
          {t.title}
        </h1>

        {/* PIN Input */}
        <div className="flex justify-center gap-4 md:gap-[18px] lg:gap-5 mb-8 md:mb-10">
          {pin.map((digit, index) => (
            <input
              key={index}
              ref={(el) => (inputRefs.current[index] = el)}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handlePinChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              className="w-pinCellSm h-pinCellSm md:w-pinCellMd md:h-pinCellMd lg:w-pinCellLg lg:h-pinCellLg text-3xl md:text-4xl lg:text-4xl font-semibold text-center border border-inputBorder rounded-md bg-white outline-none transition-all duration-[120ms] focus:border-inputBorderFocus focus:shadow-[0_0_0_3px_rgba(37,99,235,0.2)]"
            />
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-center text-base">
            {error}
          </div>
        )}

        {/* Open Button */}
        <button
          onClick={handleVerify}
          disabled={!isPinComplete || loading}
          className={`
            h-buttonHSm md:h-buttonHMd lg:h-buttonHLg rounded-lg text-lg font-semibold
            inline-flex items-center justify-center w-full max-w-buttonSm md:max-w-buttonMd lg:max-w-buttonLg mx-auto
            border-none cursor-pointer transition-all duration-[80ms]
            ${isPinComplete && !loading
              ? 'bg-buttonBg text-buttonText shadow-button hover:bg-buttonBgHover hover:-translate-y-px active:translate-y-0'
              : 'bg-buttonBgDisabled text-textSecondary cursor-not-allowed shadow-none opacity-100'
            }
          `}
        >
          {loading ? t.loading : t.open}
        </button>
      </main>

      {/* Footer Card */}
      <footer className="max-w-containerSm md:max-w-containerMd lg:max-w-containerLg mx-auto px-4 md:px-4 lg:px-8 pb-8">
        <div className="p-4 md:p-6 lg:p-6 rounded-lg border border-divider shadow-md">
          <img 
            src="/qr-hint.svg" 
            alt={t.hint}
            className="w-full h-auto max-w-xs md:max-w-sm lg:max-w-md mx-auto"
          />
        </div>
      </footer>
    </div>
  )
}

