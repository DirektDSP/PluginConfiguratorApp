"""Shared test configuration."""

import os

# Ensure Qt runs in headless environments for PySide-based tests.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
