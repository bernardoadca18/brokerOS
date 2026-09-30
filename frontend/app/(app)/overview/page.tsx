'use client'

import { ArrowDownRight, ArrowUpRight, TrendingUp, Users, DollarSign, Target } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useAuth } from '@/lib/auth-context'

const kpiData = [
  {
    title: 'New Leads',
    value: '127',
    change: '+12.5%',
    trend: 'up',
    icon: Users,
  },
  {
    title: 'Open Opportunities',
    value: '43',
    change: '+8.2%',
    trend: 'up',
    icon: Target,
  },
  {
    title: 'Won This Month',
    value: 'R$ 284.500',
    change: '+23.1%',
    trend: 'up',
    icon: DollarSign,
  },
  {
    title: 'Pipeline Value',
    value: 'R$ 1.2M',
    change: '-2.4%',
    trend: 'down',
    icon: TrendingUp,
  },
]

const recentActivity = [
  { id: 1, type: 'lead', message: 'New lead captured from website form', time: '2 min ago' },
  { id: 2, type: 'opportunity', message: 'Opportunity moved to negotiation stage', time: '15 min ago' },
  { id: 3, type: 'task', message: 'Follow-up call completed with Maria Santos', time: '1 hour ago' },
  { id: 4, type: 'proposal', message: 'Proposal sent to ABC Corp', time: '2 hours ago' },
  { id: 5, type: 'lead', message: 'Lead qualified: Roberta Lima - Vehicle Insurance', time: '3 hours ago' },
]

const pendingTasks = [
  { id: 1, title: 'Call back João regarding renewal', due: 'Today', priority: 'high' },
  { id: 2, title: 'Prepare proposal for ABC Corp', due: 'Tomorrow', priority: 'medium' },
  { id: 3, title: 'Review expired policies list', due: 'This week', priority: 'low' },
  { id: 4, title: 'Schedule meeting with consortium team', due: 'This week', priority: 'medium' },
]

export default function OverviewPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}. Here&apos;s your sales summary.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiData.map((kpi) => (
          <Card key={kpi.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{kpi.title}</CardTitle>
              <kpi.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <div className="flex items-center text-xs">
                {kpi.trend === 'up' ? (
                  <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
                ) : (
                  <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
                )}
                <span className={kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'}>
                  {kpi.change}
                </span>
                <span className="ml-1 text-muted-foreground">from last month</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Revenue Trend</CardTitle>
            <CardDescription>Monthly closed deals - Demo visualization</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex h-[200px] items-center justify-center rounded-lg border border-dashed">
              <div className="text-center text-muted-foreground">
                <TrendingUp className="mx-auto h-8 w-8 mb-2" />
                <p className="text-sm">Chart will be implemented in a future phase</p>
                <p className="text-xs mt-1">Example: Monthly revenue by product type</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Activity</CardTitle>
            <CardDescription>Latest updates from your pipeline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="mt-0.5 h-2 w-2 rounded-full bg-primary" />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Pending Tasks</CardTitle>
          <CardDescription>Items requiring your attention</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {pendingTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div className="space-y-1">
                  <p className="text-sm font-medium">{task.title}</p>
                  <p className="text-xs text-muted-foreground">Due: {task.due}</p>
                </div>
                <Badge
                  variant={
                    task.priority === 'high'
                      ? 'destructive'
                      : task.priority === 'medium'
                        ? 'default'
                        : 'secondary'
                  }
                >
                  {task.priority}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
        <p><strong>Note:</strong> This is a visual demonstration with mock data.</p>
        <p className="mt-1">Real analytics and data will be implemented in future phases.</p>
      </div>
    </div>
  )
}
