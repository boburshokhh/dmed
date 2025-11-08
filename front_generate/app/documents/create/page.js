'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { FileText, Loader2, CheckCircle, Download, Copy, Zap } from 'lucide-react'
import api from '@/lib/api'
import { DatePicker } from '@/components/ui/date-picker'
import { isSuperAdmin } from '@/lib/auth'

// База данных для быстрого заполнения формы
const mockData = {
  patients: [
    { name: "ИВАНОВ ИВАН ИВАНОВИЧ", jshshir: "12345678901234", gender: "Мужской (Erkak)", age: "25 yosh", address: "г. Ташкент, ул. Навои, д. 15, кв. 42" },
    { name: "ПЕТРОВА МАРИЯ СЕРГЕЕВНА", jshshir: "23456789012345", gender: "Женский (Ayol)", age: "32 yosh", address: "г. Ташкент, ул. Амира Темура, д. 78, кв. 12" },
    { name: "СИДОРОВ АЛЕКСАНДР ВЛАДИМИРОВИЧ", jshshir: "34567890123456", gender: "Мужской (Erkak)", age: "45 yosh", address: "г. Ташкент, ул. Университетская, д. 23, кв. 5" },
    { name: "КОЗЛОВА ЕЛЕНА ПЕТРОВНА", jshshir: "45678901234567", gender: "Женский (Ayol)", age: "28 yosh", address: "г. Ташкент, ул. Чилонзар, д. 45, кв. 89" },
    { name: "МОРОЗОВ ДМИТРИЙ АНДРЕЕВИЧ", jshshir: "56789012345678", gender: "Мужской (Erkak)", age: "38 yosh", address: "г. Ташкент, ул. Шота Руставели, д. 12, кв. 34" }
  ],
  diagnoses: [
    { diagnosis: "Острый бронхит", diagnosis_icd10_code: "J20.9", final_diagnosis: "Острый бронхит неуточненный", final_diagnosis_icd10_code: "J20.9" },
    { diagnosis: "Острая респираторная вирусная инфекция", diagnosis_icd10_code: "J06.9", final_diagnosis: "Острая инфекция верхних дыхательных путей неуточненная", final_diagnosis_icd10_code: "J06.9" },
    { diagnosis: "Гипертоническая болезнь", diagnosis_icd10_code: "I10", final_diagnosis: "Эссенциальная (первичная) гипертензия", final_diagnosis_icd10_code: "I10" },
    { diagnosis: "Остеохондроз позвоночника", diagnosis_icd10_code: "M42.9", final_diagnosis: "Остеохондроз позвоночника неуточненный", final_diagnosis_icd10_code: "M42.9" },
    { diagnosis: "Гастрит", diagnosis_icd10_code: "K29.9", final_diagnosis: "Гастрит неуточненный", final_diagnosis_icd10_code: "K29.9" },
    { diagnosis: "Пневмония", diagnosis_icd10_code: "J18.9", final_diagnosis: "Пневмония неуточненного возбудителя", final_diagnosis_icd10_code: "J18.9" }
  ],
  organizations: [
    "4-я городская поликлиника",
    "Республиканская клиническая больница №1",
    "Городская больница скорой медицинской помощи",
    "Медицинский центр 'Здоровье'",
    "Поликлиника №2 Чилонзарского района",
    "Городская детская больница"
  ],
  doctors: [
    { doctor_name: "АЛИЕВ АЛИШЕР РАХИМОВИЧ", doctor_position: "Врач-терапевт" },
    { doctor_name: "КАРИМОВА ФАРИДА ТОШПУЛАТОВНА", doctor_position: "Врач-педиатр" },
    { doctor_name: "ТУРАЕВ БАХОДИР ИСМОИЛОВИЧ", doctor_position: "Врач-невролог" },
    { doctor_name: "ЮСУПОВА НИГОРА АБДУЛЛАЕВНА", doctor_position: "Врач-кардиолог" },
    { doctor_name: "РАХИМОВ ШУКУР ДЖУРАЕВИЧ", doctor_position: "Врач-терапевт" }
  ],
  days_off_ranges: [
    { from: 3, to: 5 },
    { from: 5, to: 7 },
    { from: 7, to: 10 },
    { from: 10, to: 14 },
    { from: 14, to: 21 }
  ]
}

