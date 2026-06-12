'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Clipboard, ClipboardCheck, FileCheck2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { TaskResult } from '@/types'

interface OutputPanelProps {
  result: TaskResult | null
  finalOutput: string
}

export function OutputPanel({ result, finalOutput }: OutputPanelProps) {
  const [copied, setCopied] = useState(false)
  const output = finalOutput || result?.final_output || ''

  async function copyOutput() {
    await navigator.clipboard.writeText(output)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1200)
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 12, rotateX: -5 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ type: 'spring', stiffness: 240, damping: 24 }}
      className="depth-card min-h-96 overflow-hidden rounded-[22px] border border-white/10 bg-[#111114]/86 shadow-2xl shadow-black/35 backdrop-blur-xl"
    >
      <div className="flex items-center justify-between gap-3 border-b border-white/10 p-5">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck2 className="h-5 w-5 text-indigo-300" />
            <h2 className="text-lg font-semibold text-white">Final Output</h2>
          </div>
          {result?.critique?.score ? (
            <p className="mt-1 text-sm text-green-300">Score: {result.critique.score}/10</p>
          ) : (
            <p className="mt-1 text-sm text-[#9a9aa3]">Waiting for critic review.</p>
          )}
        </div>
        <button
          type="button"
          onClick={copyOutput}
          disabled={!output}
          className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] text-[#b8b8c3] transition hover:-translate-y-0.5 hover:border-indigo-300/60 hover:text-white disabled:opacity-40"
          aria-label="Copy final output"
        >
          {copied ? <ClipboardCheck className="h-4 w-4" /> : <Clipboard className="h-4 w-4" />}
        </button>
      </div>
      <div className="prose prose-invert max-w-none p-5 prose-pre:rounded-2xl prose-pre:border prose-pre:border-white/10 prose-pre:bg-black/70">
        {output ? (
          <ReactMarkdown>{output}</ReactMarkdown>
        ) : (
          <div className="grid min-h-72 place-items-center rounded-2xl border border-dashed border-white/15 bg-black/20 p-8 text-center">
            <div>
              <Sparkles className="mx-auto h-8 w-8 text-indigo-300" />
              <p className="mt-4 text-[#9a9aa3]">Final output will appear here after the critic finishes.</p>
            </div>
          </div>
        )}
      </div>
      {result ? (
        <div className="space-y-3 border-t border-white/10 p-5">
          <details className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <summary className="cursor-pointer text-sm font-semibold text-white">Issues Found</summary>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm leading-6 text-[#a5a5ae]">
              {(result.critique?.issues ?? []).map((issue) => <li key={issue}>{issue}</li>)}
            </ul>
          </details>
          <details className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <summary className="cursor-pointer text-sm font-semibold text-white">Improvements Made</summary>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm leading-6 text-[#a5a5ae]">
              {(result.critique?.improvements_made ?? []).map((item) => <li key={item}>{item}</li>)}
            </ul>
          </details>
          <details className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <summary className="cursor-pointer text-sm font-semibold text-white">Memory Used</summary>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-[#a5a5ae]">{result.memory_context}</p>
          </details>
        </div>
      ) : null}
    </motion.section>
  )
}
