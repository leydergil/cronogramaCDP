# 🗓️ Aplicación de Turnos 6x2 para Centro de Datos (Colombia)

Esta es una aplicación web desarrollada con [Streamlit](https://streamlit.io/) que permite generar, visualizar y exportar horarios laborales en formato 6x2 (6 días de trabajo y 2 de descanso), cumpliendo la legislación laboral colombiana.

## 🎯 Funcionalidades

- Generación automática de turnos T1 (06:00–14:00), T2 (14:00–22:00) y T3 (22:00–06:00)
- Configuración por mes y año
- Registro de vacaciones por operador
- Detección automática de festivos colombianos
- Modelo rotativo 6x2
- Exportación a Excel con los turnos generados

## 🧩 Tecnologías utilizadas

- Python 3.10+
- Streamlit
- Pandas
- Holidays

## 🚀 Cómo desplegar en Streamlit Cloud

1. Crea una cuenta en [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Conecta tu cuenta de GitHub.
3. Haz clic en "New App" y selecciona este repositorio.
4. En el campo “Main file path”, escribe: `app_turnos.py`
5. Haz clic en **Deploy**

Tu app estará disponible en pocos minutos en una URL como:  
`https://<tu-nombre>.streamlit.app`

## 📝 Notas

- Este proyecto está pensado para centros de datos que operan 24/7.
- El modelo 6x2 implica que el operador rota por los tres turnos haciendo 6 días de trabajo seguidos por 2 de descanso.
- Se está construyendo una versión con validaciones legales más detalladas (horas extra, recargos dominicales y nocturnos).
