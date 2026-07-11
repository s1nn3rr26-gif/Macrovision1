# ─────────────────────────────────────────────────────────
#  Agente_Ollama.py - VERSIÓN LOCAL CON OLLAMA
#  Estratega Jefe con Narrativa + Reglas de Trading
#  Usa Ollama local (gratuito, sin límites)
# ─────────────────────────────────────────────────────────

import os
import json
import datetime
import yfinance as yf
import ollama
import warnings
warnings.filterwarnings("ignore")

# ── CONFIGURACIÓN ──────────────────────────────────────────
# Modelo local de Ollama (cambia si usas otro, ej: "mistral", "phi3", "llama3.2")
MODELO_OLLAMA = "llama3.2"

# ── FUNCIONES DE CARGA DE CONTEXTO ──────────────────────
def cargar_contexto():
    """Carga narrativa.txt y reglas.json si existen."""
    contexto = {"narrativa": None, "reglas": None}
    
    try:
        with open("narrativa.txt", "r", encoding="utf-8") as f:
            contexto["narrativa"] = f.read().strip()
            print("📖 Narrativa cargada correctamente.")
    except FileNotFoundError:
        print("ℹ️ No se encontró narrativa.txt.")
    except Exception as e:
        print(f"⚠️ Error al leer narrativa.txt: {e}")
    
    try:
        with open("reglas.json", "r", encoding="utf-8") as f:
            contexto["reglas"] = json.load(f)
            print("📋 Reglas de trading cargadas correctamente.")
    except FileNotFoundError:
        print("ℹ️ No se encontró reglas.json.")
    except Exception as e:
        print(f"⚠️ Error al leer reglas.json: {e}")
    
    return contexto

