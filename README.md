# MacroVision — Setup en 5 minutos

## Lo que tienes en esta carpeta

```
macrovision/
├── app.py            ← Dashboard Streamlit (lo que ves en pantalla)
├── macro_fetch.py    ← Motor de descarga de datos (APIs)
├── config.py         ← Tu configuración y API keys
├── requirements.txt  ← Dependencias Python
├── launch.bat        ← Abre el dashboard (Windows)
├── launch.sh         ← Abre el dashboard (Mac/Linux)
└── Datos_Macro1.xlsm ← Tu Excel (cópialo aquí)
```

---

## PASO 1 — Instala Python (si no lo tienes)

Descarga en: https://www.python.org/downloads/
- **Importante**: marca "Add Python to PATH" durante la instalación

---

## PASO 2 — Consigue tu FRED API Key (gratis, 1 minuto)

1. Ve a: https://fred.stlouisfed.org/docs/api/api_key.html
2. Crea una cuenta gratuita
3. Copia tu API Key (se ve así: `a1b2c3d4e5f6g7h8i9j0...`)

---

## PASO 3 — Pon tu API Key en config.py

Abre `config.py` y cambia esta línea:
```python
FRED_API_KEY = "TU_FRED_API_KEY_AQUI"
```
por:
```python
FRED_API_KEY = "tu_clave_real_aqui"
```

---

## PASO 4 — Copia tu Excel aquí

Pon `Datos_Macro1.xlsm` en la misma carpeta que estos archivos.

---

## PASO 5 — Abre el dashboard

### En Windows:
Doble clic en `launch.bat`

### En Mac/Linux:
```bash
chmod +x launch.sh
./launch.sh
```

### Manualmente:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre automáticamente en: http://localhost:8501

---

## Cómo actualizar los datos

Dentro del dashboard, haz clic en el botón:

```
⟳  ACTUALIZAR DATOS
```

Esto:
1. Descarga tasas FED desde FRED API ✅
2. Descarga tasa BCE desde ECB API ✅
3. Descarga indicadores (CPI, GDP, empleo...) desde World Bank ✅
4. Calcula sentimiento automáticamente ✅
5. Guarda en macro_data.json ✅
6. Actualiza tu Excel ✅
7. El dashboard se refresca ✅

---

## Fuentes de datos (todas gratuitas)

| Banco | Fuente | API Key |
|-------|--------|---------|
| FED   | FRED (St. Louis Fed) | ✅ Sí (gratis) |
| BCE   | ECB Statistical Data Warehouse | ❌ No necesita |
| BOE, BOC, RBA, RBNZ | World Bank API | ❌ No necesita |

---

## Preguntas frecuentes

**¿Se actualiza solo?**
No, tú presionas el botón cuando quieras (antes de revisar mercados).

**¿Funciona sin internet?**
Sí, muestra los últimos datos guardados en macro_data.json.

**¿Puedo automatizarlo diario?**
Sí. En Windows, crea una tarea en el Programador de tareas que ejecute:
`python macro_fetch.py`

En Mac/Linux, agrega al cron:
`0 8 * * * cd /ruta/macrovision && python3 macro_fetch.py`

---

## Soporte

Si falla la actualización:
- Verifica tu API Key en config.py
- Asegúrate de tener internet
- El dashboard igual funciona con los últimos datos guardados
