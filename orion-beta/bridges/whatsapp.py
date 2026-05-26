"""
📱 O.R.I.O.N 3.0 — WhatsApp Bridge
Conecta o assistente ao WhatsApp via web.js.
Requer Node.js para o whatsapp-web.js.
"""

import asyncio
import logging
import subprocess
import json
import os
import signal
from pathlib import Path

logger = logging.getLogger("orion.whatsapp")

WHATSAPP_JS_CODE = """
const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: process.env.SESSION_DIR || './sessions/whatsapp' }),
    puppeteer: { headless: true, args: ['--no-sandbox'] }
});

const app = express();
app.use(express.json());

let lastMessage = null;
let messages = [];

// ── Eventos do WhatsApp ──
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('[QR] Escaneie o QR Code acima');
});

client.on('ready', () => {
    console.log('[✅] WhatsApp conectado!');
    process.send?.({ type: 'ready' });
});

client.on('message', async (msg) => {
    if (msg.from.includes('@g.us')) return; // Ignora grupos
    if (msg.fromMe) return; // Ignora próprias mensagens

    const data = {
        from: msg.from,
        body: msg.body,
        name: msg._data?.notifyName || 'Desconhecido',
        timestamp: msg.timestamp
    };
    messages.push(data);
    console.log(`[📩] ${data.name}: ${data.body}`);
});

// ── API HTTP para o Python ──
app.post('/send', async (req, res) => {
    const { to, message } = req.body;
    try {
        await client.sendMessage(to, message);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

app.get('/messages', (req, res) => {
    const msgs = [...messages];
    messages = [];
    res.json(msgs);
});

app.get('/status', (req, res) => {
    res.json({
        ready: client.info?.wid?.server === 'c.us',
        user: client.info?.pushname || null,
        phone: client.info?.wid?.user || null
    });
});

const PORT = process.env.WEBHOOK_PORT || 8888;
app.listen(PORT, () => {
    console.log(`[🌐] Webhook: http://localhost:${PORT}`);
});
"""


class WhatsAppBridge:
    def __init__(self, config: dict, responder_fn):
        self.config = config
        self.cfg = config.get("plataformas", {}).get("whatsapp", {})
        self.port = self.cfg.get("webhook_port", 8888)
        self.session_dir = os.path.expanduser(self.cfg.get("session_dir", "sessions/whatsapp"))
        self.responder = responder_fn
        self.process = None

    async def start(self):
        """Inicia o bridge do WhatsApp"""
        if not self._check_node():
            logger.warning("⚠️ Node.js não encontrado. Instale para usar WhatsApp.")
            return

        # Garante que a sessão existe
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)

        # Cria o script JS temporário
        js_path = "/tmp/orion-whatsapp.js"
        with open(js_path, "w") as f:
            f.write(WHATSAPP_JS_CODE)

        logger.info("📱 Iniciando WhatsApp bridge...")

        self.process = subprocess.Popen(
            ["node", js_path],
            env={
                **os.environ,
                "SESSION_DIR": self.session_dir,
                "WEBHOOK_PORT": str(self.port),
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Loop de mensagens
        asyncio.create_task(self._poll_messages())

        logger.info(f"✅ WhatsApp bridge iniciado na porta {self.port}")

    def _check_node(self) -> bool:
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    async def _poll_messages(self):
        """Pega mensagens novas do webhook"""
        import httpx

        async with httpx.AsyncClient() as client:
            while True:
                try:
                    resp = await client.get(f"http://localhost:{self.port}/messages", timeout=5)
                    if resp.status_code == 200:
                        messages = resp.json()
                        for msg in messages:
                            asyncio.create_task(
                                self._process_message(msg["from"], msg["name"], msg["body"])
                            )
                except Exception:
                    pass
                await asyncio.sleep(2)

    async def _process_message(self, from_number: str, name: str, body: str):
        """Processa e responde uma mensagem"""
        try:
            resposta = await asyncio.to_thread(
                self.responder, "whatsapp", from_number, name, body
            )
            await self.send_message(from_number, resposta)
        except Exception as e:
            logger.error(f"Erro WhatsApp: {e}")

    async def send_message(self, to: str, message: str):
        """Envia mensagem via webhook"""
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"http://localhost:{self.port}/send",
                    json={"to": to, "message": message},
                    timeout=10,
                )
            except Exception as e:
                logger.error(f"Erro ao enviar WhatsApp: {e}")

    async def stop(self):
        if self.process:
            self.process.send_signal(signal.SIGTERM)
            self.process = None
