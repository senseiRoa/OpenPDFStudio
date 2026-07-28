"""Translations for the OpenPDFStudio GUI."""

from __future__ import annotations

from typing import Dict

LANGUAGES = ["en", "es"]

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Window
        "window_title": "OpenPDFStudio",
        "subtitle": "Reduce your PDF file size instantly",
        # File selection
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
        # Progress
        "status_ready": "💡 Select a PDF and click Compress",
        "status_compressing": "⏳ Compressing…",
        "status_error": "❌ Error",
        # Button
        "compress": "Compress",
        # Messages
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
    },
    "es": {
        # Window
        "window_title": "OpenPDFStudio",
        "subtitle": "Reducí el tamaño de tus PDFs al instante",
        # File selection
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
        # Progress
        "status_ready": "💡 Seleccioná un PDF y presioná Comprimir",
        "status_compressing": "⏳ Comprimiendo…",
        "status_error": "❌ Error",
        # Button
        "compress": "Comprimir",
        # Messages
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
