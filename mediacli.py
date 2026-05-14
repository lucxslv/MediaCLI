#!/usr/bin/env python3
"""
mediacli — Download e transcrição de mídia em um único comando

Subcomandos:
  yt        YouTube: baixar vídeo, áudio ou transcrever
  spotify   Spotify: baixar músicas, álbuns e playlists
  transcrever  Transcrever um arquivo de áudio local

Exemplos:
  python mediacli.py yt https://youtube.com/watch?v=XXX -m audio
  python mediacli.py yt https://youtube.com/watch?v=XXX -m transcrever
  python mediacli.py spotify https://open.spotify.com/playlist/XXX -q 320
  python mediacli.py transcrever audio.mp3 -l pt
"""

import argparse
import os
import sys
import time
import tempfile
import subprocess


# ══════════════════════════════════════════════════════════════════
#  Utilitários
# ══════════════════════════════════════════════════════════════════

def verificar_imports(*pacotes: tuple[str, str]):
    """Recebe pares (import_name, pip_name) e aborta se algum faltar."""
    erros = []
    for imp, pip in pacotes:
        try:
            __import__(imp)
        except ImportError:
            erros.append(f"❌ '{pip}' não instalado. Execute: pip install {pip}")
    if erros:
        for e in erros:
            print(e)
        sys.exit(1)


def eh_url(texto: str) -> bool:
    return texto.startswith("http://") or texto.startswith("https://")


def eh_spotify(url: str) -> bool:
    return "open.spotify.com" in url or url.startswith("spotify:")


# ══════════════════════════════════════════════════════════════════
#  YouTube — funções
# ══════════════════════════════════════════════════════════════════

def yt_baixar_audio(url: str, pasta: str) -> tuple[str, str]:
    import yt_dlp

    os.makedirs(pasta, exist_ok=True)
    opcoes = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ignoreerrors": True,  # continua mesmo se uma faixa falhar
    }

    print("⬇️  Baixando áudio do YouTube...")
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        titulo = info.get("title", "audio")

    arquivo = os.path.join(pasta, f"{titulo}.mp3")
    if not os.path.exists(arquivo):
        for f in os.listdir(pasta):
            if f.endswith(".mp3"):
                arquivo = os.path.join(pasta, f)
                titulo = os.path.splitext(f)[0]
                break

    print(f"✅ Áudio salvo: {titulo}")
    return arquivo, titulo


def yt_baixar_video(url: str, qualidade: str, pasta: str) -> str:
    import yt_dlp

    os.makedirs(pasta, exist_ok=True)
    fmt = {
        "melhor": "bestvideo+bestaudio/best",
        "1080p":  "bestvideo[height<=1080]+bestaudio/best",
        "720p":   "bestvideo[height<=720]+bestaudio/best",
        "480p":   "bestvideo[height<=480]+bestaudio/best",
    }.get(qualidade, "bestvideo+bestaudio/best")

    opcoes = {
        "format": fmt,
        "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "ignoreerrors": True,  # continua mesmo se um vídeo falhar
        # Converte áudio para AAC para compatibilidade máxima com players
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
        "postprocessor_args": {
            "FFmpegVideoConvertor": ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"],
        },
    }

    print(f"⬇️  Baixando vídeo ({qualidade})...")
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        titulo = info.get("title", "video")

    print(f"✅ Vídeo salvo: {titulo}")
    print(f"📁 Pasta: {os.path.abspath(pasta)}")
    return titulo


# ══════════════════════════════════════════════════════════════════
#  Whisper — transcrição
# ══════════════════════════════════════════════════════════════════

def transcrever_arquivo(arquivo: str, modelo: str, idioma: str | None) -> str:
    import whisper

    print(f"\n🔄 Carregando modelo Whisper '{modelo}'...")
    model = whisper.load_model(modelo)
    print("🎙️  Transcrevendo...")
    inicio = time.time()

    resultado = model.transcribe(arquivo, **({"language": idioma} if idioma else {}))
    duracao = time.time() - inicio

    texto = resultado["text"].strip()
    print(f"✅ Concluído em {duracao:.1f}s | Idioma: {resultado.get('language', '?')}")
    return texto


