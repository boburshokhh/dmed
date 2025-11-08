'use client'

import { useState, useEffect } from 'react'
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
import { FileText, Download, Trash2, Filter, RotateCcw, FolderOpen, ChevronDown } from 'lucide-react'
import api from '@/lib/api'
import { isSuperAdmin } from '@/lib/auth'
import { DatePicker } from '@/components/ui/date-picker'

export default function FilesPage() {
  const [files, setFiles] = useState([])
  const [filteredFiles, setFilteredFiles] = useState([])
  const [paginatedFiles, setPaginatedFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  const [stats, setStats] = useState({
    total: 0,
    pdf: 0,
    docx: 0,
    totalSize: 0
  })
  const [filtersOpen, setFiltersOpen] = useState(false) // State for filters visibility
  const [filters, setFilters] = useState({
    type: '',
    search: '',
    dateFrom: '',
    dateTo: ''
  })

  useEffect(() => {
    loadFiles()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [files, filters])

  useEffect(() => {
    paginateFiles()
  }, [filteredFiles, currentPage])

  const loadFiles = async () => {
    try {
      const response = await api.get('/files')
      if (response.data.success) {
        setFiles(response.data.files || [])
        updateStats(response.data.files || [])
      }
    } catch (error) {
      console.error('Ошибка загрузки файлов:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...files]

    // Фильтр по типу
    if (filters.type) {
      filtered = filtered.filter(f => f.name.toLowerCase().endsWith(`.${filters.type}`))
    }

    // Поиск
    if (filters.search) {
      const search = filters.search.toLowerCase()
      filtered = filtered.filter(f =>
        f.name.toLowerCase().includes(search) ||
        f.patient_name?.toLowerCase().includes(search) ||
        f.doc_number?.toLowerCase().includes(search)
      )
    }

    // Фильтр по дате
    if (filters.dateFrom) {
      filtered = filtered.filter(f => {
        const fileDate = new Date(f.last_modified)
        return fileDate >= new Date(filters.dateFrom)
      })
    }

    if (filters.dateTo) {
      filtered = filtered.filter(f => {
        const fileDate = new Date(f.last_modified)
        const toDate = new Date(filters.dateTo)
        toDate.setHours(23, 59, 59)
        return fileDate <= toDate
      })
    }

    setFilteredFiles(filtered)
    updateStats(filtered)
  }

  const updateStats = (fileList) => {
    const total = fileList.length
    const pdf = fileList.filter(f => f.name.endsWith('.pdf')).length
    const docx = fileList.filter(f => f.name.endsWith('.docx')).length
    const totalSize = fileList.reduce((sum, f) => sum + (f.size || 0), 0)

    setStats({ total, pdf, docx, totalSize })
  }

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const paginateFiles = () => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    setPaginatedFiles(filteredFiles.slice(startIndex, endIndex))
  }

  const totalPages = Math.ceil(filteredFiles.length / itemsPerPage)

  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Вы уверены, что хотите удалить файл "${filename}"?`)) {
      return
    }

    try {
      await api.delete(`/files/delete/${encodeURIComponent(filename)}`)
      alert('Файл успешно удален')
      loadFiles()
    } catch (error) {
      alert('Ошибка удаления файла: ' + (error.response?.data?.message || error.message))
    }
  }

  const resetFilters = () => {
    setFilters({
      type: '',
      search: '',
      dateFrom: '',
      dateTo: ''
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
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">История файлов</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Управление всеми сгенерированными документами
          </p>
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
                <Label htmlFor="type">Тип файла</Label>
                <select
                  id="type"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={filters.type}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                >
                  <option value="">Все типы</option>
                  <option value="pdf">PDF</option>
                  <option value="docx">DOCX</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="search">Поиск</Label>
                <Input
                  id="search"
                  placeholder="Имя файла, UUID, пациент..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                />
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

        {/* Статистика */}
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Всего файлов</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>PDF документы</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats.pdf}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>DOCX документы</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.docx}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Общий размер</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatBytes(stats.totalSize)}</div>
            </CardContent>
          </Card>
        </div>

        {/* Таблица файлов */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FolderOpen className="h-5 w-5" />
              Список файлов
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Имя файла / Пациент</TableHead>
                    <TableHead>Тип</TableHead>
                    <TableHead>Размер</TableHead>
                    <TableHead>Дата создания</TableHead>
                    <TableHead>Номер документа</TableHead>
                    <TableHead className="text-right sticky right-0 bg-background z-10">Действия</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedFiles.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        {filteredFiles.length === 0 ? 'Файлы не найдены' : 'Нет файлов на этой странице'}
                      </TableCell>
                    </TableRow>
                  ) : (
                    paginatedFiles.map((file, index) => {
                      const type = file.name.split('.').pop().toUpperCase()
                      return (
                        <TableRow key={index}>
                          <TableCell>
                            <div className="font-semibold text-xs sm:text-sm break-words">{file.name}</div>
                            {file.patient_name && (
                              <div className="text-xs text-muted-foreground">{file.patient_name}</div>
                            )}
                          </TableCell>
                          <TableCell>
                            <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                              type === 'PDF' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                            }`}>
                              {type}
                            </span>
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {formatBytes(file.size)}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {formatDate(file.last_modified)}
                          </TableCell>
                          <TableCell className="text-muted-foreground font-mono">
                            {file.doc_number || '-'}
                          </TableCell>
                          <TableCell className="text-right sticky right-0 bg-background z-10">
                            <div className="flex justify-end gap-1 sm:gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => window.open(`${process.env.API_URL?.replace('/api', '')}/api/files/download/${encodeURIComponent(file.name)}`, '_blank')}
                                className="h-8 w-8 sm:h-10 sm:w-10 p-0"
                              >
                                <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                              </Button>
                              {isSuperAdmin() && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDelete(file.name)}
                                  className="h-8 w-8 sm:h-10 sm:w-10 p-0"
                                >
                                  <Trash2 className="h-3 w-3 sm:h-4 sm:w-4 text-destructive" />
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Пагинация */}
            {totalPages > 1 && (
              <div className="mt-4 flex items-center justify-between border-t pt-4">
                <div className="text-sm text-muted-foreground">
                  Показано {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredFiles.length)} из {filteredFiles.length} файлов
                </div>
                <div className="flex gap-1">
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
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}

