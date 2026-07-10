# ─────────────────────────────────────────────────────────
#  MacroVision · app.py (VERSIÓN INTEGRAL PROFESIONAL)
#  Dashboard Macroeconómico con IA, Correlaciones,
#  Análisis Técnico y Memoria del Agente.
# ─────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────
st.set_page_config(
    page_title="MacroVision Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh cada 4 horas (14400 segundos)
st.markdown('<meta http-equiv="refresh" content="14400">', unsafe_allow_html=True)

# ── CSS PROFESIONAL (Fusión de estilos) ──────────────────
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

    /* HEADER */
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

    /* TARJETAS DE BANCOS */
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

    /* ETIQUETAS DE SENTIMIENTO */
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

    /* TABLA DE INDICADORES */
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

    /* BOTONES */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }

    /* MÉTRICAS */
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

    /* OCULTAR ELEMENTOS POR DEFECTO */
    header { visibility: hidden; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }

    /* PANEL DE IA */
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

    /* ALERTAS */
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
</style>
""", unsafe_allow_html=True)

# ── CONFIGURACIONES GLOBALES ─────────────────────────────
BANK_COLORS = {
    "FED": "#3b82f6",
    "BCE": "#8b5cf6",
    "BOE": "#ec4899",
    "BOC": "#f97316",
    "RBA": "#10b981",
    "RBNZ": "#06b6d4"
}
CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]
CAT_ICONS = {
    "INFLACIÓN": "📊",
    "CRECIMIENTO": "📈",
    "EMPLEO": "👷",
    "CONSUMO": "🛒",
    "ACTIVIDAD": "🏭",
    "INMOBILIARIO": "🏠"
}
SENT_CLASS = {
    "BULLISH": "sent-bull",
    "BEARISH": "sent-bear",
    "NEUTRO": "sent-neut"
}

# ── FUNCIONES DE DATOS (CACHE) ────────────────────────────
@st.cache_data(ttl=14400)
def get_macro_data():
    """Obtiene precios y cambios de los principales activos macro."""
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
            close_series = data['Close'][symbol].dropna()
            if len(close_series) < 2:
                continue
            curr = float(close_series.iloc[-1])
            prev = float(close_series.iloc[-2])
            result[key] = {
                'price': curr,
                'change_pct': ((curr / prev) - 1) * 100
            }
        return result if 'dxy' in result and 'vix' in result else None
    except Exception:
        return None

@st.cache_data(ttl=86400)
def get_correlation_matrix():
    """Calcula la matriz de correlación de activos macro (1 año)."""
    try:
        tickers = {
            'DXY': 'DX-Y.NYB',
            'VIX': '^VIX',
            'S&P 500': '^GSPC',
            'Nasdaq': '^IXIC',
            'Oro': 'GC=F',
            'Bono 10Y': '^TNX'
        }
        df = yf.download(list(tickers.values()), period="1y", progress=False)
        if df.empty:
            return None
        close_df = df['Close']
        rename_dict = {v: k for k, v in tickers.items()}
        close_df = close_df.rename(columns=rename_dict)
        returns = close_df.pct_change().dropna()
        return returns.corr()
    except Exception:
        return None

@st.cache_data(ttl=14400)
def load_macro_data():
    """Carga macro_data.json con los datos de bancos centrales."""
    if os.path.exists("macro_data.json"):
        with open("macro_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=14400)
def load_ai_memory():
    """Carga el historial de decisiones de la IA desde ai_memory.json."""
    if os.path.exists("ai_memory.json"):
        with open("ai_memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def generar_alertas(macro_data):
    """Genera alertas automáticas basadas en condiciones macro."""
    if not macro_data:
        return []
    alertas = []
    dxy = macro_data.get('dxy', {})
    vix = macro_data.get('vix', {})
    oro = macro_data.get('oro', {})
    nasdaq = macro_data.get('nasdaq', {})
    bond = macro_data.get('bond10y', {})

    if dxy.get('change_pct', 0) > 0 and vix.get('change_pct', 0) > 0:
        alertas.append({"m": "🔴 DXY y VIX al alza → Riesgo-off extremo.", "c": "rojo"})
    if dxy.get('change_pct', 0) < 0 and vix.get('change_pct', 0) < 0:
        alertas.append({"m": "🟢 DXY y VIX a la baja → Apetito por riesgo.", "c": "verde"})
    if nasdaq.get('change_pct', 0) > 0 and vix.get('change_pct', 0) > 0:
        alertas.append({"m": "⚠️ Nasdaq y VIX suben juntos → Divergencia peligrosa.", "c": "rojo"})
    if bond.get('change_pct', 0) > 0 and dxy.get('change_pct', 0) > 0:
        alertas.append({"m": "📈 Tasas y dólar fuertes → Presión sobre tecnológicas.", "c": "naranja"})
    return alertas

# ── INICIALIZACIÓN DE ESTADO ──────────────────────────────
if "selected" not in st.session_state:
    st.session_state.selected = "FED"

macro = get_macro_data()
data = load_macro_data()
memoria_ia = load_ai_memory()

# ─────────────────────────────────────────────────────────────
#  HEADER PROFESIONAL
# ─────────────────────────────────────────────────────────────
col_title, col_btn = st.columns([3, 1])
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

with col_btn:
    st.write("")
    if st.button("⟳ ACTUALIZAR AHORA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── MÉTRICAS RÁPIDAS ──────────────────────────────────────
if macro:
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Dólar (DXY)",
        f"{macro['dxy']['price']:.2f}",
        f"{macro['dxy']['change_pct']:.2f}%",
        delta_color="inverse"
    )
    c2.metric(
        "Miedo (VIX)",
        f"{macro['vix']['price']:.2f}",
        f"{macro['vix']['change_pct']:.2f}%",
        delta_color="inverse"
    )
    c3.metric(
        "Bono US 10Y",
        f"{macro['bond10y']['price']:.2f}%",
        f"{macro['bond10y']['change_pct']:.2f}%"
    )

# ── PANEL DE ALERTAS ──────────────────────────────────────
alertas = generar_alertas(macro)
if alertas:
    with st.container():
        st.markdown("#### ⚡ Alertas Automáticas")
        for a in alertas:
            clase = f"alert-{a['c']}"
            st.markdown(f'<div class="alert-card {clase}">{a["m"]}</div>', unsafe_allow_html=True)

# ── TABS PRINCIPALES ──────────────────────────────────────
tabs = st.tabs([
    "📊 Sentimiento & Tasas",
    "🔍 Indicadores",
    "🔗 Correlaciones",
    "📈 Análisis de Activos",
    "🤖 IA Estratega"
])

# ============================================================
# TAB 1: SENTIMIENTO & TASAS
# ============================================================
with tabs[0]:
    # Tarjetas de bancos centrales
    st.markdown("### 🏦 Tipos de Interés de los Bancos Centrales")
    cols = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols[i]:
            ov = "BULLISH" if list(b.get("sentiment", {}).values()).count("BULLISH") > 2 else "NEUTRO"
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

    # Gráfico DXY vs VIX (últimos 3 meses)
    st.markdown("### 📈 Evolución DXY vs VIX")
    if macro:
        try:
            raw_dxy = yf.download("DX-Y.NYB", period="3mo", progress=False)
            raw_vix = yf.download("^VIX", period="3mo", progress=False)
            if not raw_dxy.empty and not raw_vix.empty:
                # Asegurar que sean Series (no DataFrames)
                if isinstance(raw_dxy['Close'], pd.DataFrame):
                    s_dxy = raw_dxy['Close'].iloc[:, 0]
                else:
                    s_dxy = raw_dxy['Close']
                if isinstance(raw_vix['Close'], pd.DataFrame):
                    s_vix = raw_vix['Close'].iloc[:, 0]
                else:
                    s_vix = raw_vix['Close']

                s_dxy.index = s_dxy.index.tz_localize(None)
                s_vix.index = s_vix.index.tz_localize(None)
                df_merged = pd.concat([s_dxy, s_vix], axis=1, keys=['DXY', 'VIX']).dropna()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_merged.index,
                    y=df_merged['DXY'],
                    name="DXY",
                    line=dict(color='#3b82f6', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df_merged.index,
                    y=df_merged['VIX'],
                    name="VIX",
                    line=dict(color='#ef4444', width=2),
                    yaxis="y2"
                ))
                fig.update_layout(
                    yaxis=dict(title="DXY", gridcolor="#1f2937", tickfont=dict(color='#3b82f6')),
                    yaxis2=dict(
                        title="VIX",
                        overlaying="y",
                        side="right",
                        gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color='#ef4444')
                    ),
                    paper_bgcolor="#0d1117",
                    plot_bgcolor="#0d1117",
                    font=dict(color="#e2e8f0"),
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    hovermode="x unified"
                )
                fig.update_xaxes(tickformat="%d %b", gridcolor="#1f2937")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo renderizar el gráfico: {e}")

    st.markdown("---")

    # Gráfico de evolución de tasas históricas
    st.markdown("### 📉 Evolución de Tipos de Interés (Histórico)")
    if data:
        fig_rates = go.Figure()
        for k, b in data.items():
            rates = b.get("rates", [])
            if rates:
                # Ordenar por fecha
                rates_sorted = sorted(rates, key=lambda x: x["date"])
                fig_rates.add_trace(go.Scatter(
                    x=[r["date"] for r in rates_sorted],
                    y=[r["r"] for r in rates_sorted],
                    name=k,
                    line=dict(color=BANK_COLORS.get(k, "#ffffff"), width=2)
                ))
        fig_rates.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font=dict(color="#e2e8f0"),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig_rates.update_xaxes(gridcolor="#1f2937")
        fig_rates.update_yaxes(gridcolor="#1f2937", ticksuffix="%")
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
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )
        fig_corr.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font=dict(color="#e2e8f0"),
            height=500
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("No se pudieron obtener datos de correlación. Intente más tarde.")

# ============================================================
# TAB 4: ANÁLISIS DE ACTIVOS
# ============================================================
with tabs[3]:
    st.markdown("### 📈 Análisis Técnico Multi-Plazo")
    col_input, _ = st.columns([1, 2])
    with col_input:
        ticker_input = st.text_input("Símbolo del Activo (ej. AAPL, BTC-USD, SPY, NVDA):", value="SPY").upper()

    if ticker_input:
        with st.spinner(f"Obteniendo datos de {ticker_input}..."):
            try:
                df_asset = yf.download(ticker_input, period="2y", progress=False)
                if not df_asset.empty:
                    # Calcular SMAs
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
                    fig_asset.add_trace(go.Scatter(
                        x=df_asset.index,
                        y=df_asset['SMA_20'].squeeze(),
                        line=dict(color='#3b82f6', width=1.5),
                        name='Corto (20d)'
                    ))
                    fig_asset.add_trace(go.Scatter(
                        x=df_asset.index,
                        y=df_asset['SMA_50'].squeeze(),
                        line=dict(color='#f59e0b', width=1.5),
                        name='Medio (50d)'
                    ))
                    fig_asset.add_trace(go.Scatter(
                        x=df_asset.index,
                        y=df_asset['SMA_200'].squeeze(),
                        line=dict(color='#ef4444', width=2),
                        name='Largo (200d)'
                    ))

                    fig_asset.update_layout(
                        title=f"Acción del Precio y Tendencias - {ticker_input}",
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

    # Mostrar última decisión si existe
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
        st.info("La IA aún no ha generado decisiones. Ejecuta `agente_ollama.py` en tu terminal y luego presiona 'ACTUALIZAR AHORA'.")

    # Generador de prompt para IA externa (copiar/pegar)
    st.markdown("---")
    st.markdown("### 📋 Prompt para IA Externa (ChatGPT / Ollama)")
    if macro:
        # Construir resumen de anomalías (similar al original)
        anomalias = []
        # Necesitamos más datos, así que usamos yfinance directamente para los activos clave
        try:
            tickers_extra = {
                'SP500': '^GSPC',
                'NASDAQ': '^IXIC',
                'ORO': 'GC=F',
                'COBRE': 'HG=F',
                'US10Y': '^TNX',
                'WTI': 'CL=F'
            }
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
                            anomalias.append(f"- {name}: Pico de Volumen extremo (Posible Clímax/Absorción Institucional)")
                        if low_act < min_20d and c_act > min_20d:
                            anomalias.append(f"- {name}: Sweep Alcista (Caza de Liquidez por debajo del mínimo de 20 días)")
                        if high_act > max_20d and c_act < max_20d:
                            anomalias.append(f"- {name}: Sweep Bajista (Caza de Liquidez por encima del máximo de 20 días)")
                    except Exception:
                        pass
        except Exception:
            pass

        anom_str = "\n".join(anomalias) if anomalias else "- Estructura de precio limpia hoy sin manipulaciones detectadas."

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

# ── FOOTER (opcional) ────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:11px; margin-top:30px; border-top:1px solid #1f2937; padding-top:15px;">
    MacroVision · Datos en tiempo real vía Yahoo Finance · IA Local con Ollama
</div>
""", unsafe_allow_html=True)