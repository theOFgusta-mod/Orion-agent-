#!/usr/bin/env bash
# -------------------------------------------------------------------
# O.R.I.O.N — Instalador One-Line
# -------------------------------------------------------------------
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/gustavoolivera/orion-dev/main/scripts/orion-install.sh | bash
# -------------------------------------------------------------------
set -euo pipefail

VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
LARANJA='\033[38;5;214m'
CIANO='\033[0;36m'
NC='\033[0m'

# ---- Configurações ----
REPO_URL="https://github.com/gustavoolivera/orion-dev.git"
ORION_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/orion"
ORION_REPO="${ORION_HOME}/repo"
ORION_BIN="${HOME}/.local/bin/orion"

echo ""
echo -e "${VERDE}╔══════════════════════════════════════╗${NC}"
echo -e "${VERDE}║      🚀 Instalando O.R.I.O.N         ║${NC}"
echo -e "${VERDE}╚══════════════════════════════════════╝${NC}"
echo ""

# ---- Verifica Git ----
if ! command -v git &>/dev/null; then
  echo -e "${VERMELHO}❌ Git não encontrado. Instale o Git primeiro:${NC}"
  echo "   sudo pacman -S git        # Arch"
  echo "   sudo apt install git      # Ubuntu/Debian"
  echo "   sudo dnf install git      # Fedora"
  exit 1
fi
echo -e "${VERDE}✓${NC} Git encontrado"

# ---- Verifica Bun ----
if ! command -v bun &>/dev/null; then
  echo -e "${LARANJA}📦 Bun não encontrado. Instalando...${NC}"
  curl -fsSL https://bun.sh/install | bash
  # Carrega o bun pro PATH agora
  export BUN_INSTALL="${HOME}/.bun"
  if [ -f "${BUN_INSTALL}/bin/bun" ]; then
    export PATH="${BUN_INSTALL}/bin:${PATH}"
  fi
  if ! command -v bun &>/dev/null; then
    echo -e "${VERMELHO}❌ Falha ao instalar Bun. Instale manualmente: curl -fsSL https://bun.sh/install | bash${NC}"
    exit 1
  fi
fi
echo -e "${VERDE}✓${NC} Bun $(bun --version)"

# ---- Cria diretório ----
mkdir -p "${ORION_HOME}"

# ---- Clona/Atualiza repo ----
if [ -d "${ORION_REPO}/.git" ]; then
  echo -e "${LARANJA}📂 Repositório já existe. Atualizando...${NC}"
  cd "${ORION_REPO}"
  git pull origin main
else
  echo -e "${LARANJA}📦 Clonando repositório...${NC}"
  git clone --depth 1 "${REPO_URL}" "${ORION_REPO}"
  cd "${ORION_REPO}"
fi

# ---- Instala dependências ----
echo -e "${LARANJA}📦 Instalando dependências...${NC}"
bun install

# ---- Cria comando 'orion' global ----
echo -e "${LARANJA}🔧 Instalando comando 'orion' em ${ORION_BIN}...${NC}"
mkdir -p "${HOME}/.local/bin"

# Copia o wrapper e ajusta o caminho
sed "s|ORION_HOME=\"\${XDG_DATA_HOME:-\$HOME/.local/share}/orion\"|ORION_HOME=\"${ORION_HOME}\"|" \
  "${ORION_REPO}/scripts/orion" > "${ORION_BIN}"
chmod +x "${ORION_BIN}"

echo ""
echo -e "${VERDE}╔══════════════════════════════════════╗${NC}"
echo -e "${VERDE}║   ✅ O.R.I.O.N instalado com sucesso! ║${NC}"
echo -e "${VERDE}╚══════════════════════════════════════╝${NC}"
echo ""
echo "Digite no terminal:"
echo -e "  ${CIANO}orion${NC}"
echo ""
echo "Para atualizar depois:"
echo -e "  ${CIANO}orion update${NC}"
echo ""

# ---- Seed de memórias (opcional) ----
if [ -f "${HOME}/memoria.md" ]; then
  echo -e "${LARANJA}🧠 ~/memoria.md encontrado! Populando memórias...${NC}"
  cd "${ORION_REPO}/packages/opencode"
  bun run script/seed-memory.ts 2>/dev/null || echo -e "${LARANJA}   (seed executado)${NC}"
fi

# ---- Aviso sobre PATH ----
if ! echo "${PATH}" | tr ':' '\n' | grep -q "${HOME}/.local/bin"; then
  echo -e "${LARANJA}⚠️  ~/.local/bin não está no seu PATH.${NC}"
  echo "   Adicione isso ao seu ~/.bashrc ou ~/.zshrc:"
  echo '   export PATH="$HOME/.local/bin:$PATH"'
  echo ""
fi

echo -e "${CIANO}Pronto! O.O.R.I.O.N está vivo. 🚀${NC}"
