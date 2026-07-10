# ─────────────────────────────────────────────────────────
#  MacroVision · agente_ollama.py
#  Agente de IA local con MEMORIA HISTÓRICA
# ─────────────────────────────────────────────────────────

import json
import ollama
import os
from datetime import datetime

ARCHIVO_DATOS = "macro_data.json"
ARCHIVO_MEMORIA = "ai_memory.json"

def cargar_datos_macro():
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró {ARCHIVO_DATOS}.")
        return None

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_memoria(memoria):
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)

def generar_decision_agente(datos_macro, historial):
    if not datos_macro:
        return

    # Extraemos el panorama actual
    resumen_datos = {
        "FED_Sentimiento": datos_macro.get("FED", {}).get("sentiment", {}),
        "FED_Tasa": datos_macro.get("FED", {}).get("currentRate"),
        "BCE_Sentimiento": datos_macro.get("BCE", {}).get("sentiment", {}),
        "BCE_Tasa": datos_macro.get("BCE", {}).get("currentRate")
    }
    contexto_str = json.dumps(resumen_datos, indent=2, ensure_ascii=False)

    # Extraemos las últimas 3 decisiones para darle contexto de su propio pasado
    memoria_reciente = historial[-3:] if len(historial) >= 3 else historial
    contexto_memoria = "\n".join([f"- {m['fecha']}: {m['decision']}" for m in memoria_reciente])
    if not contexto_memoria:
        contexto_memoria = "No hay historial previo. Esta es tu primera decisión."

    prompt_sistema = """
    Eres el Estratega Cuantitativo Jefe de MacroVision. Tu objetivo es emitir una señal de trading 
    direccional para el mercado global de renta variable (SPY).
    
    Reglas de salida:
    1. INICIA con la palabra clave: [COMPRAR], [VENDER] o [ESPERAR].
    2. Proporciona una justificación técnica basada en los datos actuales y tu memoria reciente.
    3. Evalúa si cambiaste de opinión respecto a tus decisiones anteriores.
    """

    mensaje_usuario = f"MEMORIA DE TUS ÚLTIMAS DECISIONES:\n{contexto_memoria}\n\nDATOS MACROECONÓMICOS ACTUALES:\n{contexto_str}\n\nGenera tu señal ahora."

    print("🤖 Agente MacroVision analizando los mercados y consultando su memoria...\n")

    try:
        respuesta = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': mensaje_usuario}
            ]
        )
        
        resultado_ia = respuesta['message']['content']
        
        # Guardamos la nueva decisión en la memoria
        nueva_entrada = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "decision": resultado_ia
        }
        historial.append(nueva_entrada)
        guardar_memoria(historial)
        
        print("==================================================")
        print(" 🎯 NUEVA DECISIÓN REGISTRADA EN MEMORIA")
        print("==================================================")
        print(resultado_ia)
        print("==================================================")

    except Exception as e:
        print(f"⚠️ Error al conectar con Ollama: {e}")

if __name__ == "__main__":
    datos = cargar_datos_macro()
    historial = cargar_memoria()
    
    if datos:
        generar_decision_agente(datos, historial)