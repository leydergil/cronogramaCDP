# app_turnos.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays
import io

st.title("🗓️ App de Turnos - Modelo 6x2")

# --- Inputs ---
year = st.sidebar.number_input("Año", min_value=2024, max_value=2030, value=2025)
month = st.sidebar.selectbox("Mes", list(range(1,13)), format_func=lambda x: datetime(year, x,1).strftime("%B"))
ops = ["Op1","Op2","Op3","Op4"]

# Vacaciones
st.sidebar.subheader("Vacaciones")
vac_dict = {}
for op in ops:
    vac_dict[op] = st.sidebar.date_input(f"{op}: fecha inicio y fin", [])
    
# Festivos
col_holidays = holidays.CountryHoliday('CO', years=[year])

# --- Generar fechas del mes ---
start = datetime(year, month, 1)
end = (start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
dates = pd.date_range(start, end)

# --- Función para turnos ---
def generar_turnos():
    pattern = [
        ['T1','T2','T3','X'],
        ['T1','T2','T3','X'],
        ['T1','T2','T3','X'],
        ['X','T1','T2','T3'],
        ['X','T1','T2','T3'],
        ['T3','X','T1','T2'],
        ['T2','T3','X','T1'],
        ['T2','T3','X','T1']
    ]
    rows = []
    for i, d in enumerate(dates):
        base = pattern[i % len(pattern)].copy()
        for j, op in enumerate(ops):
            # Check vacaciones
            for v in vac_dict[op]:
                if isinstance(v, datetime) and d.date() >= v and d.date() <= v:
                    base[j] = 'V'
        rows.append([d] + base)
    df = pd.DataFrame(rows, columns=["Fecha"] + ops)
    return df

df = generar_turnos()
df["Festivo"] = df["Fecha"].isin(col_holidays)
df["Domingo"] = df["Fecha"].dt.weekday==6

st.subheader("Calendario generado")
st.dataframe(df)

# --- Exportar a Excel ---
def to_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Turnos")
    buffer.seek(0)
    return buffer

st.download_button("📥 Descargar Excel", data=to_excel(df), file_name="turnos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
