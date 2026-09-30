import { CheckSquare, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground">Track follow-ups and to-dos</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Task
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Task Management</CardTitle>
          </div>
          <CardDescription>
            Organize your daily activities and follow-ups
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <CheckSquare className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Tasks Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
              <p className="text-xs mt-1 max-w-md">
                This module will include task creation, assignment, due dates,
                priority levels, and integration with leads and opportunities.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
