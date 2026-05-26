#!/usr/bin/env bash
# ═══════════════════════════════════════════════
#  📧 O.R.I.O.N Beta — Teste de E-mail
#  Testa conexão IMAP + SMTP na hora
# ═══════════════════════════════════════════════

set -e
cd "$(dirname "$0")/.."

echo "📧 O.R.I.O.N Beta — Teste de E-mail"
echo "════════════════════════════════════"
echo ""

# Pede os dados
read -rp "📧 Seu e-mail: " EMAIL
read -rsp "🔑 Senha de App: " PASSWORD
echo ""
read -rp "📥 IMAP host [imap.gmail.com]: " IMAP_HOST
IMAP_HOST="${IMAP_HOST:-imap.gmail.com}"
read -rp "📤 SMTP host [smtp.gmail.com]: " SMTP_HOST
SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"

echo ""
echo "════════════════════════════════════"
echo "🧪 Testando conexões..."
echo ""

# Passa as variáveis via ambiente pro Python (mais seguro que interpolar na string)
export TEST_EMAIL="$EMAIL"
export TEST_PASSWORD="$PASSWORD"
export TEST_IMAP="$IMAP_HOST"
export TEST_SMTP="$SMTP_HOST"

python3 << 'PYEOF'
import imaplib, smtplib, sys, os

email = os.environ.get("TEST_EMAIL", "")
password = os.environ.get("TEST_PASSWORD", "")
imap_host = os.environ.get("TEST_IMAP", "imap.gmail.com")
smtp_host = os.environ.get("TEST_SMTP", "smtp.gmail.com")

# ── Teste IMAP ──
try:
    print("📥 Conectando IMAP...")
    imap = imaplib.IMAP4_SSL(imap_host, 993)
    imap.login(email, password)
    imap.select("INBOX")
    status, msgs = imap.search(None, "UNSEEN")
    uids = msgs[0].split()
    print(f"  ✅ IMAP OK — {len(uids)} e-mails não lidos")

    if uids:
        # Mostra os últimos 3
        for uid in uids[-3:]:
            status, data = imap.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if status == "OK":
                print(f"\n  📩 {data[0][1].decode('utf-8', errors='replace').strip()}")
    imap.logout()
except Exception as e:
    print(f"  ❌ IMAP: {e}")
    sys.exit(1)

# ── Teste SMTP ──
try:
    print("\n📤 Conectando SMTP...")
    smtp = smtplib.SMTP(smtp_host, 587, timeout=10)
    smtp.starttls()
    smtp.login(email, password)
    print("  ✅ SMTP OK")
    smtp.quit()
except Exception as e:
    print(f"  ❌ SMTP: {e}")
    sys.exit(1)

print()
print("🎉 Conexões funcionando! Pode usar o O.R.I.O.N Beta.")
PYEOF
