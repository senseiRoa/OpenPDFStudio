"""Merge multiple PDFs into one."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import fitz


def merge_pdfs(input_paths: list[str], output_path: str) -> dict:
    """Merge multiple PDFs preserving page order.

    Args:
        input_paths: List of paths to PDF files to merge.
        output_path: Destination path for the merged PDF.

    Returns:
        dict with files_merged, pages_total, output_size, elapsed, method.

    Raises:
        FileNotFoundError: If any input file does not exist.
        fitz.FileDataError: If a file is not a valid PDF.
    """
    start = time.perf_counter()
    dst = fitz.open()
    total_pages = 0

    try:
        for path in input_paths:
            p = Path(path)
            if not p.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            src = fitz.open(str(p))
            dst.insert_pdf(src)
            total_pages += len(src)
            src.close()
            logging.debug("Mergeado: %s (%d páginas)", p.name, len(src))

        dst.save(str(output_path), garbage=4, deflate=True)
        logging.info(
            "Merge completado: %d archivos → %s (%d páginas)",
            len(input_paths),
            output_path,
            total_pages,
        )
    finally:
        dst.close()

    elapsed = time.perf_counter() - start
    return {
        "files_merged": len(input_paths),
        "pages_total": total_pages,
        "output_size": os.path.getsize(output_path),
        "elapsed": elapsed,
        "method": "PyMuPDF",
    }
