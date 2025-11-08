'use client'

import React, { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { getAuth } from '@/lib/auth'
import { Sidebar } from './sidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Home } from 'lucide-react'

const routeNames = {
  '/dashboard': 'Главная',
  '/documents': 'Список документов',
  '/documents/create': 'Создать документ',
  '/files': 'Управление файлами',
  '/admin/users': 'Управление админами',
}

export function MainLayout({ children }) {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const auth = getAuth()
    if (!auth) {
      router.push('/login')
    }
  }, [router])

  const getBreadcrumbs = () => {
    const paths = pathname.split('/').filter(Boolean)
    const breadcrumbs = [
      { href: '/dashboard', label: 'Главная' }
    ]

    if (paths.length > 0) {
      let currentPath = ''
      paths.forEach((path, index) => {
        currentPath += `/${path}`
        const label = routeNames[currentPath] || path.charAt(0).toUpperCase() + path.slice(1)
        if (index === paths.length - 1) {
          breadcrumbs.push({ href: currentPath, label, isLast: true })
        } else {
          breadcrumbs.push({ href: currentPath, label })
        }
      })
    }

    return breadcrumbs
  }

  const breadcrumbs = getBreadcrumbs()

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto md:ml-0">
        {/* Фиксированная шапка с breadcrumbs на мобильных - под шапкой с меню */}
        <div className="sticky top-14 z-30 bg-background border-b md:hidden">
          <div className="container mx-auto px-4 py-2">
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumbs.map((crumb, index) => (
                  <React.Fragment key={crumb.href}>
                    <BreadcrumbItem>
                      {index === breadcrumbs.length - 1 ? (
                        <BreadcrumbPage className="text-xs font-medium">
                          {crumb.label}
                        </BreadcrumbPage>
                      ) : (
                        <BreadcrumbLink asChild>
                          <Link href={crumb.href} className="text-xs">
                            {index === 0 ? <Home className="h-3 w-3" /> : crumb.label}
                          </Link>
                        </BreadcrumbLink>
                      )}
                    </BreadcrumbItem>
                    {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </div>
        
        {/* Контент с отступом сверху для мобильных (шапка h-14 + breadcrumbs ~h-10) */}
        <div className="container mx-auto p-4 md:p-6 pt-[calc(3.5rem+2.5rem+1rem)] md:pt-6">
          {/* Breadcrumbs для десктопа */}
          <div className="hidden md:block mb-4">
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumbs.map((crumb, index) => (
                  <React.Fragment key={crumb.href}>
                    <BreadcrumbItem>
                      {index === breadcrumbs.length - 1 ? (
                        <BreadcrumbPage className="text-sm font-medium">
                          {crumb.label}
                        </BreadcrumbPage>
                      ) : (
                        <BreadcrumbLink asChild>
                          <Link href={crumb.href} className="text-sm hover:text-foreground">
                            {index === 0 ? <Home className="h-4 w-4" /> : crumb.label}
                          </Link>
                        </BreadcrumbLink>
                      )}
                    </BreadcrumbItem>
                    {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          {children}
        </div>
      </main>
    </div>
  )
}
