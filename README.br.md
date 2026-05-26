<p align="center">
  <pre>
  █████╗      ██████╗      ██╗           █████╗      ███╗   ██╗
 ██╔══██╗     ██╔══██╗     ██║          ██╔══██╗     ████╗  ██║
 ██║  ██║     ██████╔╝     ██║          ██║  ██║     ██╔██╗ ██║
 ██║  ██║     ██╔══██╗     ██║          ██║  ██║     ██║╚██╗██║
 ╚█████╔╝     ██║  ██║     ██║          ╚█████╔╝     ██║ ╚████║
  ╚════╝      ╚═╝  ╚═╝     ╚═╝           ╚════╝      ╚═╝  ╚═══╝
  </pre>
</p>

<p align="center">
  <strong>O.R.I.O.N</strong> — <em>Organized Responsive Intelligent Operational Navigator</em>
</p>

<p align="center">
  Seu assistente de código com personalidade. Baseado no OpenCode, turbinado com atitude.
</p>

<br>

<p align="center">
  <a href="#-sobre">Sobre</a> •
  <a href="#-agentes">Agentes</a> •
  <a href="#-temas">Temas</a> •
  <a href="#-comandos">Comandos</a> •
  <a href="#-personalização">Personalização</a> •
  <a href="README.md">English 🇺🇸</a>
</p>

---

## 🚀 Instalação (uma linha)

```bash
curl -fsSL https://raw.githubusercontent.com/theOFgusta-mod/Orion-agent-/main/scripts/install.sh | bash
```

Depois é só digitar no terminal:

```bash
orion
```

Para atualizar depois:

```bash
orion update
```

### Manual

```bash
git clone https://github.com/theOFgusta-mod/Orion-agent-.git
cd Orion-agent-
bun install
cd packages/opencode
bun run --conditions=browser src/index.ts
```

> **Pré-requisitos:** Git, [Bun](https://bun.sh) ≥ 1.3.14

---

## ⚡ Sobre

**O.R.I.O.N** é um fork do [OpenCode](https://opencode.ai) com personalidade própria. Um agente de IA pra rodar no terminal, mas com a cara do dono.

- 🧠 **Pensa como assistente pessoal** — não é robô genérico, é o Jarvis no seu terminal
- 🗣️ **Fala português brasileiro** — "Senhor" é o tratamento padrão, modos especiais inclusos
- 🎨 **Vem com tema exclusivo** — visual escuro azul-ciano-roxo criado do zero
- 🚀 **É seu** — fork pessoal, 100% modificável, sem frescura

---

## 🤖 Agentes

O agente **O.R.I.O.N** já vem incluso. É só usar:

```bash
# Os agentes ficam em .opencode/agent/
# O opencode descobre eles automaticamente
```

| Agente | Descrição |
|--------|-----------|
| `orion` | 🔥 Agente principal — personalidade Jarvis em português brasileiro |
| `triage` | Classificação de issues no GitHub |
| `duplicate-pr` | Detecta PRs duplicadas |

---

## 🎨 Temas

| Tema | Descrição |
|------|-----------|
| `catppuccin-latte` | 🧁 Tema claro quente: bege, lavanda, rosa e detalhes em azul |
| `catppuccin` | 🐱 Tema escuro roxo: ciano, rosa e azul |
| `orion` | 🔵 Tema escuro tech: azul elétrico, ciano, roxo e dourado |

### Ativar o tema O.R.I.O.N

Edite `~/.config/opencode/tui.json`:

```json
{
  "theme": "orion"
}
```

---

## 🎮 Comandos

| Comando | Função |
|---------|--------|
| `commit` | Mensagens de commit inteligentes |
| `translate` | Tradução de código/comentários |
| `issues` | Gerenciar issues |
| `learn` | Aprendizado guiado |
| `changelog` | Gerar changelog |
| `spellcheck` | Corrigir ortografia |
| `rmslop` | Remover código morto |
| `ai-deps` | Gerenciar dependências |

---

## 🔧 Personalização

Tudo é aberto pra mexer:

- **`~/.opencode/agent/orion.md`** — Personalidade e comportamento do agente
- **`~/.opencode/themes/orion.json`** — Cores do tema
- **`~/.opencode/command/`** — Crie seus próprios comandos

Quer mudar o tom do agente? Edita o `orion.md`. Quer outras cores? Edita o `orion.json`. Simples assim.

---

## 📜 Licença

Baseado no [OpenCode](https://github.com/anomalyco/opencode) — licença original mantida.
