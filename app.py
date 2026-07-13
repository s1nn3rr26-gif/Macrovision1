# ─────────────────────────────────────────────────────────
#  MacroVision · app.py (VERSIÓN DEFINITIVA SIN ERRORES)
#  Dashboard Macroeconómico con Semáforo Macro, Alertas,
#  Reglas de Trading, Correlaciones, Análisis de Activos,
#  Módulo Trading Quant y Memoria del Agente IA (Ollama)
# ─────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import subprocess
import sys
from datetime import datetime
import yfinance as yf
import requests
import warnings
warnings.filterwarnings("ignore")

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────
st.set_page_config(
    page_title="MacroVision Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh cada 4 horas (opcional)
st.markdown('<meta http-equiv="refresh" content="14400">', unsafe_allow_html=True)

# ── LISTAS DE ACTIVOS SUGERIDOS ──────────────────────────
SUG_DIVISAS = [
    ("EUR/USD", "EURUSD=X"), ("GBP/USD", "GBPUSD=X"), ("USD/JPY", "USDJPY=X"),
    ("AUD/USD", "AUDUSD=X"), ("USD/CAD", "USDCAD=X"), ("NZD/USD", "NZDUSD=X"),
    ("USD/CHF", "USDCHF=X"), ("DXY", "DX-Y.NYB")
]

SUG_COMMODITIES = [
    ("Oro", "GC=F"), ("Plata", "SI=F"), ("Crudo WTI", "CL=F"),
    ("Gas Natural", "NG=F"), ("Cobre", "HG=F"), ("Trigo", "ZW=F"),
    ("Maíz", "ZC=F"), ("Café", "KC=F")
]

SUG_INDICES = [
    ("S&P 500", "^GSPC"), ("Nasdaq", "^IXIC"), ("Dow Jones", "^DJI"),
    ("DAX", "^GDAXI"), ("Nikkei 225", "^N225"), ("FTSE 100", "^FTSE"),
    ("Hang Seng", "^HSI")
]

SUG_CRIPTO = [
    ("Bitcoin", "BTC-USD"), ("Ethereum", "ETH-USD")
]

SUG_OTROS = [
    ("NVIDIA", "NVDA"), ("Apple", "AAPL"), ("Tesla", "TSLA")
]

# ── FUNCIÓN PARA RENDERIZAR SUGERENCIAS ──────────────────
def render_sugerencias(session_key, tickers, cols=6, label="Sugerencias:", list_name="default"):
    """
    Muestra botones de sugerencias de tickers.
    Al hacer clic, actualiza el session_state[session_key] y rerun.
    """
    st.markdown(f"**{label}**")
    cols_container = st.columns(cols)
    for i, (display, ticker) in enumerate(tickers):
        key = f"sug_{session_key}_{list_name}_{i}"
        col_idx = i % len(cols_container) if cols_container else 0
        if col_idx < len(cols_container) and cols_container[col_idx].button(display, key=key):
            st.session_state[session_key] = ticker
            st.rerun()

# ── CSS PROFESIONAL ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"], .stApp, .main, .block-container {
        background: #000000 !important;
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 100%;
    }

    .mv-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 16px;
        border-bottom: 1px solid #333333;
        margin-bottom: 20px;
    }
    .mv-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .mv-title span { color: #3b82f6; }
    .mv-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #aaaaaa;
        margin-top: 4px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px #10b981;
        display: inline-block;
    }
    .mv-badge {
        background: #1f1f1f;
        color: #cccccc;
        font-size: 10px;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    .bank-card {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 14px;
        cursor: pointer;
        transition: all 0.2s;
        margin: 5px 0;
    }
    .bank-card:hover {
        border-color: #3b82f6;
        background: #1a1a2e;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
    }
    .bank-card.selected {
        border-color: #3b82f6;
        background: #1a1a2e;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.3);
    }
    .bank-card-top {
        width: 100%;
        height: 2px;
        border-radius: 2px;
        margin-bottom: 10px;
    }
    .bank-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 16px;
        font-weight: 700;
    }
    .bank-rate {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
    }
    .bank-last {
        font-size: 10px;
        color: #8B949E;
    }

    .sent-bull {
        background: rgba(16,185,129,0.2);
        color: #4ade80;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 10px;
        font-weight: 700;
    }
    .sent-bear {
        background: rgba(239,68,68,0.2);
        color: #f87171;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 10px;
        font-weight: 700;
    }
    .sent-neut {
        background: rgba(245,158,11,0.2);
        color: #fbbf24;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 10px;
        font-weight: 700;
    }

    .ind-row {
        display: grid;
        grid-template-columns: 130px 1fr 100px 100px 120px;
        padding: 10px 16px;
        border-bottom: 1px solid #111827;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }
    .ind-header {
        background: #070b14;
        font-size: 10px;
        color: #4b5563;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }

    div[data-testid="metric-container"] {
        background: #0d1117 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px;
    }

    header { visibility: hidden; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }

    .ia-panel {
        background: #111827;
        padding: 20px;
        border-left: 5px solid #8b5cf6;
        border-radius: 5px;
        margin: 10px 0;
    }
    .ia-panel pre {
        white-space: pre-wrap;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        color: #ffffff;
    }

    .alert-card {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .alert-rojo {
        background: rgba(239,68,68,0.15);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    .alert-verde {
        background: rgba(16,185,129,0.15);
        border-left: 4px solid #10b981;
        color: #6ee7b7;
    }
    .alert-naranja {
        background: rgba(245,158,11,0.15);
        border-left: 4px solid #f59e0b;
        color: #fcd34d;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0d1117;
        border-bottom: 1px solid #1f2937;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8B949E;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff;
        border-bottom: 2px solid #3b82f6;
    }

    .risk-on { background: #10b98122; border: 1px solid #10b98144; color: #10b981; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
    .risk-off { background: #ef444422; border: 1px solid #ef444444; color: #ef4444; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
    .risk-mixed { background: #f59e0b22; border: 1px solid #f59e0b44; color: #f59e0b; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── CONFIGURACIÓN (fallback si no existe config.py) ──────
try:
    from config import BANK_COLORS, CATEGORIES, CAT_ICONS, SENT_CLASS
except ImportError:
    BANK_COLORS = {
        "FED": "#3b82f6", "BCE": "#8b5cf6", "BOE": "#ec4899",
        "BOC": "#f97316", "RBA": "#10b981", "RBNZ": "#06b6d4"
    }
    CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]
    CAT_ICONS = {"INFLACIÓN": "📊", "CRECIMIENTO": "📈", "EMPLEO": "👷", "CONSUMO": "🛒", "ACTIVIDAD": "🏭", "INMOBILIARIO": "🏠"}
    SENT_CLASS = {
        "BULLISH": "sent-bull",
        "BEARISH": "sent-bear",
        "NEUTRO": "sent-neut"
    }

# ── FUNCIONES DE DATOS (CACHE) ────────────────────────────
@st.cache_data(ttl=14400)
def get_macro_data():
    try:
        tickers = {
            'dxy': 'DX-Y.NYB',
            'vix': '^VIX',
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'oro': 'GC=F',
            'bond10y': '^TNX'
        }
        data = yf.download(list(tickers.values()), period="5d", progress=False)
        if data.empty:
            return None
        result = {}
        for key, symbol in tickers.items():
            try:
                if isinstance(data['Close'], pd.DataFrame):
                    close_series = data['Close'][symbol].dropna()
                else:
                    close_series = data['Close'].dropna() if symbol == list(tickers.values())[0] else data['Close']
                if len(close_series) < 2:
                    continue
                curr = float(close_series.iloc[-1])
                prev = float(close_series.iloc[-2])
                result[key] = {
                    'price': curr,
                    'change_pct': ((curr / prev) - 1) * 100
                }
            except (KeyError, IndexError, ValueError):
                continue
        return result if 'dxy' in result and 'vix' in result else None
    except Exception:
        return None

@st.cache_data(ttl=86400)
def get_correlation_matrix():
    try:
        tickers = {
            'DXY': 'DX-Y.NYB',
            'VIX': '^VIX',
            'S&P 500': '^GSPC',
            'Nasdaq': '^IXIC',
            'Oro': 'GC=F',
            'Bono 10Y': '^TNX',
            'Brent': 'BZ=F',
            'WTI': 'CL=F',
            'DAX': '^GDAXI',
            'Nikkei': '^N225'
        }
        df = yf.download(list(tickers.values()), period="1y", progress=False)
        if df.empty:
            return None
        close_df = df['Close']
        rename_dict = {v: k for k, v in tickers.items()}
        close_df = close_df.rename(columns=rename_dict)
        returns = close_df.pct_change().dropna()
        return returns.corr()
    except Exception as e:
        st.error(f"Error en correlación: {e}")
        return None

@st.cache_data(ttl=14400)
def load_macro_data():
    if os.path.exists("macro_data.json"):
        with open("macro_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=14400)
def load_ai_memory():
    if os.path.exists("ai_memory.json"):
        with open("ai_memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ── FUNCIONES DE ALERTAS Y CONCLUSIONES ──────────────────
def generar_alertas(macro_data):
    if not macro_data:
        return []
    alertas = []
    dxy = macro_data.get('dxy', {})
    vix = macro_data.get('vix', {})
    sp500 = macro_data.get('sp500', {})
    nasdaq = macro_data.get('nasdaq', {})
    oro = macro_data.get('oro', {})
    bond = macro_data.get('bond10y', {})

    if dxy.get('change_pct', 0) > 0 and vix.get('change_pct', 0) > 0:
        alertas.append({"m": "🔴 DXY y VIX al alza → Aversión al riesgo (Risk-Off).", "c": "rojo"})
    if dxy.get('change_pct', 0) < 0 and vix.get('change_pct', 0) < 0:
        alertas.append({"m": "🟢 DXY y VIX a la baja → Apetito por riesgo (Risk-On).", "c": "verde"})
    if dxy.get('change_pct', 0) > 0 and oro.get('change_pct', 0) < 0:
        alertas.append({"m": "📉 Dólar fuerte presiona al oro.", "c": "naranja"})
    if dxy.get('change_pct', 0) < 0 and oro.get('change_pct', 0) > 0:
        alertas.append({"m": "📈 Dólar débil impulsa al oro.", "c": "verde"})
    if nasdaq.get('change_pct', 0) > 0 and vix.get('change_pct', 0) > 0:
        alertas.append({"m": "⚠️ Nasdaq sube pero VIX sube → Divergencia peligrosa.", "c": "rojo"})
    if bond.get('change_pct', 0) > 0 and dxy.get('change_pct', 0) > 0:
        alertas.append({"m": "📈 Tasas y dólar fuertes → Presión sobre tecnológicas.", "c": "naranja"})
    if bond.get('change_pct', 0) < 0 and oro.get('change_pct', 0) > 0:
        alertas.append({"m": "📉 Tasas a la baja y oro al alza → Refugio en metales.", "c": "verde"})
    return alertas

def generar_conclusion_estrategica(macro_data):
    if not macro_data:
        return {"regimen": "SIN DATOS", "oportunidades": ["No hay datos."], "riesgos": ["No hay datos."], "recomendacion": "Verifica conexión."}
    dxy = macro_data.get('dxy', {})
    vix = macro_data.get('vix', {})
    sp500 = macro_data.get('sp500', {})
    nasdaq = macro_data.get('nasdaq', {})
    oro = macro_data.get('oro', {})
    bond = macro_data.get('bond10y', {})

    dxy_up = dxy.get('change_pct', 0) > 0
    vix_up = vix.get('change_pct', 0) > 0
    if dxy_up and vix_up:
        regimen = "🔴 AVERSIÓN AL RIESGO (Risk-Off)"
    elif not dxy_up and not vix_up:
        regimen = "🟢 APETITO POR RIESGO (Risk-On)"
    else:
        regimen = "🟡 MIXTO (Divergencia)"

    oportunidades = []
    riesgos = []

    if dxy.get('change_pct', 0) < 0 and oro.get('change_pct', 0) > 0:
        oportunidades.append("📈 Dólar débil impulsa el oro → Largos en metales preciosos.")
    if vix.get('change_pct', 0) < 0 and sp500.get('change_pct', 0) > 0:
        oportunidades.append("📊 VIX a la baja y S&P al alza → Favorable para índices.")
    if bond.get('change_pct', 0) < 0 and oro.get('change_pct', 0) > 0:
        oportunidades.append("📉 Tasas a la baja y oro al alza → Bonos y metales como refugio.")

    if dxy.get('change_pct', 0) > 0 and oro.get('change_pct', 0) < 0:
        riesgos.append("📉 Dólar fuerte presiona al oro.")
    if vix.get('change_pct', 0) > 0 and sp500.get('change_pct', 0) < 0:
        riesgos.append("📉 VIX al alza y S&P a la baja → Aumento de miedo.")
    if nasdaq.get('change_pct', 0) > 0 and vix.get('change_pct', 0) > 0:
        riesgos.append("⚠️ Nasdaq sube pero VIX sube → Posible corrección en tecnológicas.")
    if bond.get('change_pct', 0) > 0 and dxy.get('change_pct', 0) > 0:
        riesgos.append("📈 Tasas al alza y dólar fuerte → Presión sobre tecnológicas y deuda.")

    if not oportunidades:
        oportunidades.append("➡️ Sin señales claras de oportunidad. Mantener posiciones.")
    if not riesgos:
        riesgos.append("➡️ Sin riesgos extremos. Condiciones estables.")

    if "APETITO POR RIESGO" in regimen:
        recomendacion = "🟢 **Escenario favorable**: Aumentar exposición a activos de riesgo (acciones, commodities cíclicos). Buscar largos en índices."
    elif "AVERSIÓN AL RIESGO" in regimen:
        recomendacion = "🔴 **Escenario defensivo**: Reducir exposición a riesgo. Buscar refugio en oro, bonos y dólar."
    else:
        recomendacion = "🟡 **Escenario mixto**: Selección activa. No agregar riesgo de forma agresiva."

    return {"regimen": regimen, "oportunidades": oportunidades, "riesgos": riesgos, "recomendacion": recomendacion}

def evaluar_reglas(macro_data, reglas):
    if not macro_data or not reglas:
        return []
    alertas_reglas = []
    dxy = macro_data.get('dxy', {})
    vix = macro_data.get('vix', {})
    oro = macro_data.get('oro', {})
    cobre = macro_data.get('cobre', {})

    if dxy.get('change_pct', 0) > 1.0 and oro.get('change_pct', 0) < -2.0:
        alertas_reglas.append({"m": "📉 Regla DXY-Oro: DXY sube >1% y Oro cae >2% → Divergencia detectada.", "c": "naranja"})
    if vix.get('price', 0) > 25:
        vix_price = vix.get('price', 0)
        alertas_reglas.append({"m": f"🔴 VIX en {vix_price:.1f} (>25) → Activación de Risk-Off.", "c": "rojo"})
    if cobre.get('change_pct', 0) < -5:
        alertas_reglas.append({"m": "📉 Cobre cae >5% → Señal de desaceleración global.", "c": "rojo"})
    return alertas_reglas

# ── FUNCIONES DE EJECUCIÓN DE SCRIPTS ────────────────────
def ejecutar_macro_fetch():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "macro_fetch.py")
        resultado = subprocess.run([sys.executable, script_path], cwd=script_dir, capture_output=True, text=True, timeout=180)
        if resultado.returncode != 0:
            st.error(f"❌ Error en macro_fetch.py:\n```\n{resultado.stderr}\n```")
        else:
            print(resultado.stdout)
        return resultado.returncode == 0
    except subprocess.TimeoutExpired:
        st.error("⏱️ El proceso tardó demasiado. Intenta nuevamente.")
        return False
    except Exception as e:
        st.error(f"Excepción al ejecutar: {e}")
        return False

def ejecutar_agente_ia():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "Agente_Ollama.py")
    if not os.path.exists(script_path):
        st.warning("⚠️ No se encontró el archivo Agente_Ollama.py. La funcionalidad de IA no está disponible.")
        return False
    try:
        with st.spinner("🧠 Ejecutando IA local (Ollama)... esto puede tomar hasta 2 minutos."):
            resultado = subprocess.run([sys.executable, script_path], cwd=script_dir, capture_output=True, text=True, timeout=180)
            if resultado.returncode != 0:
                st.error(f"❌ Error en Agente_Ollama.py:\n```\n{resultado.stderr}\n```")
                return False
            else:
                st.success("✅ IA ejecutada correctamente.")
                return True
    except subprocess.TimeoutExpired:
        st.error("⏱️ El proceso de IA tardó demasiado (más de 3 minutos). Asegúrate de que Ollama esté corriendo y que el modelo esté descargado.")
    except Exception as e:
        st.error(f"Excepción al ejecutar: {e}")
    return False

# ── INICIALIZACIÓN DE ESTADO ──────────────────────────────
if "selected" not in st.session_state:
    st.session_state.selected = "FED"
if "ia_updated" not in st.session_state:
    st.session_state.ia_updated = False
if "data_updated" not in st.session_state:
    st.session_state.data_updated = False

macro = get_macro_data()
data = load_macro_data()
memoria_ia = load_ai_memory()

# ─────────────────────────────────────────────────────────────
#  HEADER PROFESIONAL
# ─────────────────────────────────────────────────────────────
col_title, col_btn1, col_btn2 = st.columns([3, 1, 1])
with col_title:
    st.markdown("""
    <div class="mv-header">
        <span class="live-dot"></span>
        <div>
            <p class="mv-title">MACRO<span>VISION</span></p>
            <p class="mv-subtitle">Dashboard Macroeconómico Institucional · Datos en vivo</p>
        </div>
        <span class="mv-badge">v4.0</span>
    </div>
    """, unsafe_allow_html=True)

with col_btn1:
    if st.button("⟳ ACTUALIZAR DATOS", use_container_width=True):
        with st.spinner("Descargando nuevos datos macro..."):
            if ejecutar_macro_fetch():
                st.cache_data.clear()
                st.session_state.data_updated = True
                st.success("✅ Datos macro actualizados correctamente")
                st.rerun()
            else:
                st.error("❌ Error al actualizar los datos. Revisa los mensajes anteriores.")

with col_btn2:
    if st.button("🤖 EJECUTAR IA", use_container_width=True):
        with st.spinner("Generando nueva decisión de la IA..."):
            if ejecutar_agente_ia():
                st.cache_data.clear()
                st.session_state.ia_updated = True
                st.success("✅ Nueva decisión de IA registrada")
                st.rerun()
            else:
                st.error("❌ Error al ejecutar la IA. Revisa los mensajes anteriores.")

# ─────────────────────────────────────────────────────────────
#  SEMÁFORO MACRO Y ALERTAS
# ─────────────────────────────────────────────────────────────
if macro:
    c1, c2, c3 = st.columns(3)
    c1.metric("Dólar (DXY)", f"{macro['dxy']['price']:.2f}", f"{macro['dxy']['change_pct']:.2f}%", delta_color="inverse")
    c2.metric("Miedo (VIX)", f"{macro['vix']['price']:.2f}", f"{macro['vix']['change_pct']:.2f}%", delta_color="inverse")
    c3.metric("Bono US 10Y", f"{macro['bond10y']['price']:.2f}%", f"{macro['bond10y']['change_pct']:.2f}%")

    alertas = generar_alertas(macro)
    if alertas:
        with st.container():
            st.markdown("#### ⚡ Alertas Automáticas")
            for a in alertas:
                st.markdown(f'<div class="alert-card alert-{a["c"]}">{a["m"]}</div>', unsafe_allow_html=True)

    try:
        with open("reglas.json", "r", encoding="utf-8") as f:
            reglas = json.load(f)
    except:
        reglas = None
    if reglas:
        reglas_alerts = evaluar_reglas(macro, reglas)
        if reglas_alerts:
            st.markdown("#### 📋 Alertas de Reglas")
            for a in reglas_alerts:
                st.markdown(f'<div class="alert-card alert-{a["c"]}">{a["m"]}</div>', unsafe_allow_html=True)

    conclusion = generar_conclusion_estrategica(macro)
    st.markdown(f"**Régimen actual:** {conclusion['regimen']}")
    with st.expander("🟢 Oportunidades detectadas", expanded=True):
        for op in conclusion['oportunidades']:
            st.markdown(f"- {op}")
    with st.expander("🔴 Riesgos a vigilar", expanded=True):
        for ri in conclusion['riesgos']:
            st.markdown(f"- {ri}")
    st.markdown(f"**📌 Recomendación semanal:** {conclusion['recomendacion']}")

    st.markdown("### 📈 Evolución DXY vs VIX")
    try:
        raw_dxy = yf.download("DX-Y.NYB", period="3mo", progress=False)
        raw_vix = yf.download("^VIX", period="3mo", progress=False)
        if not raw_dxy.empty and not raw_vix.empty:
            s_dxy = raw_dxy['Close'].iloc[:, 0] if isinstance(raw_dxy['Close'], pd.DataFrame) else raw_dxy['Close']
            s_vix = raw_vix['Close'].iloc[:, 0] if isinstance(raw_vix['Close'], pd.DataFrame) else raw_vix['Close']
            s_dxy.index = s_dxy.index.tz_localize(None)
            s_vix.index = s_vix.index.tz_localize(None)
            df_merged = pd.concat([s_dxy, s_vix], axis=1, keys=['DXY', 'VIX']).dropna()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_merged.index, y=df_merged['DXY'], name="DXY", line=dict(color='#3b82f6', width=2)))
            fig.add_trace(go.Scatter(x=df_merged.index, y=df_merged['VIX'], name="VIX", line=dict(color='#ef4444', width=2), yaxis="y2"))
            fig.update_layout(
                yaxis=dict(title="DXY", gridcolor="#1f2937", tickfont=dict(color='#3b82f6')),
                yaxis2=dict(title="VIX", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", tickfont=dict(color='#ef4444')),
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"),
                height=350, margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                hovermode="x unified"
            )
            fig.update_xaxes(tickformat="%d %b", gridcolor="#1f2937")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo renderizar el gráfico: {e}")

    with st.expander("📊 Tabla de variaciones diarias", expanded=False):
        df_macro = pd.DataFrame({
            'Activo': ['DXY', 'VIX', 'S&P 500', 'Nasdaq', 'Oro', 'Bono 10Y'],
            'Precio': [macro['dxy']['price'], macro['vix']['price'],
                       macro['sp500']['price'], macro['nasdaq']['price'],
                       macro['oro']['price'], macro['bond10y']['price']],
            'Cambio %': [macro['dxy']['change_pct'], macro['vix']['change_pct'],
                         macro['sp500']['change_pct'], macro['nasdaq']['change_pct'],
                         macro['oro']['change_pct'], macro['bond10y']['change_pct']]
        })
        df_macro['Cambio %'] = df_macro['Cambio %'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(df_macro, use_container_width=True, hide_index=True)

else:
    st.info("ℹ️ No se pudieron obtener datos macro (DXY/VIX). Verifica tu conexión a internet.")

# ─────────────────────────────────────────────────────────────
#  TABS PRINCIPALES (6 TABS)
# ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Sentimiento & Tasas",
    "🔍 Indicadores",
    "🔗 Correlaciones",
    "📈 Análisis de Activos",
    "🤖 IA Estratega",
    "📊 Trading Quant"
])

# ============================================================
# TAB 1: SENTIMIENTO & TASAS
# ============================================================
with tabs[0]:
    st.markdown("### 🏦 Tipos de Interés de los Bancos Centrales")
    cols = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols[i]:
            sent = b.get("sentiment", {})
            bulls = list(sent.values()).count("BULLISH")
            bears = list(sent.values()).count("BEARISH")
            ov = "BULLISH" if bulls > bears else "BEARISH" if bears > bulls else "NEUTRO"
            color = BANK_COLORS.get(k, "#ffffff")
            selected_class = " selected" if st.session_state.selected == k else ""

            st.markdown(f"""
            <div class="bank-card{selected_class}" style="border-color: {color}30;">
                <div class="bank-card-top" style="background:{color};"></div>
                <div class="bank-code" style="color:{color};">{k}</div>
                <div class="bank-rate">{b.get('currentRate', 0):.2f}%</div>
                <div class="bank-last">Última: {b.get('lastMeeting', '')}</div>
                <div><span class="{SENT_CLASS.get(ov, 'sent-neut')}">{ov}</span></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Ver {k}", key=f"sel_{k}", use_container_width=True):
                st.session_state.selected = k
                st.rerun()

    st.markdown("---")
    st.markdown("### 📉 Evolución de Tipos de Interés (Histórico)")

    MESES_ESP = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}
    MESES_ESP.update({k.capitalize(): v for k, v in MESES_ESP.items()})

    def parse_fecha(fecha_str: str) -> datetime:
        try:
            return datetime.strptime(fecha_str, "%b-%y")
        except ValueError:
            pass
        partes = fecha_str.split('-')
        if len(partes) != 2:
            raise ValueError(f"Formato de fecha no reconocido: {fecha_str}")
        mes_str, año_str = partes[0], partes[1]
        mes_num = MESES_ESP.get(mes_str)
        if mes_num is None:
            raise ValueError(f"Mes no reconocido: {mes_str}")
        año = int(año_str)
        if año < 100:
            año += 2000
        return datetime(año, mes_num, 1)

    if data:
        fig_rates = go.Figure()
        for k, b in data.items():
            rates = b.get("rates", [])
            if rates:
                rates_sorted = sorted(rates, key=lambda x: parse_fecha(x["date"]))
                fechas = [parse_fecha(r["date"]) for r in rates_sorted]
                valores = [r["r"] for r in rates_sorted]
                fig_rates.add_trace(go.Scatter(x=fechas, y=valores, name=k, line=dict(color=BANK_COLORS.get(k, "#ffffff"), width=2), mode='lines+markers'))
        fig_rates.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=300, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02), xaxis=dict(tickformat="%b-%y", gridcolor="#1f2937"), yaxis=dict(ticksuffix="%", gridcolor="#1f2937"))
        st.plotly_chart(fig_rates, use_container_width=True)

# ============================================================
# TAB 2: INDICADORES
# ============================================================
with tabs[1]:
    sel = st.session_state.selected
    st.markdown(f"### 🔍 Indicadores Actuales — {sel}")
    inds = data.get(sel, {}).get("indicators", [])
    if inds:
        header = '<div class="ind-row ind-header"><span>CATEGORÍA</span><span>INDICADOR</span><span style="text-align:right">ACTUAL</span><span style="text-align:right">PREVIO</span><span style="text-align:right">DESVIACIÓN</span></div>'
        st.markdown(header, unsafe_allow_html=True)
        for i, ind in enumerate(inds):
            bg = "transparent" if i % 2 == 0 else "#070b14"
            row = f'<div class="ind-row" style="background:{bg};">'
            row += f'<span style="font-size:10px;font-weight:600;color:#9ca3af">{ind.get("cat","")}</span>'
            row += f'<span style="font-size:12px;color:#d1d5db">{ind.get("name","")}</span>'
            row += f'<span style="text-align:right;font-size:13px;font-weight:600;color:#f9fafb">{ind.get("actual","—")}</span>'
            row += f'<span style="text-align:right;font-size:12px;color:#6b7280">{ind.get("prev","—")}</span>'
            dev = ind.get("dev", "—")
            color_dev = "#10b981" if str(dev).startswith("+") else "#ef4444" if str(dev).startswith("-") else "#fbbf24"
            row += f'<span style="text-align:right;font-size:12px;font-weight:700;color:{color_dev}">{dev}</span>'
            row += '</div>'
            st.markdown(row, unsafe_allow_html=True)
    else:
        st.info("No hay indicadores disponibles para este banco central.")

# ============================================================
# TAB 3: CORRELACIONES
# ============================================================
with tabs[2]:
    st.markdown("### 🔗 Matriz de Correlación Macroeconómica (1 Año)")
    st.caption("Muestra cómo se mueven los activos entre sí. 1.0 = movimiento idéntico, -1.0 = inverso.")
    corr_matrix = get_correlation_matrix()
    if corr_matrix is not None:
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig_corr.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=600)
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("No se pudieron obtener datos de correlación. Intente más tarde.")

# ============================================================
# TAB 4: ANÁLISIS DE ACTIVOS
# ============================================================
with tabs[3]:
    st.markdown("### 📈 Análisis Técnico Multi-Plazo")
    st.caption("Selecciona un activo para ver su gráfico con medias móviles.")

    ticker_analisis = st.text_input(
        "Símbolo del Activo (ej. AAPL, BTC-USD, SPY, NVDA):",
        value=st.session_state.get("ticker_analisis", "SPY")
    )

    st.markdown("---")
    st.markdown("**Sugerencias rápidas:**")
    render_sugerencias("ticker_analisis", SUG_DIVISAS, cols=4, label="Divisas", list_name="an_divisas")
    render_sugerencias("ticker_analisis", SUG_COMMODITIES, cols=4, label="Commodities", list_name="an_commo")
    render_sugerencias("ticker_analisis", SUG_INDICES, cols=4, label="Índices", list_name="an_indices")
    render_sugerencias("ticker_analisis", SUG_CRIPTO + SUG_OTROS, cols=4, label="Cripto / Otros", list_name="an_otros")
    st.markdown("---")

    if ticker_analisis:
        with st.spinner(f"Obteniendo datos de {ticker_analisis}..."):
            try:
                df_asset = yf.download(ticker_analisis, period="2y", progress=False)
                if not df_asset.empty:
                    df_asset['SMA_20'] = df_asset['Close'].rolling(window=20).mean()
                    df_asset['SMA_50'] = df_asset['Close'].rolling(window=50).mean()
                    df_asset['SMA_200'] = df_asset['Close'].rolling(window=200).mean()

                    fig_asset = go.Figure()
                    fig_asset.add_trace(go.Candlestick(
                        x=df_asset.index,
                        open=df_asset['Open'].squeeze(),
                        high=df_asset['High'].squeeze(),
                        low=df_asset['Low'].squeeze(),
                        close=df_asset['Close'].squeeze(),
                        name='Precio'
                    ))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_20'].squeeze(), line=dict(color='#3b82f6', width=1.5), name='Corto (20d)'))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_50'].squeeze(), line=dict(color='#f59e0b', width=1.5), name='Medio (50d)'))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_200'].squeeze(), line=dict(color='#ef4444', width=2), name='Largo (200d)'))

                    fig_asset.update_layout(
                        title=f"Acción del Precio y Tendencias - {ticker_analisis}",
                        yaxis_title="Precio USD",
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="#0d1117",
                        plot_bgcolor="#0d1117",
                        font=dict(color="#e2e8f0"),
                        height=500,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_asset, use_container_width=True)

                    st.markdown("""
                    **Guía de Interpretación:**
                    - **Corto Plazo (20d):** Precio por encima → impulso alcista inmediato.
                    - **Medio Plazo (50d):** Cruce de 20d por encima de 50d → señal de compra.
                    - **Largo Plazo (200d):** Precio por debajo → mercado bajista; operar con precaución.
                    """)
                else:
                    st.error("No se encontraron datos para ese símbolo. Verifique el ticker.")
            except Exception as e:
                st.error(f"Error al cargar el gráfico: {e}")

# ============================================================
# TAB 5: IA ESTRATEGA
# ============================================================
with tabs[4]:
    st.markdown("### 🤖 Memoria y Pensamiento del Agente IA")

    if memoria_ia:
        ultima = memoria_ia[-1]
        st.success(f"**Última actualización:** {ultima.get('fecha', 'Fecha desconocida')}")
        st.markdown(f"""
        <div class="ia-panel">
            <pre>{ultima.get('decision', 'Sin decisión disponible.')}</pre>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📚 Ver historial completo de la IA"):
            for m in reversed(memoria_ia[:-1]):
                st.markdown(f"**{m.get('fecha', '')}**")
                st.write(m.get('decision', ''))
                st.markdown("---")
    else:
        st.info("La IA aún no ha generado decisiones. Presiona el botón 'EJECUTAR IA' en la cabecera para generar la primera señal.")

    st.markdown("---")
    st.markdown("### 📋 Prompt para IA Externa (ChatGPT / Ollama)")
    if macro:
        anomalias = []
        try:
            tickers_extra = {'SP500': '^GSPC', 'NASDAQ': '^IXIC', 'ORO': 'GC=F', 'COBRE': 'HG=F', 'US10Y': '^TNX', 'WTI': 'CL=F', 'Brent': 'BZ=F', 'DAX': '^GDAXI', 'Nikkei': '^N225'}
            extra_data = yf.download(list(tickers_extra.values()), period="40d", progress=False)
            if not extra_data.empty:
                for name, symbol in tickers_extra.items():
                    try:
                        close_s = extra_data['Close'][symbol].dropna()
                        vol_s = extra_data['Volume'][symbol].dropna() if 'Volume' in extra_data else None
                        low_s = extra_data['Low'][symbol].dropna() if 'Low' in extra_data else None
                        high_s = extra_data['High'][symbol].dropna() if 'High' in extra_data else None
                        if len(close_s) < 2:
                            continue
                        c_act = float(close_s.iloc[-1])
                        vol_ratio = (float(vol_s.iloc[-1]) / float(vol_s.rolling(20).mean().iloc[-1])) if (vol_s is not None and len(vol_s)>=20 and float(vol_s.rolling(20).mean().iloc[-1]) > 0) else 1
                        min_20d = float(low_s.rolling(20).min().iloc[-2]) if low_s is not None and len(low_s)>=20 else c_act
                        max_20d = float(high_s.rolling(20).max().iloc[-2]) if high_s is not None and len(high_s)>=20 else c_act
                        low_act = float(low_s.iloc[-1]) if low_s is not None else c_act
                        high_act = float(high_s.iloc[-1]) if high_s is not None else c_act

                        if vol_ratio > 1.8:
                            anomalias.append(f"- {name}: Pico de Volumen extremo")
                        if low_act < min_20d and c_act > min_20d:
                            anomalias.append(f"- {name}: Sweep Alcista")
                        if high_act > max_20d and c_act < max_20d:
                            anomalias.append(f"- {name}: Sweep Bajista")
                    except Exception:
                        pass
        except Exception:
            pass

        anom_str = "\n".join(anomalias) if anomalias else "- Estructura de precio limpia."

        prompt_ia = f"""Eres un Analista Cuantitativo de un Hedge Fund. Lee los datos en tiempo real y dame un plan de ejecución estricto:

[DATOS MACRO]
- DXY: {macro.get('dxy', {}).get('price', 0):.2f} (Cambio: {macro.get('dxy', {}).get('change_pct', 0):.2f}%)
- VIX: {macro.get('vix', {}).get('price', 0):.2f} (Cambio: {macro.get('vix', {}).get('change_pct', 0):.2f}%)
- US10Y: {macro.get('bond10y', {}).get('price', 0):.2f}%
- SP500: {macro.get('sp500', {}).get('price', 0):.2f} | Nasdaq: {macro.get('nasdaq', {}).get('price', 0):.2f}

[ANOMALÍAS SMART MONEY]
{anom_str}

[TAREA]
1. RÉGIMEN: Define el régimen (Risk-On, Risk-Off).
2. ASIMETRÍA: Identifica 2 operaciones de alta probabilidad.
3. KILL-SWITCH: Qué activo NO debo operar hoy."""
        st.code(prompt_ia, language="markdown")
    else:
        st.warning("No hay datos de mercado para generar el prompt.")

# ============================================================
# TAB 6: TRADING QUANT (Módulos corregidos)
# ============================================================
with tabs[5]:
    st.markdown("### 📊 Módulo Cuantitativo - Trading Institucional")

    quant_tab = st.radio(
        "Selecciona módulo:",
        ["Flujo de Órdenes", "Correlaciones en Tiempo Real", "Sentimiento de Mercado", "Alertas Push (Telegram)", "Dashboard de Riesgo", "Escáner de Oportunidades"],
        horizontal=True
    )

    # ── FLUJO DE ÓRDENES ──
    if quant_tab == "Flujo de Órdenes":
        st.markdown("#### 📊 Flujo de Órdenes (Approximado)")
        st.caption("Indicadores de flujo de dinero basados en precio y volumen (OBV, VWAP).")

        ticker_of = st.text_input(
            "Activo:",
            value=st.session_state.get("ticker_of", "SPY")
        )

        st.markdown("**Sugerencias:**")
        render_sugerencias("ticker_of", SUG_DIVISAS + SUG_COMMODITIES + SUG_INDICES + SUG_CRIPTO + SUG_OTROS, cols=4, label="Sugerencias", list_name="of")

        if st.button("Calcular flujo", key="calc_of"):
            with st.spinner(f"Descargando datos de {ticker_of}..."):
                try:
                    cache_key = f"of_{ticker_of}"
                    if cache_key in st.session_state:
                        df_of = st.session_state[cache_key]
                    else:
                        df_of = yf.download(ticker_of, period="1mo", progress=False, timeout=15)
                        if df_of.empty:
                            st.error(f"No se encontraron datos para {ticker_of}. Verifica el símbolo.")
                            st.stop()
                        st.session_state[cache_key] = df_of

                    df_of['OBV'] = (df_of['Volume'] * ((df_of['Close'] > df_of['Close'].shift(1)).astype(int) - (df_of['Close'] < df_of['Close'].shift(1)).astype(int))).cumsum()
                    df_of['VWAP'] = (df_of['Volume'] * (df_of['High'] + df_of['Low'] + df_of['Close']) / 3).cumsum() / df_of['Volume'].cumsum()

                    fig_of = go.Figure()
                    fig_of.add_trace(go.Scatter(x=df_of.index, y=df_of['Close'], name="Precio", line=dict(color='#3b82f6')))
                    fig_of.add_trace(go.Scatter(x=df_of.index, y=df_of['VWAP'], name="VWAP", line=dict(color='#f59e0b', dash='dot')))
                    fig_of.add_trace(go.Bar(x=df_of.index, y=df_of['OBV'], name="OBV", yaxis="y2", marker_color='#8b5cf6'))
                    fig_of.update_layout(
                        title=f"Flujo de Órdenes - {ticker_of}",
                        yaxis=dict(title="Precio", gridcolor="#1f2937"),
                        yaxis2=dict(title="OBV", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
                        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=400
                    )
                    st.plotly_chart(fig_of, use_container_width=True)

                    st.info("💡 **Interpretación:** OBV subiendo con precio = acumulación (compradores fuertes). VWAP por encima del precio = presión vendedora.")
                except Exception as e:
                    st.error(f"Error al obtener datos: {e}. Intenta con otro símbolo.")

    # ── CORRELACIONES ──
    elif quant_tab == "Correlaciones en Tiempo Real":
        st.markdown("#### 🔗 Correlaciones en Tiempo Real (Rolling 20 días)")
        st.caption("Evolución de la correlación entre dos activos.")

        col_a, col_b = st.columns(2)
        with col_a:
            ticker_a = st.text_input(
                "Activo A:",
                value=st.session_state.get("ticker_corr_a", "GLD")
            )
            st.markdown("**Sugerencias A:**")
            render_sugerencias("ticker_corr_a", SUG_DIVISAS + SUG_COMMODITIES + SUG_INDICES + SUG_CRIPTO + SUG_OTROS, cols=3, label="Sugerencias A", list_name="corr_a")
        with col_b:
            ticker_b = st.text_input(
                "Activo B:",
                value=st.session_state.get("ticker_corr_b", "DXY")
            )
            st.markdown("**Sugerencias B:**")
            render_sugerencias("ticker_corr_b", SUG_DIVISAS + SUG_COMMODITIES + SUG_INDICES + SUG_CRIPTO + SUG_OTROS, cols=3, label="Sugerencias B", list_name="corr_b")

        if st.button("Calcular correlación dinámica"):
            with st.spinner("Descargando datos..."):
                try:
                    cache_key_a = f"corr_{ticker_a}"
                    cache_key_b = f"corr_{ticker_b}"
                    if cache_key_a in st.session_state:
                        df_a = st.session_state[cache_key_a]
                    else:
                        df_a = yf.download(ticker_a, period="3mo", progress=False, timeout=15)
                        if df_a.empty:
                            st.error(f"No se encontraron datos para {ticker_a}. Verifica el símbolo.")
                            st.stop()
                        st.session_state[cache_key_a] = df_a

                    if cache_key_b in st.session_state:
                        df_b = st.session_state[cache_key_b]
                    else:
                        df_b = yf.download(ticker_b, period="3mo", progress=False, timeout=15)
                        if df_b.empty:
                            st.error(f"No se encontraron datos para {ticker_b}. Verifica el símbolo.")
                            st.stop()
                        st.session_state[cache_key_b] = df_b

                    merged = pd.DataFrame(index=df_a.index)
                    merged[ticker_a] = df_a['Close']
                    merged[ticker_b] = df_b['Close']
                    merged = merged.dropna()
                    if len(merged) < 20:
                        st.warning("No hay suficientes datos superpuestos para calcular correlación (mínimo 20 días).")
                    else:
                        merged['Corr'] = merged[ticker_a].rolling(20).corr(merged[ticker_b]).fillna(0)

                        fig_corr = go.Figure()
                        fig_corr.add_trace(go.Scatter(x=merged.index, y=merged['Corr'], name="Correlación 20d", line=dict(color='#22c55e')))
                        fig_corr.add_hline(y=0, line_dash="dash", line_color="#ef4444")
                        fig_corr.add_hline(y=1, line_dash="dash", line_color="#4ade80")
                        fig_corr.add_hline(y=-1, line_dash="dash", line_color="#4ade80")
                        fig_corr.update_layout(
                            title=f"Correlación {ticker_a} vs {ticker_b} (20 días)",
                            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=350
                        )
                        st.plotly_chart(fig_corr, use_container_width=True)

                        corr_actual = merged['Corr'].iloc[-1]
                        if abs(corr_actual) > 0.7:
                            st.success(f"✅ Correlación fuerte ({corr_actual:.2f}). Los activos se mueven juntos.")
                        elif abs(corr_actual) > 0.3:
                            st.warning(f"⚠️ Correlación moderada ({corr_actual:.2f}).")
                        else:
                            st.info(f"ℹ️ Correlación débil ({corr_actual:.2f}). No hay relación clara.")
                except Exception as e:
                    st.error(f"Error: {e}. Intenta con otros símbolos.")

    # ── SENTIMIENTO ──
    elif quant_tab == "Sentimiento de Mercado":
        st.markdown("#### 🧠 Sentimiento de Mercado Agregado")
        st.caption("Índice de sentimiento basado en VIX, DXY y Oro.")

        with st.spinner("Calculando sentimiento..."):
            macro = get_macro_data()
            if macro:
                vix = macro.get('vix', {}).get('price', 0)
                dxy_change = macro.get('dxy', {}).get('change_pct', 0)
                oro_change = macro.get('oro', {}).get('change_pct', 0)

                sentimiento_score = 50
                if vix > 25:
                    sentimiento_score -= 20
                elif vix < 15:
                    sentimiento_score += 15
                if dxy_change > 0 and oro_change < 0:
                    sentimiento_score -= 10
                elif dxy_change < 0 and oro_change > 0:
                    sentimiento_score += 10

                sentimiento_score = max(0, min(100, sentimiento_score))
                if sentimiento_score >= 70:
                    sentimiento = "🟢 Apetito por Riesgo (Optimista)"
                    color = "#22c55e"
                elif sentimiento_score <= 30:
                    sentimiento = "🔴 Aversión al Riesgo (Pesimista)"
                    color = "#ef4444"
                else:
                    sentimiento = "🟡 Neutral (Precaución)"
                    color = "#f59e0b"

                st.markdown(f"**Índice de Sentimiento:** {sentimiento_score}/100")
                st.markdown(f"**Estado:** <span style='color:{color}; font-weight:bold;'>{sentimiento}</span>", unsafe_allow_html=True)

                fig_sent = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sentimiento_score,
                    title={'text': "Sentimiento de Mercado"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color},
                           'steps': [
                               {'range': [0, 30], 'color': 'rgba(239,68,68,0.2)'},
                               {'range': [30, 70], 'color': 'rgba(245,158,11,0.2)'},
                               {'range': [70, 100], 'color': 'rgba(34,197,94,0.2)'}
                           ]}
                ))
                fig_sent.update_layout(paper_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=250)
                st.plotly_chart(fig_sent, use_container_width=True)

                st.caption("💡 **Interpretación:** >70 = apetito por riesgo (bullish), <30 = aversión (bearish).")
            else:
                st.warning("No hay datos macro disponibles.")

    # ── ALERTAS ──
    elif quant_tab == "Alertas Push (Telegram)":
        st.markdown("#### 📨 Configuración de Alertas por Telegram")
        st.caption("Recibe notificaciones automáticas cuando se activen condiciones de mercado.")

        st.warning("⚠️ Necesitas un bot de Telegram. Crea uno con @BotFather y obtén el token.")

        with st.form("telegram_form"):
            token = st.text_input("Token del Bot de Telegram:", placeholder="123456:ABC-DEF...")
            chat_id = st.text_input("Chat ID (puedes usar @getmyid_bot):")
            enviar_prueba = st.form_submit_button("📤 Enviar mensaje de prueba")

        if enviar_prueba and token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": "✅ MacroVision: Alerta de prueba activada. El sistema funciona."}
            try:
                r = requests.post(url, json=payload, timeout=10)
                if r.status_code == 200:
                    st.success("✅ Mensaje enviado correctamente a Telegram.")
                else:
                    st.error(f"Error: {r.json()}")
            except Exception as e:
                st.error(f"Error al enviar: {e}")

        if st.button("🔔 Probar alerta de VIX > 25"):
            macro = get_macro_data()
            vix_price = macro.get('vix', {}).get('price', 0) if macro else 0
            if vix_price > 25:
                st.warning(f"🔴 VIX = {vix_price:.1f} (>25). ¡Alerta de riesgo activada!")
                if token and chat_id:
                    try:
                        msg = f"⚠️ ALERTA MACRO: VIX ha superado 25 ({vix_price:.1f}). Régimen de aversión al riesgo."
                        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg})
                        st.success("Alerta enviada a Telegram.")
                    except:
                        st.error("Error al enviar Telegram. Verifica token y chat ID.")
            else:
                st.info(f"VIX = {vix_price:.1f}. No se supera el umbral.")

    # ── RIESGO (CORREGIDO) ──
    elif quant_tab == "Dashboard de Riesgo":
        st.markdown("#### 🛡️ Dashboard de Riesgo (VaR, ES, Drawdown)")
        st.caption("Métricas de riesgo para un activo o cartera.")

        riesgo_activo = st.text_input("Activo para análisis de riesgo:", value="SPY")

        if st.button("Calcular riesgo"):
            with st.spinner(f"Calculando métricas de riesgo para {riesgo_activo}..."):
                try:
                    df_risk = yf.download(riesgo_activo, period="1y", progress=False)

                    if df_risk.empty:
                        st.error(f"No se encontraron datos para {riesgo_activo}. Verifica el símbolo.")
                    else:
                        returns = df_risk['Close'].pct_change().dropna()

                        if len(returns) < 2:
                            st.warning("No hay suficientes datos para calcular métricas de riesgo.")
                        else:
                            # Extraer todos los valores como floats nativos
                            var_95 = float(returns.quantile(0.05) * 100) if not pd.isna(returns.quantile(0.05)) else 0.0
                            var_quantile = returns.quantile(0.05)
                            es_filter = returns[returns <= var_quantile]
                            es_95 = float(es_filter.mean() * 100) if not es_filter.empty and not pd.isna(es_filter.mean()) else 0.0
                            cum_ret = (1 + returns).cumprod()
                            drawdown = (cum_ret / cum_ret.cummax() - 1) * 100
                            max_drawdown = float(drawdown.min()) if not drawdown.empty and not pd.isna(drawdown.min()) else 0.0
                            vol = float(returns.std() * (252 ** 0.5) * 100) if returns.std() != 0 else 0.0
                            sharpe = float((returns.mean() / returns.std()) * (252 ** 0.5)) if returns.std() != 0 and not pd.isna(returns.std()) else 0.0

                            c1, c2, c3, c4, c5 = st.columns(5)
                            c1.metric("VaR 95% (1d)", f"{var_95:.2f}%")
                            c2.metric("ES 95% (1d)", f"{es_95:.2f}%")
                            c3.metric("Max Drawdown", f"{max_drawdown:.2f}%")
                            c4.metric("Volatilidad (anual)", f"{vol:.2f}%")
                            c5.metric("Sharpe Ratio", f"{sharpe:.2f}")

                            fig_dd = go.Figure()
                            fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill='tozeroy', line=dict(color='#ef4444')))
                            fig_dd.update_layout(
                                title="Drawdown Histórico",
                                paper_bgcolor="#0d1117",
                                plot_bgcolor="#0d1117",
                                font=dict(color="#e2e8f0"),
                                height=250,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig_dd, use_container_width=True)

                            st.caption("💡 **Interpretación:** VaR = pérdida esperada en el peor 5% de los días. ES = promedio de pérdidas en esos días. Max Drawdown = mayor caída desde un pico histórico.")
                except Exception as e:
                    st.error(f"Error al calcular riesgos: {e}")

    # ── ESCÁNER (CORREGIDO) ──
    elif quant_tab == "Escáner de Oportunidades":
        st.markdown("#### 🔍 Escáner en Tiempo Real")
        st.caption("Detecta automáticamente activos que cumplen condiciones. (Máximo 5 activos por escaneo)")

        activos_scan = {
            "S&P 500 (SPY)": "SPY",
            "Nasdaq (QQQ)": "QQQ",
            "Oro (GLD)": "GLD",
            "Dólar (UUP)": "UUP",
            "VIX (VXX)": "VXX",
            "Crudo WTI (USO)": "USO",
            "Bitcoin (IBIT)": "IBIT"
        }

        seleccionados = st.multiselect(
            "Selecciona activos para escanear (máx. 5):",
            options=list(activos_scan.keys()),
            default=list(activos_scan.keys())[:4]
        )

        if st.button("🔎 Escanear ahora") and seleccionados:
            with st.spinner(f"Escaneando {len(seleccionados)} activos..."):
                oportunidades = []
                errores = []
                for nombre in seleccionados:
                    sym = activos_scan[nombre]
                    try:
                        df_scan = yf.download(sym, period="2mo", progress=False, timeout=15)
                        if df_scan.empty or len(df_scan) < 20:
                            errores.append(f"{nombre}: Datos insuficientes")
                            continue

                        # Extraer valores con .iloc[fila, columna] para garantizar escalar
                        close_prices = df_scan['Close'].dropna()
                        if len(close_prices) < 2:
                            errores.append(f"{nombre}: Datos insuficientes")
                            continue
                        precio = float(close_prices.iloc[-1])
                        precio_anterior = float(close_prices.iloc[-2])

                        sma_50_series = df_scan['Close'].rolling(50).mean()
                        sma_200_series = df_scan['Close'].rolling(200).mean()
                        sma_50 = float(sma_50_series.iloc[-1]) if len(df_scan) >= 50 and not pd.isna(sma_50_series.iloc[-1]) else precio
                        sma_200 = float(sma_200_series.iloc[-1]) if len(df_scan) >= 200 and not pd.isna(sma_200_series.iloc[-1]) else precio

                        cambios = df_scan['Close'].pct_change().dropna()
                        if len(cambios) >= 14:
                            ganancias = cambios[cambios > 0].sum()
                            perdidas = -cambios[cambios < 0].sum()
                            rsi = 100 - (100 / (1 + ganancias / perdidas)) if perdidas != 0 else 100
                        else:
                            rsi = 50

                        cambio = ((precio / precio_anterior) - 1) * 100 if precio_anterior != 0 else 0

                        if any(pd.isna([precio, sma_50, sma_200, rsi, cambio])):
                            errores.append(f"{nombre}: Datos incompletos (NaN)")
                            continue

                        if precio > sma_50 and sma_50 > sma_200:
                            oportunidades.append(("🟢", f"**{nombre}** | Tendencia alcista | RSI: {rsi:.0f} | Cambio: {cambio:+.2f}%"))
                        elif precio < sma_50 and sma_50 < sma_200:
                            oportunidades.append(("🔴", f"**{nombre}** | Tendencia bajista | RSI: {rsi:.0f} | Cambio: {cambio:+.2f}%"))
                        elif rsi < 30 and precio > sma_200:
                            oportunidades.append(("🟡", f"**{nombre}** | Sobreventa (RSI<30) pero sobre SMA200 → posible rebote"))
                        elif rsi > 70 and precio < sma_200:
                            oportunidades.append(("🟡", f"**{nombre}** | Sobrecompra (RSI>70) bajo SMA200 → posible caída"))
                        else:
                            oportunidades.append(("⚪", f"**{nombre}** | Sin señal clara | RSI: {rsi:.0f} | Cambio: {cambio:+.2f}%"))
                    except Exception as e:
                        errores.append(f"{nombre}: {str(e)[:60]}")

                if oportunidades:
                    st.markdown("#### 📊 Resultados del escáner:")
                    for color, msg in oportunidades:
                        st.markdown(f"{color} {msg}")
                else:
                    st.info("No se detectaron oportunidades claras en este momento.")

                if errores:
                    with st.expander("⚠️ Errores al obtener datos de algunos activos"):
                        for e in errores:
                            st.warning(e)

# ── FOOTER ──────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:11px; margin-top:30px; border-top:1px solid #1f2937; padding-top:15px;">
    MacroVision · Datos en tiempo real vía Yahoo Finance · IA Local con Ollama
</div>
""", unsafe_allow_html=True)