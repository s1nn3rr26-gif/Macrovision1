# ─────────────────────────────────────────────────────────
#  MacroVision · app.py
#  Dashboard con Análisis Técnico, Correlaciones y Memoria IA
# ─────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime
import yfinance as yf

st.set_page_config(page_title="MacroVision", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<meta http-equiv="refresh" content="14400">', unsafe_allow_html=True)

# ============================================================
# 1. FUNCIONES DE DATOS
# ============================================================
@st.cache_data(ttl=14400)
def get_macro_data():
    try:
        tickers = {'dxy': 'DX-Y.NYB', 'vix': '^VIX', 'sp500': '^GSPC', 'nasdaq': '^IXIC', 'oro': 'GC=F', 'bond10y': '^TNX'}
        data = yf.download(list(tickers.values()), period="5d", progress=False)
        if data.empty: return None
        result = {}
        for key, symbol in tickers.items():
            close_series = data['Close'][symbol].dropna() 
            if len(close_series) < 2: continue
            curr, prev = float(close_series.iloc[-1]), float(close_series.iloc[-2])
            result[key] = {'price': curr, 'change_pct': ((curr / prev) - 1) * 100}
        return result if 'dxy' in result and 'vix' in result else None
    except:
        return None

@st.cache_data(ttl=86400)
def get_correlation_matrix():
    try:
        tickers = {'DXY': 'DX-Y.NYB', 'VIX': '^VIX', 'S&P 500': '^GSPC', 'Nasdaq': '^IXIC', 'Oro': 'GC=F', 'Bono 10Y': '^TNX'}
        df = yf.download(list(tickers.values()), period="1y", progress=False)
        if df.empty: return None
        
        close_df = df['Close']
        rename_dict = {v: k for k, v in tickers.items()}
        close_df = close_df.rename(columns=rename_dict)
        
        returns = close_df.pct_change().dropna()
        return returns.corr()
    except Exception as e:
        return None

def generar_alertas(macro_data):
    if not macro_data: return []
    a = []
    dxy, vix, oro, nasdaq, bond = macro_data['dxy'], macro_data['vix'], macro_data['oro'], macro_data['nasdaq'], macro_data['bond10y']
    if dxy['change_pct'] > 0 and vix['change_pct'] > 0: a.append({'m': "🔴 DXY y VIX al alza → Risk-Off.", 'c': 'rojo'})
    if dxy['change_pct'] < 0 and vix['change_pct'] < 0: a.append({'m': "🟢 DXY y VIX a la baja → Risk-On.", 'c': 'verde'})
    if nasdaq['change_pct'] > 0 and vix['change_pct'] > 0: a.append({'m': "⚠️ Nasdaq y VIX suben → Divergencia peligrosa.", 'c': 'rojo'})
    if bond['change_pct'] > 0 and dxy['change_pct'] > 0: a.append({'m': "📈 Tasas y dólar fuertes → Riesgo para tecnológicas.", 'c': 'naranja'})
    return a

# ── CSS ──────
st.markdown("""
<meta name="google" content="notranslate">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
  html, body, div, span, p, a, h1, h2, h3, h4, h5, h6 { translate: no !important; }
  html, body, [class*="css"], .stApp, .main, .block-container { background: #000000 !important; color: #ffffff !important; font-family: 'Space Grotesk', sans-serif; }
  .block-container { padding: 1.5rem 2rem !important; max-width: 100%; }
  .mv-header { display: flex; align-items: center; gap: 12px; padding-bottom: 16px; border-bottom: 1px solid #333333; margin-bottom: 20px; }
  .mv-title { font-size: 24px; font-weight: 700; color: #ffffff; margin: 0; }
  .mv-title span { color: #3b82f6; }
  .mv-subtitle { font-family: monospace; font-size: 11px; color: #aaaaaa; margin-top: 4px; }
  .mv-badge { background: #1f1f1f; color: #cccccc; font-size: 10px; padding: 3px 10px; border-radius: 4px; font-family: monospace; }
  .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; display: inline-block; }
  .bank-card { background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 14px; cursor: pointer; }
  .bank-card-top { width: 100%; height: 2px; border-radius: 2px; margin-bottom: 10px; }
  .bank-code { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; }
  .bank-rate { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 600; color: #ffffff; }
  .sent-bull { background: rgba(16,185,129,0.2); color: #4ade80; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; }
  .sent-bear { background: rgba(239,68,68,0.2); color: #f87171; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; }
  .sent-neut { background: rgba(245,158,11,0.2); color: #fbbf24; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; }
  .stButton > button { background: linear-gradient(135deg, #1d4ed8, #2563eb) !important; color: white !important; border: none !important; border-radius: 8px !important; width: 100%; }
  div[data-testid="metric-container"] { background: #0d1117 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; padding: 14px !important; }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 26px; }
  .ind-row { display: grid; grid-template-columns: 130px 1fr 100px 100px 120px; padding: 10px 16px; border-bottom: 1px solid #111827; align-items: center; font-family: 'JetBrains Mono', monospace; }
  .ind-header { background: #070b14; font-size: 10px; color: #4b5563; }
  header { visibility: hidden; }
  footer { display: none; }
  #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

BANK_COLORS = {"FED": "#3b82f6", "BCE": "#8b5cf6", "BOE": "#ec4899", "BOC": "#f97316", "RBA": "#10b981", "RBNZ": "#06b6d4"}
CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]
CAT_ICONS  = {"INFLACIÓN": "📊", "CRECIMIENTO": "📈", "EMPLEO": "👷", "CONSUMO": "🛒", "ACTIVIDAD": "🏭", "INMOBILIARIO": "🏠"}
SENT_CLASS = {"BULLISH": "sent-bull", "BEARISH": "sent-bear", "NEUTRO": "sent-neut"}

@st.cache_data(ttl=14400)
def load_data():
    if os.path.exists("macro_data.json"):
        with open("macro_data.json", "r", encoding="utf-8") as f: return json.load(f)
    return {}

def load_ai_memory():
    if os.path.exists("ai_memory.json"):
        with open("ai_memory.json", "r", encoding="utf-8") as f: return json.load(f)
    return []

if "data" not in st.session_state: st.session_state.data = load_data()
if "selected" not in st.session_state: st.session_state.selected = "FED"

data = st.session_state.data

# ── HEADER ──
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div class="mv-header">
      <span class="live-dot"></span><div><p class="mv-title">MACRO<span>VISION</span></p><p class="mv-subtitle">Dashboard Macroeconómico Institucional</p></div>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.write("")
    if st.button("⟳ ACTUALIZAR AHORA"):
        st.cache_data.clear()
        st.rerun()

macro = get_macro_data()
if macro:
    col1, col2, col3 = st.columns(3)
    col1.metric("Dólar (DXY)", f"{macro['dxy']['price']:.2f}", f"{macro['dxy']['change_pct']:.2f}%", delta_color="inverse")
    col2.metric("Miedo (VIX)", f"{macro['vix']['price']:.2f}", f"{macro['vix']['change_pct']:.2f}%", delta_color="inverse")
    col3.metric("Bono US 10Y", f"{macro['bond10y']['price']:.2f}%", f"{macro['bond10y']['change_pct']:.2f}%")

if data:
    cols = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols[i]:
            ov = "BULLISH" if list(b.get("sentiment",{}).values()).count("BULLISH") > 2 else "NEUTRO"
            c = BANK_COLORS.get(k, "#fff")
            sty = f"border-color:{c}; box-shadow: 0 0 15px {c}33;" if st.session_state.selected == k else ""
            st.markdown(f"""<div class="bank-card" style="{sty}"><div class="bank-card-top" style="background:{c}"></div>
              <div class="bank-code" style="color:{c}">{k}</div><div class="bank-rate">{b.get('currentRate', 0):.2f}%</div>
              </div>""", unsafe_allow_html=True)
            if st.button(f"Ver {k}", key=f"sel_{k}"):
                st.session_state.selected = k
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS (NUEVA ESTRUCTURA) ──
t_sent, t_ind, t_corr, t_graf, t_ia = st.tabs(["📊 Sentimiento & Tasas", "🔍 Indicadores", "🔗 Correlaciones", "📈 Análisis de Activos", "🤖 IA Estratega"])

# 1. TABS BÁSICOS
with t_sent:
    st.markdown("### 📈 Evolución DXY vs VIX (Últimos 3 Meses)")
    if macro:
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
                    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=300,
                    margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5), hovermode="x unified"
                )
                fig.update_xaxes(tickformat="%d %b", gridcolor="#1f2937")
                st.plotly_chart(fig, width="stretch")
        except:
            st.warning("No se pudo renderizar el gráfico principal.")

with t_ind:
    sel = st.session_state.selected
    st.markdown(f"### 🔍 Indicadores Actuales — {sel}")
    inds = data.get(sel, {}).get("indicators", [])
    if inds:
        header_i = '<div class="ind-row ind-header"><span>CATEGORÍA</span><span>INDICADOR</span><span style="text-align:right">ACTUAL</span><span style="text-align:right">PREVIO</span><span style="text-align:right">DIR</span></div>'
        st.markdown(header_i, unsafe_allow_html=True)
        for idx, ind in enumerate(inds):
            bg = "transparent" if idx % 2 == 0 else "#070b14"
            row = f'<div class="ind-row" style="background:{bg}">'
            row += f'<span style="font-size:10px;font-weight:600;color:#9ca3af">{ind.get("cat","")}</span>'
            row += f'<span style="font-size:12px;color:#d1d5db">{ind.get("name","")}</span>'
            row += f'<span style="text-align:right;font-size:13px;font-weight:600;color:#f9fafb">{ind.get("actual","—")}</span>'
            row += f'<span style="text-align:right;font-size:12px;color:#6b7280">{ind.get("prev","—")}</span>'
            row += f'<span style="text-align:right;font-size:12px;color:#3b82f6">{ind.get("dev","—")}</span>'
            row += '</div>'
            st.markdown(row, unsafe_allow_html=True)
    else:
        st.info("No hay indicadores disponibles para este banco.")

# 2. PESTAÑA CORRELACIONES (Matriz de calor)
with t_corr:
    st.markdown("### 🔗 Matriz de Correlación Macroeconómica (1 Año)")
    st.write("Muestra cómo se mueven los activos entre sí. Una correlación cercana a 1.0 significa que se mueven idénticos; -1.0 que se mueven de forma inversa.")
    
    corr_matrix = get_correlation_matrix()
    if corr_matrix is not None:
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale='RdBu_r')
        fig_corr.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"))
        st.plotly_chart(fig_corr, width="stretch")
    else:
        st.warning("Descargando datos de correlación... intente nuevamente.")

# 3. PESTAÑA ANÁLISIS DE ACTIVOS (Gráfico de velas)
with t_graf:
    st.markdown("### 📈 Análisis Técnico Multi-Plazo")
    
    col_input, col_info = st.columns([1, 2])
    with col_input:
        ticker_input = st.text_input("Símbolo del Activo (ej. AAPL, BTC-USD, SPY, NVDA):", value="SPY").upper()
    
    if ticker_input:
        with st.spinner(f"Obteniendo datos de {ticker_input}..."):
            try:
                df_asset = yf.download(ticker_input, period="2y", progress=False)
                if not df_asset.empty:
                    df_asset['SMA_20'] = df_asset['Close'].rolling(window=20).mean()
                    df_asset['SMA_50'] = df_asset['Close'].rolling(window=50).mean()
                    df_asset['SMA_200'] = df_asset['Close'].rolling(window=200).mean()

                    fig_asset = go.Figure()
                    fig_asset.add_trace(go.Candlestick(x=df_asset.index, open=df_asset['Open'].squeeze(), high=df_asset['High'].squeeze(), low=df_asset['Low'].squeeze(), close=df_asset['Close'].squeeze(), name='Precio'))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_20'].squeeze(), line=dict(color='#3b82f6', width=1.5), name='Corto Plazo (20d)'))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_50'].squeeze(), line=dict(color='#f59e0b', width=1.5), name='Medio Plazo (50d)'))
                    fig_asset.add_trace(go.Scatter(x=df_asset.index, y=df_asset['SMA_200'].squeeze(), line=dict(color='#ef4444', width=2), name='Largo Plazo (200d)'))

                    fig_asset.update_layout(
                        title=f"Acción del Precio y Tendencias - {ticker_input}",
                        yaxis_title="Precio USD", xaxis_rangeslider_visible=False,
                        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"),
                        height=500, margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_asset, width="stretch")
                    
                    st.markdown("""**Guía de Inversión Rápida:**
                    * **Corto Plazo:** Si el precio está por encima de la línea azul (20d), hay impulso alcista inmediato.
                    * **Medio Plazo:** Si la línea azul cruza hacia arriba la amarilla (50d), es una señal técnica de compra a mediano plazo.
                    * **Largo Plazo:** La línea roja (200d) separa los mercados alcistas de los bajistas. Operar por debajo de ella conlleva alto riesgo.""")
                else:
                    st.error("No se encontraron datos para ese símbolo.")
            except Exception as e:
                st.error(f"Error cargando gráfico: {e}")

# 4. PESTAÑA IA ESTRATEGA
with t_ia:
    st.markdown("### 🤖 Memoria y Pensamiento del Agente IA")
    memoria_ia = load_ai_memory()
    
    if not memoria_ia:
        st.info("La IA aún no ha registrado decisiones. Ejecuta `agente_ollama.py` en tu terminal local para generar la primera señal y luego presiona 'ACTUALIZAR AHORA'.")
    else:
        ultima_decision = memoria_ia[-1]
        
        st.success(f"**Última actualización de la IA:** {ultima_decision['fecha']}")
        st.markdown(f"""
        <div style="background:#111827; padding:20px; border-left: 5px solid #8b5cf6; border-radius: 5px;">
            <pre style="white-space: pre-wrap; font-family: 'Space Grotesk', sans-serif; font-size: 16px; color:#ffffff;">{ultima_decision['decision']}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📚 Ver el historial completo (Memoria de la IA)"):
            for m in reversed(memoria_ia[:-1]):
                st.markdown(f"**{m['fecha']}**")
                st.write(m['decision'])
                st.markdown("---")