'use client'

import { useState, useEffect } from 'react'
import {
  Users,
  UserPlus,
  MoreHorizontal,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Building2,
  X,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { useAuth } from '@/lib/auth-context'
import {
  usersApi,
  organizationApi,
  UserResponse,
  OrganizationResponse,
  ApiClientError,
} from '@/lib/api'

const getRoleBadgeVariant = (role: string) => {
  switch (role) {
    case 'admin':
      return 'destructive'
    case 'manager':
      return 'default'
    case 'sales':
      return 'secondary'
    default:
      return 'outline'
  }
}

const getRoleIcon = (role: string) => {
  switch (role) {
    case 'admin':
      return ShieldAlert
    case 'manager':
      return ShieldCheck
    case 'sales':
      return Shield
    default:
      return Shield
  }
}

const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    admin: 'Administrator',
    manager: 'Manager',
    sales: 'Sales',
  }
  return labels[role] || role
}

const roleOptions = [
  { value: 'sales', label: 'Sales' },
  { value: 'manager', label: 'Manager' },
  { value: 'admin', label: 'Administrator' },
]

interface UserFormData {
  full_name: string
  email: string
  role: 'admin' | 'manager' | 'sales'
  password: string
}

const emptyFormData: UserFormData = {
  full_name: '',
  email: '',
  role: 'sales',
  password: '',
}

