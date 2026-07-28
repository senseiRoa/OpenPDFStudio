"""Translations for the OpenPDFStudio GUI.

Each language dict contains keys shared across all tabs.
New keys should be added to ALL languages.
"""

from __future__ import annotations

from typing import Dict

LANGUAGES = ["en", "es"]

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Window
        "window_title": "OpenPDFStudio",
        "subtitle": "Reduce your PDF file size instantly",
        # File selection (compress)
        "input_label": "Input PDF",
        "output_label": "Output PDF",
        "browse": "Browse…",
        "overwrite": "Overwrite output file if it already exists",
        # Quality
        "quality_frame": "JPEG Quality",
        "quality_min": "Minimum",
        "quality_max": "Maximum",
        # Max width
        "width_frame": "Max Width",
        "width_suffix": "px  ·  0 = unlimited",
        # Progress / Messages
        "status_ready": "Select a PDF and click Compress",
        "status_working": "Working…",
        "status_error": "Error",
        "error_title": "Error",
        "err_no_input": "Select an input PDF file.",
        "err_no_output": "Specify an output path.",
        "err_not_found": "File does not exist:\n{path}",
        "err_exists": "File already exists:\n{path}\n\nCheck «Overwrite» or change the path.",
        "done_title": "Completed",
        "done_original": "Original",
        "done_compressed": "Compressed",
        "done_reduction": "Reduction",
        "done_time": "Time",
        "done_seconds": "seconds",
        # Button
        "compress": "Compress",
        # Notebook tabs
        "tab_compress": "Compress",
        "tab_merge": "Merge",
        "tab_split": "Split",
        "tab_pages": "Pages",
        # Merge tab
        "merge_inputs": "Input PDFs",
        "merge_output": "Output PDF",
        "merge_add": "Add Files…",
        "merge_remove": "Remove",
        "merge_up": "▲",
        "merge_down": "▼",
        "merge_go": "Merge",
        "merge_status_ready": "Add PDF files and click Merge",
        "merge_done": "Merged {n} files ({pages} pages)",
        "merge_no_files": "Add at least one PDF file.",
        "err_merge_need_two": "Add at least two PDF files to merge.",
        # Split tab
        "split_input": "Input PDF",
        "split_output_prefix": "Output prefix",
        "split_mode": "Mode",
        "split_mode_all": "All pages (one per file)",
        "split_mode_ranges": "Page ranges",
        "split_mode_every": "Every N pages",
        "split_ranges_help": "e.g. 1-5,6-10,11-15",
        "split_every_help": "N pages per file",
        "split_go": "Split",
        "split_status_ready": "Select a PDF and click Split",
        "split_done": "Split into {n} files",
        # Pages tab
        "pages_input": "Input PDF",
        "pages_output": "Output PDF",
        "pages_operation": "Operation",
        "pages_opt_reorder": "Reorder",
        "pages_opt_delete": "Delete",
        "pages_opt_rotate": "Rotate",
        "pages_opt_extract": "Extract",
        "pages_order_help": 'Order: "reverse" or comma list, e.g. 3,1,2,4',
        "pages_pages_help": "Target pages, e.g. 1,3,5-7",
        "pages_pages_label": "Pages",
        "pages_angle_label": "Angle",
        "pages_angle_90": "90°",
        "pages_angle_180": "180°",
        "pages_angle_270": "270°",
        "pages_go": "Apply",
        "pages_status_ready": "Select a PDF and click Apply",
        "pages_done": "{op} — {n} pages affected",
    },
    "es": {
        # Window
        "window_title": "OpenPDFStudio",
        "subtitle": "Reducí el tamaño de tus PDFs al instante",
        # File selection (compress)
        "input_label": "PDF de entrada",
        "output_label": "PDF de salida",
        "browse": "Examinar…",
        "overwrite": "Sobrescribir archivo de salida si ya existe",
        # Quality
        "quality_frame": "Calidad JPEG",
        "quality_min": "Mínima",
        "quality_max": "Máxima",
        # Max width
        "width_frame": "Ancho máximo",
        "width_suffix": "px  ·  0 = sin límite",
        # Progress / Messages
        "status_ready": "Seleccioná un PDF y presioná Comprimir",
        "status_working": "Procesando…",
        "status_error": "Error",
        "error_title": "Error",
        "err_no_input": "Seleccioná un archivo PDF de entrada.",
        "err_no_output": "Indicá la ruta de salida.",
        "err_not_found": "No existe:\n{path}",
        "err_exists": "Ya existe:\n{path}\n\nMarcá «Sobrescribir» o cambiá la ruta.",
        "done_title": "Completado",
        "done_original": "Original",
        "done_compressed": "Comprimido",
        "done_reduction": "Reducción",
        "done_time": "Tiempo",
        "done_seconds": "segundos",
        # Button
        "compress": "Comprimir",
        # Notebook tabs
        "tab_compress": "Comprimir",
        "tab_merge": "Unir",
        "tab_split": "Dividir",
        "tab_pages": "Páginas",
        # Merge tab
        "merge_inputs": "PDFs de entrada",
        "merge_output": "PDF de salida",
        "merge_add": "Agregar archivos…",
        "merge_remove": "Quitar",
        "merge_up": "▲",
        "merge_down": "▼",
        "merge_go": "Unir",
        "merge_status_ready": "Agregá archivos PDF y presioná Unir",
        "merge_done": "{n} archivos unidos ({pages} páginas)",
        "merge_no_files": "Agregá al menos un archivo PDF.",
        "err_merge_need_two": "Agregá al menos dos PDFs para unir.",
        # Split tab
        "split_input": "PDF de entrada",
        "split_output_prefix": "Prefijo de salida",
        "split_mode": "Modo",
        "split_mode_all": "Todas las páginas (una por archivo)",
        "split_mode_ranges": "Rangos de páginas",
        "split_mode_every": "Cada N páginas",
        "split_ranges_help": "ej: 1-5,6-10,11-15",
        "split_every_help": "N páginas por archivo",
        "split_go": "Dividir",
        "split_status_ready": "Seleccioná un PDF y presioná Dividir",
        "split_done": "Dividido en {n} archivos",
        # Pages tab
        "pages_input": "PDF de entrada",
        "pages_output": "PDF de salida",
        "pages_operation": "Operación",
        "pages_opt_reorder": "Reordenar",
        "pages_opt_delete": "Eliminar",
        "pages_opt_rotate": "Rotar",
        "pages_opt_extract": "Extraer",
        "pages_order_help": 'Orden: "reverse" o lista separada por comas, ej: 3,1,2,4',
        "pages_pages_help": "Páginas objetivo, ej: 1,3,5-7",
        "pages_pages_label": "Páginas",
        "pages_angle_label": "Ángulo",
        "pages_angle_90": "90°",
        "pages_angle_180": "180°",
        "pages_angle_270": "270°",
        "pages_go": "Aplicar",
        "pages_status_ready": "Seleccioná un PDF y presioná Aplicar",
        "pages_done": "{op} — {n} páginas afectadas",
    },
}


def _(key: str, lang: str = "en", **kwargs) -> str:
    """Translate *key* into *lang*, optionally formatting with *kwargs*."""
    val = TRANSLATIONS.get(lang, {}).get(key)
    if val is None:
        val = TRANSLATIONS["en"].get(key, key)
    if kwargs:
        val = val.format(**kwargs)
    return val
