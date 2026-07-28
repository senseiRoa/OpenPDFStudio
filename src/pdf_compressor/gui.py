#!/usr/bin/env python3
"""GUI — modern interface with ttkbootstrap."""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox

from .core import compress, format_bytes

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
except ImportError:
    messagebox.showerror(
        "Error",
        "ttkbootstrap no está instalado.\n\n"
        "Ejecutá: pip install ttkbootstrap",
    )
    raise SystemExit(1)


class App:
    def __init__(self) -> None:
        self.root = tb.Window(themename="litera")
        self.root.title("PDF Compressor")
        self.root.geometry("560x620")
        self.root.minsize(520, 580)

        self.input_path = tb.StringVar()
        self.output_path = tb.StringVar()
        self.quality = tb.IntVar(value=70)
        self.max_width = tb.IntVar(value=1000)
        self.overwrite = tb.BooleanVar(value=False)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=BOTH, expand=True)

        # -- Header --
        tb.Label(
            main,
            text="PDF Compressor",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tb.Label(
            main,
            text="Reducí el tamaño de tus PDFs al instante",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).pack(anchor="w", pady=(0, 16))

        tb.Separator(main).pack(fill=X, pady=(0, 16))

        # -- Input file --
        self._file_row(
            main,
            "PDF de entrada",
            self.input_path,
            self._browse_input,
        )

        # -- Output file --
        self._file_row(
            main,
            "PDF de salida",
            self.output_path,
            self._browse_output,
        )

        # -- Overwrite --
        tb.Checkbutton(
            main,
            text="Sobrescribir archivo de salida si ya existe",
            variable=self.overwrite,
        ).pack(anchor="w", pady=(0, 12))

        tb.Separator(main).pack(fill=X, pady=(0, 12))

        # -- Quality --
        frame_q = tb.LabelFrame(main, text="Calidad JPEG", padding=10)
        frame_q.pack(fill=X, pady=(0, 10))

        tb.Scale(
            frame_q,
            from_=1,
            to=100,
            orient=HORIZONTAL,
            variable=self.quality,
            length=400,
        ).pack(fill=X)
        row_q = tb.Frame(frame_q)
        row_q.pack(fill=X)
        tb.Label(row_q, text="1 (mínima)", bootstyle="secondary").pack(side=LEFT)
        tb.Label(
            row_q,
            textvariable=self.quality,
            font=("", 12, "bold"),
            bootstyle="primary",
        ).pack(side=RIGHT, padx=(0, 4))
        tb.Label(row_q, text="100 (máxima)", bootstyle="secondary").pack(side=RIGHT)

        # -- Max width --
        frame_w = tb.LabelFrame(main, text="Ancho máximo", padding=10)
        frame_w.pack(fill=X, pady=(0, 10))

        row_w = tb.Frame(frame_w)
        row_w.pack(fill=X)
        tb.Entry(row_w, textvariable=self.max_width, width=8, justify="center").pack(
            side=LEFT
        )
        tb.Label(row_w, text="px  ·  0 = sin límite", bootstyle="secondary").pack(
            side=LEFT, padx=(8, 0)
        )

        # -- Progress --
        self.progress = tb.Progressbar(
            main, mode="indeterminate", bootstyle="success-striped"
        )
        self.progress.pack(fill=X, pady=(12, 0))

        self.status = tb.StringVar(value="💡 Seleccioná un PDF y presioná Comprimir")
        tb.Label(main, textvariable=self.status, bootstyle="secondary").pack(
            anchor="w", pady=(4, 12)
        )

        # -- Compress button --
        self.btn = tb.Button(
            main,
            text="Comprimir",
            command=self._compress,
            bootstyle="primary",
            padding=(40, 10),
        )
        self.btn.pack()

    def _file_row(
        self,
        parent: tb.Frame,
        label: str,
        variable: tb.StringVar,
        callback,
    ) -> None:
        frame = tb.Frame(parent)
        frame.pack(fill=X, pady=(0, 8))

        tb.Label(frame, text=label, font=("", 9, "bold")).pack(anchor="w")
        row = tb.Frame(frame)
        row.pack(fill=X, pady=(2, 0))
        tb.Entry(row, textvariable=variable).pack(side=LEFT, fill=X, expand=True)
        tb.Button(
            row,
            text="Examinar…",
            command=callback,
            bootstyle="secondary",
        ).pack(side=LEFT, padx=(6, 0))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if path:
            self.input_path.set(path)
            p = Path(path)
            self.output_path.set(str(p.with_name(f"{p.stem}_compressed.pdf")))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if path:
            self.output_path.set(path)

    def _compress(self) -> None:
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()

        errors = []
        if not inp:
            errors.append("Seleccioná un archivo PDF de entrada.")
        if not out:
            errors.append("Indicá la ruta de salida.")
        if inp and not os.path.exists(inp):
            errors.append(f"No existe:\n{inp}")
        if out and os.path.exists(out) and not self.overwrite.get():
            errors.append(f"Ya existe:\n{out}\n\nMarcá «Sobrescribir» o cambiá la ruta.")

        if errors:
            messagebox.showerror("Error", "\n\n".join(errors))
            return

        q = self.quality.get()
        w = self.max_width.get()
        if w < 0:
            w = 0

        self.btn.config(state=DISABLED)
        self.progress.start(12)
        self.status.set("⏳ Comprimiendo…")

        def task() -> None:
            try:
                result = compress(inp, out, q, w)
                self.root.after(0, self._on_done, result)
            except Exception as exc:
                self.root.after(0, self._on_error, exc)

        threading.Thread(target=task, daemon=True).start()

    def _on_done(self, result: dict) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        ratio = (1 - result["output_size"] / result["input_size"]) * 100
        self.status.set(
            f"✅ Original: {format_bytes(result['input_size'])}  →  "
            f"Comprimido: {format_bytes(result['output_size'])}  "
            f"({ratio:.1f}%  ·  {result['elapsed']:.1f}s)"
        )
        messagebox.showinfo(
            "Completado",
            f"Original:   {format_bytes(result['input_size'])}\n"
            f"Comprimido: {format_bytes(result['output_size'])}\n"
            f"Reducción:  {ratio:.1f}%\n"
            f"Tiempo:     {result['elapsed']:.1f} segundos",
        )

    def _on_error(self, exc: Exception) -> None:
        self.progress.stop()
        self.btn.config(state=NORMAL)
        self.status.set("❌ Error")
        messagebox.showerror("Error", str(exc))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    app = App()
    app.run()


if __name__ == "__main__":
    main()