export default function CreateDocumentPage() {
  const router = useRouter()
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    patient_name: '',
    gender: 'Erkak',
    age: '',
    jshshir: '',
    address: '',
    attached_medical_institution: '',
    diagnosis: '',
    diagnosis_icd10_code: '',
    final_diagnosis: '',
    final_diagnosis_icd10_code: '',
    organization: '',
    doctor_name: '',
    doctor_position: '',
    department_head_name: '',
    days_off_from: '',
    days_off_to: '',
    issue_date: new Date().toISOString().split('T')[0],
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleGenerateDocument = async (e) => {
    e.preventDefault()
    setGenerating(true)
    setResult(null)

    try {
      const response = await api.post('/documents/generate', formData)

      if (response.data.success) {
        setResult({
          doc_number: response.data.doc_number,
          pin_code: response.data.pin_code,
          download_url: response.data.download_url
        })
        setModalOpen(true)
        
        // Сбрасываем только основные поля пациента
        setFormData(prev => ({
          ...prev,
          patient_name: '',
          age: '',
          jshshir: '',
          address: '',
          diagnosis: '',
          diagnosis_icd10_code: '',
          final_diagnosis: '',
          final_diagnosis_icd10_code: '',
          days_off_from: '',
          days_off_to: '',
        }))
      }
    } catch (error) {
      alert(error.response?.data?.message || 'Ошибка генерации документа')
    } finally {
      setGenerating(false)
    }
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setResult(null)
  }

  const handleCopyPin = () => {
    if (result?.pin_code) {
      navigator.clipboard.writeText(result.pin_code)
      alert('PIN-код скопирован в буфер обмена!')
    }
  }

  const handleQuickFill = () => {
    // Случайный выбор данных из JSON БД
    const randomPatient = mockData.patients[Math.floor(Math.random() * mockData.patients.length)]
    const randomDiagnosis = mockData.diagnoses[Math.floor(Math.random() * mockData.diagnoses.length)]
    const randomOrganization = mockData.organizations[Math.floor(Math.random() * mockData.organizations.length)]
    const randomDoctor = mockData.doctors[Math.floor(Math.random() * mockData.doctors.length)]
    const randomDaysOff = mockData.days_off_ranges[Math.floor(Math.random() * mockData.days_off_ranges.length)]

    // Вычисляем даты освобождения
    const today = new Date()
    const daysOffFrom = new Date(today)
    daysOffFrom.setDate(today.getDate() + 1) // Завтра

    const daysOffTo = new Date(daysOffFrom)
    daysOffTo.setDate(daysOffFrom.getDate() + randomDaysOff.to)

    // Форматируем даты
    const formatDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    // Заполняем форму
    setFormData({
      ...formData,
      patient_name: randomPatient.name,
      jshshir: randomPatient.jshshir,
      gender: randomPatient.gender,
      age: randomPatient.age,
      address: randomPatient.address,
      diagnosis: randomDiagnosis.diagnosis,
      diagnosis_icd10_code: randomDiagnosis.diagnosis_icd10_code,
      final_diagnosis: randomDiagnosis.final_diagnosis,
      final_diagnosis_icd10_code: randomDiagnosis.final_diagnosis_icd10_code,
      organization: randomOrganization,
      doctor_name: randomDoctor.doctor_name,
      doctor_position: randomDoctor.doctor_position,
      days_off_from: formatDate(daysOffFrom),
      days_off_to: formatDate(daysOffTo),
      issue_date: formatDate(today),
    })
  }

  const handleDownload = () => {
    if (result?.doc_id) {
      // Используем doc_id для формирования правильного URL
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      window.open(`${apiBase}/api/documents/${result.doc_id}/download`, '_blank')
    } else if (result?.download_url) {
      // Если есть download_url, проверяем его формат
      let downloadUrl = result.download_url
      if (downloadUrl.startsWith('http://') || downloadUrl.startsWith('https://')) {
        window.open(downloadUrl, '_blank')
      } else if (downloadUrl.startsWith('/')) {
        // Если путь начинается с /, добавляем базовый URL
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
        window.open(`${apiBase}${downloadUrl}`, '_blank')
      } else {
        // Если это просто путь без /, формируем полный путь
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
        window.open(`${apiBase}/api/documents/${downloadUrl}/download`, '_blank')
      }
    }
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Создать документ</h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              Заполните все необходимые поля для генерации медицинского документа
            </p>
          </div>
          {isSuperAdmin() && (
            <Button
              type="button"
              variant="outline"
              onClick={handleQuickFill}
              disabled={generating}
              className="w-full sm:w-auto"
            >
              <Zap className="mr-2 h-4 w-4" />
              Быстрое заполнение
            </Button>
          )}
        </div>

        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleGenerateDocument} className="space-y-6">
              {/* Информация о пациенте */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">Информация о пациенте</h3>
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="patient_name">ФИО пациента *</Label>
                    <Input
                      id="patient_name"
                      name="patient_name"
                      value={formData.patient_name}
                      onChange={handleInputChange}
                      placeholder="ИВАНОВ ИВАН ИВАНОВИЧ"
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="jshshir">ПИНФЛ (JSHSHIR)</Label>
                    <Input
                      id="jshshir"
                      name="jshshir"
                      value={formData.jshshir}
                      onChange={handleInputChange}
                      placeholder="12345678901234"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="gender">Пол *</Label>
                    <select
                      id="gender"
                      name="gender"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={formData.gender}
                      onChange={handleInputChange}
                      required
                      disabled={generating}
                    >
                      <option value="Erkak">Мужской (Erkak)</option>
                      <option value="Ayol">Женский (Ayol)</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="age">Возраст *</Label>
                    <Input
                      id="age"
                      name="age"
                      value={formData.age}
                      onChange={handleInputChange}
                      placeholder="25 yosh"
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="address">Адрес</Label>
                    <Input
                      id="address"
                      name="address"
                      value={formData.address}
                      onChange={handleInputChange}
                      placeholder="г. Ташкент, ул. Примерная, д. 1"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="attached_medical_institution">Прикрепленное медучреждение</Label>
                    <Input
                      id="attached_medical_institution"
                      name="attached_medical_institution"
                      value={formData.attached_medical_institution}
                      onChange={handleInputChange}
                      placeholder="Поликлиника №4"
                      disabled={generating}
                    />
                  </div>
                </div>
              </div>

              {/* Диагноз */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">Диагноз</h3>
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="diagnosis">Первичный диагноз *</Label>
                    <Input
                      id="diagnosis"
                      name="diagnosis"
                      value={formData.diagnosis}
                      onChange={handleInputChange}
                      placeholder="ОРВИ"
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="diagnosis_icd10_code">Код МКБ-10</Label>
                    <Input
                      id="diagnosis_icd10_code"
                      name="diagnosis_icd10_code"
                      value={formData.diagnosis_icd10_code}
                      onChange={handleInputChange}
                      placeholder="J06.9"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="final_diagnosis">Заключительный диагноз</Label>
                    <Input
                      id="final_diagnosis"
                      name="final_diagnosis"
                      value={formData.final_diagnosis}
                      onChange={handleInputChange}
                      placeholder="ОРВИ, средней тяжести"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="final_diagnosis_icd10_code">Код МКБ-10 (заключ.)</Label>
                    <Input
                      id="final_diagnosis_icd10_code"
                      name="final_diagnosis_icd10_code"
                      value={formData.final_diagnosis_icd10_code}
                      onChange={handleInputChange}
                      placeholder="J06.9"
                      disabled={generating}
                    />
                  </div>
                </div>
              </div>

              {/* Освобождение */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">Период освобождения</h3>
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="days_off_from">Освобожден с</Label>
                    <DatePicker
                      name="days_off_from"
                      value={formData.days_off_from}
                      onChange={handleInputChange}
                      placeholder="Выберите дату начала"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="days_off_to">Освобожден по</Label>
                    <DatePicker
                      name="days_off_to"
                      value={formData.days_off_to}
                      onChange={handleInputChange}
                      placeholder="Выберите дату окончания"
                      disabled={generating}
                    />
                  </div>
                </div>
              </div>

              {/* Организация и врачи */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">Информация об организации и враче</h3>
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="organization">Организация *</Label>
                    <Input
                      id="organization"
                      name="organization"
                      value={formData.organization}
                      onChange={handleInputChange}
                      placeholder="4-я городская поликлиника"
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="issue_date">Дата выдачи *</Label>
                    <DatePicker
                      name="issue_date"
                      value={formData.issue_date}
                      onChange={handleInputChange}
                      placeholder="Выберите дату выдачи"
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="doctor_name">ФИО врача *</Label>
                    <Input
                      id="doctor_name"
                      name="doctor_name"
                      value={formData.doctor_name}
                      onChange={handleInputChange}
                      placeholder="Петров П.П."
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="doctor_position">Должность врача *</Label>
                    <Input
                      id="doctor_position"
                      name="doctor_position"
                      value={formData.doctor_position}
                      onChange={handleInputChange}
                      placeholder="Терапевт"
                      required
                      disabled={generating}
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="department_head_name">Заведующий отделением</Label>
                    <Input
                      id="department_head_name"
                      name="department_head_name"
                      value={formData.department_head_name}
                      onChange={handleInputChange}
                      placeholder="Сидоров С.С."
                      disabled={generating}
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <Button type="submit" className="flex-1" size="lg" disabled={generating}>
                  {generating ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Генерация документа...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-5 w-5" />
                      Создать документ
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/files')}
                  disabled={generating}
                >
                  Отмена
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Модальное окно успешного создания */}
        <Dialog open={modalOpen} onOpenChange={setModalOpen}>
          <DialogContent className="max-w-[95vw] sm:max-w-md">
            <DialogHeader>
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <DialogTitle className="text-center text-xl sm:text-2xl">Документ успешно создан!</DialogTitle>
              <DialogDescription className="text-center text-xs sm:text-sm">
                Сохраните PIN-код для верификации документа
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="space-y-3 rounded-lg border bg-muted p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">Номер документа:</span>
                  <span className="font-mono font-bold text-lg">{result?.doc_number}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">PIN-код:</span>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-mono font-bold text-primary">{result?.pin_code}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={handleCopyPin}
                      className="h-8 w-8"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
              
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
                <p className="text-xs text-amber-800 text-center">
                  <strong>Важно!</strong> Сохраните PIN-код. Он потребуется для верификации документа.
                </p>
              </div>
            </div>

            <DialogFooter className="flex-col gap-2 sm:flex-row">
              <Button
                onClick={handleDownload}
                className="w-full sm:w-auto"
              >
                <Download className="mr-2 h-4 w-4" />
                Скачать документ
              </Button>
              <Button
                onClick={() => {
                  handleCloseModal()
                  router.push('/documents')
                }}
                variant="outline"
                className="w-full sm:w-auto"
              >
                Перейти к списку
              </Button>
              <Button
                onClick={handleCloseModal}
                variant="secondary"
                className="w-full sm:w-auto"
              >
                Создать еще
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  )
}

