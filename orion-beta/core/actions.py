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

        # ── Ajuda ──
        if msg in ("ajuda", "help", "comandos", "o que você faz"):
            return (
                "🤖 *O.R.I.O.N 3.0 — Comandos*\n\n"
                "*🧠 Memória:*\n"
                "• `memorize que [chave] = [valor]` — Memorizar\n"
                "• `lembre de [termo]` — Buscar memória\n"
                "• `esqueça [chave]` — Apagar memória\n"
                "• `liste memórias` — Ver todas\n"
                "• `limpe memórias` — Limpar tudo\n\n"
                "*🎵 Spotify:*\n"
                "• `tocar [música]` — Tocar música\n"
                "• `pausar` / `pular` / `volume [0-100]`\n"
                "• `atual` / `fila` / `recomendar [gênero]`\n\n"
                "*⚡ Geral:*\n"
                "• `status` — Info do sistema\n"
                "• `ajuda` — Esta mensagem\n"
                "• `sair` — Encerrar"
            )

        return None
