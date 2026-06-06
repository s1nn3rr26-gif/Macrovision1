#!/bin/bash
# ─────────────────────────────────────────
#  MacroVision Launcher (Mac / Linux)
# ─────────────────────────────────────────

echo ""
echo "  =========================================="
echo "   MacroVision - Dashboard Macro Global"
echo "  =========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "  ERROR: Python3 no encontrado."
    echo "  Instala con: brew install python  (Mac)"
    exit 1
fi

# Instalar dependencias solo la primera vez
if [ ! -f ".deps_installed" ]; then
    echo "  Instalando dependencias por primera vez..."
    pip3 install -r requirements.txt -q
    touch .deps_installed
    echo "  Dependencias instaladas."
    echo ""
fi

echo "  Abriendo MacroVision en tu navegador..."
echo "  Ctrl+C para detener"
echo ""

streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
