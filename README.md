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
  O assistente de código com personalidade. Baseado no OpenCode, turbinado com atitude.
</p>

<br>

<p align="center">
  <a href="#-sobre">Sobre</a> •
  <a href="#-agentes">Agentes</a> •
  <a href="#-temas">Temas</a> •
  <a href="#-comandos">Comandos</a> •
  <a href="#-personalização">Personalização</a> •
  <a href="README.br.md">Português 🇧🇷</a>
</p>

---

## ⚡ Sobre

**O.R.I.O.N** é um fork do [OpenCode](https://opencode.ai) com personalidade própria. Um agente de IA para terminal que:

- 🧠 **Pensa como assistente pessoal** — não é só um chat, é o Jarvis no seu terminal
- 🗣️ **Fala português brasileiro** — "Senhor" pra cá, "modo seco" pra lá
- 🎨 **Vem com tema exclusivo** — visual escuro azul-ciano-roxo
- 🚀 **É seu** — fork pessoal, modificável, sem amarras

---

## 🤖 Agentes

Este fork inclui o agente **O.R.I.O.N** pronto pra usar:

```bash
# O agente descobre automaticamente na pasta .opencode/agent/
# É só iniciar o opencode no diretório do projeto
```

| Agente | Descrição |
|--------|-----------|
| `orion` | Agente principal com personalidade Jarvis-like em PT-BR |
| `triage` | Triage de issues GitHub |
| `duplicate-pr` | Detecção de PRs duplicadas |

---

## 🎨 Temas

| Tema | Descrição |
|------|-----------|
| `orion` | 🔵 Tema escuro tech: azul elétrico, ciano, roxo, dourado |
| `smoke-theme` | Padrão do OpenCode |

### Ativar o tema O.R.I.O.N

Edite `~/.config/opencode/tui.json`:

```json
{
  "theme": "orion"
}
```

---

## 🎮 Comandos

Comandos disponíveis no `.opencode/command/`:

| Comando | Função |
|---------|--------|
| `commit` | Gera mensagens de commit |
| `translate` | Traduz código/comentários |
| `issues` | Gerencia issues |
| `learn` | Aprendizado guiado |
| `changelog` | Gera changelog |
| `spellcheck` | Corrige ortografia |
| `rmslop` | Remove código morto |
| `ai-deps` | Gerencia dependências |

---

## 🔧 Personalização

Quer mudar algo? É só mexer:

- **`~/.opencode/agent/orion.md`** — Personalidade e comportamento do agente
- **`~/.opencode/themes/orion.json`** — Cores do tema
- **`~/.opencode/command/`** — Crie seus próprios comandos

---

## 📜 Licença

Baseado no [OpenCode](https://github.com/anomalyco/opencode) — licença original mantida.
