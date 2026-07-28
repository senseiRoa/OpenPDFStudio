# OpenPDFStudio

Comprime archivos PDF localmente manteniendo la mejor calidad posible.

## Requisitos

- Python 3.11+
- Opcional: [Ghostscript](https://www.ghostscript.com/) (mejor compresión)

## Instalación

### De PyPI (cuando esté publicado)

```bash
pip install openpdfstudio
```

### Desde el repositorio

```bash
git clone https://github.com/andres/pdf-compressor.git
cd pdf-compressor

# Entorno virtual
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Modo desarrollo (instalación editable)
pip install -e .

# O directamente
pip install -r requirements.txt
```

## Uso

### CLI

```bash
# Básico
compress-pdf documento.pdf

# Con parámetros
compress-pdf documento.pdf --quality 50 --max-width 800

# Con los scripts del proyecto
python compress_pdf.py documento.pdf
```

### GUI

```bash
compress-pdf-gui
# o
python compress_gui.py
```

| Parámetro       | Default | Descripción                     |
|-----------------|---------|---------------------------------|
| `--quality`     | 70      | Calidad JPEG (1–100)            |
| `--max-width`   | 1000    | Ancho máximo de imagen en px    |
| `--overwrite`   | —       | Sobrescribir si existe          |
| `--verbose`     | —       | Log detallado                   |

## Cómo funciona

1. **Ghostscript** — si está instalado, re-comprime imágenes con su motor profesional.
2. **PyMuPDF + Pillow** — fallback. Extrae cada imagen original, la re-comprime como JPEG a la calidad deseada, y reconstruye el PDF desde cero.

El archivo original nunca se modifica.

## Estructura

```
pdf-compressor/
├── src/pdf_compressor/
│   ├── __init__.py
│   ├── __main__.py       # python -m pdf_compressor
│   ├── core.py           # Motor de compresión
│   ├── cli.py            # Interfaz CLI
│   └── gui.py            # Interfaz gráfica (ttkbootstrap)
├── compress_pdf.py       # Wrapper CLI (legacy)
├── compress_gui.py       # Wrapper GUI (legacy)
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Publicar en PyPI (mantenedores)

```bash
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```
