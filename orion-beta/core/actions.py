"""
⚡ O.R.I.O.N 3.0 — Sistema de Ações
Interpreta comandos do sistema: memória, utilitários, etc.
"""

import logging
import re
import subprocess
import platform

logger = logging.getLogger("orion.actions")


class Actions:
    def __init__(self, config: dict, memory):
        self.config = config
        self.memory = memory
        self.dono = config.get("orion", {}).get("dono", "Gustavo").lower()

    def process(self, plataforma: str, usuario_id: str, usuario_nome: str, mensagem: str) -> str | None:
        """Tenta processar um comando. Retorna resposta ou None."""
        msg = mensagem.strip().lower()

        # ── Memória ──
        # "memorize que [chave] = [valor]"
        match = re.match(r"memorize?\s+que\s+(.+?)\s*(?:=|é|:)\s*(.+)", msg)
        if match:
            chave = match.group(1).strip()
            valor = match.group(2).strip()
            self.memory.lembrar(chave, valor, "memoria")
            return f"🧠 Memorizado: *{chave}* = {valor}"

        # "memorize [chave]: [valor]"
        match = re.match(r"memorize?\s+(.+?)\s*[:=]\s*(.+)", msg)
        if match:
            chave = match.group(1).strip()
            valor = match.group(2).strip()
            self.memory.lembrar(chave, valor, "memoria")
            return f"🧠 Memorizado: *{chave}* = {valor}"

        # "lembre de [o que sei sobre X]" — busca
        match = re.match(r"lembre\s+de\s+(.+)", msg)
        if match:
            termo = match.group(1).strip()
            resultados = self.memory.buscar(termo)
            if not resultados:
                return f"🧠 Não lembro de nada sobre '{termo}'."
            linhas = [f"🧠 *O que sei sobre {termo}:*"]
            for r in resultados[:10]:
                linhas.append(f"  • {r['chave']}: {r['valor']} `[{r['categoria']}]`")
            return "\n".join(linhas)

        # "esqueça [chave]"
        match = re.match(r"esqueça?\s+(.+)", msg)
        if match:
            chave = match.group(1).strip()
            self.memory.esquecer(chave)
            return f"🧹 Esquecido: *{chave}*"

        # "liste memórias" / "mostre memórias"
        if msg in ("liste memórias", "liste memorias", "mostre memórias", "mostre memorias", "memórias", "memorias"):
            memorias = self.memory.listar()
            if not memorias:
                return "🧠 Nenhuma memória armazenada."
            linhas = ["🧠 *Memórias:*"]
            for m in memorias[:20]:
                linhas.append(f"  • {m['chave']}: {m['valor']} `[{m['categoria']}]`")
            return "\n".join(linhas)

        # "limpe memórias"
        if msg in ("limpe memórias", "limpe memorias", "limpar memória", "limpar memoria"):
            self.memory.limpar()
            return "🧹 Todas as memórias foram limpas."

        # ── Sistema ──
        # "status"
        if msg in ("status", "info", "sistema"):
            return (
                f"📊 *O.R.I.O.N 3.0 — Status*\n"
                f"• Versão: {self.config.get('orion', {}).get('versao', 'desconhecida')}\n"
                f"• Dono: {self.config.get('orion', {}).get('dono', 'N/A')}\n"
                f"• IA: {self.config.get('ia', {}).get('provedor', 'N/A')}\n"
                f"• Memórias: {self.memory.contar()} registros\n"
                f"• Sistema: {platform.system()} {platform.release()}\n"
                f"• Python: {platform.python_version()}"
            )

        # ── Ajuda / Socorro / Perdido ──
        help_terms = (
            "ajuda", "help", "comandos", "o que você faz", "o que sabe fazer",
            "socorro", "não sei", "nao sei", "não entendi", "nao entendi",
            "?", "??", "???"
        )
        if msg in help_terms:
            return self._help_geral()

        # "ajuda [categoria]" ou "help [comando]"
        match = re.match(r"(?:ajuda|help|como funciona|o que é|explique|me explique|me ajuda com|pode me ajudar com|quero saber sobre|fala sobre|ensina)\s+(.+)", msg)
        if match:
            termo = match.group(1).strip().lower()
            return self._help_detalhado(termo)

        return None

    # ═══════════════════════════════════════════════
    #  SISTEMA DE AJUDA INTERATIVO
    # ═══════════════════════════════════════════════

    HELP = {
        "categorias": [
            {
                "nome": "🧠 Memória",
                "slug": "memoria",
                "descricao": "O O.R.I.O.N tem memória persistente! Ele lembra de informações que você ensina.",
                "comandos": [
                    {
                        "cmd": "memorize que [chave] = [valor]",
                        "exemplo": "memorize que cor favorita = azul",
                        "descricao": "Ensina algo ao O.R.I.O.N. Ele guarda no banco SQLite.",
                        "dica": "Use para salvar preferências, senhas, lembretes, qualquer coisa!",
                    },
                    {
                        "cmd": "lembre de [termo]",
                        "exemplo": "lembre de cor favorita",
                        "descricao": "Pergunta o que o O.R.I.O.N sabe sobre aquele assunto.",
                        "dica": "Ele busca na memória e mostra tudo relacionado.",
                    },
                    {
                        "cmd": "esqueça [chave]",
                        "exemplo": "esqueça cor favorita",
                        "descricao": "Apaga uma informação específica da memória.",
                        "dica": "Use quando algo mudar ou estiver errado.",
                    },
                    {
                        "cmd": "liste memórias",
                        "exemplo": "liste memórias",
                        "descricao": "Mostra TUDO que o O.R.I.O.N lembra.",
                        "dica": "Bom para revisar o que já foi ensinado.",
                    },
                    {
                        "cmd": "limpe memórias",
                        "exemplo": "limpe memórias",
                        "descricao": "Apaga TODAS as memórias de uma vez.",
                        "dica": "Cuidado! Essa operação não tem volta.",
                    },
                ],
            },
            {
                "nome": "🎵 Spotify",
                "slug": "spotify",
                "descricao": "Controla o Spotify direto pelo chat! Pula, pausa, toca, recomenda.",
                "comandos": [
                    {
                        "cmd": "tocar [música ou artista]",
                        "exemplo": "tocar Bohemian Rhapsody",
                        "descricao": "Busca a música no Spotify e toca no seu dispositivo.",
                        "dica": "Pode ser nome da música, artista, ou álbum.",
                    },
                    {
                        "cmd": "pausar",
                        "exemplo": "pausar",
                        "descricao": "Pausa a música atual. Se estiver pausada, volta a tocar.",
                        "dica": "Funciona como um play/pause alternado.",
                    },
                    {
                        "cmd": "pular",
                        "exemplo": "pular",
                        "descricao": "Pula para a próxima música na fila.",
                        "dica": "Só funciona no plano Premium do Spotify.",
                    },
                    {
                        "cmd": "volume [0-100]",
                        "exemplo": "volume 70",
                        "descricao": "Ajusta o volume do Spotify.",
                        "dica": "Valores de 0 (mudo) a 100 (máximo).",
                    },
                    {
                        "cmd": "atual",
                        "exemplo": "atual",
                        "descricao": "Mostra o que está tocando agora com barra de progresso.",
                        "dica": "Mostra música, artista, álbum e tempo.",
                    },
                    {
                        "cmd": "fila",
                        "exemplo": "fila",
                        "descricao": "Mostra as próximas músicas na fila.",
                        "dica": "Útil pra ver o que vem por aí.",
                    },
                    {
                        "cmd": "recomendar [gênero]",
                        "exemplo": "recomendar rock",
                        "descricao": "Recomenda músicas baseadas em um gênero.",
                        "dica": "Gêneros: rock, pop, electronic, brazil, mpb, samba, funk.",
                    },
                ],
            },
            {
                "nome": "📧 E-mail",
                "slug": "email",
                "descricao": "Lê e responde e-mails diretamente pelo chat. Conecta via IMAP/SMTP.",
                "comandos": [
                    {
                        "cmd": "ver e-mails",
                        "exemplo": "ver e-mails",
                        "descricao": "Mostra os e-mails não lidos da sua caixa de entrada.",
                        "dica": "Requer configuração de e-mail no config.yaml.",
                    },
                    {
                        "cmd": "enviar e-mail para [email]: [mensagem]",
                        "exemplo": "enviar e-mail para joao@gmail.com: Oi João, tudo bem?",
                        "descricao": "Envia um e-mail direto pelo chat.",
                        "dica": "O assunto padrão é 'Mensagem do O.R.I.O.N Beta'.",
                    },
                    {
                        "cmd": "responder [nome]: [mensagem]",
                        "exemplo": "responder Maria: Recebi seu e-mail, obrigado!",
                        "descricao": "Responde ao último e-mail da pessoa.",
                        "dica": "Funciona com nome ou e-mail parcial.",
                    },
                ],
            },
            {
                "nome": "⚡ Gerais",
                "slug": "geral",
                "descricao": "Comandos gerais do sistema O.R.I.O.N.",
                "comandos": [
                    {
                        "cmd": "status",
                        "exemplo": "status",
                        "descricao": "Mostra informações do sistema: versão, IA, memórias, etc.",
                        "dica": "Bom pra verificar se está tudo funcionando.",
                    },
                    {
                        "cmd": "ajuda",
                        "exemplo": "ajuda",
                        "descricao": "Mostra esta mensagem de ajuda.",
                        "dica": "Use 'ajuda [categoria]' ou 'ajuda [comando]' pra detalhes.",
                    },
                    {
                        "cmd": "ajuda [categoria]",
                        "exemplo": "ajuda spotify",
                        "descricao": "Mostra ajuda detalhada de uma categoria específica.",
                        "dica": "Categorias: memoria, spotify, email, geral.",
                    },
                    {
                        "cmd": "ajuda [comando]",
                        "exemplo": "ajuda tocar",
                        "descricao": "Explica um comando específico em detalhes.",
                        "dica": "Veja todos os comandos disponíveis com 'ajuda'.",
                    },
                    {
                        "cmd": "sair",
                        "exemplo": "sair",
                        "descricao": "Encerra o O.R.I.O.N.",
                        "dica": "Ou Ctrl+C para sair.",
                    },
                ],
            },
        ],
    }

    def _help_geral(self) -> str:
        """Mostra visão geral de todas as categorias e perguntas"""
        linhas = [
            "🤖 *O.R.I.O.N Beta — Central de Ajuda*",
            "",
            "📋 *Categorias de comandos:*",
        ]

        for cat in self.HELP["categorias"]:
            linhas.append(f"\n• *{cat['nome']}* — {cat['descricao']}")
            # Mostra os comandos principais
            for cmd in cat["comandos"]:
                linhas.append(f"   → `{cmd['cmd']}`")

        linhas.append(f"\n{'─'*40}")
        linhas.append("🤔 *Não sabe como usar algo?*")
        linhas.append("Digite `ajuda [categoria]` ou `ajuda [comando]` que eu explico!")
        linhas.append("")
        linhas.append("💡 *Exemplos:*")
        linhas.append("   • `ajuda memoria` — Explica TODOS os comandos de memória")
        linhas.append("   • `ajuda tocar` — Explica como tocar música no Spotify")
        linhas.append("   • `ajuda email`  — Explica tudo sobre e-mail")
        linhas.append("   • `ajuda status` — Explica o comando status")
        linhas.append("")
        linhas.append("Pode perguntar também em português:")
        linhas.append("   • `como funciona a memória?`")
        linhas.append("   • `o que é spotify?`")
        linhas.append("   • `explique ver e-mails`")

        return "\n".join(linhas)

    def _help_detalhado(self, termo: str) -> str:
        """Mostra ajuda detalhada de uma categoria ou comando"""
        termo = termo.lower().strip()

        # Remove artigos e preposições pra facilitar matching
        termo_clean = re.sub(r"^(o|a|os|as|de|do|da|dos|das|no|na|em|como|que|é|um|uma|o\s+que\s+é)\s+", "", termo)

        # 1. Procura por categoria
        for cat in self.HELP["categorias"]:
            if termo_clean == cat["slug"] or termo_clean in cat["nome"].lower():
                return self._help_categoria(cat)

        # 2. Procura por comando específico
        for cat in self.HELP["categorias"]:
            for cmd in cat["comandos"]:
                cmd_name = cmd["cmd"].split(" ")[0].lower()  # pega só o primeiro verbo
                if termo_clean == cmd_name or termo_clean in cmd["cmd"].lower():
                    return self._help_comando(cmd, cat["nome"])

        # 3. Procura parcial (ex: "memorize" funciona mesmo com "memória")
        for cat in self.HELP["categorias"]:
            if termo_clean in cat["slug"] or cat["slug"] in termo_clean:
                return self._help_categoria(cat)

        # 4. Se não achou nada
        return (
            f"🤔 Não entendi sobre o que você quer saber: '{termo}'.\n\n"
            f"Categorias disponíveis:\n"
            f"• `memoria` — Comandos de memória\n"
            f"• `spotify` — Controle do Spotify\n"
            f"• `email` — E-mail bridge\n"
            f"• `geral` — Comandos gerais\n\n"
            f"Ou digite `ajuda` pra ver a lista completa."
        )

    def _help_categoria(self, cat: dict) -> str:
        """Mostra ajuda completa de uma categoria"""
        linhas = [
            f"{cat['nome']} — Ajuda Completa",
            f"{'─'*40}",
            f"{cat['descricao']}",
            "",
            f"📋 *Comandos disponíveis:*",
        ]

        for cmd in cat["comandos"]:
            linhas.append(f"\n🔹 *{cmd['cmd']}*")
            linhas.append(f"   {cmd['descricao']}")
            linhas.append(f"   💡 *Exemplo:* `{cmd['exemplo']}")
            linhas.append(f"   📌 *Dica:* {cmd['dica']}")

        return "\n".join(linhas)

    def _help_comando(self, cmd: dict, categoria: str) -> str:
        """Mostra ajuda detalhada de um comando específico"""
        return (
            f"🔹 *Comando:* `{cmd['cmd']}`\n"
            f"📂 *Categoria:* {categoria}\n"
            f"{'─'*40}\n"
            f"{cmd['descricao']}\n\n"
            f"💡 *Exemplo:*\n"
            f"   `{cmd['exemplo']}`\n\n"
            f"📌 *Dica:* {cmd['dica']}\n\n"
            f"Quer saber de mais algum comando? É só perguntar!"
        )
