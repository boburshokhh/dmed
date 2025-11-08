'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getAuth } from '@/lib/auth'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    const auth = getAuth()
    if (!auth) {
      router.push('/login')
    } else {
      if (auth.role === 'super_admin') {
        router.push('/dashboard')
      } else {
        router.push('/documents')
      }
    }
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  )
}

