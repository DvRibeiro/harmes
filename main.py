#!/usr/bin/env python3
"""Ponto de entrada raiz para execução do HARMES."""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no PYTHONPATH
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app import main

if __name__ == "__main__":
    main()
