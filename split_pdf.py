#!/usr/bin/env python3
"""Backward-compatible entry point for Split CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pdf_compressor.cli import split_main

sys.exit(split_main())
