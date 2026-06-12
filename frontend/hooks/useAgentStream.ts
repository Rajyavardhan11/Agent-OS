'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { AgentLog, RouterDecision, TaskResult } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

export function useAgentStream() {
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([])
  const [finalOutput, setFinalOutput] = useState('')
  const [taskResult, setTaskResult] = useState<TaskResult | null>(null)
  const [routerDecision, setRouterDecision] = useState<RouterDecision | undefined>()
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sourceRef = useRef<EventSource | null>(null)

  const stop = useCallback(() => {
    sourceRef.current?.close()
    sourceRef.current = null
    setIsStreaming(false)
  }, [])

  const start = useCallback(
    (taskId: string, task: string) => {
      stop()
      setAgentLogs([])
      setFinalOutput('')
      setTaskResult(null)
      setRouterDecision(undefined)
      setError(null)
      setIsStreaming(true)

      const params = new URLSearchParams({ task })
      const source = new EventSource(`${API_BASE}/api/task/${taskId}/stream?${params}`)
      sourceRef.current = source

      source.addEventListener('agent', (event) => {
        const log = JSON.parse((event as MessageEvent).data) as AgentLog
        if (log.agent === 'router' && log.output) {
          try {
            setRouterDecision(JSON.parse(log.output) as RouterDecision)
          } catch {
            setRouterDecision(undefined)
          }
        }
        setAgentLogs((current) => {
          const index = current.findIndex((item) => item.agent === log.agent)
          if (index === -1) {
            return [...current, log]
          }
          return current.map((item, itemIndex) => (itemIndex === index ? log : item))
        })
      })

      source.addEventListener('done', (event) => {
        const payload = JSON.parse((event as MessageEvent).data) as {
          final_output: string
          state: TaskResult
        }
        setFinalOutput(payload.final_output)
        setTaskResult(payload.state)
        setRouterDecision(payload.state.router_decision)
        setAgentLogs(payload.state.agent_logs ?? [])
        stop()
      })

      source.onerror = () => {
        setError('The live stream disconnected. Check that the backend is running.')
        stop()
      }
    },
    [stop],
  )

  useEffect(() => stop, [stop])

  return { agentLogs, finalOutput, taskResult, routerDecision, isStreaming, error, start, stop }
}
