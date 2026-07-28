"""Page operations: reorder, delete, rotate, extract."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

import fitz


def _open_and_save(src_path: str, dst_path: str, pages: list[int]) -> dict:
    """Helper: open src, copy selected *pages* (0-indexed), save to dst."""
    start = time.perf_counter()
    src = fitz.open(src_path)
    dst = fitz.open()

    try:
        for p in pages:
            dst.insert_pdf(src, from_page=p, to_page=p)

        dst.save(dst_path, garbage=4, deflate=True)
        saved_pages = len(dst)
    finally:
        src.close()
        dst.close()

    return {
        "input_size": os.path.getsize(src_path),
        "output_size": os.path.getsize(dst_path),
        "pages": saved_pages,
        "elapsed": time.perf_counter() - start,
        "method": "PyMuPDF",
    }


def _validate_pages(pages: list[int], total: int, label: str = "Page") -> list[int]:
    """Convert 1-indexed pages to 0-indexed and validate bounds."""
    zero = []
    for p in pages:
        if p < 1 or p > total:
            raise ValueError(f"{label} {p} fuera de rango (1-{total})")
        zero.append(p - 1)
    return zero


def reorder_pages(
    input_path: str,
    output_path: str,
    order: list[int] | str,
) -> dict:
    """Reorder pages in a PDF.

    Args:
        order: List of 1-indexed page numbers, or ``'reverse'``.
    """
    total = len(fitz.open(input_path))
    if total == 0:
        raise ValueError("PDF vacío — no hay páginas para reordenar.")

    if isinstance(order, str):
        s = order.lower().strip()
        if s == "reverse":
            order = list(range(total, 0, -1))
        else:
            raise ValueError(f"Shorthand desconocido: '{order}'. Usá 'reverse' o una lista.")

    zero_idx = _validate_pages(order, total, "Página")
    return _open_and_save(input_path, output_path, zero_idx)


def delete_pages(
    input_path: str,
    output_path: str,
    pages: list[int],
) -> dict:
    """Delete pages from a PDF (1-indexed).

    Raises ValueError if trying to delete ALL pages.
    """
    total = len(fitz.open(input_path))
    del_set = set(_validate_pages(pages, total, "Página"))

    keep = [i for i in range(total) if i not in del_set]
    if not keep:
        raise ValueError("No se pueden eliminar TODAS las páginas.")

    return _open_and_save(input_path, output_path, keep)


def rotate_pages(
    input_path: str,
    output_path: str,
    angle: int,
    pages: Optional[list[int]] = None,
) -> dict:
    """Rotate pages in a PDF.

    Args:
        angle: 90, 180, or 270 degrees (clockwise).
        pages: 1-indexed page list. If ``None``, rotate all pages.
    """
    if angle not in (90, 180, 270):
        raise ValueError(f"Ángulo inválido: {angle}. Usá 90, 180 o 270.")

    start = time.perf_counter()
    src = fitz.open(input_path)
    total = len(src)

    try:
        if pages is None:
            target = list(range(total))
        else:
            target = _validate_pages(pages, total, "Página")

        for p in target:
            current = src[p].rotation or 0
            src[p].set_rotation((current + angle) % 360)

        src.save(output_path, garbage=4, deflate=True)
        saved_pages = len(src)
    finally:
        src.close()

    return {
        "input_size": os.path.getsize(input_path),
        "output_size": os.path.getsize(output_path),
        "pages_rotated": len(target),
        "pages_total": saved_pages,
        "elapsed": time.perf_counter() - start,
        "method": "PyMuPDF",
    }


def extract_pages(
    input_path: str,
    output_path: str,
    pages: list[int],
) -> dict:
    """Extract specific pages into a new PDF (1-indexed)."""
    total = len(fitz.open(input_path))
    zero_idx = _validate_pages(pages, total, "Página")
    return _open_and_save(input_path, output_path, zero_idx)
