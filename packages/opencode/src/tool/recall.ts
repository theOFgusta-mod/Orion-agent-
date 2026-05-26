import { Effect, Schema } from "effect"
import * as Tool from "./tool"
import { Memory } from "../memory/memory"

const Parameters = Schema.Struct({
  query: Schema.String.annotate({
    description: "O que procurar — pode ser uma chave exata ou um termo de busca",
  }),
  scope: Schema.optional(
    Schema.String.annotate({
      description: "Escopo da busca (global, project, session)",
    }),
  ),
  category: Schema.optional(
    Schema.String.annotate({
      description: "Filtrar por categoria",
    }),
  ),
})

type Metadata = {
  query: string
  matches: number
}

export const RecallTool = Tool.define<typeof Parameters, Metadata, Memory.Service>(
  "recall",
  Effect.gen(function* () {
    const memory = yield* Memory.Service

    return {
      description: `Recupera informações da memória persistente do O.R.I.O.N.
Use esta ferramenta quando o usuário disser "lembre" ou "O.R.I.O.N, lembre" seguido de algo que eu possa ter memorizado antes.
Busca primeiro por chave exata, depois por conteúdo aproximado.
Retorna todas as correspondências encontradas.`,
      parameters: Parameters,
      execute: (params: Schema.Schema.Type<typeof Parameters>, ctx: Tool.Context<Metadata>) =>
        Effect.gen(function* () {
          // Try exact key match first
          const exact = yield* memory.recall(params.query, params.scope)

          if (exact) {
            return {
              title: `🔍 Lembrei: ${params.query}`,
              output: `Aqui está o que eu lembro:\n\n📌 **${exact.key}**: ${exact.value}\n   Categoria: ${exact.category}\n   Atualizado em: ${new Date(exact.timeUpdated).toLocaleString("pt-BR")}`,
              metadata: { query: params.query, matches: 1 },
            }
          }

          // Search by content
          const results = yield* memory.search({
            query: params.query,
            scope: params.scope,
            category: params.category,
            limit: 10,
          })

          if (results.length === 0) {
            return {
              title: `❓ Não encontrei: ${params.query}`,
              output: `Não encontrei nada sobre "${params.query}" na minha memória. Quer me contar para eu memorizar?`,
              metadata: { query: params.query, matches: 0 },
            }
          }

          const lines = results.map(
            (r, i) =>
              `${i + 1}. 📌 **${r.key}**: ${r.value}\n   Categoria: ${r.category} | Atualizado: ${new Date(r.timeUpdated).toLocaleString("pt-BR")}`,
          )

          return {
            title: `🔍 Encontrei ${results.length} resultado(s)`,
            output: `Aqui está o que eu lembro sobre "${params.query}":\n\n${lines.join("\n\n")}`,
            metadata: { query: params.query, matches: results.length },
          }
        }),
    } satisfies Tool.DefWithoutID<typeof Parameters, Metadata>
  }),
)
