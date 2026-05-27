#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# O.R.I.O.N — Instalador Turbo (mais robusto que tanque de guerra)
# ═══════════════════════════════════════════════════════════════
# Uso:
#   curl -fsSL https://orion.run/install | bash
#   ou:
#   curl -fsSL https://github.com/theOFgusta-mod/Orion-agent-/raw/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════

# ── Não usar set -euo pipefail (tratamos erros manualmente com carinho) ──

R='\033[0;31m'; G='\033[0;32m'; Y='\033[38;5;214m'; C='\033[0;36m'; M='\033[0;35m'; B='\033[1m'; N='\033[0m'

# ── Utilitário de erro amigável ──
die() {
  echo -e "${R}❌ $1${N}"
  echo -e "${Y}💡 $2${N}"
  exit 1
}

check_dep() {
  if ! command -v "$1" &>/dev/null; then
    die "$1 não encontrado." "Instale: $2"
  fi
}

# ── 0. Verificar dependências mínimas ──
echo -e "${Y}🔍 Verificando dependências do sistema...${N}"
check_dep "git"     "sudo pacman -S git  |  sudo apt install git  |  sudo dnf install git"
check_dep "curl"    "sudo pacman -S curl |  sudo apt install curl |  sudo dnf install curl"
echo -e "${G}✅ Dependências básicas ok${N}"

# ── 1. Verificar/Instalar Bun (com fallback e retry) ──
if ! command -v bun &>/dev/null; then
  echo -e "${Y}📦 Bun não encontrado. Instalando...${N}"
  for attempt in 1 2 3; do
    echo -e "${Y}   Tentativa $attempt de 3...${N}"
    if curl -fsSL https://bun.sh/install | bash; then
      echo -e "${G}✅ Bun instalado com sucesso!${N}"
      break
    fi
    if [ "$attempt" -eq 3 ]; then
      die "Falha ao instalar Bun após 3 tentativas." \
"Tente manualmente: curl -fsSL https://bun.sh/install | bash
Ou instale via npm: npm install -g bun
Ou via pacman: sudo pacman -S bun (Arch Linux)"
    fi
    sleep 2
  done
  # Carregar Bun no PATH atual
  export BUN_INSTALL="${HOME}/.bun"
  export PATH="${BUN_INSTALL}/bin:${PATH}"
  if ! command -v bun &>/dev/null; then
    die "Bun instalado mas não encontrado no PATH." \
"Adicione ao ~/.bashrc: export PATH=\"\$HOME/.bun/bin:\$PATH\""
  fi
fi
echo -e "${G}✅${N} Bun $(bun --version)"

# ── 2. Verificar espaço em disco ──
MIN_SPACE_MB=500
AVAIL_SPACE_MB=$(df --output=avail "$HOME" 2>/dev/null | tail -1 || echo 0)
if [ "$AVAIL_SPACE_MB" -lt "$MIN_SPACE_MB" ] 2>/dev/null; then
  die "Espaço em disco insuficiente (~${MIN_SPACE_MB}MB mínimo)." \
"Libere espaço com: sudo pacman -Scc  |  sudo apt clean"
fi

# ── 3. Baixar o O.R.I.O.N ──
ORION_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/orion"
ORION_REPO="${ORION_HOME}/repo"
ORION_BIN="${HOME}/.local/bin/orion"

mkdir -p "${ORION_HOME}"
mkdir -p "${HOME}/.local/bin"

echo -e "${Y}📥 Baixando O.R.I.O.N...${N}"
rm -rf "${ORION_REPO}" 2>/dev/null || true

if ! git clone --depth 1 "https://github.com/theOFgusta-mod/Orion-agent-.git" "${ORION_REPO}"; then
  die "Falha ao baixar o repositório." \
"Verifique sua conexão com a internet e acesso ao GitHub.
Ou tente manualmente: git clone https://github.com/theOFgusta-mod/Orion-agent-.git"
fi

# ── 4. Instalar dependências (com feedback visual) ──
echo -e "${Y}📦 Instalando dependências (pode levar alguns minutos)...${N}"
cd "${ORION_REPO}"

if ! bun install 2>&1; then
  echo ""
  echo -e "${Y}╔══════════════════════════════════════════════════════════════╗${N}"
  echo -e "${Y}⚠️  bun install falhou. Possíveis causas e soluções:${N}"
  echo -e "${Y}╚══════════════════════════════════════════════════════════════╝${N}"
  echo ""
  echo -e "   ${B}1.🟡 Faltam ferramentas de build:${N}"
  echo "      Arch: sudo pacman -S base-devel"
  echo "      Ubuntu: sudo apt install build-essential python3"
  echo "      Fedora: sudo dnf groupinstall 'Development Tools'"
  echo ""
  echo -e "   ${B}2.🟡 Versão do Bun desatualizada:${N}"
  echo "      bun upgrade"
  echo ""
  echo -e "   ${B}3.🟡 Erro de rede ou timeout:${N}"
  echo "      Tente novamente: cd ~/.local/share/orion/repo && bun install"
  echo ""
  echo -e "   ${B}4.🟡 Quer ajuda? Abra uma issue:${N}"
  echo "      https://github.com/theOFgusta-mod/Orion-agent-/issues/new"
  echo ""
  die "Instalação das dependências falhou." "Veja as sugestões acima."
fi

# ── 5. Instalar comando global orion ──
cat > "${ORION_BIN}" << 'ORION_SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
export ORION_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/orion"
exec "${ORION_HOME}/repo/scripts/orion" "$@"
ORION_SCRIPT
chmod +x "${ORION_BIN}"

# ── 6. Seed automático ──
if [ -f "${HOME}/memoria.md" ]; then
  echo -e "${Y}🧠 Importando memórias...${N}"
  cd "${ORION_REPO}/packages/opencode"
  bun run script/seed-memory.ts 2>/dev/null || echo -e "${Y}   ℹ️ Seed de memória não executado (não crítico)${N}"
fi

# ── 7. Configurar PATH automaticamente ──
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
  SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
  SHELL_CONFIG="$HOME/.bash_profile"
fi

if [ -n "$SHELL_CONFIG" ] && ! grep -q "\.local/bin" "$SHELL_CONFIG" 2>/dev/null; then
  echo "" >> "$SHELL_CONFIG"
  echo "# O.R.I.O.N" >> "$SHELL_CONFIG"
  echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_CONFIG"
  echo -e "${Y}📌${N} ~/.local/bin adicionado ao PATH em $SHELL_CONFIG"
fi

# ── 8. Finalizar ──
echo ""
echo -e "${M}╔══════════════════════════════════════════════╗${N}"
echo -e "${M}║   🚀 O.R.I.O.N instalado com sucesso!       ║${N}"
echo -e "${M}╚══════════════════════════════════════════════╝${N}"
echo ""
echo -e "   ${B}📂 Local:${N}  ${ORION_REPO}"
echo -e "   ${B}🔧 Comando:${N} ${C}orion${N}"
echo ""
echo -e "   ${B}▶ Para começar:${N}"
echo -e "     ${C}${B}orion${N}"
echo ""
echo -e "   ${B}▶ Comandos úteis:${N}"
echo -e "     ${C}orion update${N}   → Atualizar"
echo -e "     ${C}orion uninstall${N} → Remover"
echo -e "     ${C}orion help${N}      → Ajuda"
echo ""
echo -e "   ${Y}💡 Precisa reiniciar o terminal ou rodar:${N}"
echo -e "      source $SHELL_CONFIG"
echo ""
