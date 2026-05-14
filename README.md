````md
<div align="center">

# MediaCLI

### Download, conversão e transcrição de mídia em uma única CLI.

Baixe vídeos, extraia áudio e transcreva conteúdos do YouTube, SoundCloud, TikTok e outras plataformas com uma interface simples, rápida e extensível.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.14+-blue.svg">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-black">
  <img src="https://img.shields.io/badge/license-MIT-green">
  <img src="https://img.shields.io/badge/yt--dlp-powered-red">
  <img src="https://img.shields.io/badge/whisper-transcription-orange">
</p>

</div>

---

## ✨ Features

- 🎥 Download de vídeos em múltiplas qualidades
- 🎵 Extração de áudio em alta qualidade
- 🧠 Transcrição automática com Whisper
- 🌎 Detecção automática de idioma
- ⚡ CLI simples e rápida
- 🖥 Interface gráfica com Tkinter
- 📂 Suporte para arquivos locais
- 🔧 Estrutura modular e extensível
- 🧵 Execução assíncrona na GUI (sem travamentos)

---

## 📦 Tecnologias

| Tecnologia | Função |
|---|---|
| `yt-dlp` | Download de mídia |
| `openai-whisper` | Transcrição de áudio |
| `ffmpeg` | Conversão/processamento multimídia |
| `tkinter` | Interface gráfica |
| `uv` | Gerenciamento de dependências |

---

# 🚀 Quick Start

```bash
# baixar áudio
mediacli yt <url> -m audio

# baixar vídeo
mediacli yt <url> -m video

# transcrever conteúdo
mediacli yt <url> -m transcrever
````

---

# 📋 Requisitos

* Python `>= 3.14`
* `uv`
* `ffmpeg`

---

## Instalação do FFmpeg

### Windows

```bash
winget install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install ffmpeg
```

---

# ⚙️ Instalação

Clone o repositório:

```bash
git clone https://github.com/lucxslv/mediacli
cd mediacli
```

Instale as dependências:

```bash
uv sync
```

---

# 🗂 Estrutura do Projeto

```txt
mediacli/
├── mediacli.py       # CLI principal
├── mediagui.py       # Interface gráfica
├── downloads/        # Arquivos baixados
├── pyproject.toml    # Dependências/configuração
└── README.md
```

---

# 🖥 CLI

## YouTube / URLs

```bash
uv run mediacli.py yt <url> [opções]
```

### Opções

| Flag                | Valores                                | Padrão        | Descrição          |
| ------------------- | -------------------------------------- | ------------- | ------------------ |
| `-m`, `--modo`      | `audio` `video` `transcrever` `tudo`   | `transcrever` | Define a operação  |
| `--modelo`          | `tiny` `base` `small` `medium` `large` | `base`        | Modelo Whisper     |
| `-l`, `--idioma`    | `pt` `en` `es` ...                     | `auto`        | Idioma do áudio    |
| `-q`, `--qualidade` | `melhor` `1080p` `720p` `480p`         | `melhor`      | Qualidade do vídeo |
| `-o`, `--pasta`     | caminho                                | `./downloads` | Pasta de saída     |

---

## Exemplos

### 🎵 Baixar apenas áudio

```bash
uv run mediacli.py yt https://youtube.com/watch?v=XXX -m audio
```

### 🎥 Baixar vídeo em 1080p

```bash
uv run mediacli.py yt https://youtube.com/watch?v=XXX -m video -q 1080p
```

### 🧠 Transcrever vídeo do YouTube

```bash
uv run mediacli.py yt https://youtube.com/watch?v=XXX -m transcrever -l pt
```

### 📂 Transcrever arquivo local

```bash
uv run mediacli.py yt ./audio.mp3 -m transcrever --modelo medium
```

### 🔥 Baixar + transcrever automaticamente

```bash
uv run mediacli.py yt https://youtube.com/watch?v=XXX -m tudo
```

---

# 🎙 Transcrever Arquivos Locais

```bash
uv run mediacli.py transcrever <arquivo> [opções]
```

## Exemplos

```bash
uv run mediacli.py transcrever audio.mp3
```

```bash
uv run mediacli.py transcrever gravacao.wav --modelo large -l pt
```

---

# 🖼 Interface Gráfica

Execute:

```bash
uv run mediagui.py
```

A GUI oferece as mesmas funcionalidades da CLI em uma interface simples e intuitiva.

## Funcionalidades

* ▶ Download de vídeos
* 🎵 Extração de áudio
* 🧠 Transcrição local ou via URL
* 📜 Logs em tempo real
* 🧵 Operações executadas em threads separadas

---

# 🧠 Modelos Whisper

| Modelo   | Velocidade | Precisão | RAM Aproximada |
| -------- | ---------- | -------- | -------------- |
| `tiny`   | ⚡⚡⚡⚡       | ★☆☆☆☆    | ~1 GB          |
| `base`   | ⚡⚡⚡        | ★★☆☆☆    | ~1 GB          |
| `small`  | ⚡⚡         | ★★★☆☆    | ~2 GB          |
| `medium` | ⚡          | ★★★★☆    | ~5 GB          |
| `large`  | 🐢         | ★★★★★    | ~10 GB         |

> Para português, `base` e `small` costumam oferecer o melhor equilíbrio entre velocidade e precisão.

---

# 📚 Dependências Principais

| Pacote           | Versão         |
| ---------------- | -------------- |
| `openai-whisper` | `>= 20250625`  |
| `yt-dlp`         | `>= 2026.3.17` |

---

# 🔮 Roadmap

* [ ] Suporte nativo ao SoundCloud
* [ ] Suporte ao TikTok
* [ ] Download de playlists
* [ ] Legendas automáticas `.srt`
* [ ] Exportação `.txt` / `.json`
* [ ] Interface Web
* [ ] Paralelismo de downloads
* [ ] Empacotamento binário standalone

---

# 🤝 Contribuição

Pull requests são bem-vindos.

Se quiser contribuir:

```bash
# fork
# crie uma branch
git checkout -b feature/minha-feature

# commit
git commit -m "feat: adiciona nova feature"

# push
git push origin feature/minha-feature
```

---

# 📄 Licença

Distribuído sob licença MIT.

Veja `LICENSE` para mais informações.

---

<div align="center">

### MediaCLI — simples por fora, brutal por dentro.

</div>
```
