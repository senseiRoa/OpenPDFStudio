"""Core operations for PDF manipulation."""

from pdf_compressor.core.compress import compress, detect_ghostscript, format_bytes
from pdf_compressor.core.merge import merge_pdfs
from pdf_compressor.core.split import split_pages, split_ranges, split_every
from pdf_compressor.core.pages import reorder_pages, delete_pages, rotate_pages, extract_pages

__all__ = [
    "compress",
    "detect_ghostscript",
    "format_bytes",
    "merge_pdfs",
    "split_pages",
    "split_ranges",
    "split_every",
    "reorder_pages",
    "delete_pages",
    "rotate_pages",
    "extract_pages",
]
