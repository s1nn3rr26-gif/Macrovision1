# ─────────────────────────────────────────────────────────
#  MacroVision · app.py
#  Dashboard Streamlit con botón de actualización
#  Ejecutar: streamlit run app.py
# ─────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="MacroVision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# ─────────────────────────────────────────────────────────
#  AUTORIZACIÓN (CONTRASEÑA)
# ─────────────────────────────────────────────────────────
def check_password():
    """Retorna True si el usuario está autenticado."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Contraseña fija (cámbiala por la que quieras)
    PASSWORD = "Macro2026"   # ← Cambia aquí la contraseña

    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 70vh;">
            <div style="background: #0d1117; padding: 2rem; border-radius: 20px; border: 1px solid #333; text-align: center;">
                <h2 style="color: #fff;">🔐 Acceso restringido</h2>
                <p style="color: #aaa;">Ingresa la contraseña para continuar</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    password_input = st.text_input("Contraseña", type="password", key="pass_input")
    if st.button("Entrar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    return False

# Verificar autenticación al inicio
if not check_password():
    st.stop()  # No mostrar nada más si no está autenticado
    
# ── CSS: alto contraste (fondo negro, texto blanco) ──────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  /* Todo el fondo negro y texto blanco */
  html, body, [class*="css"], .stApp, .main, .block-container {
    background: #000000 !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif;
  }
  .block-container { padding: 1.5rem 2rem !important; max-width: 100%; }
  
  .mv-header {
    display: flex; align-items: center; gap: 12px;
    padding-bottom: 16px; border-bottom: 1px solid #333333;
    margin-bottom: 20px;
  }
  .mv-title { font-size: 24px; font-weight: 700; color: #ffffff; margin: 0; }
  .mv-title span { color: #3b82f6; }
  .mv-subtitle { font-family: monospace; font-size: 11px; color: #aaaaaa; margin-top: 4px; }
  .mv-badge { background: #1f1f1f; color: #cccccc; font-size: 10px; padding: 3px 10px;
               border-radius: 4px; font-family: monospace; letter-spacing: 1px; }
  .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981;
              box-shadow: 0 0 8px #10b981; display: inline-block; margin-right: 6px; }

  .bank-card {
    background: #111111; border: 1px solid #333333; border-radius: 10px;
    padding: 14px; cursor: pointer; transition: all 0.2s; position: relative;
  }
  .bank-card.selected { background: #1a1a2e; }
  .bank-card-top { width: 100%; height: 2px; border-radius: 2px; margin-bottom: 10px; }
  .bank-code { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; }
  .bank-rate { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 600; color: #ffffff; }
  .bank-diff { font-family: monospace; font-size: 10px; margin-top: 2px; }
  .bank-date { font-family: monospace; font-size: 9px; color: #888888; margin-top: 4px; }

  .sent-bull { background: rgba(16,185,129,0.2); color: #4ade80; border: 1px solid #4ade8044;
               border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700; 
               letter-spacing: 1px; font-family: monospace; }
  .sent-bear { background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid #f8717144;
               border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700;
               letter-spacing: 1px; font-family: monospace; }
  .sent-neut { background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid #fbbf2444;
               border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 700;
               letter-spacing: 1px; font-family: monospace; }

  .section-label { font-family: monospace; font-size: 12px; color: #aaaaaa; 
                   letter-spacing: 1px; margin-bottom: 14px; }

  .stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important;
    font-size: 14px !important; padding: 12px 28px !important;
    box-shadow: 0 0 20px #3b82f633 !important; transition: all 0.2s !important;
    letter-spacing: 0.5px !important; width: 100%;
  }
  .stButton > button:hover { box-shadow: 0 0 30px #3b82f666 !important; transform: translateY(-1px); }

  div[data-testid="metric-container"] {
    background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 14px;
  }
  div[data-testid="metric-container"] label { color: #aaaaaa !important; font-size: 11px; }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] { 
    font-family: 'JetBrains Mono', monospace; font-size: 26px; color: #ffffff;
  }

  .stTabs [data-baseweb="tab-list"] { background: #111111; border-bottom: 1px solid #333333; }
  .stTabs [data-baseweb="tab"] { color: #cccccc; font-family: 'Space Grotesk'; font-weight: 600; }
  .stTabs [aria-selected="true"] { color: #fff; border-bottom: 2px solid #3b82f6; }

  .ind-row {
    display: grid; grid-template-columns: 130px 1fr 100px 100px 120px;
    padding: 10px 16px; border-bottom: 1px solid #222222; align-items: center;
    font-family: 'JetBrains Mono', monospace;
  }
  .ind-header { background: #000000; font-size: 10px; color: #aaaaaa; letter-spacing: 1px; }
  .stSelectbox > div > div { background: #111111 !important; border-color: #333333 !important; color: #ffffff !important; }
  
  footer { display: none; }
  #MainMenu { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────
#  Configuración & colores
# ────────────────────────────────────────────────────────
BANK_COLORS = {
    "FED": "#3b82f6", "BCE": "#8b5cf6", "BOE": "#ec4899",
    "BOC": "#f97316", "RBA": "#10b981", "RBNZ": "#06b6d4"
}
CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]
CAT_ICONS  = {"INFLACIÓN": "📊", "CRECIMIENTO": "📈", "EMPLEO": "👷",
               "CONSUMO": "🛒", "ACTIVIDAD": "🏭", "INMOBILIARIO": "🏠"}
SENT_ICON  = {"BULLISH": "▲", "BEARISH": "▼", "NEUTRO": "◆"}
SENT_CLASS = {"BULLISH": "sent-bull", "BEARISH": "sent-bear", "NEUTRO": "sent-neut"}

# ── Datos fallback (del Excel original) — se sobreescribe al actualizar ──
FALLBACK = {
    "FED":  {"name":"FED","flag":"🇺🇸","currency":"USD","fullName":"Federal Reserve","currentRate":3.75,"lastMeeting":"18 Mar 2026","rates":[{"date":"May-24","r":5.50},{"date":"Jun-24","r":5.50},{"date":"Sep-24","r":5.00},{"date":"Nov-24","r":4.75},{"date":"Dic-24","r":4.50},{"date":"Mar-25","r":4.50},{"date":"Sep-25","r":4.25},{"date":"Oct-25","r":4.00},{"date":"Dic-25","r":3.75},{"date":"Mar-26","r":3.75}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"BEARISH","CONSUMO":"BULLISH","ACTIVIDAD":"BEARISH","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.3%","prev":"2.4%","dev":"+0.9%","dir":1},{"cat":"CRECIMIENTO","name":"Advanced GDP q/q","actual":"0.5%","prev":"1.9%","dev":"-1.4%","dir":-1},{"cat":"EMPLEO","name":"NFP Change","actual":"178K","prev":"-133K","dev":"+311K","dir":1},{"cat":"CONSUMO","name":"Retail Sales m/m","actual":"0.6%","prev":"0.1%","dev":"+0.5%","dir":1}]},
    "BCE":  {"name":"BCE","flag":"🇪🇺","currency":"EUR","fullName":"Banco Central Europeo","currentRate":2.15,"lastMeeting":"19 Mar 2026","rates":[{"date":"Jun-24","r":4.25},{"date":"Sep-24","r":3.65},{"date":"Dic-24","r":3.15},{"date":"Mar-25","r":2.65},{"date":"Jun-25","r":2.15},{"date":"Mar-26","r":2.15}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BULLISH","EMPLEO":"BULLISH","CONSUMO":"NEUTRO","ACTIVIDAD":"NEUTRO","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"EZ CPI Flash y/y","actual":"2.6%","prev":"1.9%","dev":"+0.7%","dir":1},{"cat":"CRECIMIENTO","name":"EZ Flash GDP q/q","actual":"0.3%","prev":"0.3%","dev":"0.0%","dir":0},{"cat":"EMPLEO","name":"EZ Unemployment Rate","actual":"6.2%","prev":"6.3%","dev":"-0.1%","dir":1}]},
    "BOE":  {"name":"BOE","flag":"🇬🇧","currency":"GBP","fullName":"Bank of England","currentRate":3.75,"lastMeeting":"19 Mar 2026","rates":[{"date":"May-24","r":5.25},{"date":"Aug-24","r":5.00},{"date":"Nov-24","r":4.75},{"date":"Feb-25","r":4.50},{"date":"Aug-25","r":4.00},{"date":"Dic-25","r":3.75},{"date":"Mar-26","r":3.75}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"BEARISH","CONSUMO":"BULLISH","ACTIVIDAD":"BULLISH","INMOBILIARIO":"NEUTRO"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.3%","prev":"3.0%","dev":"+0.3%","dir":1},{"cat":"CRECIMIENTO","name":"GDP m/m","actual":"0.2%","prev":"0.3%","dev":"-0.1%","dir":-1},{"cat":"ACTIVIDAD","name":"Flash Manuf. PMI","actual":"51.6","prev":"50.6","dev":"+1.0","dir":1}]},
    "BOC":  {"name":"BOC","flag":"🇨🇦","currency":"CAD","fullName":"Bank of Canada","currentRate":2.25,"lastMeeting":"18 Mar 2026","rates":[{"date":"Jun-24","r":4.75},{"date":"Oct-24","r":3.75},{"date":"Dic-24","r":3.25},{"date":"Mar-25","r":2.75},{"date":"Oct-25","r":2.25},{"date":"Mar-26","r":2.25}],"sentiment":{"INFLACIÓN":"BEARISH","CRECIMIENTO":"NEUTRO","EMPLEO":"NEUTRO","CONSUMO":"BULLISH","ACTIVIDAD":"BEARISH","INMOBILIARIO":"BULLISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI m/m","actual":"0.9%","prev":"0.5%","dev":"+0.4%","dir":1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"-0.6%","prev":"2.4%","dev":"-3.0%","dir":-1},{"cat":"EMPLEO","name":"Employment Change","actual":"-24.8K","prev":"8.2K","dev":"-33K","dir":-1}]},
    "RBA":  {"name":"RBA","flag":"🇦🇺","currency":"AUD","fullName":"Reserve Bank of Australia","currentRate":4.10,"lastMeeting":"05 May 2026","rates":[{"date":"Jun-24","r":4.35},{"date":"Feb-25","r":4.10},{"date":"May-25","r":3.85},{"date":"Aug-25","r":3.60},{"date":"Feb-26","r":3.85},{"date":"May-26","r":4.10}],"sentiment":{"INFLACIÓN":"NEUTRO","CRECIMIENTO":"BULLISH","EMPLEO":"NEUTRO","CONSUMO":"NEUTRO","ACTIVIDAD":"BULLISH","INMOBILIARIO":"BEARISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI y/y","actual":"3.7%","prev":"3.8%","dev":"-0.1%","dir":-1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"0.8%","prev":"0.5%","dev":"+0.3%","dir":1}]},
    "RBNZ": {"name":"RBNZ","flag":"🇳🇿","currency":"NZD","fullName":"Reserve Bank of New Zealand","currentRate":2.25,"lastMeeting":"08 Apr 2026","rates":[{"date":"May-24","r":5.50},{"date":"Aug-24","r":5.25},{"date":"Nov-24","r":4.25},{"date":"Feb-25","r":3.75},{"date":"Aug-25","r":3.00},{"date":"Oct-25","r":2.50},{"date":"Apr-26","r":2.25}],"sentiment":{"INFLACIÓN":"BULLISH","CRECIMIENTO":"BEARISH","EMPLEO":"NEUTRO","CONSUMO":"BULLISH","ACTIVIDAD":"BULLISH","INMOBILIARIO":"BEARISH"},"indicators":[{"cat":"INFLACIÓN","name":"CPI q/q","actual":"0.9%","prev":"0.6%","dev":"+0.3%","dir":1},{"cat":"CRECIMIENTO","name":"GDP q/q","actual":"0.2%","prev":"0.9%","dev":"-0.7%","dir":-1}]},
}

# ────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────
def load_data() -> dict:
    if os.path.exists("macro_data.json"):
        with open("macro_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return FALLBACK

def overall_sentiment(s: dict) -> str:
    vals = list(s.values())
    b = vals.count("BULLISH"); be = vals.count("BEARISH")
    if b > be + 1: return "BULLISH"
    if be > b + 1: return "BEARISH"
    return "NEUTRO"

def sent_badge(s: str) -> str:
    cls = SENT_CLASS.get(s, "sent-neut")
    icon = SENT_ICON.get(s, "◆")
    return f'<span class="{cls}">{icon} {s}</span>'

def data_age(data: dict) -> str:
    for b in data.values():
        if "updated" in b:
            try:
                dt = datetime.fromisoformat(b["updated"])
                return dt.strftime("Actualizado: %d/%m/%Y %H:%M")
            except:
                pass
    return "Datos del archivo Excel"

# ────────────────────────────────────────────────────────
#  Estado de sesión
# ────────────────────────────────────────────────────────
if "data"     not in st.session_state: st.session_state.data     = load_data()
if "selected" not in st.session_state: st.session_state.selected = "FED"
if "tab"      not in st.session_state: st.session_state.tab      = "Sentimiento"
if "updating" not in st.session_state: st.session_state.updating = False

data = st.session_state.data

# ────────────────────────────────────────────────────────
#  HEADER
# ────────────────────────────────────────────────────────
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div class="mv-header">
      <span class="live-dot"></span>
      <div>
        <p class="mv-title">MACRO<span>VISION</span>
          &nbsp;<span class="mv-badge">LIVE · 6 CENTRAL BANKS</span>
        </p>
        <p class="mv-subtitle">Dashboard Macroeconómico Global · {data_age(data)}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    st.write("")
    st.write("")
    if st.button("⟳  ACTUALIZAR DATOS", key="update_btn"):
        st.session_state.updating = True
        with st.spinner("Descargando datos frescos de APIs…"):
            try:
                from macro_fetch import fetch_all, save_json
                fresh = fetch_all(excel_path="Datos_Macro1.xlsm")
                save_json(fresh)
                st.session_state.data = fresh
                data = fresh
                st.success("✅ Datos actualizados correctamente")
            except Exception as e:
                st.error(f"⚠ Error al actualizar: {e}\n\nVerifica tu FRED API Key en config.py")
        st.session_state.updating = False
        st.rerun()

# ────────────────────────────────────────────────────────
#  BANK CARDS (selector)
# ────────────────────────────────────────────────────────
cols = st.columns(6)
for i, (k, b) in enumerate(data.items()):
    with cols[i]:
        ov   = overall_sentiment(b.get("sentiment", {}))
        color = BANK_COLORS.get(k, "#fff")
        rates = b.get("rates", [])
        prev_r = rates[-2]["r"] if len(rates) >= 2 else b["currentRate"]
        diff   = round(b["currentRate"] - prev_r, 2)
        diff_color = "#ef4444" if diff > 0 else ("#10b981" if diff < 0 else "#6b7280")
        diff_str   = f"+{diff}%" if diff > 0 else f"{diff}%"
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

# ────────────────────────────────────────────────────────
#  TABS principales
# ────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊  Sentimiento", "📈  Tasas", "🔍  Indicadores"])

# ══════════════════════════════════════════════════════
#  TAB 1 · MATRIZ DE SENTIMIENTO
# ══════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-label">▪ MATRIZ DE SENTIMIENTO — ÚLTIMA REUNIÓN DISPONIBLE</div>', unsafe_allow_html=True)

    # Construir tabla HTML
    banks_list = list(data.keys())
    header = '<div class="ind-row ind-header" style="grid-template-columns:140px repeat(6,1fr)">'
    header += '<span>CATEGORÍA</span>'
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

    # Resumen por banco
    cols2 = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols2[i]:
            ov    = overall_sentiment(b.get("sentiment", {}))
            sent  = b.get("sentiment", {})
            bulls = list(sent.values()).count("BULLISH")
            bears = list(sent.values()).count("BEARISH")
            neuts = list(sent.values()).count("NEUTRO")
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
              <div style="margin-top:8px;font-size:9px;color:#4b5563;font-family:monospace">{b['fullName']}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  TAB 2 · TASAS HISTÓRICAS
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">▪ EVOLUCIÓN HISTÓRICA DE TASAS — TODOS LOS BANCOS CENTRALES</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for k, b in data.items():
        rates = b.get("rates", [])
        if not rates: continue
        dates = [r["date"] for r in rates]
        vals  = [r["r"]    for r in rates]
        fig.add_trace(go.Scatter(
            x=dates, y=vals, name=k, mode="lines+markers",
            line=dict(color=BANK_COLORS.get(k, "#fff"), width=2),
            marker=dict(size=4),
            connectgaps=True,
            hovertemplate=f"<b>{k}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(family="JetBrains Mono", color="#9ca3af", size=10),
        xaxis=dict(gridcolor="#1f2937", showline=False, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#1f2937", showline=False, ticksuffix="%", tickfont=dict(size=9)),
        legend=dict(bgcolor="#0d1117", bordercolor="#1f2937", borderwidth=1,
                    font=dict(family="JetBrains Mono", size=11)),
        margin=dict(l=20, r=20, t=20, b=20), height=360,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Barras de progreso min/max
    st.markdown("**COMPARATIVA TASAS — CICLO ACTUAL**", unsafe_allow_html=False)
    cols3 = st.columns(6)
    for i, (k, b) in enumerate(data.items()):
        with cols3[i]:
            rates = b.get("rates", [])
            if not rates:
                continue
            vals = [r["r"] for r in rates]
            mn, mx = min(vals), max(vals)
            cur = b["currentRate"]
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

# ══════════════════════════════════════════════════════
#  TAB 3 · INDICADORES POR BANCO
# ══════════════════════════════════════════════════════
with tab3:
    sel = st.session_state.selected
    bank = data.get(sel, {})
    color = BANK_COLORS.get(sel, "#fff")

    # Selector de banco
    bank_sel = st.selectbox("Banco Central", list(data.keys()), index=list(data.keys()).index(sel))
    if bank_sel != sel:
        st.session_state.selected = bank_sel
        st.rerun()

    st.markdown(f'<div class="section-label">▪ INDICADORES CLAVE — <span style="color:{color}">{sel}</span> {bank.get("flag","")} {bank.get("fullName","")}</div>', unsafe_allow_html=True)

    # Sentimiento por categoría
    sent = bank.get("sentiment", {})
    cols4 = st.columns(6)
    for i, cat in enumerate(CATEGORIES):
        with cols4[i]:
            s = sent.get(cat, "NEUTRO")
            cfg_bg = {"BULLISH": "rgba(16,185,129,0.12)", "BEARISH": "rgba(239,68,68,0.12)", "NEUTRO": "rgba(245,158,11,0.12)"}
            cfg_bc = {"BULLISH": "#10b98144", "BEARISH": "#ef444444", "NEUTRO": "#f59e0b44"}
            st.markdown(f"""
            <div style="background:{cfg_bg.get(s,'#0d1117')};border:1px solid {cfg_bc.get(s,'#1f2937')};
                        border-radius:8px;padding:12px 8px;text-align:center">
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
        row += f'<span style="font-size:10px;color:{cat_c};font-weight:600;letter-spacing:0.5px">{ind.get("cat","")}</span>'
        row += f'<span style="font-size:12px;color:#d1d5db">{ind.get("name","")}</span>'
        row += f'<span style="text-align:right;font-size:13px;font-weight:600;color:#f9fafb">{ind.get("actual","—")}</span>'
        row += f'<span style="text-align:right;font-size:12px;color:#6b7280">{ind.get("prev","—")}</span>'
        row += f'<span style="text-align:right;font-size:12px;font-weight:700;color:{d_color}">{d_icon} {ind.get("dev","—")}</span>'
        row += '</div>'
        st.markdown(row, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mini-gráfico de tasas del banco seleccionado
    rates = bank.get("rates", [])
    if rates:
        st.markdown(f'<div class="section-label">HISTORIAL DE TASA — {sel}</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=[r["date"] for r in rates], y=[r["r"] for r in rates],
            mode="lines+markers", line=dict(color=color, width=2, shape="hv"),
            marker=dict(size=5, color=color), name=sel,
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
        ))
        fig2.add_hline(y=bank["currentRate"], line_dash="dot", line_color=color, opacity=0.5)
        fig2.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            font=dict(family="JetBrains Mono", color="#9ca3af", size=9),
            xaxis=dict(gridcolor="#1f2937", showline=False),
            yaxis=dict(gridcolor="#1f2937", showline=False, ticksuffix="%"),
            margin=dict(l=20, r=20, t=10, b=20), height=200, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────────────────────────────────
#  FOOTER
# ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:24px;padding-top:16px;border-top:1px solid #1f2937;
            display:flex;justify-content:space-between;align-items:center">
  <span style="font-size:10px;color:#374151;font-family:monospace">
    Fuentes: FRED API · ECB SDW · World Bank · Datos_Macro1.xlsm
  </span>
  <span style="font-size:10px;color:#374151;font-family:monospace">
    MacroVision © 2026
  </span>
</div>
""", unsafe_allow_html=True)
