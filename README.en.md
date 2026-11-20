<div align="center">

[Русский](README.md) · **English**

![IMAGESTEG — Hidden in plain sight](docs/assets/imagesteg-hero.png)

**Secret text. Ordinary image.**

Hide messages in pixels and retrieve them with a single command.

![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-0d1117?style=flat-square&logo=python&logoColor=67e8f9)
![Pillow 11.2.1+](https://img.shields.io/badge/Pillow-11.2.1%2B-0d1117?style=flat-square&labelColor=161b22)
![LSB method](https://img.shields.io/badge/method-LSB-22d3ee?style=flat-square&labelColor=161b22)
![PNG output](https://img.shields.io/badge/output-PNG-2dd4bf?style=flat-square&labelColor=161b22)

[Quick start](#quick-start) · [How it works](#how-it-works) · [Commands](#commands) · [Testing](#testing)

</div>

---

## Beneath the surface

**IMAGESTEG** is a small Python utility for LSB steganography. It writes text into the least significant bits of an image’s color channels: the changes are minimal and usually imperceptible to the human eye. Use it to experiment with images and learn about hidden data transmission.

| Feature | Details |
| :--- | :--- |
| UTF-8 text | Cyrillic, Latin characters, and emoji |
| RGB and RGBA support | The alpha channel is preserved; other modes are converted to RGB |
| PNG output | Preserves the bits carrying the hidden message |
| Terminal report | Image dimensions, text size, and container usage |

## Quick start

Requires **Python 3.13+**. Run the commands from the project directory.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the dependency:

```bash
python -m pip install "Pillow>=11.2.1"
```

**01 · Hide a message**

Place your source image, `my_photo.png`, in the project directory and run:

```bash
python imagesteg.py --input my_photo.png --output hidden_message.png --message "Hello! This is a secret message."
```

**02 · Read it back**

```bash
python imagesteg.py --decode --input hidden_message.png
```

<details>
<summary>Using uv?</summary>

Install dependencies from the lockfile and run commands with `uv run`:

```bash
uv sync --locked
uv run python imagesteg.py --input my_photo.png --output hidden_message.png --message "Hello! This is a secret message."
uv run python imagesteg.py --decode --input hidden_message.png
```

</details>

## How it works

![Conceptual illustration: data hidden in the least significant bits of RGB pixels](docs/assets/imagesteg-pixels.png)

Each pixel contains **R**, **G**, and **B** channels. The utility replaces the last bit of each channel with one bit of the message. A channel value changes by at most one; transparency remains untouched.

```text
Text → UTF-8 bytes → bits → RGB least significant bits → PNG
                                                        │
Text ← UTF-8 decoding ← reading least significant bits ←─┘
```

For example, writing the bit `1` into a channel with the value `11001010` produces `11001011`: **202 → 203**.

A null byte is appended to mark the end of the message. The decoder reads the least significant bits in the same order and stops at this marker.

**Capacity** depends on the number of pixels:

```text
maximum text bytes = floor(width × height × 3 / 8) − 1
```

One byte is reserved for the end marker. For example, a **100 × 100 px** image can hold up to **3,749 bytes** of text. This counts UTF-8 bytes, not characters: Cyrillic characters and emoji take more than one byte.

## Commands

| Argument | Purpose |
| :--- | :--- |
| `--input` | Path to the source image or PNG with hidden text; required |
| `--output` | Output path ending in `.png`; required when encoding |
| `--message` | Text to embed; required when encoding |
| `--decode` | Extract a message instead of writing one |
| `--help` | Show help and examples |

### Terminal output

The utility currently displays terminal messages in Russian. Here is a sample report for a 100 × 100 px image and the message `Привет` (12 UTF-8 bytes):

```text
+--- IMAGESTEG / МИССИЯ ВЫПОЛНЕНА ---+
  Контейнер: 100 x 100 px
  Спрятано: 12 байт текста
  Заполнение: [........................] 0.3%
  Файл: hidden_message.png
  Пиксели хранят ваш секрет.
+--------------------------------------------+
```

The report shows image dimensions, embedded text size, container usage, and the output path. In an interactive terminal, the border appears in cyan; ANSI codes are disabled when output is redirected. Errors go to `stderr` with exit code `1`.

## Things to keep in mind

> **Steganography conceals the presence of text but does not encrypt it.** Anyone who knows the embedding method can extract the message. Password protection is not implemented in the current version.

- Save and share the result as the **original PNG file**. JPEG compression, resizing, and image processing can destroy the message; image-sharing services may recompress uploads.
- Text must not contain a null character (`\0`): it is used as the end marker.
- Finding an end marker does not authenticate the message. An ordinary image may occasionally be interpreted as text by chance.
- Text size is checked before writing: if the image is too small, the utility reports an error.

## Disclaimer

> This project is intended for learning and research experiments. Use it only for lawful purposes and with files you are authorized to process and share. Users are responsible for how they use the utility and for the data they transmit.
>
> The utility is provided “as is,” without guarantees of data preservation, confidentiality, or the hidden message remaining undetected. Do not rely on it as the sole means of protecting sensitive information, and keep backups of your original files.

## Testing

```bash
python -m unittest discover -s tests
```

Tests cover text encoding and decoding, alpha channel preservation, invalid inputs, and images without a message.

<details>
<summary>Ideas for future development</summary>

- Password-based message encryption before embedding.
- A header containing data length and an integrity check.
- Exploring other ways to distribute bits within an image.

These are possible future directions, not features of the current version.

</details>

---

<div align="center">
<sub>IMAGESTEG · Python / Pillow / LSB · Pixels keep your secret.</sub>
</div>
