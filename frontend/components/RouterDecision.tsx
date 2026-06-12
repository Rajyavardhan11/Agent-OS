import { RouterDecision as RouterDecisionType } from '@/types'

interface RouterDecisionProps {
  decision?: RouterDecisionType
}

export function RouterDecision({ decision }: RouterDecisionProps) {
  if (!decision?.agents_needed?.length) {
    return null
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-indigo-300/15 bg-indigo-300/[0.045] p-4 shadow-xl shadow-indigo-500/5">
      <div className="flex flex-wrap gap-2">
        <span className="rounded-full border border-indigo-300/20 bg-indigo-500/15 px-3 py-1 text-xs font-semibold text-indigo-200">
          {decision.task_type}
        </span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-[#b9b9c3]">
          {decision.complexity}
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {decision.agents_needed.map((agent) => (
          <span key={agent} className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-white">
            {agent}
          </span>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-[#9a9aa3]">
        {decision.execution_order.map((group, index) => (
          <div key={`${group.join('-')}-${index}`} className="flex items-center gap-2">
            <span className="rounded-xl border border-white/10 bg-black/35 px-2.5 py-1.5 text-white">{group.join(' + ')}</span>
            {index < decision.execution_order.length - 1 ? <span>-&gt;</span> : null}
          </div>
        ))}
      </div>
      <p className="mt-4 text-sm italic leading-6 text-[#a9a9b3]">{decision.reasoning}</p>
    </div>
  )
}
