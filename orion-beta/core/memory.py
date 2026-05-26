"""
🧠 O.R.I.O.N 3.0 — Memória Persistente
Armazena e recupera informações entre conversas e plataformas.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path


class Memory:
    def __init__(self, db_path: str = "data/memoria.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                categoria TEXT DEFAULT 'general',
                plataforma TEXT DEFAULT 'core',
                criada_em TEXT DEFAULT (datetime('now')),
                atualizada_em TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plataforma TEXT NOT NULL,
                usuario_id TEXT NOT NULL,
                usuario_nome TEXT,
                mensagem TEXT,
                resposta TEXT,
                criada_em TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def lembrar(self, chave: str, valor: str, categoria: str = "general", plataforma: str = "core"):
        """Memoriza uma informação (upsert)"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            INSERT INTO memorias (chave, valor, categoria, plataforma, atualizada_em)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                categoria = excluded.categoria,
                plataforma = excluded.plataforma,
                atualizada_em = datetime('now')
        """, (chave, valor, categoria, plataforma))
        conn.commit()
        conn.close()

    def recordar(self, chave: str) -> str | None:
        """Recupera uma informação pela chave"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("SELECT valor FROM memorias WHERE chave = ?", (chave,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def buscar(self, termo: str, categoria: str | None = None) -> list:
        """Busca informações por termo"""
        conn = sqlite3.connect(str(self.db_path))
        query = "SELECT chave, valor, categoria FROM memorias WHERE chave LIKE ? OR valor LIKE ?"
        params = [f"%{termo}%", f"%{termo}%"]
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [{"chave": r[0], "valor": r[1], "categoria": r[2]} for r in rows]

    def listar(self, categoria: str | None = None) -> list:
        """Lista todas as memórias"""
        conn = sqlite3.connect(str(self.db_path))
        if categoria:
            cursor = conn.execute(
                "SELECT chave, valor, categoria, criada_em FROM memorias WHERE categoria = ? ORDER BY atualizada_em DESC",
                (categoria,),
            )
        else:
            cursor = conn.execute(
                "SELECT chave, valor, categoria, criada_em FROM memorias ORDER BY atualizada_em DESC"
            )
        rows = cursor.fetchall()
        conn.close()
        return [{"chave": r[0], "valor": r[1], "categoria": r[2], "criada_em": r[3]} for r in rows]

    def esquecer(self, chave: str):
        """Remove uma memória"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("DELETE FROM memorias WHERE chave = ?", (chave,))
        conn.commit()
        conn.close()

    def registrar_conversa(self, plataforma: str, usuario_id: str, usuario_nome: str, mensagem: str, resposta: str):
        """Registra uma conversa no histórico"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO conversas (plataforma, usuario_id, usuario_nome, mensagem, resposta) VALUES (?, ?, ?, ?, ?)",
            (plataforma, usuario_id, usuario_nome, mensagem, resposta),
        )
        conn.commit()
        conn.close()
