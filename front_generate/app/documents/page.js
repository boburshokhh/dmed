'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { FileText, Download, Loader2, Search, Plus, Filter, RotateCcw, ChevronDown } from 'lucide-react'
import api from '@/lib/api'
import { DatePicker } from '@/components/ui/date-picker'
import { getAuth } from '@/lib/auth'

export default function DocumentsPage() {
  const router = useRouter()
  const [documents, setDocuments] = useState([])
  const [filteredDocuments, setFilteredDocuments] = useState([])
  const [paginatedDocuments, setPaginatedDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  const [filtersOpen, setFiltersOpen] = useState(false) // State for filters visibility
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    organization: '',
  })
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    const auth = getAuth()
    if (auth && auth.userData) {
      setCurrentUser(auth.userData)
    }
    fetchDocuments()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [documents, searchTerm, filters])

  useEffect(() => {
    paginateDocuments()
  }, [filteredDocuments, currentPage, itemsPerPage])

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/documents')
      setDocuments(response.data)
    } catch (error) {
      console.error('Ошибка загрузки документов:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = documents.filter(doc => {
      // Поиск по номеру или имени пациента
      const matchesSearch = !searchTerm || 
        doc.doc_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.patient_name?.toLowerCase().includes(searchTerm.toLowerCase())
      
      // Фильтр по дате от
      const matchesDateFrom = !filters.dateFrom || (() => {
        const docDate = new Date(doc.created_at)
        const fromDate = new Date(filters.dateFrom)
        fromDate.setHours(0, 0, 0, 0)
        return docDate >= fromDate
      })()
      
      // Фильтр по дате до
      const matchesDateTo = !filters.dateTo || (() => {
        const docDate = new Date(doc.created_at)
        const toDate = new Date(filters.dateTo)
        toDate.setHours(23, 59, 59, 999)
        return docDate <= toDate
      })()
      
      // Фильтр по организации
      const matchesOrganization = !filters.organization ||
        doc.organization?.toLowerCase().includes(filters.organization.toLowerCase())
      
      return matchesSearch && matchesDateFrom && matchesDateTo && matchesOrganization
    })
    setFilteredDocuments(filtered)
    setCurrentPage(1) // Сбрасываем на первую страницу при изменении фильтров
  }

  const paginateDocuments = () => {
    if (itemsPerPage === 'all') {
      setPaginatedDocuments(filteredDocuments)
    } else {
      const startIndex = (currentPage - 1) * itemsPerPage
      const endIndex = startIndex + itemsPerPage
      setPaginatedDocuments(filteredDocuments.slice(startIndex, endIndex))
    }
  }

  const totalPages = itemsPerPage === 'all' ? 1 : Math.ceil(filteredDocuments.length / itemsPerPage)

  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleItemsPerPageChange = (value) => {
    const numValue = value === 'all' ? 'all' : parseInt(value)
    setItemsPerPage(numValue)
    setCurrentPage(1)
  }

  const resetFilters = () => {
    setSearchTerm('')
    setFilters({
      dateFrom: '',
      dateTo: '',
      organization: '',
    })
    setCurrentPage(1)
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Список документов</h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              Все созданные медицинские документы
            </p>
          </div>
          <Button onClick={() => router.push('/documents/create')} className="w-full sm:w-auto">
            <Plus className="mr-2 h-4 w-4" />
            Создать документ
          </Button>
        </div>

              {/* Фильтры */}
              <Card>
                <CardHeader className="py-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Filter className="h-4 w-4" />
                      Фильтры
                    </CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setFiltersOpen(!filtersOpen)}
                      className="md:hidden h-8 px-2"
                    >
                      <ChevronDown className={`h-4 w-4 transition-transform duration-300 ${filtersOpen ? 'rotate-180' : ''}`} />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className={`grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-4 transition-all duration-300 ${
                    filtersOpen ? 'opacity-100 blur-0 max-h-[500px]' : 'opacity-40 blur-[0.5px] max-h-0 overflow-hidden md:opacity-100 md:blur-0 md:max-h-[500px]'
                  }`}>
              <div className="space-y-2">
                <Label htmlFor="search">Поиск</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Номер или имя пациента..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateFrom">Дата от</Label>
                <DatePicker
                  value={filters.dateFrom}
                  onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                  placeholder="Выберите дату от"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateTo">Дата до</Label>
                <DatePicker
                  value={filters.dateTo}
                  onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                  placeholder="Выберите дату до"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="organization">Организация</Label>
                <Input
                  id="organization"
                  placeholder="Название организации..."
                  value={filters.organization}
                  onChange={(e) => setFilters({ ...filters, organization: e.target.value })}
                />
              </div>
                  </div>
                  <div className={`mt-4 flex gap-2 transition-all duration-300 ${
                    filtersOpen ? 'opacity-100 blur-0' : 'opacity-40 blur-[0.5px] md:opacity-100 md:blur-0'
                  }`}>
                    <Button onClick={resetFilters} variant="outline">
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Сбросить
                    </Button>
                  </div>
                </CardContent>
              </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Документы</CardTitle>
                <CardDescription>
                  Поиск и управление созданными документами
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Label htmlFor="itemsPerPage" className="text-sm">Показать:</Label>
                <select
                  id="itemsPerPage"
                  className="flex h-9 w-20 rounded-md border border-input bg-background px-3 py-1 text-sm"
                  value={itemsPerPage}
                  onChange={(e) => handleItemsPerPageChange(e.target.value)}
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="all">Все</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border rounded-lg overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Номер документа</TableHead>
                      <TableHead>Пациент</TableHead>
                      <TableHead>Диагноз</TableHead>
                      <TableHead>Организация</TableHead>
                      <TableHead>Дата создания</TableHead>
                      <TableHead>Создатель</TableHead>
                      <TableHead className="text-right sticky right-0 bg-background z-10">Действия</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedDocuments.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                          {filteredDocuments.length === 0 
                            ? (searchTerm ? 'Документы не найдены' : 'Нет документов')
                            : 'Нет документов на этой странице'
                          }
                        </TableCell>
                      </TableRow>
                    ) : (
                      paginatedDocuments.map((doc) => {
                        // Скрываем создателя, если created_by === 1
                        const shouldHideCreator = doc.created_by === 1
                        const creatorDisplay = shouldHideCreator 
                          ? '-' 
                          : (doc.creator_username || doc.creator_email || '-')
                        
                        return (
                        <TableRow key={doc.id}>
                          <TableCell className="font-medium font-mono">
                            {doc.doc_number}
                          </TableCell>
                          <TableCell>{doc.patient_name}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {doc.diagnosis || '-'}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {doc.organization || '-'}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {doc.created_at 
                              ? new Date(doc.created_at).toLocaleDateString('ru-RU', {
                                  year: 'numeric',
                                  month: '2-digit',
                                  day: '2-digit',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })
                              : '-'
                            }
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {creatorDisplay}
                          </TableCell>
                          <TableCell className="text-right sticky right-0 bg-background z-10">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                // Используем функцию getBaseURL для правильного формирования URL
                                function getBaseURL() {
                                  let baseUrl = process.env.NEXT_PUBLIC_API_URL 
                                    || process.env.API_URL 
                                    || 'http://localhost:5000'
                                  
                                  // Убираем trailing slash если есть
                                  baseUrl = baseUrl.replace(/\/+$/, '')
                                  
                                  // Добавляем /api только если его еще нет
                                  if (!baseUrl.endsWith('/api')) {
                                    baseUrl = `${baseUrl}/api`
                                  }
                                  
                                  return baseUrl
                                }
                                
                                const apiBase = getBaseURL()
                                window.open(`${apiBase}/documents/${doc.id}/download`, '_blank')
                              }}
                              className="text-xs sm:text-sm"
                            >
                              <Download className="mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                              <span className="hidden sm:inline">Скачать</span>
                            </Button>
                          </TableCell>
                        </TableRow>
                        )
                      })
                    )}
                  </TableBody>
                </Table>
              </div>

              {/* Пагинация */}
              {itemsPerPage !== 'all' && totalPages > 1 && (
                <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-t pt-4">
                  <div className="text-xs sm:text-sm text-muted-foreground text-center sm:text-left">
                    Показано {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredDocuments.length)} из {filteredDocuments.length} документов
                  </div>
                  <div className="flex gap-1 justify-center sm:justify-end flex-wrap">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Назад
                    </Button>
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                      // Показываем только соседние страницы
                      if (
                        page === 1 ||
                        page === totalPages ||
                        (page >= currentPage - 1 && page <= currentPage + 1)
                      ) {
                        return (
                          <Button
                            key={page}
                            variant={currentPage === page ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => handlePageChange(page)}
                          >
                            {page}
                          </Button>
                        )
                      } else if (
                        page === currentPage - 2 ||
                        page === currentPage + 2
                      ) {
                        return <span key={page} className="px-2">...</span>
                      }
                      return null
                    })}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Вперед
                    </Button>
                  </div>
                </div>
              )}
              
              {/* Информация о количестве при "Все" */}
              {itemsPerPage === 'all' && filteredDocuments.length > 0 && (
                <div className="mt-4 text-sm text-muted-foreground text-center border-t pt-4">
                  Показано все {filteredDocuments.length} документов
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
