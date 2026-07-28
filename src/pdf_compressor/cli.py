"""CLI entry point — argparse wrapper around core.compress()."""

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
from .core import compress, detect_ghostscript, format_bytes

DEFAULT_QUALITY = 70
DEFAULT_MAX_WIDTH = 1000


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
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
        default=DEFAULT_QUALITY,
        choices=range(1, 101),
        metavar="{1..100}",
        help=f"Calidad JPEG (1-100). Por defecto: {DEFAULT_QUALITY}.",
    )
    p.add_argument(
        "--max-width",
        type=int,
        default=DEFAULT_MAX_WIDTH,
        metavar="PX",
        help=f"Ancho máximo en píxeles. Por defecto: {DEFAULT_MAX_WIDTH}.",
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
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

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


if __name__ == "__main__":
    sys.exit(main())
