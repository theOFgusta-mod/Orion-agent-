import { sqliteTable, text, integer, index } from "drizzle-orm/sqlite-core"
import { Timestamps } from "../storage/schema.sql"

/**
 * Agent memory store — key-value persistence with metadata.
 * Allows the O.R.I.O.N agent to remember facts across sessions.
 */
export const AgentMemoryTable = sqliteTable(
  "agent_memory",
  {
    id: integer().primaryKey({ autoIncrement: true }),
    key: text().notNull(),
    value: text().notNull(),
    scope: text().notNull().default("global"),
    agent_id: text().notNull().default("orion"),
    category: text().default("general"),
    ...Timestamps,
  },
  (table) => [
    index("memory_key_idx").on(table.key),
    index("memory_scope_idx").on(table.scope),
    index("memory_agent_idx").on(table.agent_id),
    index("memory_category_idx").on(table.category),
  ],
)