export default function SettingsPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<UserResponse[]>([])
  const [organization, setOrganization] = useState<OrganizationResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // Dialog states
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showDeactivateDialog, setShowDeactivateDialog] = useState(false)
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null)
  const [formData, setFormData] = useState<UserFormData>(emptyFormData)
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Determine role capabilities
  const isAdmin = currentUser?.role === 'admin'
  const isManager = currentUser?.role === 'manager' || isAdmin
  const canViewTeam = isManager
  const canManageTeam = isAdmin

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    setError('')

    try {
      // Load organization info (available to all roles)
      const orgData = await organizationApi.get()
      setOrganization(orgData)

      // Load team members only for admin/manager
      if (canViewTeam) {
        const usersResponse = await usersApi.list()
        setUsers(usersResponse.items)
      }
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message)
      } else {
        setError('Failed to load settings')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateUser = () => {
    setFormData(emptyFormData)
    setFormError('')
    setShowCreateDialog(true)
  }

  const handleEditUser = (user: UserResponse) => {
    setSelectedUser(user)
    setFormData({
      full_name: user.full_name,
      email: user.email,
      role: user.role,
      password: '',
    })
    setFormError('')
    setShowEditDialog(true)
  }

  const handleDeactivateUser = (user: UserResponse) => {
    setSelectedUser(user)
    setFormError('')
    setShowDeactivateDialog(true)
  }

  const submitCreateUser = async () => {
    if (!formData.full_name || !formData.email || !formData.password) {
      setFormError('All fields are required')
      return
    }

    setIsSubmitting(true)
    setFormError('')

    try {
      const newUser = await usersApi.create({
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
        role: formData.role,
      })
      setUsers((prev) => [newUser, ...prev])
      setShowCreateDialog(false)
      setFormData(emptyFormData)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setFormError(err.message)
      } else {
        setFormError('Failed to create user')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const submitEditUser = async () => {
    if (!selectedUser || !formData.full_name || !formData.email) {
      setFormError('Name and email are required')
      return
    }

    setIsSubmitting(true)
    setFormError('')

    try {
      const updatedUser = await usersApi.update(selectedUser.id, {
        full_name: formData.full_name,
        email: formData.email,
        role: formData.role,
      })
      setUsers((prev) => prev.map((u) => (u.id === updatedUser.id ? updatedUser : u)))
      setShowEditDialog(false)
      setSelectedUser(null)
      setFormData(emptyFormData)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setFormError(err.message)
      } else {
        setFormError('Failed to update user')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const submitDeactivateUser = async () => {
    if (!selectedUser) return

    setIsSubmitting(true)
    setFormError('')

    try {
      const updatedUser = await usersApi.update(selectedUser.id, {
        is_active: false,
      })
      setUsers((prev) => prev.map((u) => (u.id === updatedUser.id ? updatedUser : u)))
      setShowDeactivateDialog(false)
      setSelectedUser(null)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setFormError(err.message)
      } else {
        setFormError('Failed to deactivate user')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const submitActivateUser = async (user: UserResponse) => {
    try {
      const updatedUser = await usersApi.update(user.id, {
        is_active: true,
      })
      setUsers((prev) => prev.map((u) => (u.id === updatedUser.id ? updatedUser : u)))
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message)
      } else {
        setError('Failed to activate user')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Manage your team and organization</p>
        </div>
      </div>

      {/* Organization Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Organization</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-4">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : organization ? (
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">{organization.name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Slug</p>
                <p className="font-mono text-sm">{organization.slug}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <Badge variant={organization.is_active ? 'default' : 'secondary'}>
                  {organization.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">Unable to load organization info</p>
          )}
        </CardContent>
      </Card>

      {/* Team Members - Only for Admin/Manager */}
      {canViewTeam && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Team Members</CardTitle>
              </div>
              {canManageTeam && (
                <Button size="sm" onClick={handleCreateUser}>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Invite User
                </Button>
              )}
            </div>
            <CardDescription>
              {canManageTeam
                ? "Manage your organization's team members and their roles"
                : 'View your organization team members'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            ) : error ? (
              <div className="rounded-md bg-destructive/10 p-4">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            ) : users.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <Users className="h-12 w-12 mb-4" />
                <p className="text-lg font-medium">No team members found</p>
                <p className="text-sm mt-1">Add your first team member to get started</p>
              </div>
            ) : (
              <div className="divide-y">
                {users.map((user) => {
                  const RoleIcon = getRoleIcon(user.role)
                  return (
                    <div
                      key={user.id}
                      className="flex items-center justify-between py-4 first:pt-0 last:pb-0"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
                          {user.full_name
                            .split(' ')
                            .map((n) => n[0])
                            .join('')
                            .toUpperCase()
                            .slice(0, 2)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{user.full_name}</p>
                            {user.id === currentUser?.id && (
                              <Badge variant="outline" className="text-xs">
                                You
                              </Badge>
                            )}
                            {!user.is_active && (
                              <Badge variant="outline" className="text-xs text-muted-foreground">
                                Inactive
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge
                          variant={getRoleBadgeVariant(user.role)}
                          className="flex items-center gap-1"
                        >
                          <RoleIcon className="h-3 w-3" />
                          {getRoleLabel(user.role)}
                        </Badge>
                        {canManageTeam && user.id !== currentUser?.id && (
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEditUser(user)}
                              title="Edit user"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Edit user</span>
                            </Button>
                            {user.is_active ? (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeactivateUser(user)}
                                className="text-muted-foreground hover:text-destructive"
                              >
                                Deactivate
                              </Button>
                            ) : (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => submitActivateUser(user)}
                                className="text-muted-foreground hover:text-primary"
                              >
                                Activate
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* My Account - Only for Sales (who cannot view team) */}
      {!canViewTeam && (
        <Card>
          <CardHeader>
            <CardTitle>My Account</CardTitle>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent>
            {currentUser && (
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{currentUser.full_name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{currentUser.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Role</p>
                  <Badge variant={getRoleBadgeVariant(currentUser.role)}>
                    {getRoleLabel(currentUser.role)}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Organization</p>
                  <p className="font-medium">{currentUser.organization.name}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create User Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New User</DialogTitle>
            <DialogDescription>
              Add a new team member to your organization.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {formError && (
              <div className="rounded-md bg-destructive/10 p-3">
                <p className="text-sm text-destructive">{formError}</p>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="create-full_name">Full Name</Label>
              <Input
                id="create-full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="create-email">Email</Label>
              <Input
                id="create-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="create-role">Role</Label>
              <Select
                id="create-role"
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value as UserFormData['role'] })
                }
                options={roleOptions}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="create-password">Initial Password</Label>
              <Input
                id="create-password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter a secure password"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={submitCreateUser} disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create User'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Update user information and role.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {formError && (
              <div className="rounded-md bg-destructive/10 p-3">
                <p className="text-sm text-destructive">{formError}</p>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="edit-full_name">Full Name</Label>
              <Input
                id="edit-full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email</Label>
              <Input
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-role">Role</Label>
              <Select
                id="edit-role"
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value as UserFormData['role'] })
                }
                options={roleOptions}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={submitEditUser} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Deactivate User Dialog */}
      <Dialog open={showDeactivateDialog} onOpenChange={setShowDeactivateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deactivate User</DialogTitle>
            <DialogDescription>
              Are you sure you want to deactivate {selectedUser?.full_name}? They will not be able
              to access the system until reactivated.
            </DialogDescription>
          </DialogHeader>
          {formError && (
            <div className="rounded-md bg-destructive/10 p-3">
              <p className="text-sm text-destructive">{formError}</p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeactivateDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={submitDeactivateUser} disabled={isSubmitting}>
              {isSubmitting ? 'Deactivating...' : 'Deactivate'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
