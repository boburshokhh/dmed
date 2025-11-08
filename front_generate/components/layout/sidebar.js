'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  LogOut,
  Settings,
  FolderOpen,
  FilePlus,
  List,
  Menu
} from 'lucide-react'
import { clearAuth, isSuperAdmin, getAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import {
  Sheet,
  SheetContent,
} from '@/components/ui/sheet'

const menuItems = [
  {
    title: 'Главная',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['super_admin'],
  },
  {
    title: 'Создать документ',
    href: '/documents/create',
    icon: FilePlus,
    roles: ['admin', 'super_admin'],
  },
  {
    title: 'Список документов',
    href: '/documents',
    icon: List,
    roles: ['admin', 'super_admin'],
  },
  {
    title: 'Управление файлами',
    href: '/files',
    icon: FolderOpen,
    roles: ['admin', 'super_admin'],
  },
  {
    title: 'Управление админами',
    href: '/admin/users',
    icon: Users,
    roles: ['super_admin'],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [userData, setUserData] = useState(null)
  const [userIsSuperAdmin, setUserIsSuperAdmin] = useState(false)

  useEffect(() => {
    setMounted(true)
    const auth = getAuth()
    if (auth) {
      setUserData(auth.userData)
      setUserIsSuperAdmin(auth.role === 'super_admin')
    }
  }, [])

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  // Фильтруем меню только после монтирования, когда знаем роль пользователя
  const filteredMenuItems = mounted ? menuItems.filter(item => {
    if (item.roles.includes('super_admin') && !userIsSuperAdmin) {
      return false
    }
    return true
  }) : menuItems // Показываем все пункты до монтирования

  const SidebarContent = ({ onLinkClick }) => (
    <>
      <div className="flex h-16 items-center border-b px-6">
        <h2 className="text-lg font-semibold">DMED Admin</h2>
      </div>
      
      {/* Профиль пользователя - только после монтирования */}
      {mounted && userData && (
        <div className="border-b p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold">
              {userData.username?.charAt(0).toUpperCase() || 'A'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{userData.username}</p>
              <p className="text-xs text-muted-foreground truncate">{userData.email}</p>
            </div>
          </div>
          <div className="mt-2">
            <span className={cn(
              "inline-flex items-center rounded-full px-2 py-1 text-xs font-medium",
              userData.role === 'super_admin' 
                ? 'bg-purple-100 text-purple-800' 
                : 'bg-blue-100 text-blue-800'
            )}>
              {userData.role === 'super_admin' ? 'Супер-админ' : 'Админ'}
            </span>
          </div>
        </div>
      )}

      <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
        {filteredMenuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onLinkClick}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.title}
            </Link>
          )
        })}
      </nav>
      <div className="border-t p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <LogOut className="h-5 w-5" />
          Выйти
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden md:flex h-screen w-64 flex-col border-r bg-card">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar - Sheet */}
      <div className="md:hidden">
        <MobileSidebar>
          <SidebarContent onLinkClick={() => {}} />
        </MobileSidebar>
      </div>
    </>
  )
}

function MobileSidebar({ children }) {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    setOpen(false)
  }, [pathname])

  return (
    <>
      <div className="fixed top-0 left-0 right-0 z-40 flex h-14 items-center border-b bg-card px-4 md:hidden">
        <button
          onClick={() => setOpen(true)}
          className="mr-3 rounded-md p-2 hover:bg-accent"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h2 className="text-base font-semibold truncate">DMED Admin</h2>
      </div>
      <div className="h-14 md:hidden" /> {/* Spacer for fixed header */}
      
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex h-full flex-col">
            {children}
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}

