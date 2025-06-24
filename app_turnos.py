
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


# --- Novedades desde formulario ---
st.sidebar.subheader("📝 Agregar Novedades por Operador")

tipos_novedad = ["Vacaciones", "Permiso", "Incapacidad"]
novedades = []

with st.sidebar.form("form_novedades"):
    operador_sel = st.selectbox("Operador", ops)
    tipo_sel = st.selectbox("Tipo de novedad", tipos_novedad)
    rango_sel = st.date_input("Rango de fechas", [])
    submit = st.form_submit_button("Agregar novedad")

    if submit and isinstance(rango_sel, list) and len(rango_sel) == 2:
        fechas = pd.date_range(rango_sel[0], rango_sel[1]).date
        for f in fechas:
            novedades.append({"Operador": operador_sel, "Fecha": f, "Tipo": tipo_sel})
        st.success(f"Novedad registrada: {tipo_sel} para {operador_sel} ({rango_sel[0]} a {rango_sel[1]})")

# Cargar historial si ya existen
if "novedades_hist" not in st.session_state:
    st.session_state["novedades_hist"] = []

st.session_state["novedades_hist"].extend(novedades)
df_novedades = pd.DataFrame(st.session_state["novedades_hist"], columns=["Operador", "Fecha", "Tipo"])
st.sidebar.dataframe(df_novedades)

# Procesar vacaciones desde novedades
vac_dict = {op: [] for op in ops}
for op in ops:
    vacaciones = df_novedades[(df_novedades["Operador"] == op) & (df_novedades["Tipo"] == "Vacaciones")]
    vac_dict[op] = vacaciones["Fecha"].tolist()

st.sidebar.subheader("Vacaciones (rango por operador)")
vac_dict = {}
for op in ops:
    vac_range = st.sidebar.date_input(f"{op}: vacaciones", [], key=op)
    if isinstance(vac_range, list) and len(vac_range) == 2:
        vac_dict[op] = pd.date_range(vac_range[0], vac_range[1]).date
    else:
        vac_dict[op] = []

# Festivos
col_holidays = holidays.CountryHoliday('CO', years=[year])

# Generar fechas del mes
start = datetime(year, month, 1)
end = (start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
dates = pd.date_range(start, end)

# Patrón 6x2 por operador con rotación T1 → T2 → T3
turnos = ['T1', 'T2', 'T3']
ciclo = ['T1']*6 + ['X']*2  # 8 días

def generar_turnos_personalizados():
    df = pd.DataFrame({'Fecha': dates})
    for op_index, op in enumerate(ops):
        op_turnos = []
        idx = 0
        turno_idx = op_index % len(turnos)
        while len(op_turnos) < len(dates):
            bloque = [turnos[turno_idx]] * 6 + ['X'] * 2
            op_turnos.extend(bloque)
            turno_idx = (turno_idx + 1) % len(turnos)
        op_turnos = op_turnos[:len(dates)]
        # aplicar vacaciones
        turnos_final = []
        for i, d in enumerate(dates):
            if d.date() in vac_dict[op]:
                turnos_final.append('V')
            else:
                turnos_final.append(op_turnos[i])
        df[op] = turnos_final
    return df

df = generar_turnos_personalizados()
df["Festivo"] = df["Fecha"].apply(lambda d: d in col_holidays)
df["Domingo"] = df["Fecha"].dt.weekday == 6

st.subheader("📅 Calendario de turnos 6x2")
st.dataframe(df)

# Exportar a Excel
def to_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Turnos")
    buffer.seek(0)
    return buffer

st.download_button("📥 Descargar Excel", data=to_excel(df), file_name="turnos_6x2.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# Calcular resumen de horas por operador por semana calendario (lunes a domingo)
st.subheader("📊 Resumen semanal de horas")

# Definir duración por tipo de turno
duraciones = {'T1': 8, 'T2': 8, 'T3': 8, 'X': 0, 'V': 0}
nocturno_turno = 'T3'

df_horas = df.copy()

# Marcar semana ISO real (lunes a domingo)
df_horas['Semana'] = df_horas['Fecha'].dt.to_period("W").apply(lambda r: r.start_time)

# Calcular horas por día por operador
for op in ops:
    df_horas[op + '_Horas'] = df_horas[op].map(duraciones)
    df_horas[op + '_Nocturnas'] = df_horas[op].apply(lambda x: 8 if x == nocturno_turno else 0)
    df_horas[op + '_Dominicales'] = df_horas.apply(lambda row: 8 if row['Domingo'] and row[op] in ['T1','T2','T3'] else 0, axis=1)
    df_horas[op + '_Dias'] = df_horas[op].apply(lambda x: 1 if x in ['T1','T2','T3'] else 0)

# Agrupar por semana
resumen = df_horas.groupby('Semana').agg({
    **{op + '_Horas': 'sum' for op in ops},
    **{op + '_Nocturnas': 'sum' for op in ops},
    **{op + '_Dominicales': 'sum' for op in ops},
    **{op + '_Dias': 'sum' for op in ops}
}).reset_index()

# Calcular horas extras
for op in ops:
    resumen[op + '_Extras'] = resumen[op + '_Horas'].apply(lambda x: max(0, x - 46))

st.dataframe(resumen)

# Descargar con resumen en Excel
def to_excel_full(df_base, df_summary):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_base.to_excel(writer, index=False, sheet_name="Turnos")
        df_summary.to_excel(writer, index=False, sheet_name="Resumen")
    buffer.seek(0)
    return buffer

st.download_button("📥 Descargar Excel con resumen", data=to_excel_full(df, resumen), file_name="turnos_6x2_con_resumen.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
