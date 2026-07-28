"""Core compression engine — extract images, recompress, rebuild PDF."""

from __future__ import annotations

import io
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from PIL import Image

import fitz


GHOSTSCRIPT_NAMES = ("gs", "gswin64c", "gswin32c")


def format_bytes(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def detect_ghostscript() -> Optional[str]:
    for name in GHOSTSCRIPT_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def _compress_with_ghostscript(
    input_path: str,
    output_path: str,
    quality: int,
    max_width: int,
) -> dict:
    gs = detect_ghostscript()
    if gs is None:
        raise RuntimeError("Ghostscript no está instalado.")

    resolution = max(72, int(max_width / 1600 * 300))

    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.7",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
        f"-dColorImageResolution={resolution}",
        f"-dGrayImageResolution={resolution}",
        f"-dMonoImageResolution={resolution}",
        "-dColorImageDownsampleThreshold=1.0",
        "-dGrayImageDownsampleThreshold=1.0",
        "-dMonoImageDownsampleThreshold=1.0",
        "-dAutoFilterColorImages=false",
        "-dAutoFilterGrayImages=false",
        "-dColorImageFilter=/DCTEncode",
        "-dGrayImageFilter=/DCTEncode",
        "-dCompressPages=true",
        "-dDetectDuplicates=true",
        "-dOptimize=true",
        "-dEmbedAllFonts=true",
        "-dSubsetFonts=true",
        "-dPreserveOPIComments=false",
        "-dPreserveOverprintSettings=false",
        "-dUCRandBGInfo=/Remove",
        f"-dJPEGQ={quality}",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    start = time.perf_counter()
    logging.debug("Ejecutando Ghostscript…")

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if proc.returncode != 0:
        raise RuntimeError(
            f"Ghostscript falló (código {proc.returncode}):\n{proc.stderr}"
        )

    elapsed = time.perf_counter() - start
    output_size = os.path.getsize(output_path)

    return {
        "input_size": os.path.getsize(input_path),
        "output_size": output_size,
        "elapsed": elapsed,
        "method": "Ghostscript",
    }


def _compress_with_pymupdf(
    input_path: str,
    output_path: str,
    quality: int,
    max_width: int,
) -> dict:
    start = time.perf_counter()

    src = fitz.open(input_path)
    dst = fitz.open()
    page_count = len(src)

    try:
        for idx in range(page_count):
            page = src[idx]
            pr = page.rect
            imgs = page.get_images(full=True)

            if len(imgs) == 1:
                xref = imgs[0][0]
                img_dict = src.extract_image(xref)
                img = Image.open(io.BytesIO(img_dict["image"]))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                if max_width and img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality, optimize=True)
                new_page = dst.new_page(width=pr.width, height=pr.height)
                new_page.insert_image(pr, stream=buf.getvalue())
            else:
                zoom = (
                    max_width / pr.width
                    if (max_width and pr.width > max_width)
                    else 1.0
                )
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                pil_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                new_page = dst.new_page(width=pix.width, height=pix.height)
                new_page.insert_image(new_page.rect, stream=buf.getvalue())

            logging.debug(
                "Página %d/%d",
                idx + 1,
                page_count,
            )

        dst.save(output_path, garbage=4, deflate=True)
    finally:
        src.close()
        dst.close()

    elapsed = time.perf_counter() - start
    output_size = os.path.getsize(output_path)

    return {
        "input_size": os.path.getsize(input_path),
        "output_size": output_size,
        "elapsed": elapsed,
        "method": "PyMuPDF",
    }


def compress(
    input_path: str,
    output_path: str,
    quality: int = 70,
    max_width: int = 1000,
    prefer_gs: bool = True,
) -> dict:
    """Compress a PDF file.

    Returns dict with input_size, output_size, elapsed, method.
    """
    gs = detect_ghostscript()

    if gs and prefer_gs:
        try:
            return _compress_with_ghostscript(input_path, output_path, quality, max_width)
        except Exception as exc:
            logging.warning("Ghostscript falló (%s). Usando PyMuPDF.", exc)

    return _compress_with_pymupdf(input_path, output_path, quality, max_width)
