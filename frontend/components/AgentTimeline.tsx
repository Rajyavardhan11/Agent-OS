import { AgentLog, RouterDecision as RouterDecisionType } from '@/types'
import { AgentCard } from './AgentCard'
import { RouterDecision } from './RouterDecision'

interface AgentTimelineProps {
  logs: AgentLog[]
  routerDecision?: RouterDecisionType
}

export function AgentTimeline({ logs, routerDecision }: AgentTimelineProps) {
  return (
    <aside className="depth-card h-full min-h-96 overflow-hidden rounded-[22px] border border-white/10 bg-[#0f0f13]/82 shadow-2xl shadow-black/35 backdrop-blur-xl">
      <div className="border-b border-white/10 p-5">
        <h2 className="text-lg font-semibold text-white">Agent Activity</h2>
        <p className="mt-1 text-sm text-[#9a9aa3]">Live status from each specialist.</p>
      </div>
      <div className="max-h-[720px] space-y-4 overflow-y-auto p-5">
        <RouterDecision decision={routerDecision} />
        {logs.length ? (
          logs.map((log, index) => <AgentCard key={`${log.agent}-${index}`} log={log} />)
        ) : (
          <div className="rounded-2xl border border-dashed border-white/15 bg-black/20 p-6 text-sm leading-6 text-[#9a9aa3]">
            Agents will appear here when a task starts. The router decides the team, then each specialist lights up as it works.
          </div>
        )}
      </div>
    </aside>
  )
}
