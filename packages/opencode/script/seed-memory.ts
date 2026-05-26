#!/usr/bin/env bun
/**
 * Seed script — migra ~/memoria.md para o banco SQLite do O.R.I.O.N.
 *
 * Uso: bun run script/seed-memory.ts
 *
 * Lê o arquivo de memórias antigo (~/memoria.md), extrai seções e pares
 * chave-valor, e insere na tabela `agent_memory` via Drizzle ORM.
 */

import { readFileSync, existsSync } from "fs"
import { homedir } from "os"
import path from "path"
import { Client } from "../src/storage/db"
import { AgentMemoryTable } from "../src/memory/memory.sql"
import { eq, and } from "drizzle-orm"

const MEMORIA_PATH = path.join(homedir(), "memoria.md")

// ---- Parsers ----

type Entry = {
  key: string
  value: string
  category: string
  scope: string
}

function parseMemoriaFile(content: string): Entry[] {
  const entries: Entry[] = []
  const lines = content.split("\n")

  let currentSection = "general"
  let currentSub = ""

  for (const raw of lines) {
    const line = raw.trimEnd()

    // Headers (## Section) — define categoria
    const sectionMatch = line.match(/^##\s+(.+)/)
    if (sectionMatch) {
      currentSection = slugify(sectionMatch[1])
      currentSub = ""
      continue
    }

    // Sub-headers (### Sub) — opcional
    const subMatch = line.match(/^###\s+(.+)/)
    if (subMatch) {
      currentSub = slugify(subMatch[1])
      continue
    }

    // Linhas de lista (- chave: valor)
    const listMatch = line.match(/^-\s+\*\*(.+?)\*\*:\s*(.+)/)
    if (listMatch) {
      entries.push({
        key: slugify(currentSub ? `${currentSub}_${listMatch[1]}` : listMatch[1]),
        value: listMatch[2].trim(),
        category: currentSection,
        scope: currentSub || "global",
      })
      continue
    }

    // Linhas de lista simples (- texto: valor)
    const simpleMatch = line.match(/^-\s+(.+?):\s+(.+)/)
    if (simpleMatch) {
      entries.push({
        key: slugify(simpleMatch[1]),
        value: simpleMatch[2].trim(),
        category: currentSection,
        scope: currentSub || "global",
      })
      continue
    }

    // Bloco de código (ignorar)
    if (line.startsWith("```")) continue
  }

  return entries
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9áàâãéêíóôõúç_\-]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .replace(/_+/g, "_")
}

// ---- Database seed ----

function seed(entries: Entry[]) {
  const db = Client()
  let inserted = 0
  let updated = 0

  for (const entry of entries) {
    const existing = db
      .select()
      .from(AgentMemoryTable)
      .where(and(eq(AgentMemoryTable.key, entry.key), eq(AgentMemoryTable.scope, entry.scope)))
      .get()

    if (existing) {
      db.update(AgentMemoryTable)
        .set({ value: entry.value, category: entry.category, time_updated: Date.now() })
        .where(eq(AgentMemoryTable.id, existing.id))
        .run()
      updated++
    } else {
      db.insert(AgentMemoryTable)
        .values({
          key: entry.key,
          value: entry.value,
          scope: entry.scope,
          agent_id: "orion",
          category: entry.category,
        })
        .run()
      inserted++
    }
  }

  console.log(`\n✅ Seed concluído!`)
  console.log(`   📥 Inseridos: ${inserted}`)
  console.log(`   📝 Atualizados: ${updated}`)
  console.log(`   📊 Total: ${entries.length} entradas processadas`)
}

// ---- Main ----

function main() {
  console.log("🧠 O.R.I.O.N — Seed de Memórias")
  console.log(`   Arquivo: ${MEMORIA_PATH}`)
  console.log("")

  if (!existsSync(MEMORIA_PATH)) {
    console.error(`❌ Arquivo não encontrado: ${MEMORIA_PATH}`)
    console.error("   Crie ~/memoria.md ou especifique outro caminho.")
    process.exit(1)
  }

  const content = readFileSync(MEMORIA_PATH, "utf-8")
  const entries = parseMemoriaFile(content)

  if (entries.length === 0) {
    console.error("❌ Nenhuma entrada encontrada no arquivo de memórias.")
    process.exit(1)
  }

  console.log(`   📖 ${entries.length} entradas identificadas`)
  seed(entries)
}

main()
