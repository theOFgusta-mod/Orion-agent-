import { Effect, Schema } from "effect"
import * as Tool from "./tool"
import { Memory } from "../memory/memory"

const Parameters = Schema.Struct({
  key: Schema.String.annotate({
    description: "Nome da informação (ex: 'cor_preferida', 'projeto_atual', 'modo_preferido')",
  }),
  value: Schema.String.annotate({
    description: "O conteúdo/valor que o O.R.I.O.N deve lembrar",
  }),
  category: Schema.optional(
    Schema.String.annotate({
      description: "Categoria da memória: general, user_preference, project, system, behavior",
    }),
  ),
})

type Metadata = {
  key: string
  category: string
}

export const MemorizeTool = Tool.define<typeof Parameters, Metadata, Memory.Service>(
  "memorize",
  Effect.gen(function* () {
    const memory = yield* Memory.Service

    return {
      description: `Grava uma informação na memória persistente do O.R.I.O.N.
Use esta ferramenta quando o usuário disser "memorize" ou "O.R.I.O.N, memorize" seguido de algo que deve ser lembrado permanentemente.
Armazena pares chave-valor que podem ser recuperados depois com a ferramenta "recall".
Exemplos: cor preferida, nome do usuário, configurações, preferências, fatos importantes.`,
      parameters: Parameters,
      execute: (params: Schema.Schema.Type<typeof Parameters>, ctx: Tool.Context<Metadata>) =>
        Effect.gen(function* () {
          const entry = yield* memory.remember({
            key: params.key,
            value: params.value,
            category: params.category ?? "general",
          })

          return {
            title: `🧠 Memorizado: ${params.key}`,
            output: `Memorizado com sucesso! 🔖\n\nChave: ${params.key}\nValor: ${params.value}\nCategoria: ${entry.category}\n\nAgora eu sei disso e não vou esquecer.`,
            metadata: {
              key: params.key,
              category: entry.category,
            },
          }
        }),
    } satisfies Tool.DefWithoutID<typeof Parameters, Metadata>
  }),
)
