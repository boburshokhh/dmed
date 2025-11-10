'use client'

import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Настройка worker для react-pdf
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`
}

export default function DocumentPage() {
  const params = useParams()
  const uuid = params?.uuid

  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [numPages, setNumPages] = useState(null)
  const [pageWidth, setPageWidth] = useState(800)

  useEffect(() => {
    // Загружаем данные документа по UUID
    if (uuid) {
      const fetchDocument = async () => {
        setLoading(true)
        setError('')
        
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
          const response = await fetch(`${apiUrl}/api/access/${uuid}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          })

          const result = await response.json()

          if (result.success) {
            setDocument(result.document)
          } else {
            setError(result.error || 'Документ не найден')
          }
        } catch (err) {
          console.error('Error loading document:', err)
          setError('Ошибка при загрузке документа')
        } finally {
          setLoading(false)
        }
      }

      fetchDocument()
    }
  }, [uuid])

  useEffect(() => {
    // Адаптивная ширина PDF
    const handleResize = () => {
      const maxWidth = window.innerWidth - 16 // 16px padding с каждой стороны
      const pdfWidth = Math.min(maxWidth, 1000) // Максимальная ширина 1000px
      setPageWidth(pdfWidth)
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages)
  }

  const handlePrint = () => {
    // Открываем модальное окно печати браузера
    window.print()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-6">
          {/* Modern spinner */}
          <div className="relative">
            <div className="w-16 h-16 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin" style={{ animationDuration: '1.5s' }}></div>
          </div>
          <div className="text-xl font-medium text-gray-700 animate-pulse">Загрузка документа...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="text-center">
          <div className="text-xl font-semibold text-red-600 mb-4">{error}</div>
          <a
            href="/"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Вернуться на главную
          </a>
        </div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl font-semibold text-red-600">Документ не найден</div>
      </div>
    )
  }

  const pdfUrl = document.pdf_url_by_uuid || document.pdf_url

  if (!pdfUrl) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="text-center">
          <div className="text-xl font-semibold text-red-600 mb-4">PDF документ недоступен</div>
          <a
            href="/"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Вернуться на главную
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* PDF Viewer */}
      <div className="flex flex-col items-center py-4 px-2 sm:px-4">
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center gap-6">
                {/* Double spinner for loading effect */}
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>
                  <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin" style={{ animationDuration: '1.5s' }}></div>
                </div>
                <div className="text-lg font-medium text-gray-700 animate-pulse">Загрузка PDF документа...</div>
              </div>
            </div>
          }
          error={
            <div className="flex items-center justify-center py-20 px-4">
              <div className="text-center max-w-md">
                <div className="text-lg font-semibold text-red-600 mb-4">
                  Ошибка при загрузке PDF
                </div>
                <p className="text-gray-600 mb-4">
                  Не удалось загрузить документ. Попробуйте открыть его в новой вкладке.
                </p>
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors duration-200"
                >
                  Открыть в новой вкладке
                </a>
              </div>
            </div>
          }
          className="w-full"
        >
          {Array.from(new Array(numPages), (el, index) => (
            <div key={`page_${index + 1}`} className="mb-4 flex justify-center">
              <Page
                pageNumber={index + 1}
                width={pageWidth}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="shadow-lg bg-white rounded-sm"
                loading={
                  <div className="flex items-center justify-center py-10 bg-gray-50" style={{ width: pageWidth, minHeight: '600px' }}>
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-10 h-10 border-3 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                      <div className="text-sm text-gray-500">Загрузка страницы {index + 1}...</div>
                    </div>
                  </div>
                }
              />
            </div>
          ))}
        </Document>
      </div>

      {/* Print Button - Fixed Bottom Right */}
      <button
        onClick={handlePrint}
        className="fixed bottom-8 right-8 bg-white border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 hover:bg-gray-50 active:bg-gray-100 z-50 flex items-center justify-center w-12 h-12 p-0"
        aria-label="Печать документа"
        title="Печать"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-5 h-5"
        >
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
          <path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"></path>
          <rect x="6" y="14" width="12" height="8" rx="1"></rect>
        </svg>
      </button>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          @page {
            size: A4;
            margin: 0;
          }
          
          /* Скрываем все элементы кроме PDF */
          body > *:not(.react-pdf__Document) {
            display: none !important;
          }
          
          /* Показываем только PDF контейнеры */
          .react-pdf__Document,
          .react-pdf__Page {
            display: block !important;
            visibility: visible !important;
            page-break-after: always;
            page-break-inside: avoid;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: auto !important;
          }
          
          /* Canvas должен занимать всю ширину страницы */
          .react-pdf__Page__canvas {
            display: block !important;
            visibility: visible !important;
            width: 100% !important;
            height: auto !important;
            max-width: 100% !important;
            margin: 0 auto !important;
            padding: 0 !important;
            page-break-after: always;
            page-break-inside: avoid;
          }
          
          /* Контейнер страницы */
          .react-pdf__Page {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            border: none !important;
          }
          
          /* Скрываем кнопки и другие элементы */
          button,
          .fixed,
          nav,
          header,
          footer {
            display: none !important;
          }
          
          /* Убираем все отступы */
          html, body {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
          }
          
          /* Контейнер с PDF */
          div[class*="flex"] {
            display: block !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
          }
        }
      `}</style>
    </div>
  )
}

