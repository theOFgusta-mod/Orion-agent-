"""
🤖 O.R.I.O.N 3.0 — Telegram Bridge
Conecta o assistente ao Telegram via Bot API.
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger("orion.telegram")


class TelegramBridge:
    def __init__(self, config: dict, responder_fn):
        """
        responder_fn: (plataforma, usuario_id, usuario_nome, mensagem) -> str
        """
        self.config = config
        self.token = config.get("plataformas", {}).get("telegram", {}).get("token", "")
        self.admins = config.get("plataformas", {}).get("telegram", {}).get("admins", [])
        self.responder = responder_fn
        self.app = None

    async def start(self):
        if not self.token:
            logger.warning("⚠️ Telegram token não configurado")
            return

        self.app = Application.builder().token(self.token).build()

        # Comandos
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("memoria", self.cmd_memoria))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("spotify", self.cmd_spotify))

        # Mensagens normais
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("✅ Telegram bridge iniciado")
        await self.app.run_polling()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("❓ Ajuda", callback_data="help")],
            [InlineKeyboardButton("🧠 Memórias", callback_data="memoria")],
            [InlineKeyboardButton("🎵 Spotify", callback_data="spotify")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 *O.R.I.O.N 3.0*\n\n"
            "Assistente pessoal multi-plataforma.\n"
            "Estou aqui pelo Telegram também!\n\n"
            "Comandos:\n"
            "/help — Ajuda\n"
            "/memoria — Ver memórias\n"
            "/status — Status do sistema\n"
            "/spotify — Controle do Spotify",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 *O.R.I.O.N 3.0 — Comandos*\n\n"
            "Envie qualquer mensagem que eu respondo!\n\n"
            "*Comandos especiais:*\n"
            "• memorize que [info] — Me faz memorizar algo\n"
            "• lembre de [info] — Pergunta o que lembro\n"
            "• tocar [música] — Toca no Spotify\n"
            "• pular — Pula música\n"
            "• pausar — Pausa música\n"
            "• status — Info do sistema",
            parse_mode="Markdown",
        )

    async def cmd_memoria(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra as memórias armazenadas"""
        from ..core.memory import Memory

        memory = Memory()
        memorias = memory.listar()

        if not memorias:
            await update.message.reply_text("🧠 Nenhuma memória ainda.")
            return

        texto = "🧠 *Minhas Memórias:*\n\n"
        for m in memorias[:15]:
            texto += f"• *{m['chave']}*: {m['valor']} `[{m['categoria']}]`\n"

        await update.message.reply_text(texto, parse_mode="Markdown")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        import platform, time

        texto = (
            "📊 *O.R.I.O.N 3.0 — Status*\n\n"
            f"🖥 Sistema: {platform.system()} {platform.release()}\n"
            f"🐍 Python: {platform.python_version()}\n"
            f"🤖 Plataforma: Telegram\n"
            f"⚡ Versão: 3.0.0-beta\n"
        )
        await update.message.reply_text(texto, parse_mode="Markdown")

    async def cmd_spotify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🎵 *Spotify Controller*\n\n"
            "Comandos:\n"
            "• `tocar [música]` — Toca uma música\n"
            "• `pausar` — Pausa/Volta\n"
            "• `pular` — Próxima música\n"
            "• `volume [0-100]` — Ajusta volume\n"
            "• `fila` — Mostra a fila",
            parse_mode="Markdown",
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto"""
        user = update.effective_user
        if not user or not update.message or not update.message.text:
            return

        usuario_id = str(user.id)
        usuario_nome = user.full_name or "Usuário"
        mensagem = update.message.text.strip()

        # Indica que está pensando
        await update.message.chat.send_action("typing")
        await asyncio.sleep(0.5)

        try:
            resposta = self.responder("telegram", usuario_id, usuario_nome, mensagem)
            # Telegram tem limite de 4096 caracteres
            if len(resposta) > 4000:
                resposta = resposta[:4000] + "\n\n*(resposta truncada)*"
            await update.message.reply_text(resposta)
        except Exception as e:
            logger.error(f"Erro ao responder: {e}")
            await update.message.reply_text(f"❌ Erro ao processar: {e}")
