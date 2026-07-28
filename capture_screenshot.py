#!/usr/bin/env python3
"""Capture a screenshot of the GUI for documentation."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_compressor.gui import App

app = App()

app.root.update_idletasks()
w = app.root.winfo_width()
h = app.root.winfo_height()
x = (app.root.winfo_screenwidth() // 2) - (w // 2)
y = (app.root.winfo_screenheight() // 2) - (h // 2)
app.root.geometry(f"+{x}+{y}")
app.root.update()
time.sleep(0.5)

from PIL import ImageGrab

x1 = app.root.winfo_rootx()
y1 = app.root.winfo_rooty()
x2 = x1 + app.root.winfo_width()
y2 = y1 + app.root.winfo_height()

img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
out = Path(__file__).parent / "docs" / "screenshot.png"
img.save(out)
app.root.destroy()
print(f"✅ Screenshot saved: {out}")
