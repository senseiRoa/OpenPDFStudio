"""CLI entry points — argparse wrappers around core operations."""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import fitz

from . import __version__
from .core import (
    compress,
    delete_pages,
    detect_ghostscript,
    extract_pages,
    format_bytes,
    merge_pdfs,
    reorder_pages,
    rotate_pages,
    split_every,
    split_pages,
    split_ranges,
)
from .core.split import _parse_ranges

# ---------------------------------------------------------------------------
# Compress
# ---------------------------------------------------------------------------


def _build_compress_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Comprime un archivo PDF reduciendo su tamaño.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  compress-pdf documento.pdf\n"
            "  compress-pdf documento.pdf --quality 50\n"
            "  compress-pdf documento.pdf --max-width 2000 --overwrite\n"
        ),
    )
    p.add_argument("input", type=str, help="Ruta al archivo PDF de entrada.")
    p.add_argument(
        "--quality",
        type=int,
        default=70,
        choices=range(1, 101),
        metavar="{1..100}",
        help="Calidad JPEG (1-100). Por defecto: 70.",
    )
    p.add_argument(
        "--max-width",
        type=int,
        default=1000,
        metavar="PX",
        help="Ancho máximo en píxeles. Por defecto: 1000.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribir el archivo de salida si existe.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada del proceso.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def compress_main(argv: Optional[list[str]] = None) -> int:
    args = _build_compress_parser().parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    input_path = Path(args.input).resolve()

    try:
        if not input_path.exists():
            raise FileNotFoundError(f"El archivo '{input_path}' no existe.")
        if not input_path.is_file():
            raise IsADirectoryError(f"'{input_path}' es un directorio.")
        if input_path.suffix.lower() != ".pdf":
            logging.warning("El archivo no tiene extensión .pdf. Se intentará igual.")

        stem = input_path.stem
        output_path = input_path.with_name(f"{stem}_compressed.pdf")

        if output_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"'{output_path}' ya existe. Usa --overwrite para sobrescribirlo."
            )

        gs = detect_ghostscript()
        if gs:
            logging.info("Ghostscript detectado — usándolo como backend principal.")
        else:
            logging.info("Usando PyMuPDF.")

        logging.info("Comprimiendo: %s", input_path.name)
        result = compress(
            input_path=str(input_path),
            output_path=str(output_path),
            quality=args.quality,
            max_width=args.max_width,
            prefer_gs=True,
        )

        ratio = (1 - result["output_size"] / result["input_size"]) * 100
        print()
        print(f"  Archivo original:    {format_bytes(result['input_size'])}")
        print(f"  Archivo comprimido:  {format_bytes(result['output_size'])}")
        print(f"  Reducción:           {ratio:.2f} %")
        print(f"  Tiempo:              {result['elapsed']:.2f} segundos")
        print(f"  Método:              {result['method']}")
        print()
        return 0

    except FileNotFoundError as exc:
        logging.error(exc)
    except FileExistsError as exc:
        logging.error(exc)
    except IsADirectoryError as exc:
        logging.error(exc)
    except fitz.FileDataError as exc:
        logging.error("El archivo no es un PDF válido: %s", exc)
    except subprocess.TimeoutExpired:
        logging.error("Tiempo máximo excedido (5 min).")
    except Exception as exc:
        logging.exception("Error: %s", exc)

    return 1


def main(argv: Optional[list[str]] = None) -> int:
    """Deprecated — kept for backward compat. Use compress_main() instead."""
    return compress_main(argv)


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


def _build_merge_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Une múltiples archivos PDF en uno solo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  merge-pdf a.pdf b.pdf\n"
            "  merge-pdf *.pdf -o completo.pdf\n"
            "  merge-pdf a.pdf b.pdf --overwrite\n"
        ),
    )
    p.add_argument("inputs", nargs="+", type=str, help="Archivos PDF a unir.")
    p.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Archivo de salida. Por defecto: merged.pdf",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribir si el archivo de salida existe.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def merge_main(argv: Optional[list[str]] = None) -> int:
    args = _build_merge_parser().parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        output = args.output or "merged.pdf"
        out_path = Path(output).resolve()

        if out_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"'{out_path}' ya existe. Usa --overwrite para sobrescribirlo."
            )

        for p in args.inputs:
            if not Path(p).exists():
                raise FileNotFoundError(f"Archivo no encontrado: {p}")

        logging.info("Mergeando %d archivos → %s", len(args.inputs), out_path.name)
        result = merge_pdfs(args.inputs, str(out_path))

        print()
        print(f"  Archivos mergeados:  {result['files_merged']}")
        print(f"  Páginas totales:     {result['pages_total']}")
        print(f"  Tamaño:              {format_bytes(result['output_size'])}")
        print(f"  Tiempo:              {result['elapsed']:.2f} segundos")
        print()
        return 0

    except FileNotFoundError as exc:
        logging.error(exc)
    except FileExistsError as exc:
        logging.error(exc)
    except fitz.FileDataError as exc:
        logging.error("Archivo PDF inválido: %s", exc)
    except Exception as exc:
        logging.exception("Error: %s", exc)

    return 1


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------


