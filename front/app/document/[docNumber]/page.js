'use client'

import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function DocumentPage({ params }) {
  const searchParams = useSearchParams()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Загрузка...</div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">Документ не найден</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Документ: {document.doc_number}
          </h1>
          <p className="text-gray-600">Дата выдачи: {document.issue_date}</p>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Пациент</h2>
            <p className="text-gray-800">{document.patient_name}</p>
            <p className="text-gray-600">Пол: {document.gender}</p>
            <p className="text-gray-600">Возраст: {document.age}</p>
          </div>

          {document.diagnosis && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-2">Диагноз</h2>
              <p className="text-gray-800">{document.diagnosis}</p>
            </div>
          )}

          {document.organization && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-2">Организация</h2>
              <p className="text-gray-800">{document.organization}</p>
            </div>
          )}

          {document.doctor_name && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-2">Врач</h2>
              <p className="text-gray-800">{document.doctor_name}</p>
              {document.doctor_position && (
                <p className="text-gray-600">{document.doctor_position}</p>
              )}
            </div>
          )}

          {document.table_data && document.table_data.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Данные</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">№</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Описание</th>
                    </tr>
                  </thead>
                  <tbody>
                    {document.table_data.map((row, index) => (
                      <tr key={index}>
                        <td className="border border-gray-300 px-4 py-2">{row.index}</td>
                        <td className="border border-gray-300 px-4 py-2">{row.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {document.pdf_url && (
            <div className="mt-8">
              <a
                href={document.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                Скачать PDF
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

