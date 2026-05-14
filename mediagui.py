#!/usr/bin/env python3
"""
mediagui — Interface gráfica para o mediacli
Uso: python mediagui.py
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext


# ══════════════════════════════════════════════════════════════════
#  Cores e estilos
# ══════════════════════════════════════════════════════════════════

CORES = {
    "bg":           "#0f0f0f",
    "surface":      "#1a1a1a",
    "surface2":     "#242424",
    "border":       "#2e2e2e",
    "accent_yt":    "#ff0000",
    "accent_sp":    "#1db954",
    "accent_tr":    "#a78bfa",
    "text":         "#f0f0f0",
    "text_dim":     "#888888",
    "text_dimmer":  "#555555",
    "success":      "#22c55e",
    "error":        "#ef4444",
    "warning":      "#f59e0b",
}

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_LABEL  = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 9)
FONT_MONO   = ("Courier New", 9)
FONT_BTN    = ("Courier New", 10, "bold")
FONT_TAB    = ("Courier New", 11, "bold")


# ══════════════════════════════════════════════════════════════════
#  Widgets customizados
# ══════════════════════════════════════════════════════════════════

class StyledEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            bg=CORES["surface2"],
            fg=CORES["text"],
            insertbackground=CORES["text"],
            relief="flat",
            bd=0,
            font=FONT_MONO,
            **kwargs
        )
        self._placeholder = placeholder
        self._has_placeholder = False
        if placeholder:
            self._set_placeholder()
            self.bind("<FocusIn>",  self._clear_placeholder)
            self.bind("<FocusOut>", self._restore_placeholder)

    def _set_placeholder(self):
        self.insert(0, self._placeholder)
        self.config(fg=CORES["text_dimmer"])
        self._has_placeholder = True

    def _clear_placeholder(self, _=None):
        if self._has_placeholder:
            self.delete(0, "end")
            self.config(fg=CORES["text"])
            self._has_placeholder = False

    def _restore_placeholder(self, _=None):
        if not self.get():
            self._set_placeholder()

    def get_value(self):
        return "" if self._has_placeholder else self.get()


class StyledCombo(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=FONT_MONO, state="readonly", **kwargs)
        self.configure(background=CORES["surface2"])


class StyledButton(tk.Button):
    def __init__(self, parent, accent=None, **kwargs):
        color = accent or CORES["accent_tr"]
        super().__init__(
            parent,
            bg=color,
            fg="#000000",
            activebackground=color,
            activeforeground="#000000",
            relief="flat",
            bd=0,
            font=FONT_BTN,
            cursor="hand2",
            padx=16,
            pady=8,
            **kwargs
        )
        self.bind("<Enter>", lambda _: self.config(bg=self._lighten(color)))
        self.bind("<Leave>", lambda _: self.config(bg=color))

    @staticmethod
    def _lighten(hex_color):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r, g, b = min(255, r + 30), min(255, g + 30), min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"


def label(parent, text, font=FONT_LABEL, fg=None, **kwargs):
    return tk.Label(
        parent, text=text, font=font,
        fg=fg or CORES["text_dim"],
        bg=CORES["surface"],
        **kwargs
    )


def separator(parent):
    return tk.Frame(parent, bg=CORES["border"], height=1)


# ══════════════════════════════════════════════════════════════════
#  Painel de log compartilhado
# ══════════════════════════════════════════════════════════════════

class LogPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CORES["bg"])
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=CORES["bg"])
        header.pack(fill="x", pady=(0, 6))

        tk.Label(header, text="► LOG", font=FONT_SMALL,
                 fg=CORES["text_dimmer"], bg=CORES["bg"]).pack(side="left")

        tk.Button(header, text="limpar", font=FONT_SMALL,
                  fg=CORES["text_dimmer"], bg=CORES["bg"],
                  activebackground=CORES["bg"], activeforeground=CORES["text"],
                  relief="flat", bd=0, cursor="hand2",
                  command=self.clear).pack(side="right")

        self.text = scrolledtext.ScrolledText(
            self,
            bg=CORES["surface"],
            fg=CORES["text"],
            font=FONT_MONO,
            relief="flat",
            bd=0,
            wrap="word",
            height=12,
            state="disabled",
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("ok",      foreground=CORES["success"])
        self.text.tag_config("erro",    foreground=CORES["error"])
        self.text.tag_config("aviso",   foreground=CORES["warning"])
        self.text.tag_config("info",    foreground=CORES["text_dim"])
        self.text.tag_config("destaque",foreground=CORES["text"])

    def write(self, msg, tag="info"):
        self.text.config(state="normal")
        self.text.insert("end", msg + "\n", tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


# ══════════════════════════════════════════════════════════════════
#  Aba YouTube
# ══════════════════════════════════════════════════════════════════

class AbaYT(tk.Frame):
    def __init__(self, parent, log: LogPanel):
        super().__init__(parent, bg=CORES["surface"])
        self.log = log
        self._build()

    def _build(self):
        pad = {"padx": 20, "pady": 6}

        # URL
        label(self, "URL do YouTube ou arquivo local").pack(anchor="w", **pad)
        url_frame = tk.Frame(self, bg=CORES["surface"])
        url_frame.pack(fill="x", padx=20, pady=(0, 6))

        self.entry_url = StyledEntry(url_frame, placeholder="https://youtube.com/watch?v=...")
        self.entry_url.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

        tk.Button(
            url_frame, text="📂", font=FONT_BTN,
            bg=CORES["surface2"], fg=CORES["text"],
            activebackground=CORES["border"], relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._escolher_arquivo
        ).pack(side="left", ipady=6)

        separator(self).pack(fill="x", padx=20, pady=4)

        # Opções em grid
        opts = tk.Frame(self, bg=CORES["surface"])
        opts.pack(fill="x", **pad)

        def col(text, row, col_, widget_fn):
            label(opts, text).grid(row=row*2,   column=col_, sticky="w", padx=(0, 24))
            widget_fn().grid(       row=row*2+1, column=col_, sticky="ew", padx=(0, 24), pady=(2, 10))

        # Modo
        self.modo = tk.StringVar(value="transcrever")
        col("MODO", 0, 0, lambda: StyledCombo(
            opts, textvariable=self.modo, width=14,
            values=["transcrever", "audio", "video", "tudo"]
        ))

        # Qualidade
        self.qualidade = tk.StringVar(value="melhor")
        col("QUALIDADE", 0, 1, lambda: StyledCombo(
            opts, textvariable=self.qualidade, width=10,
            values=["melhor", "1080p", "720p", "480p"]
        ))

        # Modelo Whisper
        self.modelo = tk.StringVar(value="base")
        col("MODELO WHISPER", 0, 2, lambda: StyledCombo(
            opts, textvariable=self.modelo, width=10,
            values=["tiny", "base", "small", "medium", "large"]
        ))

        # Idioma
        self.idioma = tk.StringVar(value="auto")
        col("IDIOMA", 0, 3, lambda: StyledCombo(
            opts, textvariable=self.idioma, width=8,
            values=["auto", "pt", "en", "es", "fr", "de", "it", "ja", "zh"]
        ))

        # Pasta
        separator(self).pack(fill="x", padx=20, pady=4)
        label(self, "PASTA DE DESTINO").pack(anchor="w", **pad)
        pasta_frame = tk.Frame(self, bg=CORES["surface"])
        pasta_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.entry_pasta = StyledEntry(pasta_frame, placeholder="downloads")
        self.entry_pasta.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

        tk.Button(
            pasta_frame, text="📁", font=FONT_BTN,
            bg=CORES["surface2"], fg=CORES["text"],
            activebackground=CORES["border"], relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._escolher_pasta
        ).pack(side="left", ipady=6)

        # Botão
        self.btn = StyledButton(self, text="▶  EXECUTAR", accent=CORES["accent_yt"],
                                command=self._executar)
        self.btn.pack(pady=12)

    def _escolher_arquivo(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de áudio",
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a *.ogg *.flac"), ("Todos", "*.*")]
        )
        if path:
            self.entry_url._clear_placeholder()
            self.entry_url.delete(0, "end")
            self.entry_url.insert(0, path)
            self.entry_url.config(fg=CORES["text"])

    def _escolher_pasta(self):
        path = filedialog.askdirectory(title="Selecionar pasta de destino")
        if path:
            self.entry_pasta._clear_placeholder()
            self.entry_pasta.delete(0, "end")
            self.entry_pasta.insert(0, path)
            self.entry_pasta.config(fg=CORES["text"])

    def _executar(self):
        entrada = self.entry_url.get_value().strip()
        if not entrada:
            self.log.write("❌ Informe uma URL ou arquivo.", "erro")
            return

        pasta   = self.entry_pasta.get_value().strip() or "downloads"
        modo    = self.modo.get()
        modelo  = self.modelo.get()
        idioma  = None if self.idioma.get() == "auto" else self.idioma.get()
        qual    = self.qualidade.get()

        self.btn.config(state="disabled", text="⏳ Aguarde...")
        threading.Thread(
            target=self._rodar,
            args=(entrada, modo, modelo, idioma, qual, pasta),
            daemon=True
        ).start()

    def _rodar(self, entrada, modo, modelo, idioma, qualidade, pasta):
        try:
            # importa aqui pra evitar travar a GUI
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from mediacli import (
                yt_baixar_audio, yt_baixar_video,
                transcrever_arquivo, salvar_transcricao,
                eh_url
            )
            import tempfile

            self.log.write(f"\n▶ YouTube | modo={modo} | pasta={pasta}", "destaque")
            entrada_eh_url = eh_url(entrada)

            if modo == "audio":
                yt_baixar_audio(entrada, pasta)
                self.log.write(f"✅ Áudio salvo em: {os.path.abspath(pasta)}", "ok")

            elif modo == "video":
                yt_baixar_video(entrada, qualidade, pasta)
                self.log.write(f"✅ Vídeo salvo em: {os.path.abspath(pasta)}", "ok")

            elif modo == "transcrever":
                if entrada_eh_url:
                    with tempfile.TemporaryDirectory() as tmp:
                        arquivo, titulo = yt_baixar_audio(entrada, tmp)
                        texto = transcrever_arquivo(arquivo, modelo, idioma)
                else:
                    titulo = os.path.splitext(os.path.basename(entrada))[0]
                    texto = transcrever_arquivo(entrada, modelo, idioma)
                salvar_transcricao(texto, titulo, pasta)
                self.log.write("─" * 50, "info")
                self.log.write(texto[:1000] + ("..." if len(texto) > 1000 else ""), "destaque")
                self.log.write(f"✅ Transcrição salva em: {os.path.abspath(pasta)}", "ok")

            elif modo == "tudo":
                yt_baixar_video(entrada, qualidade, pasta)
                with tempfile.TemporaryDirectory() as tmp:
                    arquivo, titulo = yt_baixar_audio(entrada, tmp)
                    texto = transcrever_arquivo(arquivo, modelo, idioma)
                salvar_transcricao(texto, titulo, pasta)
                self.log.write(f"✅ Concluído! Arquivos em: {os.path.abspath(pasta)}", "ok")

        except Exception as e:
            self.log.write(f"❌ Erro: {e}", "erro")
        finally:
            self.btn.config(state="normal", text="▶  EXECUTAR")


# ══════════════════════════════════════════════════════════════════
#  Aba Spotify
# ══════════════════════════════════════════════════════════════════

class AbaSpotify(tk.Frame):
    def __init__(self, parent, log: LogPanel):
        super().__init__(parent, bg=CORES["surface"])
        self.log = log
        self._build()

    def _build(self):
        pad = {"padx": 20, "pady": 6}

        label(self, "URL DO SPOTIFY").pack(anchor="w", **pad)
        self.entry_url = StyledEntry(self, placeholder="https://open.spotify.com/...")
        self.entry_url.pack(fill="x", padx=20, pady=(0, 8), ipady=8)

        separator(self).pack(fill="x", padx=20, pady=4)

        opts = tk.Frame(self, bg=CORES["surface"])
        opts.pack(fill="x", **pad)

        def col(text, col_, widget_fn):
            label(opts, text).grid(row=0, column=col_, sticky="w", padx=(0, 24))
            widget_fn().grid(       row=1, column=col_, sticky="ew", padx=(0, 24), pady=(2, 10))

        self.formato = tk.StringVar(value="mp3")
        col("FORMATO", 0, lambda: StyledCombo(
            opts, textvariable=self.formato, width=10,
            values=["mp3", "flac", "ogg", "opus", "m4a", "wav"]
        ))

        self.qualidade = tk.StringVar(value="192")
        col("QUALIDADE", 1, lambda: StyledCombo(
            opts, textvariable=self.qualidade, width=10,
            values=["128", "192", "256", "320"]
        ))

        self.threads = tk.StringVar(value="4")
        col("THREADS", 2, lambda: StyledCombo(
            opts, textvariable=self.threads, width=6,
            values=["1", "2", "4", "8"]
        ))

        separator(self).pack(fill="x", padx=20, pady=4)
        label(self, "PASTA DE DESTINO").pack(anchor="w", **pad)
        pasta_frame = tk.Frame(self, bg=CORES["surface"])
        pasta_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.entry_pasta = StyledEntry(pasta_frame, placeholder="downloads")
        self.entry_pasta.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

        tk.Button(
            pasta_frame, text="📁", font=FONT_BTN,
            bg=CORES["surface2"], fg=CORES["text"],
            activebackground=CORES["border"], relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._escolher_pasta
        ).pack(side="left", ipady=6)

        self.btn = StyledButton(self, text="▶  BAIXAR", accent=CORES["accent_sp"],
                                command=self._executar)
        self.btn.pack(pady=12)

    def _escolher_pasta(self):
        path = filedialog.askdirectory(title="Selecionar pasta de destino")
        if path:
            self.entry_pasta._clear_placeholder()
            self.entry_pasta.delete(0, "end")
            self.entry_pasta.insert(0, path)
            self.entry_pasta.config(fg=CORES["text"])

    def _executar(self):
        url = self.entry_url.get_value().strip()
        if not url:
            self.log.write("❌ Informe uma URL do Spotify.", "erro")
            return
        if "open.spotify.com" not in url:
            self.log.write("❌ URL inválida. Use https://open.spotify.com/...", "erro")
            return

        pasta    = self.entry_pasta.get_value().strip() or "downloads"
        formato  = self.formato.get()
        qualidade = self.qualidade.get()
        threads  = int(self.threads.get())

        self.btn.config(state="disabled", text="⏳ Baixando...")
        threading.Thread(
            target=self._rodar,
            args=(url, formato, qualidade, pasta, threads),
            daemon=True
        ).start()

    def _rodar(self, url, formato, qualidade, pasta, threads):
        import subprocess
        try:
            self.log.write(f"\n▶ Spotify | {formato} {qualidade}kbps | threads={threads}", "destaque")
            os.makedirs(pasta, exist_ok=True)
            cmd = [
                sys.executable, "-m", "spotdl", "download", url,
                "--format", formato,
                "--bitrate", f"{qualidade}k",
                "--output", os.path.join(pasta, "{artists} - {title}.{output-ext}"),
                "--threads", str(threads),
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True)
            if resultado.stdout:
                for linha in resultado.stdout.splitlines():
                    self.log.write(linha, "info")
            if resultado.returncode == 0:
                self.log.write(f"✅ Download concluído! Arquivos em: {os.path.abspath(pasta)}", "ok")
            else:
                self.log.write(f"❌ Erro: {resultado.stderr}", "erro")
        except Exception as e:
            self.log.write(f"❌ Erro: {e}", "erro")
        finally:
            self.btn.config(state="normal", text="▶  BAIXAR")


# ══════════════════════════════════════════════════════════════════
#  Aba Transcrever
# ══════════════════════════════════════════════════════════════════

class AbaTranscrever(tk.Frame):
    def __init__(self, parent, log: LogPanel):
        super().__init__(parent, bg=CORES["surface"])
        self.log = log
        self._build()

    def _build(self):
        pad = {"padx": 20, "pady": 6}

        label(self, "ARQUIVO DE ÁUDIO").pack(anchor="w", **pad)
        arq_frame = tk.Frame(self, bg=CORES["surface"])
        arq_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_arq = StyledEntry(arq_frame, placeholder="Selecione um arquivo de áudio...")
        self.entry_arq.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

        tk.Button(
            arq_frame, text="📂", font=FONT_BTN,
            bg=CORES["surface2"], fg=CORES["text"],
            activebackground=CORES["border"], relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._escolher_arquivo
        ).pack(side="left", ipady=6)

        separator(self).pack(fill="x", padx=20, pady=4)

        opts = tk.Frame(self, bg=CORES["surface"])
        opts.pack(fill="x", **pad)

        self.modelo = tk.StringVar(value="base")
        label(opts, "MODELO WHISPER").grid(row=0, column=0, sticky="w", padx=(0, 24))
        StyledCombo(opts, textvariable=self.modelo, width=12,
                    values=["tiny", "base", "small", "medium", "large"]
                    ).grid(row=1, column=0, sticky="ew", padx=(0, 24), pady=(2, 10))

        self.idioma = tk.StringVar(value="auto")
        label(opts, "IDIOMA").grid(row=0, column=1, sticky="w", padx=(0, 24))
        StyledCombo(opts, textvariable=self.idioma, width=10,
                    values=["auto", "pt", "en", "es", "fr", "de", "it", "ja", "zh"]
                    ).grid(row=1, column=1, sticky="ew", padx=(0, 24), pady=(2, 10))

        separator(self).pack(fill="x", padx=20, pady=4)
        label(self, "PASTA DE DESTINO").pack(anchor="w", **pad)
        pasta_frame = tk.Frame(self, bg=CORES["surface"])
        pasta_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.entry_pasta = StyledEntry(pasta_frame, placeholder="downloads")
        self.entry_pasta.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        tk.Button(
            pasta_frame, text="📁", font=FONT_BTN,
            bg=CORES["surface2"], fg=CORES["text"],
            activebackground=CORES["border"], relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._escolher_pasta
        ).pack(side="left", ipady=6)

        self.btn = StyledButton(self, text="▶  TRANSCREVER", accent=CORES["accent_tr"],
                                command=self._executar)
        self.btn.pack(pady=12)

    def _escolher_arquivo(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de áudio",
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a *.ogg *.flac"), ("Todos", "*.*")]
        )
        if path:
            self.entry_arq._clear_placeholder()
            self.entry_arq.delete(0, "end")
            self.entry_arq.insert(0, path)
            self.entry_arq.config(fg=CORES["text"])

    def _escolher_pasta(self):
        path = filedialog.askdirectory(title="Selecionar pasta de destino")
        if path:
            self.entry_pasta._clear_placeholder()
            self.entry_pasta.delete(0, "end")
            self.entry_pasta.insert(0, path)
            self.entry_pasta.config(fg=CORES["text"])

    def _executar(self):
        arquivo = self.entry_arq.get_value().strip()
        if not arquivo:
            self.log.write("❌ Selecione um arquivo de áudio.", "erro")
            return
        if not os.path.exists(arquivo):
            self.log.write(f"❌ Arquivo não encontrado: {arquivo}", "erro")
            return

        pasta  = self.entry_pasta.get_value().strip() or "downloads"
        modelo = self.modelo.get()
        idioma = None if self.idioma.get() == "auto" else self.idioma.get()

        self.btn.config(state="disabled", text="⏳ Transcrevendo...")
        threading.Thread(
            target=self._rodar,
            args=(arquivo, modelo, idioma, pasta),
            daemon=True
        ).start()

    def _rodar(self, arquivo, modelo, idioma, pasta):
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from mediacli import transcrever_arquivo, salvar_transcricao

            self.log.write(f"\n▶ Transcrevendo: {os.path.basename(arquivo)}", "destaque")
            titulo = os.path.splitext(os.path.basename(arquivo))[0]
            texto = transcrever_arquivo(arquivo, modelo, idioma)
            salvar_transcricao(texto, titulo, pasta)
            self.log.write("─" * 50, "info")
            self.log.write(texto[:1000] + ("..." if len(texto) > 1000 else ""), "destaque")
            self.log.write(f"✅ Salvo em: {os.path.abspath(pasta)}", "ok")
        except Exception as e:
            self.log.write(f"❌ Erro: {e}", "erro")
        finally:
            self.btn.config(state="normal", text="▶  TRANSCREVER")


# ══════════════════════════════════════════════════════════════════
#  Janela principal
# ══════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mediacli")
        self.configure(bg=CORES["bg"])
        self.geometry("780x720")
        self.minsize(680, 600)
        self._estilizar_ttk()
        self._build()

    def _estilizar_ttk(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=CORES["surface2"],
                        background=CORES["surface2"],
                        foreground=CORES["text"],
                        arrowcolor=CORES["text_dim"],
                        bordercolor=CORES["border"],
                        lightcolor=CORES["surface2"],
                        darkcolor=CORES["surface2"],
                        selectbackground=CORES["border"],
                        selectforeground=CORES["text"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", CORES["surface2"])],
                  background=[("readonly", CORES["surface2"])])

    def _build(self):
        # Header
        header = tk.Frame(self, bg=CORES["bg"], pady=16)
        header.pack(fill="x", padx=24)

        tk.Label(header, text="MEDIA", font=FONT_TITLE,
                 fg=CORES["text"], bg=CORES["bg"]).pack(side="left")
        tk.Label(header, text="CLI", font=FONT_TITLE,
                 fg=CORES["accent_yt"], bg=CORES["bg"]).pack(side="left")
        tk.Label(header, text="  /  download & transcrição", font=FONT_SMALL,
                 fg=CORES["text_dimmer"], bg=CORES["bg"]).pack(side="left", padx=(8, 0))

        tk.Frame(self, bg=CORES["border"], height=1).pack(fill="x")

        # Notebook (abas)
        nb_frame = tk.Frame(self, bg=CORES["bg"])
        nb_frame.pack(fill="x")

        self._abas = {}
        self._aba_ativa = tk.StringVar(value="yt")
        self._btn_abas = {}

        abas_def = [
            ("yt",          "▶ YouTube",     CORES["accent_yt"]),
            ("transcrever", "✦ Transcrever", CORES["accent_tr"]),
        ]

        tab_bar = tk.Frame(self, bg=CORES["bg"])
        tab_bar.pack(fill="x")

        for key, texto, cor in abas_def:
            btn = tk.Button(
                tab_bar, text=texto, font=FONT_TAB,
                fg=CORES["text_dim"], bg=CORES["bg"],
                activebackground=CORES["bg"], activeforeground=cor,
                relief="flat", bd=0, cursor="hand2",
                padx=20, pady=12,
                command=lambda k=key, c=cor: self._trocar_aba(k, c)
            )
            btn.pack(side="left")
            self._btn_abas[key] = (btn, cor)

        tk.Frame(self, bg=CORES["border"], height=1).pack(fill="x")

        # Container das abas
        self._container = tk.Frame(self, bg=CORES["surface"])
        self._container.pack(fill="both", expand=True, padx=0, pady=0)

        # Log
        tk.Frame(self, bg=CORES["border"], height=1).pack(fill="x")
        self.log = LogPanel(self)
        self.log.pack(fill="both", padx=16, pady=12)

        # Instancia as abas
        self._abas["yt"]          = AbaYT(self._container, self.log)
        self._abas["transcrever"] = AbaTranscrever(self._container, self.log)

        self._trocar_aba("yt", CORES["accent_yt"])
        self.log.write("mediacli pronto. Selecione uma aba e configure sua operação.", "info")

    def _trocar_aba(self, key, cor):
        for frame in self._abas.values():
            frame.pack_forget()
        self._abas[key].pack(fill="both", expand=True, padx=0, pady=0)
        self._aba_ativa.set(key)

        for k, (btn, c) in self._btn_abas.items():
            if k == key:
                btn.config(fg=c, bg=CORES["surface"],
                           relief="flat",
                           borderwidth=0)
            else:
                btn.config(fg=CORES["text_dim"], bg=CORES["bg"])


if __name__ == "__main__":
    app = App()
    app.mainloop()