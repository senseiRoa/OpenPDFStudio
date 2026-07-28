#!/usr/bin/env python3
"""Backward-compatible entry point for Merge CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pdf_compressor.cli import merge_main

sys.exit(merge_main())
