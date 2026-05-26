#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║              O.R.I.O.N 3.0 — Main                   ║
║  Orchestrator central: carga, init, loop            ║
╚══════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

import yaml

from core.memory import Memory
from core.ai import AI
from core.actions import Actions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("orion")


class Orion:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.memory = Memory(self.config)
        self.ai = AI(self.config, self.memory)
        self.actions = Actions(self.config, self.memory)
        self.bridges = {}
        self._running = True

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            logger.warning(f"⚠️ Config não encontrada em {self.config_path}, usando defaults")
            return self._default_config()

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        return {
            "orion": {
                "nome": "O.R.I.O.N",
                "dono": "Gustavo",
                "lingua": "pt-BR",
                "versao": "3.0.0-beta",
            },
            "ia": {"provedor": "gemini", "gemini": {"api_key": "", "modelo": "gemini-2.0-flash"}},
            "plataformas": {
                "telegram": {"token": "", "admins": []},
                "whatsapp": {"webhook_port": 8888, "session_dir": "sessions/whatsapp"},
                "spotify": {"client_id": "", "client_secret": "", "redirect_uri": "http://localhost:8888/callback"},
            },
        }

    def responder(self, plataforma: str, usuario_id: str, usuario_nome: str, mensagem: str) -> str:
        """Função de resposta usada por todas as bridges"""

        # 1. Tenta interpretar como comando do sistema
        cmd_response = self.actions.process(plataforma, usuario_id, usuario_nome, mensagem)
        if cmd_response:
            return cmd_response

        # 2. Tenta comando do Spotify via IA
        spotify = self.bridges.get("spotify")
        if spotify:
            spot_cmd = spotify.process_command(mensagem)
            if spot_cmd:
                return spot_cmd

        # 3. Tenta comando de E-mail
        email = self.bridges.get("email")
        if email:
            email_cmd = email.process_command(mensagem)
            if email_cmd:
                return email_cmd

        # 4. Resposta da IA
        return self.ai.responder(plataforma, usuario_id, usuario_nome, mensagem)

    async def iniciar(self):
        """Inicia todas as bridges"""
        logger.info("🚀 Iniciando O.R.I.O.N 3.0...")

        # ── Memory ──
        logger.info(f"🧠 Memória: {self.memory.status()}")

        # ── Spotify ──
        from bridges.spotify import SpotifyBridge

        spotify = SpotifyBridge(self.config)
        if spotify.authenticate():
            self.bridges["spotify"] = spotify
            logger.info("🎵 Spotify conectado")

        # ── Telegram ──
        from bridges.telegram import TelegramBridge

        telegram = TelegramBridge(self.config, self.responder)
        self.bridges["telegram"] = telegram

        # ── WhatsApp ──
        from bridges.whatsapp import WhatsAppBridge

        whatsapp = WhatsAppBridge(self.config, self.responder)
        self.bridges["whatsapp"] = whatsapp

        # ── E-mail ──
        from bridges.email import EmailBridge

        email = EmailBridge(self.config, self.responder)
        self.bridges["email"] = email

        # ── Inicia bridges concorrentes ──
        tasks = []
        if self.config.get("plataformas", {}).get("telegram", {}).get("token"):
            logger.info("📱 Telegram habilitado")
            tasks.append(asyncio.create_task(telegram.start()))
        else:
            logger.info("📱 Telegram desabilitado (sem token)")

        if self.config.get("plataformas", {}).get("whatsapp", {}).get("enabled", False):
            tasks.append(asyncio.create_task(whatsapp.start()))

        # ── E-mail ──
        email_cfg = self.config.get("plataformas", {}).get("email", {})
        if email_cfg.get("ativo", False) or email_cfg.get("enabled", False):
            logger.info("📧 E-mail habilitado")
            tasks.append(asyncio.create_task(email.start()))

        # ── CLI interativa (fallback) ──
        if not tasks:
            await self._cli_loop()
        else:
            # Mantém vivo enquanto bridges rodam
            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                pass

    async def _cli_loop(self):
        """Modo terminal interativo"""
        print(f"\n{'='*54}")
        print(f"  🤖 {self.config['orion']['nome']} 3.0")
        print(f"  🧪 BETA — Multi-plataforma em desenvolvimento")
        print(f"  {'─'*50}")
        print(f"  Plataformas: Telegram 🧪 | WhatsApp 🧪 | E-mail 📧 | Spotify 🎵")
        print(f"  Comandos: memorize | lembre de | status | ajuda")
        print(f"  Digite 'sair' ou Ctrl+C para encerrar")
        print(f"{'='*54}\n")

        while self._running:
            try:
                msg = await asyncio.get_event_loop().run_in_executor(None, input, "Você: ")
                if msg.lower().strip() in ("sair", "exit", "quit"):
                    print("\n👋 Até mais, Senhor!")
                    break

                resposta = self.responder("cli", "local", "Você", msg)
                print(f"\n{self.config['orion']['nome']}: {resposta}\n")

            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Encerrando...")
                break

    def parar(self):
        """Encerra tudo graciosamente"""
        self._running = False
        logger.info("🛑 O.R.I.O.N 3.0 encerrado.")


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    orion = Orion(config_path)

    def _signal_handler(sig, frame):
        orion.parar()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    asyncio.run(orion.iniciar())


if __name__ == "__main__":
    main()
