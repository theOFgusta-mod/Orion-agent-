import { Effect, Context, Layer } from "effect"
import { eq, like, or, and, desc } from "drizzle-orm"
import { Client } from "../storage/db"
import { AgentMemoryTable } from "./memory.sql"

// ---- Data types ----

export interface MemoryEntry {
  id: number
  key: string
  value: string
  scope: string
  agentId: string
  category: string
  timeCreated: number
  timeUpdated: number
}

export interface CreateMemoryInput {
  key: string
  value: string
  scope?: string
  agentId?: string
  category?: string
}

export interface SearchMemoryInput {
  query?: string
  scope?: string
  agentId?: string
  category?: string
  limit?: number
}

// ---- Service Interface ----

export interface Interface {
  /** Store a fact in memory (upserts by key+scope) */
  readonly remember: (input: CreateMemoryInput) => Effect.Effect<MemoryEntry>

  /** Retrieve a specific fact by key */
  readonly recall: (key: string, scope?: string) => Effect.Effect<MemoryEntry | null>

  /** Search memory by content (full-text LIKE on key and value) */
  readonly search: (input: SearchMemoryInput) => Effect.Effect<MemoryEntry[]>

  /** List all memory entries for a scope/agent */
  readonly list: (scope?: string, agentId?: string) => Effect.Effect<MemoryEntry[]>

  /** Remove a specific fact */
  readonly forget: (key: string, scope?: string) => Effect.Effect<void>

  /** Clear all memories (for a scope or everything) */
  readonly clear: (scope?: string) => Effect.Effect<void>

  /** Get all memories formatted as a context string for the agent prompt */
  readonly formatContext: (scope?: string, agentId?: string) => Effect.Effect<string>
}

// ---- Service Implementation ----

export class Service extends Context.Service<Service, Interface>()("@opencode/Memory") {}

const make = Effect.gen(function* () {
  const db = () => Client()

  const toEntry = (row: typeof AgentMemoryTable.$inferSelect): MemoryEntry => ({
    id: row.id,
    key: row.key,
    value: row.value,
    scope: row.scope,
    agentId: row.agent_id,
    category: row.category ?? "general",
    timeCreated: row.time_created,
    timeUpdated: row.time_updated,
  })

  const remember = (input: CreateMemoryInput): Effect.Effect<MemoryEntry> =>
    Effect.gen(function* () {
      const scope = input.scope ?? "global"
      const agentId = input.agentId ?? "orion"
      const category = input.category ?? "general"

      // Check if entry exists (upsert)
      const existing = Effect.sync(() =>
        db()
          .select()
          .from(AgentMemoryTable)
          .where(and(eq(AgentMemoryTable.key, input.key), eq(AgentMemoryTable.scope, scope)))
          .get(),
      )

      if (yield* existing) {
        const updated = yield* Effect.sync(() =>
          db()
            .update(AgentMemoryTable)
            .set({ value: input.value, category, time_updated: Date.now() })
            .where(and(eq(AgentMemoryTable.key, input.key), eq(AgentMemoryTable.scope, scope)))
            .returning()
            .get()!,
        )
        return toEntry(updated)
      }

      const inserted = yield* Effect.sync(() =>
        db()
          .insert(AgentMemoryTable)
          .values({ key: input.key, value: input.value, scope, agent_id: agentId, category })
          .returning()
          .get()!,
      )
      return toEntry(inserted)
    })

  const recall = (key: string, scope?: string): Effect.Effect<MemoryEntry | null> =>
    Effect.gen(function* () {
      const conditions = [eq(AgentMemoryTable.key, key)]
      if (scope) conditions.push(eq(AgentMemoryTable.scope, scope))
      const result = yield* Effect.sync(() =>
        db().select().from(AgentMemoryTable).where(and(...conditions)).get(),
      )
      return result ? toEntry(result) : null
    })

  const search = (input: SearchMemoryInput): Effect.Effect<MemoryEntry[]> =>
    Effect.gen(function* () {
      const conditions: any[] = []
      if (input.query) {
        const pattern = `%${input.query}%`
        conditions.push(or(like(AgentMemoryTable.key, pattern), like(AgentMemoryTable.value, pattern)))
      }
      if (input.scope) conditions.push(eq(AgentMemoryTable.scope, input.scope))
      if (input.agentId) conditions.push(eq(AgentMemoryTable.agent_id, input.agentId))
      if (input.category) conditions.push(eq(AgentMemoryTable.category, input.category))

      const limit = input.limit ?? 50
      const results = yield* Effect.sync(() =>
        db()
          .select()
          .from(AgentMemoryTable)
          .where(conditions.length > 0 ? and(...conditions) : undefined)
          .orderBy(desc(AgentMemoryTable.time_updated))
          .limit(limit)
          .all(),
      )
      return results.map(toEntry)
    })

  const list = (scope?: string, agentId?: string): Effect.Effect<MemoryEntry[]> =>
    Effect.gen(function* () {
      const conditions: any[] = []
      if (scope) conditions.push(eq(AgentMemoryTable.scope, scope))
      if (agentId) conditions.push(eq(AgentMemoryTable.agent_id, agentId))
      const results = yield* Effect.sync(() =>
        db()
          .select()
          .from(AgentMemoryTable)
          .where(conditions.length > 0 ? and(...conditions) : undefined)
          .orderBy(desc(AgentMemoryTable.time_updated))
          .all(),
      )
      return results.map(toEntry)
    })

  const forget = (key: string, scope?: string): Effect.Effect<void> =>
    Effect.sync(() => {
      const conditions = [eq(AgentMemoryTable.key, key)]
      if (scope) conditions.push(eq(AgentMemoryTable.scope, scope))
      db().delete(AgentMemoryTable).where(and(...conditions)).run()
    })

  const clear = (scope?: string): Effect.Effect<void> =>
    Effect.sync(() => {
      if (scope) {
        db().delete(AgentMemoryTable).where(eq(AgentMemoryTable.scope, scope)).run()
      } else {
        db().delete(AgentMemoryTable).run()
      }
    })

  const formatContext = (scope?: string, agentId?: string): Effect.Effect<string> =>
    Effect.gen(function* () {
      const entries = yield* list(scope, agentId)
      if (entries.length === 0) return ""
      const lines = entries.map(
        (e) => `- **${e.key}**: ${e.value}  [${e.category}]`,
      )
      return `## 🧠 Memórias do O.R.I.O.N\n\n${lines.join("\n")}`
    })

  return {
    remember, recall, search, list, forget, clear, formatContext,
  } satisfies Interface
})

export const layer = Layer.effect(Service, make)

export const defaultLayer = layer

export * as Memory from "./memory"
