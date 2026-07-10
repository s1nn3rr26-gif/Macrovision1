# ─────────────────────────────────────────────────────────
#  MacroVision · config.py
#  Archivo de configuración central
# ─────────────────────────────────────────────────────────

import os

# 1. Tu llave de la FRED
FRED_API_KEY = "5b53bdf5fe99ed21dc2af47440603b37"

if not FRED_API_KEY or FRED_API_KEY == "TU_LLAVE_AQUI":
    print("⚠️ ADVERTENCIA: FRED_API_KEY no está configurada. Las actualizaciones de datos fallarán.")

# 2. FRED series para FED (USA)
FRED_SERIES = {
    "FEDFUNDS":           ("Tasa FED",              "TASAS"),
    "CPIAUCSL":           ("CPI y/y",               "INFLACIÓN"),
    "CPILFESL":           ("Core CPI",              "INFLACIÓN"),
    "A191RL1Q225SBEA":    ("GDP q/q",               "CRECIMIENTO"),
    "PAYEMS":             ("Non-Farm Payrolls",      "EMPLEO"),
    "UNRATE":             ("Unemployment Rate",      "EMPLEO"),
    "RSXFS":              ("Retail Sales",           "CONSUMO"),
    "MANEMP":             ("Manuf Employment",       "ACTIVIDAD"),
    "PERMIT":             ("Building Permits",       "INMOBILIARIO"),
}

# 3. Bancos centrales urls
BANK_RATE_URLS = {
    "BCE": "https://data-api.ecb.europa.eu/service/data/ICP/M.U2.EUR.4F.DP00?format=jsondata&lastNObservations=1",
    "BOE": "https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Jan&FY=2024&TD=31&TM=Dec&TY=2026&VFD=Y&html.x=66&html.y=26&C=BYQ&Filter=N",
}

# 4. World bank
WORLD_BANK_SERIES = {
    "FP.CPI.TOTL.ZG":    ("CPI Inflation y/y",     "INFLACIÓN"),
    "NY.GDP.MKTP.KD.ZG":  ("GDP Growth y/y",        "CRECIMIENTO"),
    "SL.UEM.TOTL.ZS":     ("Unemployment Rate",     "EMPLEO"),
    "NE.CON.TOTL.KD.ZG":  ("Household Consumption", "CONSUMO"),
}

WORLD_BANK_COUNTRIES = {
    "FED":  "US",
    "BCE":  "XC",   
    "BOE":  "GB",
    "BOC":  "CA",
    "RBA":  "AU",
    "RBNZ": "NZ",
}

# 5. Metadata visual
BANK_META = {
    "FED":  {"name": "Federal Reserve",               "flag": "🇺🇸", "currency": "USD", "color": "#3b82f6"},
    "BCE":  {"name": "Banco Central Europeo",          "flag": "🇪🇺", "currency": "EUR", "color": "#8b5cf6"},
    "BOE":  {"name": "Bank of England",                "flag": "🇬🇧", "currency": "GBP", "color": "#ec4899"},
    "BOC":  {"name": "Bank of Canada",                 "flag": "🇨🇦", "currency": "CAD", "color": "#f97316"},
    "RBA":  {"name": "Reserve Bank of Australia",      "flag": "🇦🇺", "currency": "AUD", "color": "#10b981"},
    "RBNZ": {"name": "Reserve Bank of New Zealand",    "flag": "🇳🇿", "currency": "NZD", "color": "#06b6d4"},
}

CATEGORIES = ["INFLACIÓN", "CRECIMIENTO", "EMPLEO", "CONSUMO", "ACTIVIDAD", "INMOBILIARIO"]