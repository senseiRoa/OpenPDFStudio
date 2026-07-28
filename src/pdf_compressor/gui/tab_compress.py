"""Compress tab — reduce PDF file size."""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..core import compress, format_bytes
from ..locale import _


class TabCompress(tb.Frame):
    """Compress a single PDF file with quality and max-width controls."""

    def __init__(self, parent: tb.Window, app) -> None:
        super().__init__(parent)
        self.app = app
        self._tr_map: dict = {}

        self.input_path = tb.StringVar()
        self.output_path = tb.StringVar()
        self.quality = tb.IntVar(value=70)
        self.max_width = tb.IntVar(value=1000)
        self.overwrite = tb.BooleanVar(value=False)

        self._build_ui()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tr(self, widget, key):
        self._tr_map[id(widget)] = (widget, key)
        return widget

    def _file_row(self, parent, label_key, variable, callback):
        frame = tb.Frame(parent)
        frame.pack(fill=X, pady=(0, 8))
        lbl = tb.Label(frame, text="", font=("", 9, "bold"))
        self._tr(lbl, label_key)
        lbl.pack(anchor="w")
        row = tb.Frame(frame)
        row.pack(fill=X, pady=(2, 0))
        tb.Entry(row, textvariable=variable).pack(side=LEFT, fill=X, expand=True)
        btn = tb.Button(row, text="", command=callback, bootstyle="secondary")
        self._tr(btn, "browse")
        btn.pack(side=LEFT, padx=(6, 0))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": (0, 4)}
        main = tb.Frame(self, padding=12)
        main.pack(fill=BOTH, expand=True)

        # -- Subtitle --
        lbl_sub = tb.Label(main, text="", font=("Segoe UI", 10), bootstyle="secondary")
        self._tr(lbl_sub, "subtitle")
        lbl_sub.pack(anchor="w", **pad)

        tb.Separator(main).pack(fill=X, **pad)

        # -- Input / Output --
        self._file_row(main, "input_label", self.input_path, self._browse_input)
        self._file_row(main, "output_label", self.output_path, self._browse_output)

        chk = tb.Checkbutton(main, text="", variable=self.overwrite)
        self._tr(chk, "overwrite")
        chk.pack(anchor="w", **pad)

        tb.Separator(main).pack(fill=X, **pad)

        # -- Quality --
        frame_q = tb.LabelFrame(main, text="", padding=10)
        self._tr(frame_q, "quality_frame")
        frame_q.pack(fill=X, **pad)

        tb.Scale(
            frame_q, from_=1, to=100, orient=HORIZONTAL,
            variable=self.quality, length=400,
        ).pack(fill=X)

        row_q = tb.Frame(frame_q)
        row_q.pack(fill=X)
        lbl_min = tb.Label(row_q, text="", bootstyle="secondary")
        self._tr(lbl_min, "quality_min")
        lbl_min.pack(side=LEFT)
        tb.Label(
            row_q,
            textvariable=self.quality,
            font=("", 12, "bold"),
            bootstyle="primary",
        ).pack(side=RIGHT, padx=(0, 4))
        lbl_max = tb.Label(row_q, text="", bootstyle="secondary")
        self._tr(lbl_max, "quality_max")
        lbl_max.pack(side=RIGHT)

        # -- Max width --
        frame_w = tb.LabelFrame(main, text="", padding=10)
        self._tr(frame_w, "width_frame")
        frame_w.pack(fill=X, **pad)

        row_w = tb.Frame(frame_w)
        row_w.pack(fill=X)
        tb.Entry(
            row_w, textvariable=self.max_width, width=8, justify="center",
        ).pack(side=LEFT)
        lbl_suf = tb.Label(row_w, text="", bootstyle="secondary")
        self._tr(lbl_suf, "width_suffix")
        lbl_suf.pack(side=LEFT, padx=(8, 0))

        # -- Progress --
        self.progress = tb.Progressbar(main, mode="indeterminate", bootstyle="success-striped")
        self.progress.pack(fill=X, **pad)

        self.status = tb.StringVar(value="")
        lbl_st = tb.Label(main, textvariable=self.status, bootstyle="secondary")
        self._tr(lbl_st, "status_ready")
        lbl_st.pack(anchor="w", **pad)

        # -- Compress button --
        self.btn = tb.Button(
            main,
            text="",
            command=self._compress,
            bootstyle="primary",
            padding=(40, 10),
        )
        self._tr(self.btn, "compress")
        self.btn.pack(pady=(4, 0))

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def apply_language(self) -> None:
        for widget, key in self._tr_map.values():
            text = _(key, self.app.lang)
            try:
                if isinstance(widget, (tb.Label, tb.Button, tb.Checkbutton, tb.LabelFrame)):
                    widget.config(text=text)
            except Exception:
                pass
        self.status.set(_("status_ready", self.app.lang))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title=_("input_label", self.app.lang),
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")],
        )
        if path:
            self.input_path.set(path)
            p = Path(path)
            self.output_path.set(str(p.with_name(f"{p.stem}_compressed.pdf")))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title=_("output_label", self.app.lang),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.output_path.set(path)

    def _compress(self) -> None:
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()
        lang = self.app.lang

        errors = []
        if not inp:
            errors.append(_("err_no_input", lang))
        if not out:
            errors.append(_("err_no_output", lang))
        if inp and not os.path.exists(inp):
            errors.append(_("err_not_found", lang, path=inp))
        if out and os.path.exists(out) and not self.overwrite.get():
            errors.append(_("err_exists", lang, path=out))

        if errors:
            messagebox.showerror(_("error_title", lang), "\n\n".join(errors))
            return

        q = self.quality.get()
        w = self.max_width.get()
        if w < 0:
            w = 0

        self.btn.config(state=DISABLED)
        self.progress.start(12)
        self.status.set(_("status_working", lang))

        def task() -> None:
            try:
                result = compress(inp, out, q, w)
                self.app.root.after(0, self._on_done, result, lang)
            except Exception as exc:
                self.app.root.after(0, self._on_error, exc, lang)

        threading.Thread(target=task, daemon=True).start()

    def _on_done(self, result: dict, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        ratio = (1 - result["output_size"] / result["input_size"]) * 100
        self.status.set(
            f"{_('done_original', lang)}: {format_bytes(result['input_size'])}  →  "
            f"{_('done_compressed', lang)}: {format_bytes(result['output_size'])}  "
            f"({ratio:.1f}%  ·  {result['elapsed']:.1f}s)"
        )
        messagebox.showinfo(
            _("done_title", lang),
            f"{_('done_original', lang)}:   {format_bytes(result['input_size'])}\n"
            f"{_('done_compressed', lang)}: {format_bytes(result['output_size'])}\n"
            f"{_('done_reduction', lang)}:  {ratio:.1f}%\n"
            f"{_('done_time', lang)}:     {result['elapsed']:.1f} {_('done_seconds', lang)}",
        )

    def _on_error(self, exc: Exception, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        self.status.set(_("status_error", lang))
        messagebox.showerror(_("error_title", lang), str(exc))
