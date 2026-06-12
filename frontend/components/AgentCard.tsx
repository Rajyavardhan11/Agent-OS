'use client'

import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Brain, CheckCircle2, Circle, Code2, Compass, Database, FilePenLine, Microscope, Sparkles, XCircle } from 'lucide-react'
import { AgentLog } from '@/types'

const agentMeta = {
  memory_manager: { label: 'Memory', icon: Database, color: 'text-emerald-300', glow: 'shadow-emerald-500/10' },
  router: { label: 'Router', icon: Compass, color: 'text-indigo-300', glow: 'shadow-indigo-500/10' },
  planner: { label: 'Planner', icon: Brain, color: 'text-sky-300', glow: 'shadow-sky-500/10' },
  researcher: { label: 'Researcher', icon: Microscope, color: 'text-cyan-300', glow: 'shadow-cyan-500/10' },
  coder: { label: 'Coder', icon: Code2, color: 'text-violet-300', glow: 'shadow-violet-500/10' },
  writer: { label: 'Writer', icon: FilePenLine, color: 'text-rose-300', glow: 'shadow-rose-500/10' },
  critic: { label: 'Critic', icon: Sparkles, color: 'text-amber-300', glow: 'shadow-amber-500/10' },
}

interface AgentCardProps {
  log: AgentLog
}

export function AgentCard({ log }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false)
  const isRunning = log.status === 'running'
  const isDone = log.status === 'done'
  const isError = log.status === 'error'
  const meta = agentMeta[log.agent as keyof typeof agentMeta] ?? agentMeta.planner
  const Icon = meta.icon

  return (
    <motion.button
      type="button"
      layout
      onClick={() => setExpanded((value) => !value)}
      initial={{ opacity: 0, y: 12, rotateX: -6 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      whileHover={{ y: -3, scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 260, damping: 22 }}
      className={`agent-card-3d relative w-full overflow-hidden rounded-2xl border border-white/10 bg-[#111114]/88 p-4 text-left shadow-xl ${meta.glow} transition hover:border-white/20`}
    >
      <AnimatePresence>
        {isRunning ? (
          <motion.span
            initial={{ x: '-120%' }}
            animate={{ x: '120%' }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.3, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-y-0 left-0 w-1/2 bg-gradient-to-r from-transparent via-indigo-300/10 to-transparent"
          />
        ) : null}
      </AnimatePresence>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.04] shadow-inner shadow-white/5">
            <Icon className={`h-5 w-5 ${meta.color}`} />
          </div>
          <div>
          <div className="text-xs uppercase tracking-[0.18em] text-[#888888]">{meta.label}</div>
          <h3 className="mt-1 text-sm font-semibold capitalize text-white">{log.agent.replace('_', ' ')}</h3>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#888888]">
          {isRunning ? <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-blue-400 shadow-[0_0_16px_rgba(96,165,250,0.9)]" /> : null}
          {isDone ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : null}
          {isError ? <XCircle className="h-4 w-4 text-red-500" /> : null}
          {!isRunning && !isDone && !isError ? <Circle className="h-4 w-4 text-[#888888]" /> : null}
          {isRunning ? 'thinking...' : log.status}
        </div>
      </div>
      {log.output ? (
        <p className={`mt-4 rounded-2xl border border-white/10 bg-black/25 p-3 text-sm leading-6 text-[#a5a5ae] ${expanded ? '' : 'line-clamp-2'}`}>
          {log.output}
        </p>
      ) : null}
    </motion.button>
  )
}
