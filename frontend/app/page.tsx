'use client'

import { motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { Activity, Database, Network, ShieldCheck } from 'lucide-react'
import { AgentTimeline } from '@/components/AgentTimeline'
import { MemoryPanel } from '@/components/MemoryPanel'
import { OutputPanel } from '@/components/OutputPanel'
import { TaskInput } from '@/components/TaskInput'
import { useAgentStream } from '@/hooks/useAgentStream'

export default function Home() {
  const { agentLogs, finalOutput, taskResult, routerDecision, isStreaming, error, start } = useAgentStream()

  function handleSubmit(task: string) {
    start(crypto.randomUUID(), task)
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#08080a] text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(99,102,241,0.22),transparent_28%),radial-gradient(circle_at_78%_8%,rgba(20,184,166,0.12),transparent_25%),radial-gradient(circle_at_50%_90%,rgba(244,114,182,0.10),transparent_26%)]" />
        <div className="grid-plane absolute left-1/2 top-24 h-[520px] w-[1200px] -translate-x-1/2 opacity-50" />
        <motion.div
          aria-hidden="true"
          animate={{ rotateX: [62, 58, 62], rotateZ: [0, 2, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
          className="data-orbit absolute left-1/2 top-28 h-72 w-72 -translate-x-1/2 rounded-full border border-indigo-300/20"
        />
      </div>

      <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 md:px-6">
        <header className="grid gap-6 pt-4 lg:grid-cols-[1fr_auto] lg:items-end">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-[#b8b8c3] shadow-lg shadow-black/20 backdrop-blur"
            >
              <Network className="h-3.5 w-3.5 text-indigo-300" />
              Agent mesh online
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="max-w-3xl text-5xl font-semibold tracking-normal text-white md:text-7xl"
            >
              Agent OS
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mt-4 max-w-2xl text-base leading-7 text-[#a1a1aa]"
            >
              A live multi-agent workspace with shared memory, parallel execution, and visible reasoning flow.
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 14, rotateX: -8 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ delay: 0.16 }}
            className="depth-card grid min-w-72 gap-3 rounded-[22px] border border-white/10 bg-[#101013]/75 p-4 shadow-2xl shadow-black/40 backdrop-blur-xl"
          >
            <StatusMetric icon={<Activity className="h-4 w-4" />} label="Runtime" value={isStreaming ? 'Active' : 'Ready'} />
            <StatusMetric icon={<Database className="h-4 w-4" />} label="Memory" value={taskResult?.memory_context ? 'Context loaded' : 'Standing by'} />
            <StatusMetric icon={<ShieldCheck className="h-4 w-4" />} label="Quality gate" value={taskResult?.critique?.score ? `${taskResult.critique.score}/10` : 'Pending'} />
          </motion.div>
        </header>

        <TaskInput disabled={isStreaming} onSubmit={handleSubmit} />

        {error ? (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>
        ) : null}

        <section className="grid gap-6 lg:grid-cols-[minmax(0,0.4fr)_minmax(0,0.6fr)]">
          <AgentTimeline logs={agentLogs} routerDecision={routerDecision} />
          <OutputPanel result={taskResult} finalOutput={finalOutput} />
        </section>

        <MemoryPanel />
      </div>
    </main>
  )
}

interface StatusMetricProps {
  icon: ReactNode
  label: string
  value: string
}

function StatusMetric({ icon, label, value }: StatusMetricProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-black/25 px-3 py-2.5">
      <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[#8b8b95]">
        <span className="text-indigo-300">{icon}</span>
        {label}
      </span>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  )
}
