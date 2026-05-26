# 🤖 O.R.I.O.N 3.0 — Beta

> Assistente pessoal multi-plataforma com memória persistente e IA.
> "Organized Responsive Intelligent Operational Navigator"
>
> 🧪 **Beta** — WhatsApp e Telegram estão em desenvolvimento.
> Eles funcionam, mas ainda podem ter mudanças na API.
>
> ✅ **E-mail** — Funcional! Leia e responda e-mails com IA.

---

## ✨ Funcionalidades

### 🧠 Memória Persistente
- Banco **SQLite** local com auto-aprendizado
- Categorias: `user_preference`, `system`, `conversation`, `memory`
- Comandos: memorizar, lembrar, esquecer, listar, limpar
- Memorização automática: nomes, preferências, sistemas

### 🤖 IA Integrada
- **Gemini 2.0 Flash** (padrão, grátis)
- **OpenAI GPT-4o** (alternativo)
- Prompt de sistema personalizável por plataforma
- Contexto enriquecido com memórias relevantes

### 📱 Telegram Bridge 🧪
- Bot interativo com comandos `/start`, `/help`, `/memoria`, `/status`, `/spotify`
- Teclado inline com atalhos
- Suporte a Markdown nas respostas
- ⚠️ Em desenvolvimento — pode ter mudanças

### 💬 WhatsApp Bridge 🧪
- Baseado em `whatsapp-web.js` + Node.js
- QR Code para autenticação
- Sessão persistente (não precisa escanear toda vez)
- API HTTP local para comunicação Python ↔ Node
- ⚠️ Em desenvolvimento — pode ter mudanças

### 📧 E-mail Bridge ✅
- Leitura de e-mails via **IMAP** (Gmail, Outlook, qualquer servidor)
- Envio de e-mails via **SMTP** com suporte a TLS
- Polling automático de e-mails não lidos
- Resposta automática com **IA** (opcional)
- Comandos: `ver e-mails`, `enviar e-mail para [email]: [msg]`, `responder [nome]: [msg]`
- Suporte a **App Password** do Google

### 🎵 Spotify Controller
- Autenticação OAuth com cache
- Comandos: tocar, pausar, pular, volume, fila
- Barra de progresso visual
- Recomendações por gênero
- Busca inteligente de músicas

### ⚡ CLI Interativa
- Modo terminal completo (fallback quando sem bridges)
- Comandos de memória, sistema, ajuda
- Experiência completa sem depender de APIs externas

---

## 📦 Instalação

**One-line:**
```bash
curl -fsSL https://github.com/theOFgusta-mod/Orion-agent-/raw/refs/heads/main/orion-beta/install.sh | bash
```

**Manual:**
```bash
git clone https://github.com/theOFgusta-mod/Orion-agent-.git
cd Orion-agent-/orion-beta
pip install -r requirements.txt
cp config/config.yaml config/config.yaml  # edite com suas chaves
python main.py
```

---

## ⚙️ Configuração

Edite `config/config.yaml`:

```yaml
orion:
  nome: "O.R.I.O.N Beta"
  dono: "Gustavo"
  lingua: "pt-BR"
  versao: "3.0.0-beta"

ia:
  provedor: "gemini"  # gemini | openai
  gemini:
    api_key: ""        # Sua chave do Gemini
    modelo: "gemini-2.0-flash"
  openai:
    api_key: ""        # Sua chave da OpenAI
    modelo: "gpt-4o"

plataformas:
  telegram:
    enabled: false     # EM DESENVOLVIMENTO
    token: ""          # Token do BotFather
    admins: []
  whatsapp:
    enabled: false     # EM DESENVOLVIMENTO — Requer Node.js
    webhook_port: 8888
    session_dir: "sessions/whatsapp"
  email:
    enabled: false     # Mude para true após configurar
    user: ""           # Seu e-mail (ex: seu@gmail.com)
    password: ""       # Senha de App (16 dígitos) ou senha normal
    imap_host: "imap.gmail.com"
    smtp_host: "smtp.gmail.com"
    poll_interval: 60  # Segundos entre verificações
    auto_reply: false  # Responder automaticamente com IA?
    max_emails: 5
    default_subject: "Mensagem do O.R.I.O.N Beta"
  spotify:
    enabled: false
    client_id: ""      # Spotify Developer ID
    client_secret: ""
    redirect_uri: "http://localhost:8888/callback"
```

