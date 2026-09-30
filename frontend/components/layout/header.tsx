'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { Menu, Moon, Sun, Bell, LogOut, Settings } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth-context'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const [theme, setTheme] = React.useState<'light' | 'dark'>('dark')
  const [dropdownOpen, setDropdownOpen] = React.useState(false)
  const { user, logout } = useAuth()
  const dropdownRef = React.useRef<HTMLDivElement>(null)
  const router = useRouter()

  React.useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark')
    setTheme(isDark ? 'dark' : 'light')
  }, [])

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.classList.toggle('dark')
  }

  const handleLogout = async () => {
    setDropdownOpen(false)
    await logout()
  }

  const handleSettings = () => {
    setDropdownOpen(false)
    router.push('/settings')
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      admin: 'Administrator',
      manager: 'Manager',
      sales: 'Sales Representative',
    }
    return roleLabels[role] || role
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-card px-4 lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <div className="flex flex-1 items-center justify-end gap-2">
        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        <div className="relative" ref={dropdownRef}>
          <button
            type="button"
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="ml-2 flex items-center gap-3 rounded-md p-1 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="User menu"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
              {user ? getInitials(user.full_name) : 'U'}
            </div>
            <div className="hidden text-left text-sm sm:block">
              <p className="font-medium">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground">
                {user ? getRoleLabel(user.role) : 'Loading...'}
              </p>
            </div>
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-md border bg-popover shadow-lg">
              <div className="p-2">
                <div className="px-2 py-1.5 text-sm font-medium">{user?.full_name}</div>
                <div className="px-2 py-1 text-xs text-muted-foreground">{user?.email}</div>
              </div>
              <div className="border-t" />
              <div className="p-1">
                <button
                  type="button"
                  onClick={handleSettings}
                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </button>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive hover:bg-accent"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
