#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  O.R.I.O.N Beta — Instalador Automático
#  WhatsApp + Telegram + Spotify + IA
#  Uso: curl -fsSL https://raw.githubusercontent.com/... | bash
# ══════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

REPO="theOFgusta-mod/Orion-agent-"
BRANCH="main"
ORION_DIR="orion-beta"
INSTALL_DIR="$HOME/orion-beta"
BIN_DIR="$HOME/.local/bin"
CMD_NAME="orion-beta"

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════╗"
echo "║         O.R.I.O.N Beta — Instalação             ║"
echo "║   WhatsApp + Telegram + Spotify + IA            ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Detectar sistema ──
OS="$(uname -s)"
ARCH="$(uname -m)"
echo -e "${BLUE}🔍${NC} Sistema: $OS $ARCH"

# ── Verificar Python ──
if command -v python3 &>/dev/null; then
    PYTHON=$(command -v python3)
    echo -e "${GREEN}✅${NC} Python: $($PYTHON --version 2>&1)"
elif command -v python &>/dev/null; then
    PYTHON=$(command -v python)
    echo -e "${GREEN}✅${NC} Python: $($PYTHON --version 2>&1)"
else
    echo -e "${RED}❌${NC} Python 3 não encontrado."
    echo "  sudo pacman -S python python-pip  # Arch"
    echo "  sudo apt install python3 python3-pip python3-venv  # Debian/Ubuntu"
    exit 1
fi

# ── Verificar pip ──
if ! $PYTHON -m pip --version &>/dev/null; then
    echo -e "${RED}❌${NC} pip não encontrado."
    echo "  sudo pacman -S python-pip"
    echo "  sudo apt install python3-pip"
    exit 1
fi

# ── Detectar gerenciador de pacotes ──
if command -v pacman &>/dev/null; then
    PKG_MGR="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
elif command -v apt &>/dev/null; then
    PKG_MGR="apt"
    INSTALL_CMD="sudo apt install -y"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
    INSTALL_CMD="sudo dnf install -y"
elif command -v pkg &>/dev/null; then
    PKG_MGR="pkg"
    INSTALL_CMD="sudo pkg install -y"
else
    PKG_MGR=""
    INSTALL_CMD=""
fi

if [ -n "$PKG_MGR" ]; then
    echo -e "${BLUE}📦${NC} Gerenciador: $PKG_MGR"
fi

# ── Clonar ou atualizar ──
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}📂${NC} Atualizando O.R.I.O.N Beta..."
    cd "$INSTALL_DIR"
    git pull origin "$BRANCH" 2>/dev/null || echo -e "${YELLOW}⚠️  Git pull falhou, continuando...${NC}"
    # Atualiza subdiretório específico
    git fetch origin "$BRANCH" 2>/dev/null
    git checkout "$BRANCH" -- "$ORION_DIR/" 2>/dev/null || true
else
    echo -e "${BLUE}📥${NC} Baixando O.R.I.O.N Beta..."
    if command -v git &>/dev/null; then
        git clone -b "$BRANCH" "https://github.com/$REPO.git" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    else
        echo -e "${YELLOW}📥${NC} Git não encontrado, baixando ZIP..."
        ZIP_URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.zip"
        TMP_DIR=$(mktemp -d)
        cd "$TMP_DIR"
        curl -fsSL "$ZIP_URL" -o repo.zip
        unzip -q repo.zip
        mv "Orion-agent--$BRANCH" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        rm -rf "$TMP_DIR"
    fi
    echo -e "${GREEN}✅${NC} Baixado com sucesso!"
fi

# ── Navega para o diretório do beta ──
cd "$INSTALL_DIR/$ORION_DIR"

# ── Virtual env ──
VENV_DIR="$INSTALL_DIR/$ORION_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}🐍${NC} Criando ambiente virtual..."
    $PYTHON -m venv "$VENV_DIR"
fi

echo -e "${BLUE}📦${NC} Instalando dependências Python..."
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q -r requirements.txt 2>&1 | tail -3

# ── Node.js para WhatsApp ──
echo ""
echo -e "${YELLOW}⚡ WhatsApp e Telegram estão em DESENVOLVIMENTO${NC}"
echo -e "${YELLOW}   Ainda podem ter mudanças e ajustes.${NC}"
echo ""

