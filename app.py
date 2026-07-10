# ─────────────────────────────────────────────────────────
#  MacroVision · app.py
#  Dashboard Definitivo con Bancos Centrales + IA + Análisis
# ─────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime
import yfinance as yf

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="MacroVision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('<meta http-equiv="refresh" content="14400">', unsafe_allow_html=True)

# ============================================================
# 1. FUNCIONES DE DATOS MACRO Y CORRELACIONES
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
            curr = float(close_series.iloc[-1])
            prev = float(close_series.iloc[-2])
            result[key] = {'price': curr, 'change_pct': ((curr / prev) - 1) * 100}
            
        if 'dxy' not in result or 'vix' not in result: return None
        return result
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
        return close_df.pct_change().dropna().corr()
    except:
        return None

def generar_alertas(macro_data):
    if not macro_data: return []
    alertas = []
    dxy, vix, sp500, nasdaq, oro, bond = macro_data['dxy'], macro_data['vix'], macro_data['sp500'], macro_data['nasdaq'], macro_data['oro'], macro_data['bond10y']

    if dxy['change_pct'] > 0 and vix['change_pct'] > 0: alertas.append({'mensaje': "🔴 DXY y VIX al alza → Risk-Off.", 'color': 'rojo'})
    if dxy['change_pct'] < 0 and vix['change_pct'] < 0: alertas.append({'mensaje': "🟢 DXY y VIX a la baja → Risk-On.", 'color': 'verde'})
    if dxy['change_pct'] > 0 and oro['change_pct'] < 0: alertas.append({'mensaje': "📉 Dólar fuerte presiona al oro.", 'color': 'naranja'})
    if dxy['change_pct'] < 0 and oro['change_pct'] > 0: alertas.append({'mensaje': "📈 Dólar débil impulsa al oro.", 'color': 'verde'})
    if nasdaq['change_pct'] > 0 and vix['change_pct'] > 0: alertas.append({'mensaje': "⚠️ Nasdaq y VIX suben → Divergencia peligrosa.", 'color': 'rojo'})
    if bond['change_pct'] > 0 and dxy['change_pct'] > 0: alertas.append({'mensaje': "📈 Tasas y dólar fuertes → Presión a tecnológicas.", 'color': 'naranja'})
    if bond['change_pct'] < 0 and oro['change_pct'] > 0: alertas.append({'mensaje': "📉 Tasas bajas y oro al alza → Refugio activo.", 'color': 'verde'})
    return alertas

def generar_conclusion_estrategica(alertas, macro):
    if not macro: return {"regimen": "SIN DATOS", "oportunidades": [], "riesgos": [], "recomendacion": "Verifica datos."}
    dxy, vix = macro['dxy'], macro['vix']
    dxy_up, vix_up = dxy['change_pct'] > 0, vix['change_pct'] > 0
    
    if dxy_up and vix_up: regimen, color = "AVERSIÓN AL RIESGO (Risk-Off)", "🔴"
    elif not dxy_up and not vix_up: regimen, color = "APETITO POR RIESGO (Risk-On)", "🟢"
    else: regimen, color = "MIXTO (Divergencia)", "🟡"

    recomendacion = "🟢 Favorable: Aumentar riesgo." if regimen == "APETITO POR RIESGO (Risk-On)" else ("🔴 Defensivo: Reducir riesgo." if regimen == "AVERSIÓN AL RIESGO (Risk-Off)" else "🟡 Mixto: Selección activa.")
    
    return {"regimen": f"{color} {regimen}", "oportunidades": ["Mantener posiciones" if not alertas else "Revisar alertas verdes"], "riesgos": ["Revisar alertas rojas/naranjas"], "recomendacion": recomendacion}

