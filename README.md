# OpenPDFStudio

> **A modern open-source toolkit for PDF processing, optimization and automation.**

OpenPDFStudio is an extensible collection of tools for working with PDF documents.

The project is focused on providing fast, lightweight, and automation-friendly utilities that can be used from the command line, integrated into scripts, or embedded into larger workflows.

The first release focuses on **high-quality PDF compression**, with many more capabilities planned for future releases.

---

## Features

### Available

- Compress PDF files
- Reduce document size
- Optimize embedded images
- Preserve document quality
- Cross-platform support
- Command Line Interface (CLI)
- Modern Graphical User Interface (GUI)

---

### Planned Features

- Merge PDF files
- Split PDF documents
- Extract pages
- Delete pages
- Rotate pages
- Reorder pages
- Compress folders
- Batch processing
- OCR support
- PDF → Markdown
- PDF → Images
- Images → PDF
- Extract images
- Extract text
- Watermarks
- Password protection
- Metadata editor
- Digital signatures
- REST API
- Docker support
- Python package
- MCP Server
- AI Agent integration
- Windmill integration
- LangChain integration
- OpenCode integration

---

## Installation

```bash
git clone https://github.com/senseiRoa/OpenPDFStudio.git
cd OpenPDFStudio

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### GUI (recommended)

```bash
python compress_gui.py
```

### CLI

Compress a PDF:

```bash
python compress_pdf.py document.pdf
```

Custom quality:

```bash
python compress_pdf.py document.pdf --quality 45
```

Limit image width:

```bash
python compress_pdf.py document.pdf --max-width 1600
```

Allow overwrite:

```bash
python compress_pdf.py document.pdf --overwrite
```

Verbose output:

```bash
python compress_pdf.py document.pdf --verbose
```

---

## Philosophy

OpenPDFStudio follows a few simple principles:

- **Open Source** — forever free and transparent
- **Cross-platform** — Windows, Linux, macOS
- **Fast** — optimized for performance
- **Lightweight** — minimal dependencies
- **Easy to automate** — CLI-first design
- **Modular architecture** — extensible by design
- **Community-driven** — built for and by the community

---

## Roadmap

### Version 1.x

- PDF Compression
- Performance improvements
- Better image optimization

### Version 2.x

- Merge PDFs
- Split PDFs
- Page operations

### Version 3.x

- OCR
- Markdown conversion
- Image extraction
- Metadata editor

### Version 4.x

- REST API
- Docker image
- Python SDK
- MCP Server
- AI workflow integration

---

## Contributing

Contributions are welcome.

If you have ideas, improvements, or bug fixes, feel free to open an Issue or submit a Pull Request.

---

## License

Apache License 2.0

---

## Vision

Our vision is to make OpenPDFStudio one of the leading open-source PDF toolkits for developers, automation engineers, AI platforms, and technical users.

Instead of being a single-purpose utility, OpenPDFStudio aims to become a complete ecosystem for PDF processing that is easy to use, easy to extend, and free for everyone.