# ── OBTENER DATOS MACRO ──────────────────────────────────
def get_macro_data():
    """Obtiene datos actuales de DXY, VIX, SP500, Nasdaq, Oro, Bono 10Y, WTI, BTC, Cobre."""
    try:
        tickers = {
            'dxy': 'DX-Y.NYB',
            'vix': '^VIX',
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'oro': 'GC=F',
            'bond10y': '^TNX',
            'wti': 'CL=F',
            'btc': 'BTC-USD',
            'copper': 'HG=F'
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
    except Exception as e:
        print(f"❌ Error obteniendo datos macro: {e}")
        return None

# ── GENERAR INFORME CON OLLAMA ──────────────────────────
def generar_informe(macro_data, contexto):
    """Genera el informe ejecutivo semanal usando Ollama."""
    
    if not macro_data:
        return {
            "error": "No se pudieron obtener datos macro.",
            "informe": "Sin datos disponibles.",
            "confianza": 0
        }

    # 1. Contexto de datos macro
    contexto_macro = f"""
    DATOS MACRO ACTUALES:
    - DXY: {macro_data['dxy']['price']:.2f} (Cambio: {macro_data['dxy']['change_pct']:.2f}%)
    - VIX: {macro_data['vix']['price']:.2f} (Cambio: {macro_data['vix']['change_pct']:.2f}%)
    - SP500: {macro_data['sp500']['price']:.2f} (Cambio: {macro_data['sp500']['change_pct']:.2f}%)
    - Nasdaq: {macro_data['nasdaq']['price']:.2f} (Cambio: {macro_data['nasdaq']['change_pct']:.2f}%)
    - Oro: {macro_data['oro']['price']:.2f} (Cambio: {macro_data['oro']['change_pct']:.2f}%)
    - Bono 10Y: {macro_data['bond10y']['price']:.2f}% (Cambio: {macro_data['bond10y']['change_pct']:.2f}%)
    - WTI: {macro_data['wti']['price']:.2f} (Cambio: {macro_data['wti']['change_pct']:.2f}%)
    - Bitcoin: {macro_data['btc']['price']:.2f} (Cambio: {macro_data['btc']['change_pct']:.2f}%)
    - Cobre: {macro_data['copper']['price']:.2f} (Cambio: {macro_data['copper']['change_pct']:.2f}%)
    """

    # 2. Contexto de narrativa
    contexto_narrativa = ""
    if contexto.get("narrativa"):
        contexto_narrativa = f"""
        CONTEXTO HISTÓRICO Y NARRATIVA DE MERCADO (de narrativa.txt):
        {contexto["narrativa"]}
        """

    # 3. Contexto de reglas
    contexto_reglas = ""
    if contexto.get("reglas"):
        reglas_text = json.dumps(contexto["reglas"], ensure_ascii=False, indent=2)
        contexto_reglas = f"""
        REGLAS DE FILTRO DE MERCADO Y ASIGNACIÓN (de reglas.json):
        {reglas_text}

        INSTRUCCIÓN ADICIONAL: Evalúa si alguna de estas reglas se está cumpliendo con los datos macro actuales. Menciona en el análisis si hay activación de Risk-Off o Risk-On según estas reglas, y sugiere asignaciones de cartera alineadas con el protocolo.
        """

    # 4. Prompt completo
    prompt = f"""
    {contexto_macro}
    {contexto_narrativa}
    {contexto_reglas}

    Actúa como el **estratega jefe de un fondo de inversión global multiactivo**. Tu experiencia combina macroeconomía, geopolítica, análisis de flujos de capital y psicología de mercado.

    **INSTRUCCIONES IMPORTANTES:**
    1. Utiliza los **datos macro actuales** para contextualizar el momento presente.
    2. Utiliza la **narrativa histórica** (si está disponible) para enriquecer el análisis.
    3. Evalúa explícitamente las **reglas de trading** (si están disponibles) y menciona si el régimen actual es Risk-On o Risk-Off según tus propios criterios.
    4. Genera un **informe ejecutivo semanal** que sintetice los eventos clave y señale oportunidades de trading/inversión para la semana próxima.
    5. El informe debe ser **esencial, accionable y libre de verborrea**.

    **ESTRUCTURA OBLIGATORIA DEL INFORME:**

    **SEMANA [Número] - RESUMEN EJECUTIVO DE MERCADOS**

    **📌 Contexto Global (Macro/Geo/Sentimiento):**
    [Máximo 4 oraciones por sección:
    1. Macroeconómico: Los 2-3 datos/declaraciones de bancos centrales más impactantes y su efecto en tasas.
    2. Geopolítico: El factor principal que influye en el apetito/aversión al riesgo.
    3. Sentimiento de Mercado: Define el estado de ánimo (ej: "Aversión al Riesgo Moderada" o "Optimismo Cauteloso") y justifícalo brevemente.]

    **📈 Análisis por Activo (Forex, Crypto, Comm., Sectores):**
    [Máximo 1 párrafo por activo. Enfócate en tendencia, evento clave y nivel técnico crucial (soporte/resistencia).]

    **🎯 Radar de Oportunidades (Próxima Semana):**
    [Lista 3-5 configuraciones con este formato exacto:
    - **Activo/Configuración:** [Nombre]
    - **Catalizador/Tesis:** [Máx. 2 líneas]
    - **Nivel Clave:** [Entrada, stop-loss, objetivo]
    - **Tipo de Oportunidad:** [Divergencia, Evento, Estacionalidad, Small Cap, Otro]
    - **Nivel de Riesgo:** [Alto / Medio / Bajo]]

    **📅 Calendario de Eventos Críticos:**
    [Lista cronológica (Lunes a Viernes) de 3-5 eventos/ anuncios económicos más importantes de la próxima semana, con hora (GMT) y activo(s) afectado(s).]

    **Nota de responsabilidad final:** *"Este análisis es para fines informativos y educativos. No constituye asesoramiento de inversión. Los mercados financieros son volátiles. Realice su propia investigación (DYOR) y considere su situación financiera individual antes de operar."*
    """

    try:
        # Llamada a Ollama local
        response = ollama.chat(
            model=MODELO_OLLAMA,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response['message']['content'].strip()
        
        return {
            "informe": text,
            "confianza": 85,
            "fecha": datetime.datetime.now().isoformat(),
            "narrativa_usada": contexto.get("narrativa") is not None,
            "reglas_usadas": contexto.get("reglas") is not None,
            "modelo_usado": MODELO_OLLAMA
        }
    except Exception as e:
        return {
            "error": str(e),
            "informe": f"Error al generar el informe con Ollama. Asegúrate de que el modelo '{MODELO_OLLAMA}' esté descargado (ollama pull {MODELO_OLLAMA}) y que el servidor esté corriendo (ollama serve).",
            "confianza": 0
        }

# ── GUARDAR EN ARCHIVO ─────────────────────────────────────
def guardar_informe(informe):
    archivo = "ai_memory.json"
    historial = []
    
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                historial = json.load(f)
            except:
                historial = []
    
    if "error" in informe and informe["error"]:
        entrada = {
            "fecha": datetime.datetime.now().isoformat(),
            "decision": f"⚠️ Error: {informe['error']}",
            "fuente": f"Ollama ({MODELO_OLLAMA})",
            "tipo": "error"
        }
    else:
        entrada = {
            "fecha": informe.get("fecha", datetime.datetime.now().isoformat()),
            "decision": informe.get("informe", "Sin contenido"),
            "confianza": informe.get("confianza", 0),
            "fuente": f"Ollama ({MODELO_OLLAMA}) - Estratega Jefe",
            "tipo": "informe_semanal",
            "narrativa_usada": informe.get("narrativa_usada", False),
            "reglas_usadas": informe.get("reglas_usadas", False),
            "modelo_usado": informe.get("modelo_usado", MODELO_OLLAMA)
        }
    
    historial.append(entrada)
    
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    
    print("✅ Informe guardado en ai_memory.json")
    print("📋 Resumen del informe:")
    print("-" * 80)
    if len(entrada["decision"]) > 500:
        print(entrada["decision"][:500] + "...\n")
    else:
        print(entrada["decision"])
    print("-" * 80)
    
    if entrada.get("narrativa_usada", False):
        print("📖 El informe ha integrado la narrativa histórica de narrativa.txt")
    if entrada.get("reglas_usadas", False):
        print("📋 El informe ha integrado las reglas de trading de reglas.json")
    print(f"🧠 Modelo utilizado: {entrada.get('modelo_usado', MODELO_OLLAMA)}")

# ── EJECUCIÓN PRINCIPAL ──────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AGENTE IA - ESTRATEGA JEFE (OLLAMA LOCAL)")
    print("📊 Generando informe ejecutivo semanal")
    print("=" * 60)
    
    # Verificar que Ollama está corriendo (opcional)
    try:
        ollama.list()
    except Exception:
        print("❌ No se pudo conectar con Ollama. Asegúrate de que esté corriendo (ollama serve).")
        exit(1)
    
    # Cargar contexto
    contexto = cargar_contexto()
    
    # Obtener datos macro
    macro_data = get_macro_data()
    if macro_data:
        print("✅ Datos macro obtenidos correctamente.")
    else:
        print("❌ No se pudieron obtener datos macro. Verifica la conexión a internet.")
        guardar_informe({
            "error": "Sin datos macro disponibles",
            "informe": "No se pudieron obtener datos macro para generar el informe.",
            "confianza": 0
        })
        exit(1)
    
    print(f"🧠 Generando análisis con {MODELO_OLLAMA}...")
    informe = generar_informe(macro_data, contexto)
    guardar_informe(informe)
    
    print("\n✅ Proceso completado. Puedes ver el informe en el dashboard de MacroVision.")
    print("=" * 60)