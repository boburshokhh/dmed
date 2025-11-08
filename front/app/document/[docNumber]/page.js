'use client'

import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Настройка worker для react-pdf
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`
}

export default function DocumentPage({ params }) {
  const searchParams = useSearchParams()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  const [numPages, setNumPages] = useState(null)
  const [pageWidth, setPageWidth] = useState(800)

  useEffect(() => {
    const dataParam = searchParams.get('data')
    if (dataParam) {
      try {
        const docData = JSON.parse(decodeURIComponent(dataParam))
        setDocument(docData)
      } catch (error) {
        console.error('Error parsing document data:', error)
      }
    }
    setLoading(false)
  }, [searchParams])

  useEffect(() => {
    // Адаптивная ширина PDF
    const handleResize = () => {
      const maxWidth = window.innerWidth - 32 // 16px padding с каждой стороны
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
    if (document?.pdf_url_by_uuid || document?.pdf_url) {
      // Открываем PDF в новом окне для печати
      const pdfUrl = document.pdf_url_by_uuid || document.pdf_url
      window.open(pdfUrl, '_blank')
    } else {
      // Если нет прямой ссылки, используем печать текущей страницы
      window.print()
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl font-medium text-gray-600">Загрузка...</div>
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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl font-semibold text-red-600">PDF документ недоступен</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* PDF Viewer */}
      <div className="flex flex-col items-center py-4 px-4">
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={
            <div className="flex items-center justify-center py-20">
              <div className="text-lg font-medium text-gray-600">Загрузка документа...</div>
            </div>
          }
          error={
            <div className="flex items-center justify-center py-20">
              <div className="text-lg font-semibold text-red-600">
                Ошибка при загрузке PDF
                <div className="mt-4">
                  <a
                    href={pdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline text-base font-normal"
                  >
                    Открыть документ в новой вкладке
                  </a>
                </div>
              </div>
            </div>
          }
          className="shadow-lg"
        >
          {Array.from(new Array(numPages), (el, index) => (
            <div key={`page_${index + 1}`} className="mb-4">
              <Page
                pageNumber={index + 1}
                width={pageWidth}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="shadow-md bg-white"
              />
            </div>
          ))}
        </Document>
      </div>

      {/* Print Button - Fixed Bottom Right */}
      <button
        onClick={handlePrint}
        className="fixed bottom-8 right-8 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all duration-200 hover:scale-105 active:scale-95 z-50 flex items-center justify-center"
        aria-label="Печать документа"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z"
          />
        </svg>
      </button>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .react-pdf__Page__canvas {
            visibility: visible;
            position: absolute;
            left: 0;
            top: 0;
          }
          button {
            display: none !important;
          }
        }
      `}</style>
    </div>
  )
}
