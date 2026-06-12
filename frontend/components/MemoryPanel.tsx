'use client'

import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Brain, ChevronDown, Trash2 } from 'lucide-react'
import { MemoryItem } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

export function MemoryPanel() {
  const [items, setItems] = useState<MemoryItem[]>([])
  const [open, setOpen] = useState(false)

  async function loadMemory() {
    const response = await fetch(`${API_BASE}/api/memory`)
    if (response.ok) {
      setItems(await response.json())
    }
  }

  async function clearMemory() {
    await fetch(`${API_BASE}/api/memory`, { method: 'DELETE' })
    setItems([])
  }

  useEffect(() => {
    void loadMemory()
  }, [])

  return (
    <section className="depth-card overflow-hidden rounded-[22px] border border-white/10 bg-[#111114]/82 shadow-2xl shadow-black/30 backdrop-blur-xl">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 p-5 text-left"
      >
        <span className="inline-flex items-center gap-2 text-lg font-semibold text-white">
          <span className="grid h-10 w-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Brain className="h-5 w-5 text-indigo-300" />
          </span>
          What the Agent OS has learned
        </span>
        <span className="inline-flex items-center gap-3 text-sm text-[#9a9aa3]">
          {items.length} memories
          <ChevronDown className={`h-4 w-4 transition ${open ? 'rotate-180' : ''}`} />
        </span>
      </button>
      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-white/10"
          >
            <div className="p-5">
              <div className="mb-4 flex justify-end">
                <button
                  type="button"
                  onClick={clearMemory}
                  className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-[#a5a5ae] transition hover:-translate-y-0.5 hover:border-red-400/50 hover:text-red-200"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear Memory
                </button>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                {items.length ? (
                  items.map((item) => (
                    <article key={`${item.task_id}-${item.timestamp}`} className="rounded-2xl border border-white/10 bg-black/20 p-4 shadow-lg shadow-black/20">
                      <div className="text-sm font-semibold text-white">{item.task || 'Stored result'}</div>
                      <p className="mt-2 line-clamp-3 text-sm leading-6 text-[#a5a5ae]">{item.content}</p>
                      <div className="mt-3 text-xs text-[#8b8b95]">
                        {item.score ? `Score ${item.score}/10 - ` : null}
                        {item.timestamp}
                      </div>
                    </article>
                  ))
                ) : (
                  <p className="text-sm text-[#9a9aa3]">No long-term memories yet.</p>
                )}
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </section>
  )
}