---

## 🚀 Como Usar

### Modo CLI (recomendado para testes)
1. Instale: `curl -fsSL https://github.com/theOFgusta-mod/Orion-agent-/raw/refs/heads/main/orion-beta/install.sh | bash`
2. Execute: `orion-beta`
3. Digite comandos como `status`, `memorize que`, `ajuda`

### Telegram 🧪
1. Crie um bot com [@BotFather](https://t.me/botfather)
2. Coloque o token no `config.yaml` (`telegram.token`)
3. Ative: `telegram.enabled: true`
4. Inicie: `orion-beta`
5. Envie `/start` no Telegram

### E-mail ✅
1. Gere uma **Senha de App** (Gmail): https://myaccount.google.com/apppasswords
2. Coloque no `config.yaml` (`email.user` e `email.password`)
3. Ative: `email.enabled: true` (ou `ativo: true`)
4. Inicie: `orion-beta`
5. Teste: `ver e-mails`

### WhatsApp 🧪
1. Certifique-se de ter Node.js instalado (o instalador pergunta se quer instalar)
2. Ative `whatsapp.enabled: true` no config
3. Inicie: `orion-beta`
4. Escaneie o QR Code com o WhatsApp

---

## 📁 Estrutura

```
orion-beta/                   # Dentro do repositório Orion-agent-
├── main.py                 # Orquestrador principal
├── install.sh              # Instalador one-line
├── package.json            # Dependências Node (WhatsApp)
├── requirements.txt        # Dependências Python
├── BETA.md                 # Esta documentação
├── scripts/
│   └── test-email.sh       # Teste rápido de e-mail
├── config/
│   └── config.yaml         # Configuração central
├── core/
│   ├── __init__.py
│   ├── memory.py           # SQLite persistente
│   ├── ai.py               # Gemini/OpenAI
│   └── actions.py          # Sistema de comandos
├── bridges/
│   ├── __init__.py
│   ├── telegram.py         # Telegram Bot 🧪
│   ├── whatsapp.py         # WhatsApp Web 🧪
│   ├── email.py            # E-mail IMAP/SMTP ✅
│   └── spotify.py          # Spotify Controller
└── sessions/               # Sessões (criado runtime)
```

---

## 🛠 Requisitos

| Componente | Versão | Obrigatório |
|-----------|--------|-------------|
| Python    | ≥ 3.10  | ✅ Sim |
| Node.js   | ≥ 18    | ⚠️ Só para WhatsApp |
| SQLite    | built-in | ✅ Sim |

### Pacotes Python
- `google-generativeai` — IA Gemini
- `openai` — IA OpenAI (alternativa)
- `python-telegram-bot` — Telegram 🧪
- `spotipy` — Spotify
- `pyyaml` — Config
- `httpx` — HTTP requests
- *(E-mail usa apenas libs nativas: `imaplib`, `smtplib`, `email`)*

---

## 🧪 Roadmap

- [x] Memória persistente SQLite
- [x] IA Gemini/OpenAI
- [x] Telegram Bridge 🧪
- [x] WhatsApp Bridge 🧪
- [x] Spotify Controller
- [x] E-mail Bridge (IMAP/SMTP)
- [x] CLI interativo
- [x] Instalação one-line com auto-deps
- [ ] Estabilizar WhatsApp e Telegram
- [ ] Agendador de tarefas
- [ ] Plugins de terceiros
- [ ] Web UI
- [ ] Reconhecimento de voz
- [ ] Integração com calendário
- [ ] Modo offline (modelo local)

---

## 📝 Licença

MIT — Use, modifique, compartilhe.

---

<p align="center">
  <sub>🧪 Beta — Em desenvolvimento ativo</sub>
  <br>
  <sub>Feito com ☕ por Gustavo</sub>
</p>
