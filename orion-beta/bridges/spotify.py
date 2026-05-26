"""
🎵 O.R.I.O.N 3.0 — Spotify Bridge
Controla o Spotify e recomenda músicas.
"""

import logging
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger("orion.spotify")


class SpotifyBridge:
    def __init__(self, config: dict):
        self.config = config
        self.cfg = config.get("plataformas", {}).get("spotify", {})
        self.sp = None
        self.device_id = None

    def authenticate(self) -> bool:
        """Autentica no Spotify"""
        cid = self.cfg.get("client_id", "")
        secret = self.cfg.get("client_secret", "")
        redirect = self.cfg.get("redirect_uri", "http://localhost:8888/callback")

        if not cid or not secret:
            logger.warning("⚠️ Spotify credentials não configuradas")
            return False

        try:
            scope = (
                "user-read-playback-state "
                "user-modify-playback-state "
                "user-read-currently-playing "
                "playlist-read-private "
                "playlist-modify-public "
                "playlist-modify-private"
            )
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=cid,
                    client_secret=secret,
                    redirect_uri=redirect,
                    scope=scope,
                    open_browser=False,
                    cache_path=".spotify_cache",
                )
            )
            # Testa conexão
            self.sp.current_user()
            logger.info("✅ Spotify autenticado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro Spotify: {e}")
            return False

    def _get_device(self):
        """Pega o dispositivo ativo"""
        if not self.sp:
            return None
        try:
            devices = self.sp.devices()
            for d in devices.get("devices", []):
                if d.get("is_active"):
                    return d.get("id")
            # Pega o primeiro disponível
            if devices.get("devices"):
                return devices["devices"][0].get("id")
        except Exception:
            return None
        return None

    def play(self, query: str) -> str:
        """Toca uma música no Spotify"""
        if not self.sp:
            return "❌ Spotify não configurado."

        try:
            results = self.sp.search(q=query, limit=1, type="track")
            if not results["tracks"]["items"]:
                return f"❌ Música '{query}' não encontrada."

            track = results["tracks"]["items"][0]
            uri = track["uri"]
            device = self._get_device()

            if device:
                self.sp.start_playback(device_id=device, uris=[uri])
            else:
                self.sp.start_playback(uris=[uri])

            return (
                f"🎵 *Tocando agora:*\n"
                f"• {track['name']} — {track['artists'][0]['name']}\n"
                f"• Álbum: {track['album']['name']}\n"
                f"• Duração: {track['duration_ms'] // 60000}:{track['duration_ms'] % 60000 // 60:02d}\n"
                f"[Abrir no Spotify]({track['external_urls']['spotify']})"
            )
        except Exception as e:
            return f"❌ Erro ao tocar: {e}"

    def pause(self) -> str:
        """Pausa/Resume a música"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            current = self.sp.current_playback()
            if current and current.get("is_playing"):
                self.sp.pause_playback()
                return "⏸️ Música pausada."
            else:
                self.sp.start_playback()
                return "▶️ Música retomada."
        except Exception as e:
            return f"❌ Erro: {e}"

    def skip(self) -> str:
        """Pula para a próxima música"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            self.sp.next_track()
            return "⏭️ Pulando para a próxima música..."
        except Exception as e:
            return f"❌ Erro: {e}"

    def volume(self, level: int) -> str:
        """Ajusta o volume (0-100)"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            level = max(0, min(100, level))
            device = self._get_device()
            if device:
                self.sp.volume(level, device_id=device)
            return f"🔊 Volume ajustado para {level}%."
        except Exception as e:
            return f"❌ Erro: {e}"

    def current(self) -> str:
        """Mostra a música atual"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            current = self.sp.current_playback()
            if not current or not current.get("item"):
                return "🎵 Nada tocando no momento."

            item = current["item"]
            progress = current["progress_ms"] // 1000
            duration = item["duration_ms"] // 1000
            bar = self._progress_bar(progress, duration)

            return (
                f"🎵 *Tocando agora:*\n"
                f"• {item['name']} — {item['artists'][0]['name']}\n"
                f"• {bar} {progress//60}:{progress%60:02d} / {duration//60}:{duration%60:02d}\n"
                f"• Dispositivo: {current.get('device', {}).get('name', 'Desconhecido')}"
            )
        except Exception as e:
            return f"❌ Erro: {e}"

    def queue(self) -> str:
        """Mostra a fila"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            queue = self.sp.queue()
            if not queue or not queue.get("queue"):
                return "📋 Fila vazia."

            lines = ["📋 *Fila de músicas:*\n"]
            for i, track in enumerate(queue["queue"][:10], 1):
                lines.append(f"{i}. {track['name']} — {track['artists'][0]['name']}")

            return "\n".join(lines)
        except Exception as e:
            return f"❌ Erro: {e}"

    def recommend(self, genre: str = "") -> str:
        """Recomenda músicas baseadas em gênero"""
        if not self.sp:
            return "❌ Spotify não configurado."
        try:
            genres = ["rock", "pop", "electronic", "brazil", "mpb", "samba", "funk"]
            seed = genre if genre in genres else "pop"

            results = self.sp.recommendations(seed_genres=[seed], limit=5)
            if not results["tracks"]:
                return "❌ Nenhuma recomendação encontrada."

            lines = [f"🎧 *Recomendações ({seed}):*\n"]
            for i, track in enumerate(results["tracks"], 1):
                lines.append(f"{i}. {track['name']} — {track['artists'][0]['name']}")

            return "\n".join(lines)
        except Exception as e:
            return f"❌ Erro: {e}"

    def process_command(self, mensagem: str) -> str | None:
        """Processa comandos do Spotify. Retorna None se não for comando."""
        msg = mensagem.lower().strip()

        # tocar [música]
        match = re.match(r"tocar\s+(.+)", msg)
        if match:
            return self.play(match.group(1))

        # pular | próximo
        if msg in ("pular", "próximo", "proxima", "next"):
            return self.skip()

        # pausar | parar
        if msg in ("pausar", "parar", "pause", "stop"):
            return self.pause()

        # volume [0-100]
        match = re.match(r"volume\s*(\d+)", msg)
        if match:
            return self.volume(int(match.group(1)))

        # atual | tocando
        if msg in ("atual", "tocando", "now", "current"):
            return self.current()

        # fila | queue
        if msg in ("fila", "queue"):
            return self.queue()

        # recomendar [gênero]
        match = re.match(r"recomendar\s*(.+)", msg)
        if match:
            return self.recommend(match.group(1).strip())
        if msg == "recomendar":
            return self.recommend()

        return None

    @staticmethod
    def _progress_bar(progress: int, duration: int) -> str:
        """Cria uma barra de progresso visual"""
        if duration == 0:
            return "[⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪]"
        filled = int((progress / duration) * 10)
        bar = "🔵" * filled + "⚪" * (10 - filled)
        return f"[{bar}]"