# ── CSS (Con Bloqueo de Traductor) ──────
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
  .mv-badge { background: #1f1f1f; color: #cccccc; font-size: 10px; padding: 3px 10px; border-radius: 4px; font-family: monospace; letter-spacing: 1px; }
  .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; display: inline-block; margin-right: 6px; }

  .bank-card { background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 14px; cursor: pointer; transition: all 0.2s; position: relative; }
  .bank-card.selected { background: #1a1a2e; }
  .bank-card-top { width: 100%; height: 2px; border-radius: 2px; margin-bottom: 10px; }
  .bank-code { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; }
  .bank-rate { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 600; color: #ffffff; }
  .bank-diff { font-family: monospace; font-size: 10px; margin-top: 2px; }
  .bank-date { font-family: monospace; font-size: 9px; color: #888888; margin-top: 4px; }

  .sent-bull { background: rgba(16,185,129,0.2); color: #4ade80; border: 1px solid #4ade8044; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; letter-spacing: 1px; font-family: monospace; }
  .sent-bear { background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid #f8717144; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; letter-spacing: 1px; font-family: monospace; }
  .sent-neut { background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid #fbbf2444; border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; letter-spacing: 1px; font-family: monospace; }

  .section-label { font-family: monospace; font-size: 12px; color: #aaaaaa; letter-spacing: 1px; margin-bottom: 14px; }

  .stButton > button { background: linear-gradient(135deg, #1d4ed8, #2563eb) !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; font-size: 14px !important; padding: 12px 28px !important; width: 100%; }
  
  div[data-testid="metric-container"] { background: #0d1117 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; padding: 14px !important; }
  div[data-testid="metric-container"] label { color: #6b7280 !important; font-size: 11px; }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 26px; color: #f9fafb; }

  .ind-row { display: grid; grid-template-columns: 130px 1fr 100px 100px 120px; padding: 10px 16px; border-bottom: 1px solid #111827; align-items: center; font-family: 'JetBrains Mono', monospace; }
  .ind-header { background: #070b14; font-size: 10px; color: #4b5563; letter-spacing: 1px; }
  
  .risk-on { background: #10b98122; border: 1px solid #10b98144; color: #10b981; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
  .risk-off { background: #ef444422; border: 1px solid #ef444444; color: #ef4444; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
  .risk-mixed { background: #f59e0b22; border: 1px solid #f59e0b44; color: #f59e0b; padding: 12px 20px; border-radius: 8px; font-weight: 600; }
  
  footer { display: none; }
  #MainMenu { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────
#  Configuración & Fallback
# ────────────────────────────────────────────────────────
BANK_COLORS = {"FED": "#3b82f6", "BCE": "#8b5cf6", "BOE": "#ec4899", "BOC": "#f97316", "RBA": "#10b981", "RBNZ": "#06b6d4"}
CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]
CAT_ICONS  = {"INFLACIÓN": "📊", "CRECIMIENTO": "📈", "EMPLEO": "👷", "CONSUMO": "🛒", "ACTIVIDAD": "🏭", "INMOBILIARIO": "🏠"}
SENT_ICON  = {"BULLISH": "▲", "BEARISH": "▼", "NEUTRO": "◆"}
SENT_CLASS = {"BULLISH": "sent-bull", "BEARISH": "sent-bear", "NEUTRO": "sent-neut"}

FALLBACK = {
    "FED":  {"name":"FED","flag":"🇺🇸","currency":"USD","fullName":"Federal Reserve","currentRate":3.75,"lastMeeting":"18 Mar 2026","rates":[{"date":"May-24","r":5.50},{"date":"Jun-24","r":5.50},{"date":"Sep-24","r":5.00},{"date":"Nov-24","r":4.75},{"date":"Dic-24","r":4.50},{"date":"Mar-25","r":4.50},{"date":"Sep-25","r":4.25},{"date":"Oct-25","r":4.00},{"date":"Dic-25","r":3.75},{"date":"Mar-26","r":3.75}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"BEARISH","CONSUMO":"BULLISH","ACTIVIDAD":"BEARISH","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.3%","prev":"2.4%","dev":"+0.9%","dir":1},{"cat":"CRECIMIENTO","name":"Advanced GDP q/q","actual":"0.5%","prev":"1.9%","dev":"-1.4%","dir":-1},{"cat":"EMPLEO","name":"NFP Change","actual":"178K","prev":"-133K","dev":"+311K","dir":1},{"cat":"CONSUMO","name":"Retail Sales m/m","actual":"0.6%","prev":"0.1%","dev":"+0.5%","dir":1}]},
    "BCE":  {"name":"BCE","flag":"🇪🇺","currency":"EUR","fullName":"Banco Central Europeo","currentRate":2.15,"lastMeeting":"19 Mar 2026","rates":[{"date":"Jun-24","r":4.25},{"date":"Sep-24","r":3.65},{"date":"Dic-24","r":3.15},{"date":"Mar-25","r":2.65},{"date":"Jun-25","r":2.15},{"date":"Mar-26","r":2.15}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BULLISH","EMPLEO":"BULLISH","CONSUMO":"NEUTRO","ACTIVIDAD":"NEUTRO","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"EZ CPI Flash y/y","actual":"2.6%","prev":"1.9%","dev":"+0.7%","dir":1},{"cat":"CRECIMIENTO","name":"EZ Flash GDP q/q","actual":"0.3%","prev":"0.3%","dev":"0.0%","dir":0},{"cat":"EMPLEO","name":"EZ Unemployment Rate","actual":"6.2%","prev":"6.3%","dev":"-0.1%","dir":1}]},
    "BOE":  {"name":"BOE","flag":"🇬🇧","currency":"GBP","fullName":"Bank of England","currentRate":3.75,"lastMeeting":"19 Mar 2026","rates":[{"date":"May-24","r":5.25},{"date":"Aug-24","r":5.00},{"date":"Nov-24","r":4.75},{"date":"Feb-25","r":4.50},{"date":"Aug-25","r":4.00},{"date":"Dic-25","r":3.75},{"date":"Mar-26","r":3.75}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"BEARISH","CONSUMO":"BULLISH","ACTIVIDAD":"BULLISH","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.3%","prev":"3.0%","dev":"+0.3%","dir":1},{"cat":"CRECIMIENTO","name":"GDP m/m","actual":"0.2%","prev":"0.3%","dev":"-0.1%","dir":-1},{"cat":"ACTIVIDAD","name":"Flash Manuf. PMI","actual":"51.6","prev":"50.6","dev":"+1.0","dir":1}]},
    "BOC":  {"name":"BOC","flag":"🇨🇦","currency":"CAD","fullName":"Bank of Canada","currentRate":2.25,"lastMeeting":"18 Mar 2026","rates":[{"date":"Jun-24","r":4.75},{"date":"Oct-24","r":3.75},{"date":"Dic-24","r":3.25},{"date":"Mar-25","r":2.75},{"date":"Oct-25","r":2.25},{"date":"Mar-26","r":2.25}],"sentiment":{"INFLACIÓN":"BEARISH","CRECIMIENTO":"NEUTRO","EMPLEO":"NEUTRO","CONSUMO":"BULLISH","ACTIVIDAD":"BEARISH","INMOBILIARIO":"BULLISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI m/m","actual":"0.9%","prev":"0.5%","dev":"+0.4%","dir":1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"-0.6%","prev":"2.4%","dev":"-3.0%","dir":-1},{"cat":"EMPLEO","name":"Employment Change","actual":"-24.8K","prev":"8.2K","dev":"-33K","dir":-1}]},
    "RBA":  {"name":"RBA","flag":"🇦🇺","currency":"AUD","fullName":"Reserve Bank of Australia","currentRate":4.10,"lastMeeting":"05 May 2026","rates":[{"date":"Jun-24","r":4.35},{"date":"Feb-25","r":4.10},{"date":"May-25","r":3.85},{"date":"Aug-25","r":3.60},{"date":"Feb-26","r":3.85},{"date":"May-26","r":4.10}],"sentiment":{"INFLACIÓN":"NEUTRO","CRECIMIENTO":"BULLISH","EMPLEO":"NEUTRO","CONSUMO":"NEUTRO","ACTIVIDAD":"BULLISH","INMOBILIARIO":"BEARISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.7%","prev":"3.8%","dev":"-0.1%","dir":-1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"0.8%","prev":"0.5%","dev":"+0.3%","dir":1}]},
    "RBNZ": {"name":"RBNZ","flag":"🇳🇿","currency":"NZD","fullName":"Reserve Bank of New Zealand","currentRate":2.25,"lastMeeting":"08 Apr 2026","rates":[{"date":"May-24","r":5.50},{"date":"Aug-24","r":5.25},{"date":"Nov-24","r":4.25},{"date":"Feb-25","r":3.75},{"date":"Aug-25","r":3.00},{"date":"Oct-25","r":2.50},{"date":"Apr-26","r":2.25}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"NEUTRO","CONSUMO":"BULLISH","ACTIVIDAD":"BULLISH","INMOBILIARIO":"BEARISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI q/q","actual":"0.9%","prev":"0.6%","dev":"+0.3%","dir":1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"0.2%","prev":"0.9%","dev":"-0.7%","dir":-1}]},
}

@st.cache_data(ttl=14400)
def load_data() -> dict:
    if os.path.exists("macro_data.json"):
        with open("macro_data.json", "r", encoding="utf-8") as f: return json.load(f)
    return FALLBACK

def load_ai_memory():
    if os.path.exists("ai_memory.json"):
        with open("ai_memory.json", "r", encoding="utf-8") as f: return json.load(f)
    return []

def overall_sentiment(s: dict) -> str:
    vals = list(s.values())
    b, be = vals.count("BULLISH"), vals.count("BEARISH")
    if b > be + 1: return "BULLISH"
    if be > b + 1: return "BEARISH"
    return "NEUTRO"

def sent_badge(s: str) -> str:
    cls = SENT_CLASS.get(s, "sent-neut")
    icon = SENT_ICON.get(s, "◆")
    return f'<span class="{cls}">{icon} {s}</span>'

# ── Estado de Sesión ──
if "data" not in st.session_state: st.session_state.data = load_data()
if "selected" not in st.session_state: st.session_state.selected = "FED"

data = st.session_state.data

# ────────────────────────────────────────────────────────
#  HEADER
# ────────────────────────────────────────────────────────
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div class="mv-header">
      <span class="live-dot"></span>
      <div>
        <p class="mv-title">MACRO<span>VISION</span>
          &nbsp;<span class="mv-badge">INSTITUCIONAL · 6 CENTRAL BANKS</span>
        </p>
        <p class="mv-subtitle">Dashboard Macroeconómico y Terminal IA</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    st.write("")
    if st.button("⟳ ACTUALIZAR DATOS"):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════
#  SEMÁFORO MACRO Y ALERTAS
# ═══════════════════════════════════════════════════════════
macro = get_macro_data()

if macro:
    st.markdown("### 📊 Semáforo de Régimen Macro")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Dólar (DXY)", f"{macro['dxy']['price']:.2f}", f"{macro['dxy']['change_pct']:.2f}%", delta_color="inverse")
    with col2: st.metric("Miedo (VIX)", f"{macro['vix']['price']:.2f}", f"{macro['vix']['change_pct']:.2f}%", delta_color="inverse")
    with col3: st.metric("Bono US 10Y", f"{macro['bond10y']['price']:.2f}%", f"{macro['bond10y']['change_pct']:.2f}%", delta_color="normal")

    dxy_up, vix_up = macro['dxy']['change_pct'] > 0, macro['vix']['change_pct'] > 0
    if dxy_up and vix_up:
        st.markdown('<div class="risk-off">🔴 ALERTA: DXY y VIX al alza → Aversión al Riesgo (Risk-Off). Precaución.</div>', unsafe_allow_html=True)
    elif not dxy_up and not vix_up:
        st.markdown('<div class="risk-on">🟢 VÍA LIBRE: DXY y VIX a la baja → Apetito por Riesgo (Risk-On). Favorable.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="risk-mixed">🟡 Régimen mixto: Señales divergentes. Selección activa de activos.</div>', unsafe_allow_html=True)

    # Gráfico DXY vs VIX (Expandible general)
    with st.expander("📈 Evolución DXY vs VIX (Últimos 3 meses)", expanded=False):
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
                    title="Correlación DXY vs VIX",
                    yaxis=dict(title="DXY", gridcolor="#1f2937", tickfont=dict(color='#3b82f6')),
                    yaxis2=dict(title="VIX", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", tickfont=dict(color='#ef4444')),
                    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=300,
                    margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5), hovermode="x unified"
                )
                fig.update_xaxes(tickformat="%d %b", gridcolor="#1f2937")
                st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.warning(f"Error renderizando gráfico DXY/VIX: {e}")

else:
    st.info("ℹ️ No se pudieron obtener datos macro (DXY/VIX).")

# ────────────────────────────────────────────────────────
#  TARJETAS DE BANCOS (SELECTOR)
# ────────────────────────────────────────────────────────
cols = st.columns(6)
for i, (k, b) in enumerate(data.items()):
    with cols[i]:
        ov = overall_sentiment(b.get("sentiment", {}))
        color = BANK_COLORS.get(k, "#fff")
        rates = b.get("rates", [])
        prev_r = rates[-2]["r"] if len(rates) >= 2 else b["currentRate"]
        diff = round(b["currentRate"] - prev_r, 2)
        diff_color = "#ef4444" if diff > 0 else ("#10b981" if diff < 0 else "#6b7280")
        diff_str = f"+{diff}%" if diff > 0 else f"{diff}%"
        selected_style = f"border-color:{color}; box-shadow: 0 0 20px {color}33;" if st.session_state.selected == k else ""

        st.markdown(f"""
        <div class="bank-card" style="{selected_style}">
          <div class="bank-card-top" style="background:{color}"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div>
              <div style="font-size:10px;color:#4b5563;font-family:monospace">{b['flag']} {b['currency']}</div>
              <div class="bank-code" style="color:{color}">{k}</div>
            </div>
            {sent_badge(ov)}
          </div>
          <div class="bank-rate">{b['currentRate']:.2f}%</div>
          <div class="bank-diff" style="color:{diff_color}">{diff_str} vs anterior</div>
          <div class="bank-date">{b['lastMeeting']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Ver {k}", key=f"sel_{k}", help=b["fullName"]):
            st.session_state.selected = k
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  NUEVAS PESTAÑAS (6 EN TOTAL)
# ══════════════════════════════════════════════════════
t_sent, t_tasas, t_ind, t_corr, t_graf, t_ia = st.tabs([
    "📊 Sentimiento", "📈 Tasas", "🔍 Indicadores", "🔗 Correlaciones", "📊 Activos", "🤖 IA Estratega"
])

# ── 1. MATRIZ DE SENTIMIENTO ──
with t_sent:
    st.markdown('<div class="section-label">▪ MATRIZ DE SENTIMIENTO — TODOS LOS BANCOS</div>', unsafe_allow_html=True)

    banks_list = list(data.keys())
    header = '<div class="ind-row ind-header" style="grid-template-columns:140px repeat(6,1fr)"><span>CATEGORÍA</span>'
    for k in banks_list:
        col = BANK_COLORS.get(k, "#fff")
        rate = data[k]["currentRate"]
        header += f'<span style="text-align:center;color:{col};font-weight:700">{k}<br><span style="color:#4b5563;font-size:9px">{rate:.2f}%</span></span>'
    header += '</div>'
    st.markdown(header, unsafe_allow_html=True)

    for cat in CATEGORIES:
        row = f'<div class="ind-row" style="grid-template-columns:140px repeat(6,1fr)">'
        row += f'<span style="font-size:11px;color:#9ca3af;font-weight:600">{CAT_ICONS[cat]} {cat}</span>'
        for k in banks_list:
            s = data[k].get("sentiment", {}).get(cat, "NEUTRO")
            row += f'<span style="text-align:center">{sent_badge(s)}</span>'
        row += '</div>'
        st.markdown(row, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols2[i]:
            ov = overall_sentiment(b.get("sentiment", {}))
            sent = b.get("sentiment", {})
            bulls, bears, neuts = list(sent.values()).count("BULLISH"), list(sent.values()).count("BEARISH"), list(sent.values()).count("NEUTRO")
            color = BANK_COLORS.get(k, "#fff")
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #1f2937;border-radius:10px;padding:14px">
              <div style="font-size:11px;color:{color};font-weight:700;margin-bottom:8px;font-family:monospace">{k} — Resumen</div>
              {sent_badge(ov)}
              <div style="margin-top:10px;display:flex;gap:8px">
                <span style="color:#10b981;font-size:10px;font-family:monospace">▲{bulls}</span>
                <span style="color:#ef4444;font-size:10px;font-family:monospace">▼{bears}</span>
                <span style="color:#f59e0b;font-size:10px;font-family:monospace">◆{neuts}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── 2. TASAS HISTÓRICAS ──
with t_tasas:
    st.markdown('<div class="section-label">▪ EVOLUCIÓN HISTÓRICA DE TASAS</div>', unsafe_allow_html=True)
    fig_tasas = go.Figure()

    def parse_month_year(date_str):
        meses = {"Ene":"Jan","Feb":"Feb","Mar":"Mar","Abr":"Apr","May":"May","Jun":"Jun","Jul":"Jul","Ago":"Aug","Sep":"Sep","Oct":"Oct","Nov":"Nov","Dic":"Dec"}
        for es, en in meses.items(): date_str = date_str.replace(es, en)
        try: return datetime.strptime(date_str, "%b-%y")
        except: return datetime(1900, 1, 1)

    for k, b in data.items():
        rates = b.get("rates", [])
        if not rates: continue
        rates_sorted = sorted(rates, key=lambda x: parse_month_year(x["date"]))
        dates, vals = [r["date"] for r in rates_sorted], [r["r"] for r in rates_sorted]
        fig_tasas.add_trace(go.Scatter(
            x=dates, y=vals, name=k, mode="lines+markers",
            line=dict(color=BANK_COLORS.get(k, "#fff"), width=3),
            marker=dict(size=6, symbol="circle", line=dict(width=1, color="white")),
            hovertemplate=f"<b>{k}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"
        ))

    fig_tasas.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(family="JetBrains Mono", color="#e2e8f0", size=11),
        xaxis=dict(gridcolor="#1f2937", tickangle=-30, type="category", categoryorder="array", categoryarray=sorted(set([r["date"] for b in data.values() for r in b.get("rates",[])]), key=parse_month_year)),
        yaxis=dict(gridcolor="#1f2937", ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5), margin=dict(l=40, r=40, t=20, b=80), height=400, hovermode="x unified"
    )
    st.plotly_chart(fig_tasas, width="stretch")

    st.markdown("**COMPARATIVA TASAS — CICLO ACTUAL**")
    cols3 = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols3[i]:
            rates = b.get("rates", [])
            if not rates: continue
            vals = [r["r"] for r in rates]
            mn, mx, cur = min(vals), max(vals), b["currentRate"]
            pct = int(((cur - mn) / (mx - mn)) * 100) if mx != mn else 100
            color = BANK_COLORS.get(k, "#fff")
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #1f2937;border-radius:10px;padding:16px">
              <div style="font-size:11px;color:{color};font-weight:700;font-family:monospace;margin-bottom:8px">{b['flag']} {k}</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:600;color:#f9fafb">{cur:.2f}<span style="font-size:13px;color:#6b7280">%</span></div>
              <div style="margin-top:10px;height:4px;background:#1f2937;border-radius:2px">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:2px"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:4px">
                <span style="font-size:9px;color:#4b5563;font-family:monospace">Min: {mn}%</span>
                <span style="font-size:9px;color:#4b5563;font-family:monospace">Max: {mx}%</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── 3. INDICADORES DEL BANCO ──
with t_ind:
    sel = st.session_state.selected
    bank = data.get(sel, {})
    color = BANK_COLORS.get(sel, "#fff")
    
    st.markdown(f'<div class="section-label">▪ INDICADORES CLAVE — <span style="color:{color}">{sel}</span> {bank.get("flag","")} {bank.get("fullName","")}</div>', unsafe_allow_html=True)
    
    # Cajitas de sentimiento por categoría
    sent = bank.get("sentiment", {})
    cols4 = st.columns(6)
    for i, cat in enumerate(CATEGORIES):
        with cols4[i]:
            s = sent.get(cat, "NEUTRO")
            cfg_bg = {"BULLISH": "rgba(16,185,129,0.12)", "BEARISH": "rgba(239,68,68,0.12)", "NEUTRO": "rgba(245,158,11,0.12)"}
            cfg_bc = {"BULLISH": "#10b98144", "BEARISH": "#ef444444", "NEUTRO": "#f59e0b44"}
            st.markdown(f"""
            <div style="background:{cfg_bg.get(s,'#0d1117')};border:1px solid {cfg_bc.get(s,'#1f2937')};border-radius:8px;padding:12px 8px;text-align:center">
              <div style="font-size:18px;margin-bottom:4px">{CAT_ICONS[cat]}</div>
              <div style="font-size:9px;color:#6b7280;font-family:monospace;letter-spacing:1px;margin-bottom:6px">{cat}</div>
              {sent_badge(s)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabla de indicadores
    indicators = bank.get("indicators", [])
    cat_colors = {"INFLACIÓN":"#3b82f6","CRECIMIENTO":"#8b5cf6","EMPLEO":"#10b981","CONSUMO":"#f59e0b","ACTIVIDAD":"#ec4899","INMOBILIARIO":"#06b6d4"}
    
    header_i = '<div class="ind-row ind-header"><span>CATEGORÍA</span><span>INDICADOR</span><span style="text-align:right">ACTUAL</span><span style="text-align:right">PREVIO</span><span style="text-align:right">DESVIACIÓN</span></div>'
    st.markdown(header_i, unsafe_allow_html=True)
    for idx, ind in enumerate(indicators):
        d = ind.get("dir", 0)
        d_color = "#10b981" if d > 0 else ("#ef4444" if d < 0 else "#f59e0b")
        d_icon  = "▲" if d > 0 else ("▼" if d < 0 else "◆")
        cat_c   = cat_colors.get(ind.get("cat",""), "#9ca3af")
        bg      = "transparent" if idx % 2 == 0 else "#070b14"
        row = f'<div class="ind-row" style="background:{bg}">'
        row += f'<span style="font-size:10px;color:{cat_c};font-weight:600;">{ind.get("cat","")}</span>'
        row += f'<span style="font-size:12px;color:#d1d5db">{ind.get("name","")}</span>'
        row += f'<span style="text-align:right;font-size:13px;font-weight:600;color:#f9fafb">{ind.get("actual","—")}</span>'
        row += f'<span style="text-align:right;font-size:12px;color:#6b7280">{ind.get("prev","—")}</span>'
        row += f'<span style="text-align:right;font-size:12px;font-weight:700;color:{d_color}">{d_icon} {ind.get("dev","—")}</span>'
        row += '</div>'
        st.markdown(row, unsafe_allow_html=True)

    # Gráfico individual de tasa
    rates = bank.get("rates", [])
    if rates:
        st.markdown(f'<br><div class="section-label">HISTORIAL DE TASA — {sel}</div>', unsafe_allow_html=True)
        fig_ind = go.Figure()
        fig_ind.add_trace(go.Scatter(x=[r["date"] for r in rates], y=[r["r"] for r in rates], mode="lines+markers", line=dict(color=color, width=2, shape="hv"), marker=dict(size=5, color=color)))
        fig_ind.add_hline(y=bank["currentRate"], line_dash="dot", line_color=color, opacity=0.5)
        fig_ind.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(family="JetBrains Mono", color="#9ca3af", size=9), xaxis=dict(gridcolor="#1f2937", showline=False), yaxis=dict(gridcolor="#1f2937", showline=False, ticksuffix="%"), margin=dict(l=20, r=20, t=10, b=20), height=200, showlegend=False)
        st.plotly_chart(fig_ind, width="stretch")

# ── 4. CORRELACIONES ──
with t_corr:
    st.markdown("### 🔗 Matriz de Correlación Macroeconómica (1 Año)")
    st.write("Identifica si dos activos se mueven juntos (1.0), de forma inversa (-1.0) o no tienen relación (0.0).")
    corr_matrix = get_correlation_matrix()
    if corr_matrix is not None:
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale='RdBu_r')
        fig_corr.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"))
        st.plotly_chart(fig_corr, width="stretch")
    else:
        st.warning("Descargando datos de correlación...")

# ── 5. ANÁLISIS DE ACTIVOS ──
with t_graf:
    st.markdown("### 📈 Análisis Técnico Multi-Plazo (Medias Móviles)")
    col_input, col_info = st.columns([1, 2])
    with col_input: ticker_input = st.text_input("Símbolo del Activo (ej. AAPL, BTC-USD, SPY, NVDA):", value="SPY").upper()
    
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

                    fig_asset.update_layout(title=f"Acción del Precio y Tendencias - {ticker_input}", yaxis_title="Precio USD", xaxis_rangeslider_visible=False, paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#e2e8f0"), height=500, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_asset, width="stretch")
                else: st.error("No se encontraron datos para ese símbolo.")
            except: st.error("Error cargando gráfico.")

# ── 6. IA ESTRATEGA ──
with t_ia:
    st.markdown("### 🤖 Memoria y Pensamiento del Agente IA")
    memoria_ia = load_ai_memory()
    if not memoria_ia:
        st.info("La IA aún no ha registrado decisiones. Ejecuta `agente_ollama.py` en tu terminal local para generar la primera señal.")
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