if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    echo -e "${GREEN}✅${NC} Node.js: $NODE_VER"
else
    echo -e "${YELLOW}⚠️  Node.js não encontrado (necessário para WhatsApp)${NC}"
    echo -e "${BLUE}📥${NC} Deseja instalar Node.js automaticamente? (S/n)"
    read -r INSTALL_NODE
    if [[ ! "$INSTALL_NODE" =~ ^[nN]$ ]]; then
        echo -e "${BLUE}📥${NC} Instalando Node.js..."
        if [ "$PKG_MGR" = "pacman" ]; then
            $INSTALL_CMD nodejs npm
        elif [ "$PKG_MGR" = "apt" ]; then
            curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
            $INSTALL_CMD nodejs
        elif [ "$PKG_MGR" = "dnf" ]; then
            $INSTALL_CMD nodejs npm
        else
            echo -e "${RED}❌${NC} Não foi possível instalar automaticamente."
            echo "  Instale manualmente: https://nodejs.org"
        fi
    fi
fi

# ── npm dependencies para WhatsApp ──
if command -v node &>/dev/null && command -v npm &>/dev/null; then
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦${NC} Instalando dependências do WhatsApp..."
        npm install --silent 2>&1 | tail -2
        echo -e "${GREEN}✅${NC} WhatsApp bridge pronto!"
    else
        echo -e "${GREEN}✅${NC} Dependências WhatsApp já instaladas"
    fi
fi

# ── Config padrão ──
if [ ! -f "config/config.yaml" ]; then
    echo -e "${YELLOW}📝${NC} Criando config.yaml padrão..."
    cat > config/config.yaml << 'EOF'
# ════════════════════════════════════════════════════════
# O.R.I.O.N Beta — Configuração
# WhatsApp e Telegram estão em desenvolvimento
# ════════════════════════════════════════════════════════

orion:
  nome: "O.R.I.O.N Beta"
  dono: "Gustavo"
  lingua: "pt-BR"
  versao: "3.0.0-beta"

ia:
  provedor: "gemini"           # gemini | openai
  gemini:
    api_key: ""                # https://aistudio.google.com/apikey
    modelo: "gemini-2.0-flash"
  openai:
    api_key: ""
    modelo: "gpt-4o"

plataformas:
  telegram:
    enabled: false             # EM DESENVOLVIMENTO
    token: ""                  # @BotFather no Telegram
    admins: []
  whatsapp:
    enabled: false             # EM DESENVOLVIMENTO — Requer Node.js
    webhook_port: 8888
    session_dir: "sessions/whatsapp"
  spotify:
    enabled: false
    client_id: ""              # https://developer.spotify.com
    client_secret: ""
    redirect_uri: "http://localhost:8888/callback"
EOF
    echo -e "${YELLOW}⚠️  Edite ~/orion-beta/$ORION_DIR/config/config.yaml com suas chaves!${NC}"
fi

# ── Comando global ──
mkdir -p "$BIN_DIR"
CMD_PATH="$BIN_DIR/$CMD_NAME"

cat > "$CMD_PATH" << SCRIPT
#!/usr/bin/env bash
cd "$INSTALL_DIR/$ORION_DIR"
"$VENV_DIR/bin/python" main.py "\$@"
SCRIPT

chmod +x "$CMD_PATH"

# ── Detectar PATH ──
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    fi
    echo "" >> "$SHELL_CONFIG"
    echo "# O.R.I.O.N Beta" >> "$SHELL_CONFIG"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_CONFIG"
    echo -e "${YELLOW}📌${NC} Adicionado $BIN_DIR ao PATH em $SHELL_CONFIG"
    echo -e "${YELLOW}💡${NC} Execute: source $SHELL_CONFIG"
fi

# ── Sucesso ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     O.R.I.O.N Beta instalado com sucesso!      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  📂  Diretório: ${CYAN}$INSTALL_DIR/$ORION_DIR${NC}"
echo -e "  🚀  Comando:   ${CYAN}$CMD_NAME${NC}"
echo -e "  🐍  Python:    ${CYAN}$("$VENV_DIR/bin/python" --version 2>&1)${NC}"
if command -v node &>/dev/null; then
    echo -e "  🟢  Node.js:   ${CYAN}$(node --version)${NC}"
fi
echo ""
echo -e "  ${YELLOW}▶ Para iniciar (modo CLI):${NC}"
echo -e "     ${CYAN}$CMD_NAME${NC}"
echo ""
echo -e "  ${YELLOW}▶ Para usar WhatsApp ou Telegram:${NC}"
echo -e "     Edite ${CYAN}$INSTALL_DIR/$ORION_DIR/config/config.yaml${NC}"
echo ""
echo -e "  ${PURPLE}⚡ WhatsApp e Telegram estão em DESENVOLVIMENTO${NC}"
echo -e "  ${PURPLE}   Eles funcionam, mas ainda podem ter mudanças.${NC}"
echo -e "  ${PURPLE}   Reporte bugs e sugira melhorias!${NC}"
echo ""
