import { Building2, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function CustomersPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Customers</h1>
          <p className="text-muted-foreground">Manage your customer database</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Customer
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Customer Management</CardTitle>
          </div>
          <CardDescription>
            View and manage customer information, policies, and history
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <Building2 className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Customers Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
              <p className="text-xs mt-1 max-w-md">
                This module will include customer profiles, policy management,
                interaction history, and renewal tracking.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
