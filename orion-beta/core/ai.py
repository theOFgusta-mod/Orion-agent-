"""
🤖 O.R.I.O.N 3.0 — Motor de IA
Conecta com Gemini ou OpenAI para processar mensagens.
"""

import google.generativeai as genai
from openai import OpenAI
from .memory import Memory


class AI:
    def __init__(self, config: dict, memory: Memory):
        self.config = config
        self.memory = memory
        self.provedor = config.get("ia", {}).get("provedor", "gemini")
        self._init_client()

    def _init_client(self):
        cfg = self.config.get("ia", {})
        if self.provedor == "gemini":
            key = cfg.get("gemini", {}).get("api_key", "")
            if key:
                genai.configure(api_key=key)
                self.model = genai.GenerativeModel(
                    cfg.get("gemini", {}).get("modelo", "gemini-2.0-flash")
                )
        elif self.provedor == "openai":
            key = cfg.get("openai", {}).get("api_key", "")
            if key:
                self.client = OpenAI(api_key=key)
                self.model_name = cfg.get("openai", {}).get("modelo", "gpt-4o")

    def build_prompt(self, plataforma: str, usuario_nome: str, mensagem: str) -> str:
        """Constrói o prompt com contexto e memórias"""
        sistema = f"""Você é {self.config['orion']['nome']} 3.0, um assistente pessoal.
O dono se chama {self.config['orion']['dono']}.
Idioma: {self.config['orion']['lingua']}.
Plataforma atual: {plataforma}.
Usuário: {usuario_nome}.

REGRAS:
- Trate o usuário como "Senhor" se for o dono.
- Seja espirituoso, rápido e direto.
- Responda no idioma {self.config['orion']['lingua']}.
- Use as memórias abaixo como contexto.
"""

        # Adiciona memórias relevantes
        memorias = self.memory.buscar(mensagem.split()[-1] if mensagem.split() else "")
        if not memorias:
            memorias = self.memory.listar()

        if memorias:
            sistema += "\n📌 Memórias relevantes:\n"
            for m in memorias[:10]:
                sistema += f"  • {m['chave']}: {m['valor']} [{m['categoria']}]\n"

        sistema += f"\n{usuario_nome}: {mensagem}\n{self.config['orion']['nome']}:"
        return sistema

    def responder(self, plataforma: str, usuario_id: str, usuario_nome: str, mensagem: str) -> str:
        """Processa uma mensagem e retorna a resposta"""
        prompt = self.build_prompt(plataforma, usuario_nome, mensagem)

        try:
            if self.provedor == "gemini":
                response = self.model.generate_content(prompt)
                resposta = response.text
            elif self.provedor == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                resposta = response.choices[0].message.content
            else:
                resposta = f"⚠️ Provedor '{self.provedor}' não configurado."
        except Exception as e:
            resposta = f"❌ Erro na IA: {e}"

        # Registra a conversa
        self.memory.registrar_conversa(plataforma, usuario_id, usuario_nome, mensagem, resposta)

        # Auto-memoriza informações importantes
        self._auto_learn(usuario_nome, mensagem, resposta)

        return resposta

    def _auto_learn(self, usuario_nome: str, mensagem: str, resposta: str):
        """Tenta extrair informações para memorizar automaticamente"""
        import re

        # Detecta "meu nome é X" ou "me chamo X"
        nome_match = re.search(r"(?:meu nome é|me chamo|meu nome)\s+(\w+)", mensagem, re.IGNORECASE)
        if nome_match:
            self.memory.lembrar(f"nome_{usuario_nome.lower()}", nome_match.group(1), "user_preference")

        # Detecta "uso X" ou "meu sistema é X"
        sistema_match = re.search(r"(?:uso|meu sistema é|meu os é)\s+(\w+)", mensagem, re.IGNORECASE)
        if sistema_match:
            self.memory.lembrar(f"sistema_{usuario_nome.lower()}", sistema_match.group(1), "system")

        # Detecta "gosto de X" ou "prefiro X"
        pref_match = re.search(r"(?:gosto de|prefiro|adoro)\s+(.+)", mensagem, re.IGNORECASE)
        if pref_match:
            self.memory.lembrar(f"preferencia_{usuario_nome.lower()}", pref_match.group(1).strip(), "user_preference")