def salvar_transcricao(texto: str, nome_base: str, pasta: str):
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"{nome_base}_transcricao.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"💾 Transcrição salva: {os.path.abspath(caminho)}")


def exibir_transcricao(texto: str):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


# ══════════════════════════════════════════════════════════════════
#  Subcomando: yt
# ══════════════════════════════════════════════════════════════════

def cmd_yt(args):
    modo = args.modo

    if modo in ("audio", "video", "tudo"):
        verificar_imports(("yt_dlp", "yt-dlp"))
    if modo in ("transcrever", "tudo"):
        verificar_imports(("whisper", "openai-whisper"))
    if modo in ("audio", "video", "transcrever", "tudo") and not eh_url(args.entrada) and modo != "transcrever":
        verificar_imports(("yt_dlp", "yt-dlp"))

    entrada_eh_url = eh_url(args.entrada)

    # Só áudio
    if modo == "audio":
        if not entrada_eh_url:
            print("❌ Forneça uma URL do YouTube para o modo 'audio'.")
            sys.exit(1)
        yt_baixar_audio(args.entrada, args.pasta)
        print(f"📁 Pasta: {os.path.abspath(args.pasta)}")
        return

    # Só vídeo
    if modo == "video":
        if not entrada_eh_url:
            print("❌ Forneça uma URL do YouTube para o modo 'video'.")
            sys.exit(1)
        yt_baixar_video(args.entrada, args.qualidade, args.pasta)
        return

    # Transcrever (URL ou arquivo local)
    if modo == "transcrever":
        if entrada_eh_url:
            with tempfile.TemporaryDirectory() as tmp:
                arquivo, titulo = yt_baixar_audio(args.entrada, tmp)
                texto = transcrever_arquivo(arquivo, args.modelo, args.idioma)
        else:
            if not os.path.exists(args.entrada):
                print(f"❌ Arquivo não encontrado: {args.entrada}")
                sys.exit(1)
            titulo = os.path.splitext(os.path.basename(args.entrada))[0]
            texto = transcrever_arquivo(args.entrada, args.modelo, args.idioma)
        exibir_transcricao(texto)
        salvar_transcricao(texto, titulo, args.pasta)
        return

    # Tudo: baixa vídeo + transcreve
    if modo == "tudo":
        if not entrada_eh_url:
            print("❌ Forneça uma URL do YouTube para o modo 'tudo'.")
            sys.exit(1)
        yt_baixar_video(args.entrada, args.qualidade, args.pasta)
        with tempfile.TemporaryDirectory() as tmp:
            arquivo, titulo = yt_baixar_audio(args.entrada, tmp)
            texto = transcrever_arquivo(arquivo, args.modelo, args.idioma)
        exibir_transcricao(texto)
        salvar_transcricao(texto, titulo, args.pasta)


# ══════════════════════════════════════════════════════════════════
#  Subcomando: spotify
# ══════════════════════════════════════════════════════════════════

def cmd_spotify(args):
    verificar_imports(("spotdl", "spotdl"))

    if not eh_spotify(args.url):
        print("❌ URL inválida. Use um link do Spotify (https://open.spotify.com/...)")
        sys.exit(1)

    tipos = {"track": "música", "album": "álbum", "playlist": "playlist", "artist": "artista"}
    tipo = next((v for k, v in tipos.items() if k in args.url), "conteúdo")

    print(f"🎵 Baixando {tipo} do Spotify...")
    print(f"📁 Destino: {os.path.abspath(args.pasta)}")
    print(f"🎧 Formato: {args.formato} | Qualidade: {args.qualidade}kbps | Threads: {args.threads}\n")

    os.makedirs(args.pasta, exist_ok=True)
    cmd = [
        sys.executable, "-m", "spotdl", "download", args.url,
        "--format", args.formato,
        "--bitrate", f"{args.qualidade}k",
        "--output", os.path.join(args.pasta, "{artists} - {title}.{output-ext}"),
        "--threads", str(args.threads),
    ]
    if args.client_id:
        cmd += ["--client-id", args.client_id]
    if args.client_secret:
        cmd += ["--client-secret", args.client_secret]

    resultado = subprocess.run(cmd)
    if resultado.returncode == 0:
        print(f"\n✅ Download concluído! Arquivos em: {os.path.abspath(args.pasta)}")
    else:
        print("\n❌ Erro durante o download.")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════
