"""Split PDF into multiple files."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

import fitz


def _make_prefix(input_path: str, output_prefix: Optional[str] = None) -> Path:
    """Resolve the output prefix path."""
    inp = Path(input_path)
    if output_prefix:
        prefix = Path(output_prefix)
        if prefix.suffix:
            return prefix.parent / prefix.stem
        return prefix
    return inp.parent / f"{inp.stem}_page"


def _parse_ranges(range_str: str) -> list[tuple[int, int]]:
    """Parse a range string like '1-5,6-10,11-15' into list of (start, end) tuples.

    Each range is 1-indexed and inclusive.
    """
    ranges = []
    for part in range_str.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a.strip()), int(b.strip())
        else:
            start = end = int(part)
        if start < 1:
            raise ValueError(f"Invalid page number: {start}. Pages are 1-indexed.")
        ranges.append((start, end))
    return ranges


def split_pages(
    input_path: str,
    output_prefix: Optional[str] = None,
) -> list[dict]:
    """Split PDF into individual pages, one PDF per page.

    Args:
        input_path: Path to the input PDF.
        output_prefix: Optional prefix for output files. Defaults to ``<input>_page``.

    Returns:
        List of dicts with path, page, pages_total, size, elapsed per file.
    """
    prefix = _make_prefix(input_path, output_prefix)
    src = fitz.open(input_path)
    total = len(src)
    results = []

    try:
        for i in range(total):
            page_start = time.perf_counter()
            dst = fitz.open()
            dst.insert_pdf(src, from_page=i, to_page=i)
            out_path = f"{prefix}_{i + 1:03d}.pdf"
            dst.save(out_path, garbage=4, deflate=True)
            dst.close()

            results.append(
                {
                    "path": out_path,
                    "page": i + 1,
                    "pages_total": total,
                    "size": os.path.getsize(out_path),
                    "elapsed": time.perf_counter() - page_start,
                }
            )
            logging.debug("Página %d/%d → %s", i + 1, total, out_path)
    finally:
        src.close()

    return results


def split_ranges(
    input_path: str,
    ranges: list[tuple[int, int]],
    output_prefix: Optional[str] = None,
) -> list[dict]:
    """Split PDF by custom page ranges (1-indexed, inclusive).

    Each tuple is ``(start, end)``. Returns list of dicts.
    """
    prefix = _make_prefix(input_path, output_prefix)
    src = fitz.open(input_path)
    total = len(src)
    results = []

    try:
        for idx, (start, end) in enumerate(ranges, 1):
            if start < 1 or end > total or start > end:
                raise ValueError(
                    f"Invalid range {start}-{end}. File has {total} pages (1-indexed)."
                )
            dst = fitz.open()
            dst.insert_pdf(src, from_page=start - 1, to_page=end - 1)
            out_path = f"{prefix}_{idx:03d}.pdf"
            dst.save(out_path, garbage=4, deflate=True)
            dst.close()
            results.append(
                {
                    "path": out_path,
                    "range": f"{start}-{end}",
                    "pages": end - start + 1,
                    "size": os.path.getsize(out_path),
                }
            )
            logging.debug("Rango %d: páginas %d-%d → %s", idx, start, end, out_path)
    finally:
        src.close()

    return results


def split_every(
    input_path: str,
    n: int,
    output_prefix: Optional[str] = None,
) -> list[dict]:
    """Split PDF every N pages.

    E.g. ``n=3``: pages 1-3 → file 1, 4-6 → file 2, etc.
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    prefix = _make_prefix(input_path, output_prefix)
    src = fitz.open(input_path)
    total = len(src)
    results = []

    try:
        for chunk_start in range(0, total, n):
            chunk_end = min(chunk_start + n - 1, total - 1)
            dst = fitz.open()
            dst.insert_pdf(src, from_page=chunk_start, to_page=chunk_end)
            idx = chunk_start // n + 1
            out_path = f"{prefix}_{idx:03d}.pdf"
            dst.save(out_path, garbage=4, deflate=True)
            dst.close()
            results.append(
                {
                    "path": out_path,
                    "pages": chunk_end - chunk_start + 1,
                    "range": f"{chunk_start + 1}-{chunk_end + 1}",
                    "size": os.path.getsize(out_path),
                }
            )
    finally:
        src.close()

    return results
