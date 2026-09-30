import { BarChart3, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">Insights and performance metrics</p>
        </div>
        <Button variant="outline">
          <Calendar className="mr-2 h-4 w-4" />
          Last 30 days
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Sales Analytics</CardTitle>
          </div>
          <CardDescription>
            Performance dashboards and business intelligence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center text-muted-foreground">
              <BarChart3 className="mx-auto h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Analytics Module</p>
              <p className="text-sm mt-2">To be implemented in a future phase</p>
              <p className="text-xs mt-1 max-w-md">
                This module will include sales dashboards, conversion metrics,
                team performance, product analysis, and custom reports.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
