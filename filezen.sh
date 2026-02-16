#!/usr/bin/env bash
# ─────────────────────────────────────────────
# FileZen – Iniciar GUI no Linux
# ─────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

# Cria venv se não existir
if [ ! -d "$VENV" ]; then
    echo "Criando ambiente virtual…"
    python3 -m venv "$VENV"
fi

# Ativa venv
source "$VENV/bin/activate"

# Instala dependências se necessário
if ! python -c "import PySide6" 2>/dev/null; then
    echo "Instalando PySide6…"
    pip install --upgrade pip -q
    pip install PySide6 -q
fi

# Executa a GUI
exec python "$SCRIPT_DIR/src/gui.py"
