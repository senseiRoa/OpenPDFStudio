"""Merge tab — combine multiple PDFs into one."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..core import merge_pdfs, format_bytes
from ..locale import _


class TabMerge(tb.Frame):
    """Merge multiple PDF files into one document."""

    def __init__(self, parent: tb.Window, app) -> None:
        super().__init__(parent)
        self.app = app
        self._tr_map: dict = {}
        self._file_list: list[str] = []

        self.output_path = tb.StringVar(value="merged.pdf")

        self._build_ui()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tr(self, widget, key):
        self._tr_map[id(widget)] = (widget, key)
        return widget

    def _refresh_listbox(self) -> None:
        self.listbox.delete(0, END)
        for p in self._file_list:
            self.listbox.insert(END, Path(p).name)
        self._update_status()

    def _update_status(self) -> None:
        n = len(self._file_list)
        if n == 0:
            self.status.set(_("merge_status_ready", self.app.lang))
        else:
            self.status.set(f"{n} file(s) selected")

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tb.Frame(self, padding=12)
        main.pack(fill=BOTH, expand=True)

        # -- File list --
        lbl_inputs = tb.Label(main, text="", font=("", 9, "bold"))
        self._tr(lbl_inputs, "merge_inputs")
        lbl_inputs.pack(anchor="w")

        list_frame = tb.Frame(main)
        list_frame.pack(fill=BOTH, expand=True, pady=(4, 8))

        self.listbox = tb.Treeview(
            list_frame,
            columns=("path",),
            show="",
            height=6,
        )
        self.listbox.column("path", width=400)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scroll = tb.Scrollbar(list_frame, orient=VERTICAL, command=self.listbox.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.listbox.configure(yscrollcommand=scroll.set)

        # -- Buttons row --
        btn_row = tb.Frame(main)
        btn_row.pack(fill=X, pady=(0, 8))

        btn_add = tb.Button(btn_row, text="", command=self._add_files, bootstyle="secondary")
        self._tr(btn_add, "merge_add")
        btn_add.pack(side=LEFT, padx=(0, 4))

        btn_remove = tb.Button(btn_row, text="", command=self._remove_selected, bootstyle="secondary")
        self._tr(btn_remove, "merge_remove")
        btn_remove.pack(side=LEFT, padx=4)

        tb.Button(btn_row, text=_("merge_up", "en"), command=self._move_up, width=3).pack(
            side=LEFT, padx=4
        )
        tb.Button(btn_row, text=_("merge_down", "en"), command=self._move_down, width=3).pack(
            side=LEFT, padx=4
        )

        # -- Output --
        out_frame = tb.Frame(main)
        out_frame.pack(fill=X, pady=(0, 8))

        lbl_out = tb.Label(out_frame, text="", font=("", 9, "bold"))
        self._tr(lbl_out, "merge_output")
        lbl_out.pack(anchor="w")

        out_row = tb.Frame(out_frame)
        out_row.pack(fill=X, pady=(2, 0))
        tb.Entry(out_row, textvariable=self.output_path).pack(side=LEFT, fill=X, expand=True)
        btn_out = tb.Button(out_row, text="", command=self._browse_output, bootstyle="secondary")
        self._tr(btn_out, "browse")
        btn_out.pack(side=LEFT, padx=(6, 0))

        # -- Progress --
        self.progress = tb.Progressbar(main, mode="indeterminate", bootstyle="success-striped")
        self.progress.pack(fill=X, pady=(4, 4))

        self.status = tb.StringVar(value="")
        tb.Label(main, textvariable=self.status, bootstyle="secondary").pack(anchor="w")

        # -- Merge button --
        self.btn = tb.Button(
            main,
            text="",
            command=self._merge,
            bootstyle="primary",
            padding=(40, 10),
        )
        self._tr(self.btn, "merge_go")
        self.btn.pack(pady=(8, 0))

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
        self._update_status()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title=_("merge_inputs", self.app.lang),
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")],
        )
        for p in paths:
            if p not in self._file_list:
                self._file_list.append(p)
        self._refresh_listbox()

    def _remove_selected(self) -> None:
        sel = self.listbox.selection()
        if not sel:
            return
        indices = sorted(
            [self.listbox.index(i) for i in sel],
            reverse=True,
        )
        for idx in indices:
            if 0 <= idx < len(self._file_list):
                self._file_list.pop(idx)
        self._refresh_listbox()

    def _move_up(self) -> None:
        sel = self.listbox.selection()
        if not sel:
            return
        idx = self.listbox.index(sel[0])
        if idx > 0:
            self._file_list[idx], self._file_list[idx - 1] = (
                self._file_list[idx - 1],
                self._file_list[idx],
            )
            self._refresh_listbox()

    def _move_down(self) -> None:
        sel = self.listbox.selection()
        if not sel:
            return
        idx = self.listbox.index(sel[0])
        if idx < len(self._file_list) - 1:
            self._file_list[idx], self._file_list[idx + 1] = (
                self._file_list[idx + 1],
                self._file_list[idx],
            )
            self._refresh_listbox()

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title=_("merge_output", self.app.lang),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.output_path.set(path)

    def _merge(self) -> None:
        files = list(self._file_list)
        out = self.output_path.get().strip()
        lang = self.app.lang

        if len(files) < 2:
            messagebox.showerror(
                _("error_title", lang),
                _("err_merge_need_two", lang),
            )
            return

        if not out:
            messagebox.showerror(_("error_title", lang), _("err_no_output", lang))
            return

        self.btn.config(state=DISABLED)
        self.progress.start(12)
        self.status.set(_("status_working", lang))

        def task() -> None:
            try:
                result = merge_pdfs(files, out)
                self.app.root.after(0, self._on_done, result, lang)
            except Exception as exc:
                self.app.root.after(0, self._on_error, exc, lang)

        threading.Thread(target=task, daemon=True).start()

    def _on_done(self, result: dict, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        msg = _("merge_done", lang, n=result["files_merged"], pages=result["pages_total"])
        self.status.set(f"✅ {msg}  ·  {format_bytes(result['output_size'])}")
        messagebox.showinfo(
            _("done_title", lang),
            f"{msg}\n"
            f"{_('done_compressed', lang)}: {format_bytes(result['output_size'])}\n"
            f"{_('done_time', lang)}: {result['elapsed']:.1f} {_('done_seconds', lang)}",
        )

    def _on_error(self, exc: Exception, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        self.status.set(_("status_error", lang))
        messagebox.showerror(_("error_title", lang), str(exc))
