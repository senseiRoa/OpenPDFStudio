#!/usr/bin/env python3
"""Backward-compatible entry point for CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pdf_compressor.cli import main

sys.exit(main())
