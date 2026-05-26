# O.R.I.O.N — Agentes

Este repositório contém os agentes do **O.R.I.O.N**, um fork personalizado do OpenCode.

## Agentes Disponíveis

### 🤖 O.R.I.O.N (orion.md)
Agente principal com personalidade de assistente pessoal — tipo Jarvis em português brasileiro.
- Trata o usuário como "Senhor"
- Modos: seco, normal, discord, dev
- Banner ASCII ORION na inicialização
- Comandos de memória (memorize/lembre)

### 🔄 Triage (triage.md)
Agente para triagem de issues no GitHub.

### 🔁 Duplicate PR (duplicate-pr.md)
Agente para detecção de PRs duplicadas.

## Como usar

OS agentes são descobertos automaticamente pela presença na pasta `.opencode/agent/`. Basta iniciar o opencode no diretório do projeto.

## Criar um agente novo

1. Crie um arquivo `.md` em `.opencode/agent/`
2. Adicione o frontmatter YAML:
   ```yaml
   ---
   mode: primary
   model: opencode/gpt-5.4-nano
   color: "#HEXCOLOR"
   tools:
     "*": true
   ---
   ```
3. Escreva o prompt do agente em markdown
4. Pronto! O opencode descobre automaticamente
