import { Settings, Users, Building2, Bell, Shield, Palette } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const settingsSections = [
  {
    title: 'Profile',
    description: 'Manage your personal information and preferences',
    icon: Users,
  },
  {
    title: 'Organization',
    description: 'Company settings and branding',
    icon: Building2,
  },
  {
    title: 'Notifications',
    description: 'Configure alerts and email preferences',
    icon: Bell,
  },
  {
    title: 'Security',
    description: 'Password, two-factor authentication, sessions',
    icon: Shield,
  },
  {
    title: 'Appearance',
    description: 'Theme, display preferences, accessibility',
    icon: Palette,
  },
]

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account and application preferences</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {settingsSections.map((section) => (
          <Card key={section.title} className="cursor-pointer transition-colors hover:bg-accent">
            <CardHeader>
              <div className="flex items-center gap-2">
                <section.icon className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-base">{section.title}</CardTitle>
              </div>
              <CardDescription className="text-sm">{section.description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Application Settings</CardTitle>
          </div>
          <CardDescription>
            System configuration and organization preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[200px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <Settings className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Settings Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
