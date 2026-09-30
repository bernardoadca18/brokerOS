import { TrendingUp, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function PipelinePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Pipeline</h1>
          <p className="text-muted-foreground">Manage opportunities through the sales funnel</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Opportunity
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Sales Pipeline</CardTitle>
          </div>
          <CardDescription>
            Visualize and manage opportunities from qualification to closure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <TrendingUp className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Pipeline Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
              <p className="text-xs mt-1 max-w-md">
                This module will include a kanban-style pipeline view, opportunity cards,
                stage management, and drag-and-drop functionality.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
