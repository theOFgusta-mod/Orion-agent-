"""
📧 O.R.I.O.N Beta — E-mail Bridge
Lê e responde e-mails via IMAP + SMTP.
Suporta Gmail, Outlook, e qualquer servidor.
"""

import asyncio
import email
import logging
import re
import smtplib
import time
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parsedate_to_datetime
from pathlib import Path
from typing import Optional

import imaplib

logger = logging.getLogger("orion.email")


class EmailBridge:
    def __init__(self, config: dict, responder_fn):
        self.config = config
        self.cfg = config.get("plataformas", {}).get("email", {})
        self.responder = responder_fn
        self.imap = None
        self.smtp = None
        self._running = False
        self._last_check = 0
        self._processed_uids = set()

    # ── Conexão IMAP ──

    def _connect_imap(self) -> bool:
        """Conecta ao servidor IMAP"""
        host = self.cfg.get("imap_host", "imap.gmail.com")
        port = self.cfg.get("imap_port", 993)
        user = self.cfg.get("user", "")
        password = self.cfg.get("password", "")

        if not user or not password:
            logger.warning("⚠️ E-mail: credenciais não configuradas")
            return False

        try:
            self.imap = imaplib.IMAP4_SSL(host, port)
            self.imap.login(user, password)
            self.imap.select("INBOX")
            logger.info(f"📧 Conectado ao IMAP {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro IMAP: {e}")
            return False

    def _disconnect_imap(self):
        try:
            if self.imap:
                self.imap.logout()
        except Exception:
            pass
        self.imap = None

    # ── Conexão SMTP ──

    def _connect_smtp(self) -> bool:
        """Conecta ao servidor SMTP"""
        host = self.cfg.get("smtp_host", "smtp.gmail.com")
        port = self.cfg.get("smtp_port", 587)
        user = self.cfg.get("user", "")
        password = self.cfg.get("password", "")

        if not user or not password:
            return False

        try:
            self.smtp = smtplib.SMTP(host, port, timeout=10)
            self.smtp.starttls()
            self.smtp.login(user, password)
            logger.info(f"📧 Conectado ao SMTP {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro SMTP: {e}")
            return False

    def _disconnect_smtp(self):
        try:
            if self.smtp:
                self.smtp.quit()
        except Exception:
            pass
        self.smtp = None

    # ── Decodificação ──

    @staticmethod
    def _decode_header(header_value) -> str:
        """Decodifica cabeçalhos de e-mail"""
        if not header_value:
            return ""
        parts = decode_header(header_value)
        result = []
        for part, charset in parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(charset or "utf-8", errors="replace"))
                except LookupError:
                    result.append(part.decode("utf-8", errors="replace"))
            else:
                result.append(str(part))
        return " ".join(result)

    @staticmethod
    def _get_email_body(msg) -> str:
        """Extrai o texto do corpo do e-mail"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        body += payload.decode(charset, errors="replace")
                    except Exception:
                        continue
                elif content_type == "text/html" and not body:
                    # Fallback pra HTML se não achou texto puro
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        html = payload.decode(charset, errors="replace")
                        # Remove tags HTML simples
                        body += re.sub(r"<[^>]+>", "", html)
                    except Exception:
                        continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
            except Exception:
                body = ""
        return body.strip()

    # ── Buscar e-mails ──

    def fetch_unread(self, max_emails: int = 5) -> list[dict]:
        """Busca e-mails não lidos"""
        if not self.imap:
            if not self._connect_imap():
                return []

        emails_list = []
        try:
            # Procura não lidos
            status, messages = self.imap.search(None, "UNSEEN")
            if status != "OK":
                return []

            uids = messages[0].split()
            if not uids:
                return []

            # Pega os mais recentes
            for uid in uids[-max_emails:]:
                uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)
                if uid_str in self._processed_uids:
                    continue

                status, data = self.imap.fetch(uid, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = self._decode_header(msg["Subject"])
                sender_raw = msg.get("From", "")
                sender = self._decode_header(sender_raw)
                date = msg.get("Date", "")
                body = self._get_email_body(msg)

                # Extrai nome e e-mail do remetente
                sender_name, sender_email = self._parse_sender(sender_raw)

                emails_list.append({
                    "uid": uid_str,
                    "subject": subject,
                    "sender": sender,
                    "sender_name": sender_name,
                    "sender_email": sender_email,
                    "date": date,
                    "body": body[:2000],  # Limita tamanho
                })
                self._processed_uids.add(uid_str)

        except imaplib.IMAP4.abort:
            logger.warning("📧 Conexão IMAP perdida, reconectando...")
            self._disconnect_imap()
            self._connect_imap()
        except Exception as e:
            logger.error(f"❌ Erro ao buscar e-mails: {e}")

        return emails_list

    @staticmethod
    def _parse_sender(sender_raw: str) -> tuple[str, str]:
        """Extrai nome e email de 'Nome <email@example.com>'"""
        match = re.search(r"([^<]+)\s*<([^>]+)>", sender_raw)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        # Só email
        return sender_raw.strip(), sender_raw.strip()

    # ── Enviar e-mail ──

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Envia um e-mail"""
        if not self.smtp:
            if not self._connect_smtp():
                return False

        user = self.cfg.get("user", "")
        nome = self.config.get("orion", {}).get("nome", "O.R.I.O.N Beta")

        try:
            msg = MIMEMultipart()
            msg["From"] = formataddr((nome, user))
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            self.smtp.sendmail(user, [to], msg.as_string())
            logger.info(f"📧 E-mail enviado para {to}: {subject}")
            return True
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPException):
            logger.warning("📧 Conexão SMTP perdida, reconectando...")
            self._disconnect_smtp()
            # Tenta de novo
            if self._connect_smtp():
                try:
                    msg = MIMEMultipart()
                    msg["From"] = formataddr((nome, user))
                    msg["To"] = to
                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, "plain", "utf-8"))
                    self.smtp.sendmail(user, [to], msg.as_string())
                    return True
                except Exception as e2:
                    logger.error(f"❌ Erro SMTP (2ª tentativa): {e2}")
                    return False
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail: {e}")
            return False

    # ── Responder e-mail ──

    def reply_to_email(self, original: dict, reply_body: str) -> bool:
        """Responde a um e-mail"""
        subject = original.get("subject", "")
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        to = original.get("sender_email") or original.get("sender")
        if not to:
            logger.warning("📧 Não foi possível determinar o destinatário")
            return False

        return self.send_email(to, subject, reply_body)

    # ── Processar com IA ──

    def process_email_with_ai(self, email_data: dict) -> str | None:
        """Processa um e-mail com a IA e retorna resposta pronta"""
        if not email_data:
            return None

        prompt = (
            f"Você recebeu um e-mail. Aqui está:\n\n"
            f"Assunto: {email_data['subject']}\n"
            f"De: {email_data['sender']}\n"
            f"Corpo:\n{email_data['body'][:1000]}\n\n"
            f"Escreva uma resposta educada e útil para este e-mail. "
            f"Seja conciso e direto. Não invente informações."
        )

        # Usa o AI da instância principal (via responder)
        resposta = self.responder("email", email_data["sender_email"], email_data["sender_name"], prompt)

        # Se a resposta for muito longa, avisa
        if len(resposta) > 5000:
            resposta = resposta[:5000] + "\n\n[... continuação truncada]"

        return resposta

    # ── Loop de polling ──

    async def start(self):
        """Inicia o polling de e-mails"""
        if not self._check_config():
            logger.info("📧 E-mail desabilitado (config incompleta)")
            return

        self._running = True
        intervalo = self.cfg.get("poll_interval", 60)  # segundos
        responder_auto = self.cfg.get("auto_reply", False)

        logger.info(f"📧 Iniciando polling de e-mails (a cada {intervalo}s)")

        # Conecta
        self._connect_imap()
        self._connect_smtp()

        while self._running:
            try:
                emails = self.fetch_unread(self.cfg.get("max_emails", 5))

                for email_data in emails:
                    logger.info(f"📧 Novo e-mail: {email_data['subject']} — {email_data['sender']}")

                    if responder_auto:
                        resposta = self.process_email_with_ai(email_data)
                        if resposta:
                            self.reply_to_email(email_data, resposta)
                            logger.info(f"📧 Respondido: {email_data['subject']}")

                await asyncio.sleep(intervalo)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no polling de e-mail: {e}")
                await asyncio.sleep(intervalo * 2)  # Espera o dobro em caso de erro

        self._disconnect_imap()
        self._disconnect_smtp()

    def _check_config(self) -> bool:
        """Verifica se a config de e-mail está completa"""
        cfg = self.cfg
        return bool(cfg.get("user")) and bool(cfg.get("password")) and (cfg.get("ativo", False) or cfg.get("enabled", False))

    def stop(self):
        self._running = False

    # ── Comandos ──

    def process_command(self, mensagem: str) -> str | None:
        """Processa comandos de e-mail"""
        msg = mensagem.lower().strip()

        # "ver e-mails" / "check emails"
        if msg in ("ver e-mails", "ver emails", "check emails", "check email", "ler e-mails", "ler emails"):
            emails = self.fetch_unread(5)
            if not emails:
                return "📧 Nenhum e-mail não lido."

            lines = ["📧 *E-mails não lidos:*\n"]
            for i, e in enumerate(emails, 1):
                lines.append(f"{i}. *{e['subject']}*")
                lines.append(f"   De: {e['sender']}")
                lines.append(f"   {e['body'][:100]}...")
                lines.append("")
            return "\n".join(lines)

        # "enviar e-mail para [email]: [mensagem]"
        match = re.match(r"enviar e-?mail\s+para\s+([^\s]+@[^\s]+)\s*[::]\s*(.+)", msg, re.IGNORECASE)
        if match:
            to = match.group(1)
            body = match.group(2)
            subject = self.cfg.get("default_subject", "Mensagem do O.R.I.O.N Beta")
            if self.send_email(to, subject, body):
                return f"📧 E-mail enviado para {to} ✅"
            else:
                return f"❌ Erro ao enviar e-mail para {to}"

        # "responder [nome/email]: [mensagem]" — responde ao último e-mail de alguém
        match = re.match(r"responder\s+(.+?)\s*[::]\s*(.+)", msg, re.IGNORECASE)
        if match:
            alvo = match.group(1).lower()
            resposta = match.group(2)
            # Busca e-mails recentes desse remetente
            emails = self.fetch_unread(20)
            for e in emails:
                if alvo in e["sender"].lower() or alvo in e["sender_email"].lower():
                    if self.reply_to_email(e, resposta):
                        return f"📧 Respondido {e['sender']} ✅"
            return f"❌ Não encontrei e-mail de '{alvo}' para responder."

        return None