#  Subcomando: transcrever
# ══════════════════════════════════════════════════════════════════

def cmd_transcrever(args):
    verificar_imports(("whisper", "openai-whisper"))

    if not os.path.exists(args.arquivo):
        print(f"❌ Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)

    titulo = os.path.splitext(os.path.basename(args.arquivo))[0]
    texto = transcrever_arquivo(args.arquivo, args.modelo, args.idioma)
    exibir_transcricao(texto)
    salvar_transcricao(texto, titulo, args.pasta)


# ══════════════════════════════════════════════════════════════════
#  Parser principal
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="mediacli",
        description="Download e transcrição de mídia — YouTube e Spotify",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python mediacli.py yt https://youtube.com/watch?v=XXX -m audio\n"
            "  python mediacli.py yt https://youtube.com/watch?v=XXX -m transcrever -l pt\n"
            "  python mediacli.py yt https://youtube.com/watch?v=XXX -m tudo -q 1080p\n"
            "  python mediacli.py spotify https://open.spotify.com/playlist/XXX -q 320\n"
            "  python mediacli.py transcrever audio.mp3 -l pt\n"
        )
    )

    sub = parser.add_subparsers(dest="comando", required=True)

    # ── yt ────────────────────────────────────────────────────────
    p_yt = sub.add_parser("yt", help="YouTube: baixar vídeo, áudio ou transcrever")
    p_yt.add_argument("entrada", help="URL do YouTube ou arquivo de áudio local")
    p_yt.add_argument(
        "-m", "--modo",
        default="transcrever",
        choices=["transcrever", "audio", "video", "tudo"],
        help="transcrever (padrão) | audio | video | tudo"
    )
    p_yt.add_argument("--modelo", default="base",
                      choices=["tiny", "base", "small", "medium", "large"],
                      help="Modelo Whisper (padrão: base)")
    p_yt.add_argument("-l", "--idioma", default=None,
                      help="Idioma do áudio, ex: 'pt', 'en'")
    p_yt.add_argument("-q", "--qualidade", default="melhor",
                      choices=["melhor", "1080p", "720p", "480p"],
                      help="Qualidade do vídeo (padrão: melhor)")
    p_yt.add_argument("-o", "--pasta", default="downloads",
                      help="Pasta de destino (padrão: ./downloads)")
    p_yt.set_defaults(func=cmd_yt)

    # ── spotify ───────────────────────────────────────────────────
    p_sp = sub.add_parser("spotify", help="Spotify: baixar músicas, álbuns e playlists")
    p_sp.add_argument("url", help="URL do Spotify")
    p_sp.add_argument("-f", "--formato", default="mp3",
                      choices=["mp3", "flac", "ogg", "opus", "m4a", "wav"],
                      help="Formato de saída (padrão: mp3)")
    p_sp.add_argument("-q", "--qualidade", default="192",
                      choices=["128", "192", "256", "320"],
                      help="Qualidade em kbps (padrão: 192)")
    p_sp.add_argument("-o", "--pasta", default="downloads",
                      help="Pasta de destino (padrão: ./downloads)")
    p_sp.add_argument("-t", "--threads", type=int, default=4,
                      help="Downloads simultâneos (padrão: 4)")
    p_sp.add_argument("--client-id", default=None,
                      help="Spotify Client ID (evita rate limit)")
    p_sp.add_argument("--client-secret", default=None,
                      help="Spotify Client Secret (evita rate limit)")
    p_sp.set_defaults(func=cmd_spotify)

    # ── transcrever ───────────────────────────────────────────────
    p_tr = sub.add_parser("transcrever", help="Transcrever um arquivo de áudio local")
    p_tr.add_argument("arquivo", help="Caminho para o arquivo de áudio")
    p_tr.add_argument("--modelo", default="base",
                      choices=["tiny", "base", "small", "medium", "large"],
                      help="Modelo Whisper (padrão: base)")
    p_tr.add_argument("-l", "--idioma", default=None,
                      help="Idioma do áudio, ex: 'pt', 'en'")
    p_tr.add_argument("-o", "--pasta", default="downloads",
                      help="Pasta para salvar a transcrição (padrão: ./downloads)")
    p_tr.set_defaults(func=cmd_transcrever)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()