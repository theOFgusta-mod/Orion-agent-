#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# O.R.I.O.N — Instalador
# ═══════════════════════════════════════════════════════════════
# Uso:
#   curl -fsSL https://orion.run/install | bash
#   ou:
#   curl -fsSL https://github.com/theOFgusta-mod/Orion-agent-/raw/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

R='\033[0;31m'; G='\033[0;32m'; Y='\033[38;5;214m'; C='\033[0;36m'; M='\033[0;35m'; B='\033[1m'; N='\033[0m'

# ── 1. Verificar Git ──
if ! command -v git &>/dev/null; then
  echo -e "${R}❌ Git não encontrado.${N}"
  echo "   Instale: sudo pacman -S git  |  sudo apt install git  |  sudo dnf install git"
  exit 1
fi

# ── 2. Verificar/Instalar Bun ──
if ! command -v bun &>/dev/null; then
  echo -e "${Y}📦 Instalando Bun...${N}"
  curl -fsSL https://bun.sh/install | bash
  export BUN_INSTALL="${HOME}/.bun"
  export PATH="${BUN_INSTALL}/bin:${PATH}"
  if ! command -v bun &>/dev/null; then
    echo -e "${R}❌ Falha ao instalar Bun.${N}"
    exit 1
  fi
fi
echo -e "${G}✓${N} Bun $(bun --version)"

# ── 3. Baixar e instalar orion ──
ORION_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/orion"
ORION_REPO="${ORION_HOME}/repo"
ORION_BIN="${HOME}/.local/bin/orion"

mkdir -p "${ORION_HOME}"
mkdir -p "${HOME}/.local/bin"

echo -e "${Y}📦 Clonando O.R.I.O.N...${N}"
rm -rf "${ORION_REPO}" 2>/dev/null || true
git clone --depth 1 "https://github.com/theOFgusta-mod/Orion-agent-.git" "${ORION_REPO}"

echo -e "${Y}📦 Instalando dependências...${N}"
cd "${ORION_REPO}"
bun install 2>&1 | tail -3

# ── 4. Instalar comando global orion ──
cat > "${ORION_BIN}" << 'ORION_SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
export ORION_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/orion"
exec "${ORION_HOME}/repo/scripts/orion" "$@"
ORION_SCRIPT
chmod +x "${ORION_BIN}"

# ── 5. Seed automático ──
if [ -f "${HOME}/memoria.md" ]; then
  echo -e "${Y}🧠 Importando memórias...${N}"
  cd "${ORION_REPO}/packages/opencode"
  bun run script/seed-memory.ts 2>/dev/null || true
fi

# ── 6. Finalizar ──
echo ""
echo -e "${M}╔══════════════════════════════════════╗${N}"
echo -e "${M}║   ✅ O.R.I.O.N instalado!            ║${N}"
echo -e "${M}╚══════════════════════════════════════╝${N}"
echo ""
echo -e "Digite no terminal:"
echo -e "  ${C}${B}orion${N}"
echo ""
echo -e "Comandos: ${C}orion update${N} | ${C}orion uninstall${N} | ${C}orion help${N}"

# Aviso do PATH
if ! echo "${PATH}" | tr ':' '\n' | grep -q "${HOME}/.local/bin" 2>/dev/null; then
  echo ""
  echo -e "${Y}⚠️  ~/.local/bin não está no seu PATH.${N}"
  echo "   Adicione ao ~/.bashrc ou ~/.zshrc:"
  echo -e "   ${B}export PATH=\"\$HOME/.local/bin:\$PATH\"${N}"
fi
echo ""