def _build_split_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Divide un PDF en múltiples archivos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  split-pdf documento.pdf\n"
            "  split-pdf documento.pdf --pages 1-5,6-10\n"
            "  split-pdf documento.pdf --every 3 -o capitulo\n"
        ),
    )
    p.add_argument("input", type=str, help="Archivo PDF a dividir.")

    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Rangos personalizados, ej: 1-5,6-10,11-15",
    )
    group.add_argument(
        "--every",
        type=int,
        default=None,
        metavar="N",
        help="Dividir cada N páginas.",
    )

    p.add_argument(
        "-o", "--output-prefix",
        type=str,
        default=None,
        help="Prefijo para archivos de salida. Por defecto: <input>_page",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def split_main(argv: Optional[list[str]] = None) -> int:
    args = _build_split_parser().parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        input_path = Path(args.input).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        if args.pages:
            ranges = _parse_ranges(args.pages)
            results = split_ranges(
                str(input_path),
                ranges,
                output_prefix=args.output_prefix,
            )
        elif args.every:
            results = split_every(
                str(input_path),
                args.every,
                output_prefix=args.output_prefix,
            )
        else:
            results = split_pages(
                str(input_path),
                output_prefix=args.output_prefix,
            )

        print()
        print(f"  Dividido en {len(results)} archivos:\n")
        for r in results:
            size = format_bytes(r["size"])
            if "page" in r:
                print(f"    [{r['page']}/{r['pages_total']}]  {r['path']}  ({size})")
            elif "range" in r:
                print(f"    [{r['range']}]  {r['path']}  ({size})")
        print()
        return 0

    except FileNotFoundError as exc:
        logging.error(exc)
    except fitz.FileDataError as exc:
        logging.error("Archivo PDF inválido: %s", exc)
    except Exception as exc:
        logging.exception("Error: %s", exc)

    return 1


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def _parse_page_list(s: str) -> list[int]:
    """Parse '1,3,5-7' into a flat list of page numbers (1-indexed)."""
    pages: list[int] = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a.strip()), int(b.strip()) + 1))
        else:
            pages.append(int(part))
    return pages


def _build_pages_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Operaciones sobre páginas de un PDF: reordenar, eliminar, rotar, extraer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  pages-pdf doc.pdf --reorder reverse\n"
            "  pages-pdf doc.pdf --delete 2,5,7\n"
            "  pages-pdf doc.pdf --rotate 90 --pages 1,3,5\n"
            "  pages-pdf doc.pdf --extract 2,4,6 -o seleccion.pdf\n"
        ),
    )
    p.add_argument("input", type=str, help="Archivo PDF de entrada.")

    op = p.add_mutually_exclusive_group(required=True)
    op.add_argument(
        "--reorder",
        type=str,
        default=None,
        metavar="ORDER",
        help='Orden: "reverse" o lista separada por comas, ej: 3,1,2,4',
    )
    op.add_argument(
        "--delete",
        type=str,
        default=None,
        metavar="PAGES",
        help="Páginas a eliminar, ej: 2,5,7",
    )
    op.add_argument(
        "--rotate",
        type=int,
        default=None,
        choices=[90, 180, 270],
        metavar="{90,180,270}",
        help="Ángulo de rotación (90, 180, 270).",
    )
    op.add_argument(
        "--extract",
        type=str,
        default=None,
        metavar="PAGES",
        help="Páginas a extraer, ej: 2,4,6",
    )

    p.add_argument("--pages", type=str, default=None, help="Páginas objetivo, ej: 1,3,5")
    p.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Archivo de salida (por defecto: <input>_<op>.pdf)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribir si el archivo de salida existe.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return p


def pages_main(argv: Optional[list[str]] = None) -> int:
    args = _build_pages_parser().parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        input_path = Path(args.input).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        # Determine output path
        stem = input_path.stem
        op_names = {"reorder": "reordenado", "delete": "sin_eliminadas",
                    "rotate": "rotado", "extract": "extraido"}
        op = next(o for o in op_names if getattr(args, o) is not None)
        output = args.output or str(input_path.with_name(f"{stem}_{op_names[op]}.pdf"))
        out_path = Path(output).resolve()

        if out_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"'{out_path}' ya existe. Usa --overwrite para sobrescribirlo."
            )

        if op == "reorder":
            if args.reorder.lower() == "reverse":
                order = "reverse"
            else:
                order = _parse_page_list(args.reorder)
            result = reorder_pages(str(input_path), str(out_path), order)
            label = "Reordenadas"

        elif op == "delete":
            pages = _parse_page_list(args.delete)
            result = delete_pages(str(input_path), str(out_path), pages)
            label = "Eliminadas"

        elif op == "rotate":
            target = _parse_page_list(args.pages) if args.pages else None
            result = rotate_pages(str(input_path), str(out_path), args.rotate, target)
            label = "Rotadas"

        elif op == "extract":
            pages = _parse_page_list(args.extract)
            result = extract_pages(str(input_path), str(out_path), pages)
            label = "Extraídas"

        else:
            raise RuntimeError("No se especificó ninguna operación.")

        ratio = (1 - result["output_size"] / result["input_size"]) * 100
        print()
        print(f"  Operación:           {label}")
        print(f"  Archivo original:    {format_bytes(result['input_size'])}")
        print(f"  Archivo resultante:  {format_bytes(result['output_size'])}")
        if "pages" in result:
            print(f"  Páginas:             {result['pages']}")
        if "pages_rotated" in result:
            print(f"  Páginas rotadas:     {result['pages_rotated']}")
        print(f"  Cambio:              {'+' if ratio < 0 else ''}{ratio:.2f} %")
        print(f"  Tiempo:              {result['elapsed']:.2f} segundos")
        print()
        return 0

    except FileNotFoundError as exc:
        logging.error(exc)
    except FileExistsError as exc:
        logging.error(exc)
    except ValueError as exc:
        logging.error(exc)
    except fitz.FileDataError as exc:
        logging.error("Archivo PDF inválido: %s", exc)
    except Exception as exc:
        logging.exception("Error: %s", exc)

    return 1


# ---------------------------------------------------------------------------
# Script entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
