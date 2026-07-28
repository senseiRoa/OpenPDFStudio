"""Pages tab — reorder, delete, rotate, extract pages."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..core import reorder_pages, delete_pages, rotate_pages, extract_pages, format_bytes
from ..locale import _


def _parse_page_list(s: str) -> list[int]:
    """Parse '1,3,5-7' into a flat list of page numbers (1-indexed)."""
    pages: list[int] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a.strip()), int(b.strip()) + 1))
        else:
            pages.append(int(part))
    return pages


class TabPages(tb.Frame):
    """Page operations: reorder, delete, rotate, extract."""

    def __init__(self, parent: tb.Window, app) -> None:
        super().__init__(parent)
        self.app = app
        self._tr_map: dict = {}

        self.input_path = tb.StringVar()
        self.output_path = tb.StringVar()
        self.operation = tb.StringVar(value="reorder")
        self.order = tb.StringVar(value="reverse")
        self.pages = tb.StringVar(value="1,3,5")
        self.angle = tb.IntVar(value=90)
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

    def _show_op_options(self) -> None:
        """Show/hide operation-specific input widgets."""
        op = self.operation.get()
        self._reorder_frame.pack_forget()
        self._rotate_frame.pack_forget()
        self._pages_frame.pack_forget()

        if op == "reorder":
            self._reorder_frame.pack(fill=X, pady=(0, 8))
        elif op == "rotate":
            self._rotate_frame.pack(fill=X, pady=(0, 8))
            self._pages_frame.pack(fill=X, pady=(0, 8))
        else:
            # delete / extract also need pages
            self._pages_frame.pack(fill=X, pady=(0, 8))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tb.Frame(self, padding=12)
        main.pack(fill=BOTH, expand=True)

        # -- Input / Output --
        self._file_row(main, "pages_input", self.input_path, self._browse_input)
        self._file_row(main, "pages_output", self.output_path, self._browse_output)

        chk = tb.Checkbutton(main, text="", variable=self.overwrite)
        self._tr(chk, "overwrite")
        chk.pack(anchor="w", pady=(0, 8))

        tb.Separator(main).pack(fill=X, pady=(4, 8))

        # -- Operation selector --
        lbl_op = tb.Label(main, text="", font=("", 9, "bold"))
        self._tr(lbl_op, "pages_operation")
        lbl_op.pack(anchor="w")

        op_row = tb.Frame(main)
        op_row.pack(fill=X, pady=(4, 8))

        ops = [
            ("pages_opt_reorder", "reorder"),
            ("pages_opt_delete", "delete"),
            ("pages_opt_rotate", "rotate"),
            ("pages_opt_extract", "extract"),
        ]
        for key, val in ops:
            rb = tb.Radiobutton(
                op_row,
                text="",
                variable=self.operation,
                value=val,
                command=self._show_op_options,
            )
            self._tr(rb, key)
            rb.pack(side=LEFT, padx=(0, 12))

        # -- Reorder input --
        self._reorder_frame = tb.Frame(main)
        lbl_o = tb.Label(self._reorder_frame, text="", bootstyle="secondary")
        self._tr(lbl_o, "pages_order_help")
        lbl_o.pack(anchor="w")
        tb.Entry(self._reorder_frame, textvariable=self.order).pack(fill=X, pady=(2, 0))

        # -- Pages input (for delete, extract, rotate target) --
        self._pages_frame = tb.Frame(main)
        lbl_p = tb.Label(self._pages_frame, text="", bootstyle="secondary")
        self._tr(lbl_p, "pages_pages_help")
        lbl_p.pack(anchor="w")
        tb.Entry(self._pages_frame, textvariable=self.pages).pack(fill=X, pady=(2, 0))

        # -- Rotate angle --
        self._rotate_frame = tb.Frame(main)
        lbl_a = tb.Label(self._rotate_frame, text="", font=("", 9))
        self._tr(lbl_a, "pages_angle_label")
        lbl_a.pack(anchor="w")
        angle_row = tb.Frame(self._rotate_frame)
        angle_row.pack(fill=X, pady=(2, 0))
        for deg, key in [(90, "pages_angle_90"), (180, "pages_angle_180"), (270, "pages_angle_270")]:
            rb = tb.Radiobutton(
                angle_row,
                text="",
                variable=self.angle,
                value=deg,
            )
            self._tr(rb, key)
            rb.pack(side=LEFT, padx=(0, 12))

        tb.Separator(main).pack(fill=X, pady=(4, 8))

        # -- Progress --
        self.progress = tb.Progressbar(main, mode="indeterminate", bootstyle="success-striped")
        self.progress.pack(fill=X, pady=(4, 4))

        self.status = tb.StringVar(value="")
        lbl_st = tb.Label(main, textvariable=self.status, bootstyle="secondary")
        self._tr(lbl_st, "pages_status_ready")
        lbl_st.pack(anchor="w")

        # -- Apply button --
        self.btn = tb.Button(
            main,
            text="",
            command=self._apply,
            bootstyle="primary",
            padding=(40, 10),
        )
        self._tr(self.btn, "pages_go")
        self.btn.pack(pady=(8, 0))

        # Initial state
        self._show_op_options()

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
        self.status.set(_("pages_status_ready", self.app.lang))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title=_("pages_input", self.app.lang),
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")],
        )
        if path:
            self.input_path.set(path)
            p = Path(path)
            if not self.output_path.get():
                self.output_path.set(str(p.with_name(f"{p.stem}_editado.pdf")))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title=_("pages_output", self.app.lang),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.output_path.set(path)

    def _apply(self) -> None:
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()
        op = self.operation.get()
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

        self.btn.config(state=DISABLED)
        self.progress.start(12)
        self.status.set(_("status_working", lang))

        def task() -> None:
            try:
                if op == "reorder":
                    order: list[int] | str = self.order.get().strip()
                    if order.lower() == "reverse":
                        pass  # pass str "reverse" directly
                    else:
                        order = _parse_page_list(order)
                    result = reorder_pages(inp, out, order)
                    label = _("pages_opt_reorder", lang)

                elif op == "delete":
                    pages = _parse_page_list(self.pages.get().strip())
                    result = delete_pages(inp, out, pages)
                    label = _("pages_opt_delete", lang)

                elif op == "rotate":
                    target = (
                        _parse_page_list(self.pages.get().strip())
                        if self.pages.get().strip()
                        else None
                    )
                    result = rotate_pages(inp, out, self.angle.get(), target)
                    label = _("pages_opt_rotate", lang)

                elif op == "extract":
                    pages = _parse_page_list(self.pages.get().strip())
                    result = extract_pages(inp, out, pages)
                    label = _("pages_opt_extract", lang)

                else:
                    raise RuntimeError(f"Unknown operation: {op}")

                self.app.root.after(0, self._on_done, result, label, lang)
            except Exception as exc:
                self.app.root.after(0, self._on_error, exc, lang)

        threading.Thread(target=task, daemon=True).start()

    def _on_done(self, result: dict, label: str, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)

        n = result.get("pages", result.get("pages_rotated", 0))
        msg = _("pages_done", lang, op=label, n=n)
        ratio = (1 - result["output_size"] / result["input_size"]) * 100

        self.status.set(
            f"✅ {_('done_original', lang)}: {format_bytes(result['input_size'])}  →  "
            f"{format_bytes(result['output_size'])}  ({ratio:.1f}%)"
        )

        info = (
            f"{msg}\n\n"
            f"{_('done_original', lang)}:   {format_bytes(result['input_size'])}\n"
            f"{_('done_compressed', lang)}: {format_bytes(result['output_size'])}\n"
            f"{_('done_reduction', lang)}:  {ratio:.1f}%\n"
            f"{_('done_time', lang)}:     {result['elapsed']:.1f} {_('done_seconds', lang)}"
        )
        messagebox.showinfo(_("done_title", lang), info)

    def _on_error(self, exc: Exception, lang: str) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        self.status.set(_("status_error", lang))
        messagebox.showerror(_("error_title", lang), str(exc))
