import { Users, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LeadsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Leads</h1>
          <p className="text-muted-foreground">Capture and qualify potential customers</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Lead
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Lead Management</CardTitle>
          </div>
          <CardDescription>
            Track and nurture potential customers through the qualification process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <Users className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Leads Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
              <p className="text-xs mt-1 max-w-md">
                This module will include lead capture forms, qualification workflows,
                lead scoring, and assignment to sales representatives.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
