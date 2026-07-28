#!/usr/bin/env python3
"""GUI — modern ttkbootstrap interface with notebook tabs and live language switching."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
except ImportError:
    messagebox.showerror(
        "Error",
        "ttkbootstrap is not installed.\n\nRun: pip install ttkbootstrap",
    )
    raise SystemExit(1)

from .tab_compress import TabCompress
from .tab_merge import TabMerge
from .tab_split import TabSplit
from .tab_pages import TabPages
from ..locale import _, LANGUAGES


class App:
    """Main application window with notebook (tabbed) interface."""

    def __init__(self) -> None:
        self.root = tb.Window(themename="litera")
        self.root.title("OpenPDFStudio")
        self.root.geometry("640x700")
        self.root.minsize(580, 640)

        self.lang = "en"

        self._build_ui()
        self._apply_language()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tb.Frame(self.root, padding=12)
        main.pack(fill=BOTH, expand=True)

        # -- Language switcher (top-right) --
        lang_row = tb.Frame(main)
        lang_row.pack(fill=X, pady=(0, 4))

        lbl_title = tb.Label(
            lang_row,
            text="OpenPDFStudio",
            font=("Segoe UI", 16, "bold"),
        )
        lbl_title.pack(side=LEFT)

        self.lang_cb = tb.Combobox(
            lang_row,
            values=["EN", "ES"],
            state="readonly",
            width=6,
            justify="center",
        )
        self.lang_cb.set("EN")
        self.lang_cb.bind("<<ComboboxSelected>>", self._on_lang_change)
        self.lang_cb.pack(side=RIGHT)

        # -- Notebook (tabs) --
        self.notebook = tb.Notebook(main)
        self.notebook.pack(fill=BOTH, expand=True, pady=(6, 0))

        self.tab_compress = TabCompress(self.notebook, self)
        self.tab_merge = TabMerge(self.notebook, self)
        self.tab_split = TabSplit(self.notebook, self)
        self.tab_pages = TabPages(self.notebook, self)

        # Tab texts are set via _apply_language
        self._tab_keys = ["tab_compress", "tab_merge", "tab_split", "tab_pages"]
        self._tab_widgets = [
            self.tab_compress,
            self.tab_merge,
            self.tab_split,
            self.tab_pages,
        ]

        for i, w in enumerate(self._tab_widgets):
            self.notebook.add(w, text=self._tab_keys[i])

        # -- Status bar --
        self.status = tb.StringVar(value="")
        self.status_bar = tb.Label(
            main,
            textvariable=self.status,
            bootstyle="secondary",
            anchor="w",
        )
        self.status_bar.pack(fill=X, pady=(6, 0))

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def _on_lang_change(self, *_):
        self.lang = "es" if self.lang_cb.get() == "ES" else "en"
        self._apply_language()

    def _apply_language(self) -> None:
        """Update all tab labels and notebook tab texts."""
        for i, key in enumerate(self._tab_keys):
            self.notebook.tab(i, text=_(key, self.lang))

        for w in self._tab_widgets:
            w.apply_language()

        self.root.title(_("window_title", self.lang))

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    app = App()
    app.run()


if __name__ == "__main__":
    main()
