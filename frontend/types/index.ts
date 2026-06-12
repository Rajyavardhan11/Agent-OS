export interface AgentLog {
  agent: string
  status: 'waiting' | 'running' | 'done' | 'error'
  output: string
  timestamp: string
}

export interface RouterDecision {
  task_type: string
  complexity: string
  agents_needed: string[]
  execution_order: string[][]
  reasoning: string
}

export interface Critique {
  score: number
  issues: string[]
  improvements_made: string[]
  improved_output?: string
}

export interface TaskResult {
  task_id: string
  original_task: string
  final_output: string
  agent_logs: AgentLog[]
  router_decision: RouterDecision
  critique: Critique
  memory_context?: string
}

export interface MemoryItem {
  task_id: string
  task: string
  content: string
  score?: number
  timestamp: string
}

