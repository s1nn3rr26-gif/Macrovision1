@echo off
title MacroVision Launcher
color 0A

echo.
echo  ==========================================
echo   MacroVision - Dashboard Macro Global
echo  ==========================================
echo.

REM ── Verificar Python ─────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no encontrado.
    echo  Descarga Python en https://python.org
    pause
    exit /b 1
)

REM ── Instalar dependencias (solo primera vez) ──
if not exist ".deps_installed" (
    echo  Instalando dependencias por primera vez...
    pip install -r requirements.txt -q
    echo done > .deps_installed
    echo  Dependencias instaladas.
    echo.
)

REM ── Abrir dashboard ──────────────────────────
echo  Abriendo MacroVision en tu navegador...
echo  (Cierra esta ventana para detener el servidor)
echo.
streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

pause
