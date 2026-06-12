'use client'

import { FormEvent, useState } from 'react'
import type { ReactNode } from 'react'
import { BrainCircuit, FileText, Gauge, Globe2, Layers3, Loader2, Search, Send, SlidersHorizontal, Sparkles } from 'lucide-react'

interface TaskInputProps {
  disabled: boolean
  onSubmit: (task: string) => void
}

const examples = [
  'Research top AI frameworks and compare them',
  'Build a FastAPI CRUD app with SQLite',
  'Design a launch plan for an AI study assistant',
]

const modes = ['Auto', 'Research', 'Build', 'Write', 'Strategy']
const formats = ['Markdown', 'Report', 'Code + explanation', 'Executive brief']
const tones = ['Precise', 'Creative', 'Boardroom', 'Developer']
const depths = ['Fast', 'Balanced', 'Deep']

export function TaskInput({ disabled, onSubmit }: TaskInputProps) {
  const [task, setTask] = useState('')
  const [mode, setMode] = useState('Auto')
  const [format, setFormat] = useState('Markdown')
  const [tone, setTone] = useState('Precise')
  const [depth, setDepth] = useState('Balanced')
  const [useMemory, setUseMemory] = useState(true)
  const [preferSearch, setPreferSearch] = useState(true)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = task.trim()
    if (trimmed) {
      const optionBlock = [
        `Execution mode: ${mode}`,
        `Output format: ${format}`,
        `Tone: ${tone}`,
        `Depth: ${depth}`,
        `Use shared memory: ${useMemory ? 'yes' : 'no'}`,
        `Prefer web research when useful: ${preferSearch ? 'yes' : 'no'}`,
      ].join('\n')
      onSubmit(`${trimmed}\n\nUser-selected options:\n${optionBlock}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-6xl">
      <div className="depth-card overflow-hidden rounded-[22px] border border-white/10 bg-[#101013]/82 shadow-2xl shadow-black/40 backdrop-blur-xl">
        <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="p-4 md:p-5">
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-[#a1a1aa]">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">
                <Sparkles className="h-3.5 w-3.5 text-indigo-300" />
                Live multi-agent run
              </span>
              <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-emerald-200">
                Memory enabled
              </span>
            </div>
            <textarea
              value={task}
              onChange={(event) => setTask(event.target.value)}
              disabled={disabled}
              rows={4}
              maxLength={2000}
              placeholder="Give Agent OS a complex task..."
              className="min-h-36 w-full resize-none rounded-2xl border border-white/10 bg-black/45 p-5 text-base leading-7 text-white outline-none transition placeholder:text-[#666666] focus:border-indigo-300/70 focus:bg-black/60 focus:shadow-[0_0_0_4px_rgba(99,102,241,0.12)] disabled:cursor-not-allowed disabled:opacity-60"
            />
            <div className="mt-4 flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
              <div className="flex flex-wrap gap-2">
                {examples.map((example) => (
                  <button
                    key={example}
                    type="button"
                    disabled={disabled}
                    onClick={() => setTask(example)}
                    className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-[#b4b4bd] transition hover:-translate-y-0.5 hover:border-indigo-300/60 hover:bg-indigo-400/10 hover:text-white disabled:opacity-60"
                  >
                    {example}
                  </button>
                ))}
              </div>
              <button
                type="submit"
                disabled={disabled || !task.trim()}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-black shadow-[0_18px_50px_rgba(99,102,241,0.24)] transition hover:-translate-y-0.5 hover:bg-indigo-100 disabled:cursor-not-allowed disabled:bg-[#222222] disabled:text-[#888888]"
              >
                {disabled ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                {disabled ? 'Agents running' : 'Launch agents'}
              </button>
            </div>
          </div>

          <div className="border-t border-white/10 bg-white/[0.035] p-4 lg:border-l lg:border-t-0">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
              <SlidersHorizontal className="h-4 w-4 text-indigo-300" />
              Run Options
            </div>
            <div className="grid gap-3">
              <OptionGroup icon={<BrainCircuit className="h-4 w-4" />} label="Mode" values={modes} selected={mode} onSelect={setMode} disabled={disabled} />
              <OptionGroup icon={<FileText className="h-4 w-4" />} label="Format" values={formats} selected={format} onSelect={setFormat} disabled={disabled} />
              <OptionGroup icon={<Gauge className="h-4 w-4" />} label="Tone" values={tones} selected={tone} onSelect={setTone} disabled={disabled} />
              <OptionGroup icon={<Layers3 className="h-4 w-4" />} label="Depth" values={depths} selected={depth} onSelect={setDepth} disabled={disabled} />
            </div>

            <div className="mt-4 grid gap-2">
              <ToggleOption icon={<Globe2 className="h-4 w-4" />} label="Use shared memory" checked={useMemory} onChange={setUseMemory} disabled={disabled} />
              <ToggleOption icon={<Search className="h-4 w-4" />} label="Prefer web research" checked={preferSearch} onChange={setPreferSearch} disabled={disabled} />
            </div>

          </div>
        </div>
      </div>
    </form>
  )
}

interface OptionGroupProps {
  icon: ReactNode
  label: string
  values: string[]
  selected: string
  disabled: boolean
  onSelect: (value: string) => void
}

function OptionGroup({ icon, label, values, selected, disabled, onSelect }: OptionGroupProps) {
  return (
    <div>
      <div className="mb-1.5 flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.18em] text-[#8b8b95]">
        {icon}
        {label}
      </div>
      <div className="flex flex-wrap gap-2">
        {values.map((value) => (
          <button
            key={value}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(value)}
            className={`rounded-full border px-3 py-1.5 text-[11px] transition ${
              selected === value
                ? 'border-indigo-300/60 bg-indigo-300/15 text-white shadow-[0_0_26px_rgba(99,102,241,0.18)]'
                : 'border-white/10 bg-black/25 text-[#9b9ba4] hover:border-white/25 hover:text-white'
            } disabled:opacity-50`}
          >
            {value}
          </button>
        ))}
      </div>
    </div>
  )
}

interface ToggleOptionProps {
  icon: ReactNode
  label: string
  checked: boolean
  disabled: boolean
  onChange: (value: boolean) => void
}

function ToggleOption({ icon, label, checked, disabled, onChange }: ToggleOptionProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/25 px-3 py-2.5 text-sm text-white transition hover:border-white/25 disabled:opacity-50"
    >
      <span className="inline-flex items-center gap-2 text-[#d6d6dd]">
        <span className="text-indigo-300">{icon}</span>
        {label}
      </span>
      <span className={`relative h-6 w-11 rounded-full transition ${checked ? 'bg-indigo-400' : 'bg-[#2b2b31]'}`}>
        <span className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${checked ? 'left-6' : 'left-1'}`} />
      </span>
    </button>
  )
}
