"""Split tab — divide a PDF into multiple files."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..core import split_pages, split_ranges, split_every, format_bytes
from ..core.split import _parse_ranges
from ..locale import _


class TabSplit(tb.Frame):
    """Split a PDF into multiple files (all pages, ranges, or every N)."""

    def __init__(self, parent: tb.Window, app) -> None:
        super().__init__(parent)
        self.app = app
        self._tr_map: dict = {}

        self.input_path = tb.StringVar()
        self.mode = tb.StringVar(value="all")
        self.ranges = tb.StringVar(value="1-5,6-10")
        self.every_n = tb.IntVar(value=2)
        self.output_prefix = tb.StringVar()

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

    def _show_mode_options(self) -> None:
        """Show/hide mode-specific input widgets."""
        mode = self.mode.get()
        self._ranges_frame.pack_forget()
        self._every_frame.pack_forget()

        if mode == "ranges":
            self._ranges_frame.pack(fill=X, pady=(0, 8))
        elif mode == "every":
            self._every_frame.pack(fill=X, pady=(0, 8))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tb.Frame(self, padding=12)
        main.pack(fill=BOTH, expand=True)

        # -- Input --
        self._file_row(main, "split_input", self.input_path, self._browse_input)

        # -- Output prefix --
        pref_frame = tb.Frame(main)
        pref_frame.pack(fill=X, pady=(0, 8))
        lbl_pref = tb.Label(pref_frame, text="", font=("", 9, "bold"))
        self._tr(lbl_pref, "split_output_prefix")
        lbl_pref.pack(anchor="w")
        row_pref = tb.Frame(pref_frame)
        row_pref.pack(fill=X, pady=(2, 0))
        self.prefix_entry = tb.Entry(row_pref, textvariable=self.output_prefix)
        self.prefix_entry.pack(fill=X)

        tb.Separator(main).pack(fill=X, pady=(4, 8))

        # -- Mode --
        lbl_mode = tb.Label(main, text="", font=("", 9, "bold"))
        self._tr(lbl_mode, "split_mode")
        lbl_mode.pack(anchor="w")

        mode_row = tb.Frame(main)
        mode_row.pack(fill=X, pady=(4, 8))

        modes = [
            ("split_mode_all", "all"),
            ("split_mode_ranges", "ranges"),
            ("split_mode_every", "every"),
        ]
        for key, val in modes:
            rb = tb.Radiobutton(
                mode_row,
                text="",
                variable=self.mode,
                value=val,
                command=self._show_mode_options,
            )
            self._tr(rb, key)
            rb.pack(side=LEFT, padx=(0, 16))

        # -- Ranges input (hidden by default) --
        self._ranges_frame = tb.Frame(main)
        lbl_r = tb.Label(self._ranges_frame, textvariable=self.ranges, bootstyle="secondary")
        self._tr(lbl_r, "split_ranges_help")
        lbl_r.pack(anchor="w")
        tb.Entry(self._ranges_frame, textvariable=self.ranges).pack(fill=X, pady=(2, 0))

        # -- Every-N input (hidden by default) --
        self._every_frame = tb.Frame(main)
        lbl_e = tb.Label(self._every_frame, text="", bootstyle="secondary")
        self._tr(lbl_e, "split_every_help")
        lbl_e.pack(anchor="w")
        tb.Entry(
            self._every_frame, textvariable=self.every_n, width=8, justify="center",
        ).pack(anchor="w", pady=(2, 0))

        tb.Separator(main).pack(fill=X, pady=(4, 8))

        # -- Progress --
        self.progress = tb.Progressbar(main, mode="indeterminate", bootstyle="success-striped")
        self.progress.pack(fill=X, pady=(4, 4))

        self.status = tb.StringVar(value="")
        lbl_st = tb.Label(main, textvariable=self.status, bootstyle="secondary")
        self._tr(lbl_st, "split_status_ready")
        lbl_st.pack(anchor="w")

        # -- Split button --
        self.btn = tb.Button(
            main,
            text="",
            command=self._split,
            bootstyle="primary",
            padding=(40, 10),
        )
        self._tr(self.btn, "split_go")
        self.btn.pack(pady=(8, 0))

        # Initial mode state
        self._show_mode_options()

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def apply_language(self) -> None:
        for widget, key in self._tr_map.values():
            text = _(key, self.app.lang)
            try:
                if isinstance(widget, (tb.Label, tb.Button, tb.Checkbutton, tb.LabelFrame, tb.Radiobutton)):
                    widget.config(text=text)
            except Exception:
                pass
        self.status.set(_("split_status_ready", self.app.lang))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title=_("split_input", self.app.lang),
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")],
        )
        if path:
            self.input_path.set(path)
            p = Path(path)
            if not self.output_prefix.get():
                self.output_prefix.set(str(p.parent / p.stem))

    def _split(self) -> None:
        inp = self.input_path.get().strip()
        prefix = self.output_prefix.get().strip() or None
        lang = self.app.lang

        if not inp:
            messagebox.showerror(_("error_title", lang), _("err_no_input", lang))
            return
        if not os.path.exists(inp):
            messagebox.showerror(_("error_title", lang), _("err_not_found", lang, path=inp))
            return

        self.btn.config(state=DISABLED)
        self.progress.start(12)
        self.status.set(_("status_working", lang))

        def task() -> None:
            try:
                mode = self.mode.get()
                if mode == "ranges":
                    ranges = _parse_ranges(self.ranges.get().strip())
                    results = split_ranges(inp, ranges, prefix)
                elif mode == "every":
                    n = self.every_n.get()
                    if n < 1:
                        raise ValueError("N must be >= 1")
                    results = split_every(inp, n, prefix)
                else:
                    results = split_pages(inp, prefix)
                self.app.root.after(0, self._on_done, results, lang)
            except Exception as exc:
                self.app.root.after(0, self._on_error, exc, lang)

        threading.Thread(target=task, daemon=True).start()

    def _on_done(self, results: list[dict], lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        msg = _("split_done", lang, n=len(results))
        self.status.set(f"✅ {msg}")
        detail = "\n".join(
            r.get("path", "") + f"  ({format_bytes(r['size'])})" for r in results
        )
        messagebox.showinfo(_("done_title", lang), f"{msg}:\n\n{detail}")

    def _on_error(self, exc: Exception, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        self.status.set(_("status_error", lang))
        messagebox.showerror(_("error_title", lang), str(exc))
