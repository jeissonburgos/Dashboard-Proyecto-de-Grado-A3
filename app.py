import os
import re
import time
import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import statsmodels.api as sm
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GAMMA_KEY = os.getenv("GAMMA_API_KEY", "").strip()

st.set_page_config(
    page_title="Dashboard - Acerías Paz del Río",
    page_icon="🟢",
    layout="wide"
)

# --- ESTILOS VISUALES GERENCIALES ---
st.markdown("""
<style>
    .banner-control {
        border: 2px dashed #059669;
        border-radius: 12px;
        padding: 16px 22px;
        background: #F0FDF4;
        margin-bottom: 20px;
    }
    .traffic-lights { font-size: 26px; vertical-align: middle; margin-right: 12px; }
    .banner-title { font-size: 21px; font-weight: 800; color: #064E3B; vertical-align: middle; }
    .banner-sub { color: #047857; font-size: 13px; margin-top: 4px; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 700;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado formal del proyecto
st.markdown("""
<div class="banner-control">
    <span class="traffic-lights">🟢 🟡 🔴</span>
    <span class="banner-title">DASHBOARD ACTIVIDAD A3  | CASO DE ESTUDIO ACERÍAS PAZ DEL RÍO</span>
    <div class="banner-sub">
        PRESENTACIÓN DE RESULTADOS
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# BASES DE DATOS MAESTRAS (LOS 5 CORTES REALES)
# ==============================================================================

# 1. EVM (Curva S)
meses_evm = ["Ago/25", "Sep/25", "Oct/25", "Nov/25", "Dic/25", "Ene/26", "Feb/26", "Mar/26", "Abr/26", "May/26", "Jun/26", "Jul/26", "Ago/26"]
pv_master = [25283816, 51725607, 82854179, 94844562, 94844562, 94844562, 111787831, 134963523, 155756514, 165968761, 165968761, 165968761, 241137901]
ev_master = [35011392, 65119963, 89186467, 99944731, 99944731, 99944731, 118127917, 145825232, 157397418, 165288145, 165288145, 165288145, 204378020]
ac_master = [28215140, 60301283, 99813743, 111572412, 111572412, 111572412, 154299168, 175649504, 182580030, 183045899, 183045899, 183045899, 239549957]

datos_cortes_evm = {
    "Corte 1 (09/03/2026)": {"mes": "Mar/26", "idx": 7, "pv": 117237047, "ev": 137140459, "ac": 167231197, "spi": 1.17, "cpi": 0.82, "vme": 56030654, "vte": 58, "cal_global": 75.3},
    "Corte 2 (09/04/2026)": {"mes": "Abr/26", "idx": 8, "pv": 141142775, "ev": 144592668, "ac": 181236304, "spi": 1.02, "cpi": 0.80, "vme": 65017971, "vte": 67, "cal_global": 83.0},
    "Corte 3 (09/05/2026)": {"mes": "May/26", "idx": 9, "pv": 160991512, "ev": 160786090, "ac": 181515230, "spi": 1.00, "cpi": 0.89, "vme": 65309331, "vte": 67, "cal_global": 91.6},
    "Corte 4 (25/05/2026)": {"mes": "May/26", "idx": 9, "pv": 165968761, "ev": 165968761, "ac": 183045899, "spi": 1.00, "cpi": 0.91, "vme": 65309331, "vte": 67, "cal_global": 100.0},
    "Corte 5 (24/08/2026)": {"mes": "Ago/26", "idx": 12, "pv": 241137901, "ev": 204378020, "ac": 239549957, "spi": 0.85, "cpi": 0.85, "vme": 74845748, "vte": 77, "cal_global": 86.0},
    "Comparativa Global": {"mes": "Ago/26", "idx": 12, "pv": 241137901, "ev": 204378020, "ac": 239549957, "spi": 0.85, "cpi": 0.85, "vme": 74845748, "vte": 77, "cal_global": 86.0}
}

# 2. EDT (Estructura de Desglose del Trabajo)
edt_master = [
    {"Fase": "Fase 1: Inicio y Planeación", "Codigo": "1.0", "Nombre": "Fase 1 Consolidada", "Pto": 114050915, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 1: Inicio y Planeación", "Codigo": "1.1", "Nombre": "Búsqueda y recolección de información", "Pto": 14200370, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 1: Inicio y Planeación", "Codigo": "1.2", "Nombre": "Estructura y planteamiento metodológico", "Pto": 9723247, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 1: Inicio y Planeación", "Codigo": "1.6", "Nombre": "Project Charter formalizado", "Pto": 12290474, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 1: Inicio y Planeación", "Codigo": "1.7", "Nombre": "Línea base y planes de dirección", "Pto": 47254472, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.0", "Nombre": "Fase 2 Consolidada", "Pto": 68994984, "C1": 53, "C2": 62, "C3": 83, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.1", "Nombre": "Diagnóstico inicial de trituración", "Pto": 15457382, "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.2", "Nombre": "Análisis de variables operativas", "Pto": 11042781, "C1": 50, "C2": 80, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.3", "Nombre": "Identificación de causas raíz (CAL 08)", "Pto": 8834225, "C1": 53, "C2": 95, "C3": 100, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.4", "Nombre": "Cuantificación de línea base operativa/financiera", "Pto": 15747038, "C1": 0, "C2": 35, "C3": 91, "C4": 100, "C5": 100},
    {"Fase": "Fase 2: Diagnóstico y Estrategia", "Codigo": "2.5", "Nombre": "Diseño de estrategia de reprocesamiento", "Pto": 17913558, "C1": 0, "C2": 0, "C3": 25, "C4": 100, "C5": 100},
    {"Fase": "Fase 3: Piloto y Cierre", "Codigo": "3.0", "Nombre": "Fase 3 Consolidada", "Pto": 56504058, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 22},
    {"Fase": "Fase 3: Piloto y Cierre", "Codigo": "3.1", "Nombre": "Estructuración y preparación de prueba piloto", "Pto": 34520114, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 30},
    {"Fase": "Fase 3: Piloto y Cierre", "Codigo": "3.2", "Nombre": "Ejecución de piloto y medición de reducción", "Pto": 11200000, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0},
    {"Fase": "Fase 3: Piloto y Cierre", "Codigo": "3.3", "Nombre": "Evaluación de rentabilidad (ROI) y caso de negocio", "Pto": 5600000, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0},
    {"Fase": "Fase 3: Piloto y Cierre", "Codigo": "3.4", "Nombre": "Lecciones aprendidas y cierre del proyecto", "Pto": 5183944, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}
]
df_edt_master = pd.DataFrame(edt_master)

# 3. RIESGOS (20 Riesgos con evolución de Probabilidad e Impacto)
riesgos_db = [
    {"ID": "R1", "Nombre": "Diagnóstico erróneo muestra mineral", "P_C1": 0.25, "I_C1": 3.5, "P_C5": 0.03, "I_C5": 1.0, "Estado_C5": "Cerrado 🟢"},
    {"ID": "R2", "Nombre": "Desgaste acelerado en equipos", "P_C1": 0.35, "I_C1": 2.3, "P_C5": 0.45, "I_C5": 2.7, "Estado_C5": "Monitoreado 🟡"},
    {"ID": "R3", "Nombre": "Oportunidad optimización finos/gruesos", "P_C1": 0.05, "I_C1": 3.5, "P_C5": 0.03, "I_C5": 1.2, "Estado_C5": "Cerrado 🟢"},
    {"ID": "R4", "Nombre": "Falla técnica detiene planta en piloto", "P_C1": 0.35, "I_C1": 2.7, "P_C5": 0.45, "I_C5": 3.0, "Estado_C5": "Monitoreado 🟡"},
    {"ID": "R5", "Nombre": "Piloto no alcanza reducción 3%", "P_C1": 0.40, "I_C1": 3.1, "P_C5": 0.20, "I_C5": 4.7, "Estado_C5": "Monitoreado 🟡"},
    {"ID": "R8", "Nombre": "Humedad/finos atascan equipos", "P_C1": 0.35, "I_C1": 2.0, "P_C5": 0.70, "I_C5": 2.4, "Estado_C5": "Crítico 🔴"},
    {"ID": "R10", "Nombre": "Planta reasigna personal clave", "P_C1": 0.56, "I_C1": 4.1, "P_C5": 0.45, "I_C5": 4.0, "Estado_C5": "Materializado 🔴"},
    {"ID": "R11", "Nombre": "Cruce obligaciones equipo maestría", "P_C1": 0.70, "I_C1": 3.7, "P_C5": 0.70, "I_C5": 5.0, "Estado_C5": "Materializado 🔴"},
    {"ID": "R12", "Nombre": "Conflicto expectativas ROI vs Técnico", "P_C1": 0.20, "I_C1": 2.7, "P_C5": 0.50, "I_C5": 3.8, "Estado_C5": "Monitoreado 🟡"},
    {"ID": "R14", "Nombre": "Retraso permisos detiene piloto", "P_C1": 0.31, "I_C1": 3.6, "P_C5": 0.85, "I_C5": 3.7, "Estado_C5": "Crítico 🔴"},
    {"ID": "R19", "Nombre": "Lluvias intensas saturan mineral", "P_C1": 0.31, "I_C1": 3.2, "P_C5": 0.62, "I_C5": 3.5, "Estado_C5": "Crítico 🔴"},
    {"ID": "R20", "Nombre": "Paro laboral detiene proyecto", "P_C1": 0.18, "I_C1": 4.0, "P_C5": 0.10, "I_C5": 3.0, "Estado_C5": "Latente 🟢"}
]
df_riesgos_master = pd.DataFrame(riesgos_db)

# 4. CALIDAD (CAL 01 a CAL 15)
calidad_master = [
    {"ID": "CAL 01", "Requisito": "Disponibilidad de información técnica", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 02", "Requisito": "Cumplimiento estándar PMBOK", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 03", "Requisito": "Normativas HSE y ambientales", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 04", "Requisito": "Clasificación integral de Stakeholders", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 05", "Requisito": "Síntesis visual e infografía ejecutiva", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 06", "Requisito": "Project Charter formalizado", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 07", "Requisito": "Planes de gestión (Líneas Base)", "C1": 100, "C2": 100, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 08", "Requisito": "Diagnóstico validado de causas raíz", "C1": 53, "C2": 95, "C3": 100, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 09", "Requisito": "Línea base operativa y financiera", "C1": 0, "C2": 35, "C3": 91, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 10", "Requisito": "Viabilidad técnica del diseño", "C1": 0, "C2": 0, "C3": 25, "C4": 100, "C5": 100, "Estado": "Cumple Satisfactoriamente 🟢"},
    {"ID": "CAL 11", "Requisito": "Estructuración técnica prueba piloto", "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 30, "Estado": "No Cumple (Observaciones) 🔴"},
    {"ID": "CAL 12", "Requisito": "Meta de reducción mínima 3%", "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "Estado": "No Iniciado ⚪"},
    {"ID": "CAL 13", "Requisito": "Evaluación económica y ROI", "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "Estado": "No Iniciado ⚪"},
    {"ID": "CAL 14", "Requisito": "Documentación lecciones aprendidas", "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "Estado": "No Iniciado ⚪"},
    {"ID": "CAL 15", "Requisito": "Cierre formal y sustentación", "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "Estado": "No Iniciado ⚪"}
]
df_calidad_master = pd.DataFrame(calidad_master)

# Calificación de cumplimiento y observaciones REALES por corte, tal como
# aparecen en "Calidad todos los cortes.pdf" (Matriz MAT-CAL-001). Solo CAL08
# a CAL11 cambian de calificación entre cortes; el resto queda fijo en su
# "Estado" (Cumple Satisfactoriamente o No Iniciado) durante toda la ventana.
CALIFICACIONES_REALES = {
    ("CAL 08", "C1"): "Cumple con Observaciones 🟡", ("CAL 08", "C2"): "Cumple Satisfactoriamente 🟢",
    ("CAL 08", "C3"): "Cumple Satisfactoriamente 🟢", ("CAL 08", "C4"): "Cumple Satisfactoriamente 🟢",
    ("CAL 08", "C5"): "Cumple Satisfactoriamente 🟢",
    ("CAL 09", "C1"): "No Iniciado ⚪", ("CAL 09", "C2"): "No Cumple 🔴",
    ("CAL 09", "C3"): "Cumple con Observaciones 🟡", ("CAL 09", "C4"): "Cumple Satisfactoriamente 🟢",
    ("CAL 09", "C5"): "Cumple Satisfactoriamente 🟢",
    ("CAL 10", "C1"): "No Iniciado ⚪", ("CAL 10", "C2"): "No Iniciado ⚪",
    ("CAL 10", "C3"): "No Cumple 🔴", ("CAL 10", "C4"): "Cumple Satisfactoriamente 🟢",
    ("CAL 10", "C5"): "Cumple Satisfactoriamente 🟢",
    ("CAL 11", "C1"): "No Iniciado ⚪", ("CAL 11", "C2"): "No Iniciado ⚪",
    ("CAL 11", "C3"): "No Iniciado ⚪", ("CAL 11", "C4"): "No Iniciado ⚪",
    ("CAL 11", "C5"): "No Cumple 🔴",
}

OBSERVACIONES_REALES = {
    ("CAL 08", "C1"): "Avance con estado 'Aprobado con observaciones'. Conforme al plan de acción de calidad, el equipo debe agendar una reunión con el equipo técnico para identificar y corregir las brechas metodológicas.",
    ("CAL 08", "C2"): "El diagnóstico técnico está finalizado y cumple con todos los criterios de calidad. El 5% restante corresponde a la recolección de la firma de aceptación del Sponsor. No se requieren retrabajos técnicos.",
    ("CAL 08", "C3"): "Hito técnico finalizado con éxito. El diagnóstico de causas raíz fue aprobado formalmente por el Sponsor, cerrando satisfactoriamente las brechas metodológicas identificadas en cortes anteriores.",
    ("CAL 09", "C2"): "Durante la revisión financiera parcial del avance se identificaron desviaciones en los costos asociados a la generación de partícula intermedia. Se activa plan de acción para recalcular la línea base financiera.",
    ("CAL 09", "C3"): "Se califica 'Con Observaciones': el cálculo de KPIs está finalizado, pero queda pendiente una conciliación final de un rubro de costos con el Sponsor Principal antes de la aprobación definitiva.",
    ("CAL 09", "C4"): "Entregable finalizado: se ejecutó con éxito la conciliación del rubro de costos pendiente. La línea base operativa y financiera obtuvo su aprobación formal y definitiva.",
    ("CAL 10", "C3"): "Se califica 'No Cumple': la revisión preliminar detectó que las modificaciones propuestas no responden completamente a las variables operativas validadas en el diagnóstico de causas raíz (CAL 08). Se activa plan de contingencia para pivotar el diseño.",
    ("CAL 10", "C4"): "Entregable finalizado: el plan de contingencia técnico se ejecutó exitosamente y el nuevo diseño obtuvo la aceptación formal de viabilidad técnica por parte del Sponsor.",
    ("CAL 11", "C5"): "Avance parcial del 30% en la estructuración preliminar del plan de prueba piloto. Se califica 'No Cumple' por observaciones sobre la disponibilidad de ventanas operativas de trituración y el ajuste de protocolos HSE.",
}

# ==============================================================================
# CONTROL DE CORTES (compartido entre las 4 pestañas de seguimiento)
# ==============================================================================
lista_cortes = list(datos_cortes_evm.keys())
KEYS_SELECTOR_CORTE = ["corte_sel_costos", "corte_sel_edt", "corte_sel_riesgos", "corte_sel_calidad"]
if "corte_global" not in st.session_state:
    st.session_state.corte_global = lista_cortes[4]  # Corte 5 por defecto


def _sync_corte_global(origen_key):
    # Un selectbox con "key" recuerda su propio valor en session_state entre
    # reruns e ignora el parámetro "index" una vez creado, así que hay que
    # sobrescribir explícitamente el session_state de los OTROS selectores
    # para que de verdad reflejen el cambio (no solo corte_global).
    nuevo_valor = st.session_state[origen_key]
    st.session_state.corte_global = nuevo_valor
    for k in KEYS_SELECTOR_CORTE:
        if k != origen_key:
            st.session_state[k] = nuevo_valor


def _panel_control_cortes(origen_key, contexto="costos"):
    """Panel de selección de corte, repetido en cada pestaña de seguimiento y
    sincronizado vía session_state. El resumen de 4 columnas cambia según la
    pestaña: cada una muestra sus propios indicadores en vez de repetir
    BAC/VME/VTE/Salud (eso es exclusivo de Costos)."""
    st.markdown("##### 🎛️ Control de Cortes")
    col_sel, col_a, col_b, col_c, col_d = st.columns([1.6, 1, 1, 1, 1])
    with col_sel:
        st.selectbox("Seleccionar Hito de Control:", lista_cortes,
                     index=lista_cortes.index(st.session_state.corte_global),
                     key=origen_key, on_change=_sync_corte_global, args=(origen_key,))

    if contexto == "costos":
        with col_a:
            st.markdown(f"**Presupuesto (BAC):**  \n`${BAC/1e6:.2f} M COP`")
        with col_b:
            st.markdown(f"**Reserva Contingencia (VME):**  \n`${VME_val/1e6:.2f} M`")
        with col_c:
            st.markdown(f"**Reserva Tiempo (VTE):**  \n`{VTE_val} Días`")
        with col_d:
            st.markdown(f"**Salud Contractual:**  \n{'🟢 En meta' if (SPI>=1.0 and CPI>=0.95) else '🟡 Alerta' if (SPI>=0.9 or CPI>=0.85) else '🔴 Crítico'}")

    elif contexto == "edt":
        df_fases_edt = df_edt_master[df_edt_master["Codigo"].isin(["1.0", "2.0", "3.0"])]
        presupuesto_total_edt = df_fases_edt["Pto"].sum()
        avance_ponderado = (df_fases_edt["Pto"] * df_fases_edt[col_activa]).sum() / presupuesto_total_edt
        df_paquetes_edt = df_edt_master[~df_edt_master["Codigo"].isin(["1.0", "2.0", "3.0"])]
        completados = (df_paquetes_edt[col_activa] == 100).sum()
        total_paquetes = len(df_paquetes_edt)
        with col_a:
            st.markdown(f"**Presupuesto Total (EDT):**  \n`${presupuesto_total_edt/1e6:.2f} M COP`")
        with col_b:
            st.markdown(f"**Avance Físico Ponderado:**  \n`{avance_ponderado:.1f}%`")
        with col_c:
            st.markdown(f"**Paquetes Finalizados:**  \n`{completados} / {total_paquetes}`")
        with col_d:
            st.markdown(f"**Estado General:**  \n{'🟢 En meta' if avance_ponderado >= 95 else '🟡 En curso' if avance_ponderado > 0 else '🔴 Sin iniciar'}")

    elif contexto == "riesgos":
        col_p_panel = "P_C5" if col_activa == "C5" else "P_C1"
        col_i_panel = "I_C5" if col_activa == "C5" else "I_C1"
        total_riesgos = len(df_riesgos_master)
        riesgos_criticos = df_riesgos_master["Estado_C5"].str.contains("Crítico|Materializado", regex=True).sum()
        exposicion_prom = (df_riesgos_master[col_p_panel] * df_riesgos_master[col_i_panel]).mean()
        with col_a:
            st.markdown(f"**Reserva Contingencia (VME):**  \n`${VME_val/1e6:.2f} M`")
        with col_b:
            st.markdown(f"**Reserva Tiempo (VTE):**  \n`{VTE_val} Días`")
        with col_c:
            st.markdown(f"**Riesgos Críticos/Materializados:**  \n`{riesgos_criticos} / {total_riesgos}`")
        with col_d:
            st.markdown(f"**Exposición Promedio (P×I):**  \n`{exposicion_prom:.2f}`")

    # contexto == "calidad": sin columnas de resumen aquí; la pestaña de
    # Calidad ya muestra estos mismos indicadores en grande (fila de KPIs +
    # semáforo), así que repetirlos aquí en chico sería redundante.

    st.markdown("---")


corte_seleccionado = st.session_state.corte_global
datos_corte = datos_cortes_evm[corte_seleccionado]
idx_corte = datos_corte["idx"]
BAC = 241137901.0
PV = float(datos_corte["pv"])
EV = float(datos_corte["ev"])
AC = float(datos_corte["ac"])
SPI = datos_corte["spi"]
CPI = datos_corte["cpi"]
SV = EV - PV
CV = EV - AC
EAC = BAC / CPI if CPI > 0 else BAC
ETC = EAC - AC
VAC = BAC - EAC
VME_val = datos_corte["vme"]
VTE_val = datos_corte["vte"]
col_corte_map = {"Corte 1 (09/03/2026)": "C1", "Corte 2 (09/04/2026)": "C2", "Corte 3 (09/05/2026)": "C3", "Corte 4 (25/05/2026)": "C4", "Corte 5 (24/08/2026)": "C5", "Comparativa Global": "C5"}
col_activa = col_corte_map[corte_seleccionado]

# ==============================================================================
# NAVEGACIÓN EN PESTAÑAS (ESTRUCTURA DEL INFORME DE REFERENCIA)
# ==============================================================================
tab_costos, tab_edt, tab_riesgos, tab_calidad, tab_ia = st.tabs([
    "📈 C. Curva S y Costos (EVM)",
    "🌳 B. Seguimiento Alcance (EDT)",
    "⚠️ E. Gestión de Riesgos",
    "🎯 D. Control de Calidad",
    "🤖 Storytelling con IA"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: COSTOS Y CRONOGRAMA (EVM)
# ------------------------------------------------------------------------------
with tab_costos:
    _panel_control_cortes("corte_sel_costos")
    st.subheader(f"Seguimiento y Control de Costos (EVM) - {corte_seleccionado}")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Valor Planificado (PV)", f"${PV/1e6:.1f} M")
    k2.metric("Valor Ganado (EV)", f"${EV/1e6:.1f} M")
    k3.metric("Costo Real (AC)", f"${AC/1e6:.1f} M")
    k4.metric("Variación Costo (CV)", f"${CV/1e6:.1f} M", delta=f"{CV/1e6:.1f} M")
    k5.metric("Variación Cronograma (SV)", f"${SV/1e6:.1f} M", delta=f"{SV/1e6:.1f} M")

    st.markdown("---")
    st.markdown("**🔍 Comparativo de Informes de Seguimiento (Zoom EVM)**")
    cortes_reales = list(datos_cortes_evm.keys())[:5]
    csel1, csel2 = st.columns(2)
    informe1_sel = csel1.selectbox("Primer Informe", cortes_reales, index=0, key="informe1_evm")
    informe2_sel = csel2.selectbox("Segundo Informe", cortes_reales, index=1, key="informe2_evm")

    def _fecha_corte(nombre):
        m = re.search(r"\((.*?)\)", nombre)
        return m.group(1) if m else ""

    def _calc_metrics_corte(nombre):
        d = datos_cortes_evm[nombre]
        pv_i, ev_i, ac_i, cpi_i = float(d["pv"]), float(d["ev"]), float(d["ac"]), d["cpi"]
        eac_i = BAC / cpi_i if cpi_i > 0 else BAC
        return {
            "mes": d["mes"], "fecha": _fecha_corte(nombre), "idx": d["idx"],
            "pv": pv_i, "ev": ev_i, "ac": ac_i,
            "sv": ev_i - pv_i, "cv": ev_i - ac_i,
            "eac": eac_i, "etc": eac_i - ac_i, "vac": BAC - eac_i,
        }

    m1 = _calc_metrics_corte(informe1_sel)
    m2 = _calc_metrics_corte(informe2_sel)

    idx_show = max(idx_corte, m1["idx"], m2["idx"])
    y_range_max = BAC * 1.12
    xdom0, xdom1 = 0.24, 0.80
    ydom0, ydom1 = 0.02, 0.90

    # Ticks del eje Y en pasos de $50M, formateados como "$XXXM"
    paso_tick = 50_000_000
    y_tickvals = list(range(0, int(y_range_max) + paso_tick, paso_tick))
    y_ticktext = [f"${v/1e6:.0f}M" for v in y_tickvals]

    fig_s = go.Figure()
    # Curva Base PV
    fig_s.add_trace(go.Scatter(x=meses_evm, y=pv_master, mode='lines+markers', name='PV (Planificado)', line=dict(color='#10B981', width=3.5, shape='spline')))
    # Curva Real EV
    fig_s.add_trace(go.Scatter(x=meses_evm[:idx_show+1], y=ev_master[:idx_show+1], mode='lines+markers', name='EV (Valor Ganado)', line=dict(color='#2563EB', width=3.5, shape='spline')))
    # Curva Real AC
    fig_s.add_trace(go.Scatter(x=meses_evm[:idx_show+1], y=ac_master[:idx_show+1], mode='lines+markers', name='AC (Costo Real)', line=dict(color='#F59E0B', width=3.5, shape='spline')))

    # BAC
    fig_s.add_hline(y=BAC, line_dash="solid", line_color="#0F172A", line_width=1.5, annotation_text=f"BAC ${BAC/1e6:.1f}M", annotation_position="top left")

    # Líneas tenues para los cortes reales que NO están en la comparación
    # (se agrupan por mes para no duplicar líneas cuando 2 cortes caen en el mismo mes)
    meses_no_comparados = {}
    for nombre_c in cortes_reales:
        if nombre_c in (informe1_sel, informe2_sel):
            continue
        dc = datos_cortes_evm[nombre_c]
        meses_no_comparados.setdefault(dc["mes"], []).append(nombre_c.split(" (")[0])
    for mes_c, etiquetas in meses_no_comparados.items():
        fig_s.add_vline(x=mes_c, line_width=1, line_dash="dot", line_color="#94A3B8")
        fig_s.add_annotation(x=mes_c, y=y_range_max*0.97, text="/".join(etiquetas), showarrow=False, font=dict(color="#94A3B8", size=9))

    # Líneas resaltadas de los 2 informes comparados (con lupas)
    # Las etiquetas quedan dentro de la gráfica, ancladas cerca de la base y
    # desplazadas levemente a la derecha de su línea para no taparla.
    fig_s.add_vline(x=m1["mes"], line_width=2.5, line_color="#DC2626")
    fig_s.add_annotation(x=m1["mes"], y=y_range_max*0.04, yanchor="bottom", xshift=10, text=f"<b>PRIMER INFORME<br>FECHA CORTE<br>({m1['fecha']})</b>", showarrow=False, textangle=-90, font=dict(color="#DC2626", size=13))

    fig_s.add_vline(x=m2["mes"], line_width=2.5, line_color="#DC2626")
    fig_s.add_annotation(x=m2["mes"], y=y_range_max*0.04, yanchor="bottom", xshift=10, text=f"<b>SEGUNDO INFORME<br>FECHA CORTE<br>({m2['fecha']})</b>", showarrow=False, textangle=-90, font=dict(color="#DC2626", size=13))

    # Cada "lupa" es un mini-gráfico real (ejes secundarios) recortado con un
    # círculo, mostrando el cruce efectivo de PV/EV/AC en la fecha del corte.
    layout_axes = {}

    def _dibujar_lupa(fig, metrics, x0, x1, axis_suffix):
        y0c, y1c = 0.58, 0.99

        idx_c = metrics["idx"]
        idx_lo = max(0, idx_c - 2)
        idx_hi = min(len(meses_evm) - 1, idx_c + 2)
        v_meses = meses_evm[idx_lo:idx_hi + 1]
        v_pv = pv_master[idx_lo:idx_hi + 1]
        v_ev = ev_master[idx_lo:idx_hi + 1]
        v_ac = ac_master[idx_lo:idx_hi + 1]
        y_vals = v_pv + v_ev + v_ac
        y_lo, y_hi = min(y_vals), max(y_vals)
        pad = (y_hi - y_lo) * 0.45 or y_hi * 0.15
        y_rango = [y_lo - pad, y_hi + pad]

        ax_x = f"x{axis_suffix}"
        ax_y = f"y{axis_suffix}"
        # Las etiquetas siempre crecen hacia el interior del círculo, para no
        # recortarse contra el borde de la figura.
        es_izquierda = x1 <= 0.5
        xanchor_lbl = "left" if es_izquierda else "right"
        xshift_lbl = 6 if es_izquierda else -6

        # Fondo blanco circular detrás de las trazas del mini-zoom
        fig.add_shape(type="circle", xref="paper", yref="paper", x0=x0, x1=x1, y0=y0c, y1=y1c,
                      line=dict(width=0), fillcolor="white", layer="below")

        fig.add_trace(go.Scatter(x=v_meses, y=v_pv, mode="lines", line=dict(color="#10B981", width=3, shape="spline"),
                                  xaxis=ax_x, yaxis=ax_y, showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=v_meses, y=v_ev, mode="lines", line=dict(color="#2563EB", width=3, shape="spline"),
                                  xaxis=ax_x, yaxis=ax_y, showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=v_meses, y=v_ac, mode="lines", line=dict(color="#F59E0B", width=3, shape="spline"),
                                  xaxis=ax_x, yaxis=ax_y, showlegend=False, hoverinfo="skip"))

        fig.add_shape(type="line", xref=ax_x, yref=ax_y, x0=metrics["mes"], x1=metrics["mes"],
                      y0=y_rango[0], y1=y_rango[1], line=dict(color="#DC2626", width=2))

        # Las 3 etiquetas se separan verticalmente un mínimo (en vez de ir
        # exactamente sobre su valor real) para que no se superpongan cuando
        # dos métricas quedan muy cerca o son iguales (p. ej. PV = EV).
        etiquetas_lupa = sorted([
            ("PV", metrics["pv"], "#10B981"),
            ("EV", metrics["ev"], "#2563EB"),
            ("AC", metrics["ac"], "#F59E0B"),
        ], key=lambda t: t[1])
        gap_min = (y_rango[1] - y_rango[0]) * 0.14
        for i in range(1, len(etiquetas_lupa)):
            nombre_i, y_i, color_i = etiquetas_lupa[i]
            y_prev = etiquetas_lupa[i - 1][1]
            if y_i - y_prev < gap_min:
                etiquetas_lupa[i] = (nombre_i, y_prev + gap_min, color_i)
        for nombre, y_etiqueta, color in etiquetas_lupa:
            valor_real = {"PV": metrics["pv"], "EV": metrics["ev"], "AC": metrics["ac"]}[nombre]
            fig.add_annotation(x=metrics["mes"], y=y_etiqueta, xref=ax_x, yref=ax_y, xanchor=xanchor_lbl, xshift=xshift_lbl,
                                text=f"<b>{nombre} ${valor_real/1e6:.1f}M</b>", showarrow=False, font=dict(color=color, size=11))

        # Borde circular punteado encima (efecto lupa)
        fig.add_shape(type="circle", xref="paper", yref="paper", x0=x0, x1=x1, y0=y0c, y1=y1c,
                      line=dict(color="#64748B", width=1.5, dash="dot"), fillcolor="rgba(0,0,0,0)")

        # Líneas conectoras tipo cono hacia el punto real en la curva principal
        n_meses = len(meses_evm)
        idx_mes = meses_evm.index(metrics["mes"])
        frac_x = (idx_mes + 0.5) / n_meses
        paper_x_punto = xdom0 + frac_x * (xdom1 - xdom0)
        x_edge_paper = x1 if x1 <= 0.5 else x0
        for y_edge_paper, y_target in [(0.95, BAC * 1.03), (0.60, BAC * 0.55)]:
            frac_y = y_target / y_range_max
            paper_y_punto = ydom0 + frac_y * (ydom1 - ydom0)
            fig.add_shape(
                type="line", xref="paper", yref="paper",
                x0=x_edge_paper, y0=y_edge_paper, x1=paper_x_punto, y1=paper_y_punto,
                line=dict(color="#94A3B8", width=1.3, dash="dot")
            )

        layout_axes[f"xaxis{axis_suffix}"] = dict(domain=[x0, x1], visible=False,
                                                    categoryorder="array", categoryarray=v_meses, type="category")
        layout_axes[f"yaxis{axis_suffix}"] = dict(domain=[y0c, y1c], range=y_rango, visible=False)

    # Se ordenan por fecha (idx) para que la lupa izquierda siempre sea la más
    # antigua y la derecha la más reciente, evitando que las líneas conectoras
    # se crucen cuando el usuario elige los informes en orden inverso.
    informe_izq, informe_der = sorted([m1, m2], key=lambda m: m["idx"])
    _dibujar_lupa(fig_s, informe_izq, 0.0, 0.17, "2")
    _dibujar_lupa(fig_s, informe_der, 0.83, 1.0, "3")

    fig_s.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248, 250, 252, 0.7)",
        yaxis=dict(tickmode="array", tickvals=y_tickvals, ticktext=y_ticktext, showgrid=True, gridcolor="#E2E8F0", domain=[ydom0, ydom1], range=[0, y_range_max]),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", domain=[xdom0, xdom1]),
        height=600,
        margin=dict(l=10, r=10, t=40, b=20), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **layout_axes
    )
    st.plotly_chart(fig_s, width="stretch")

    st.markdown("---")

    # Trazabilidad de SPI / CPI / TCPI a lo largo del proyecto, con banda de
    # tolerancia y una marca de "Fecha Corte" en el corte elegido por el usuario.
    idx_default_trend = cortes_reales.index(corte_seleccionado) if corte_seleccionado in cortes_reales else 0
    corte_trend_sel = st.selectbox("Seleccionar corte a marcar en la gráfica:", cortes_reales,
                                    index=idx_default_trend, key="corte_trend")
    corte_trend_info = datos_cortes_evm[corte_trend_sel]
    idx_marcado = corte_trend_info["idx"]
    fecha_marcada = _fecha_corte(corte_trend_sel)

    idx_show_trend = max(idx_corte, idx_marcado)
    periodos = meses_evm[:idx_show_trend + 1]
    hist_spi = [ev_master[i] / pv_master[i] for i in range(idx_show_trend + 1)]
    hist_cpi = [ev_master[i] / ac_master[i] for i in range(idx_show_trend + 1)]
    hist_tcpi = [
        (BAC - ev_master[i]) / (BAC - ac_master[i]) if (BAC - ac_master[i]) != 0 else None
        for i in range(idx_show_trend + 1)
    ]

    y_min_t, y_max_t = 0.6, 1.45
    # El TCPI (a BAC) puede dispararse a valores enormes cuando el presupuesto
    # está casi agotado (AC ≈ BAC) mientras falta trabajo por ejecutar: es un
    # resultado matemáticamente correcto (señala que la meta original ya no es
    # alcanzable), pero deja la línea fuera del lienzo. Se "recorta" la línea
    # al borde superior y se marca con ▲, conservando el valor real en la
    # etiqueta y en la tabla.
    tope_visible = y_max_t - 0.03
    hist_tcpi_graf = [min(v, tope_visible) if v is not None else None for v in hist_tcpi]
    idx_fuera_escala = [i for i, v in enumerate(hist_tcpi) if v is not None and v > tope_visible]

    fig_trend = go.Figure()

    # Banda de tolerancia: fondo tostado, franja blanca entre 0.9 y 1.1
    fig_trend.add_shape(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=y_min_t, y1=0.9,
                         fillcolor="#FBE3C2", line=dict(width=0), layer="below")
    fig_trend.add_shape(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=1.1, y1=y_max_t,
                         fillcolor="#FBE3C2", line=dict(width=0), layer="below")

    fig_trend.add_trace(go.Scatter(x=periodos, y=hist_spi, mode="lines", name="SPI", line=dict(color="#1E3A8A", width=3)))
    fig_trend.add_trace(go.Scatter(x=periodos, y=hist_cpi, mode="lines", name="CPI", line=dict(color="#EAB308", width=3)))
    fig_trend.add_trace(go.Scatter(x=periodos, y=hist_tcpi_graf, mode="lines", name="TCPI", line=dict(color="#14B8A6", width=3)))
    if idx_fuera_escala:
        fig_trend.add_trace(go.Scatter(
            x=[periodos[i] for i in idx_fuera_escala], y=[tope_visible] * len(idx_fuera_escala),
            mode="markers", marker=dict(symbol="triangle-up", size=11, color="#14B8A6"),
            name="TCPI fuera de escala", showlegend=False, hoverinfo="skip"
        ))

    # Se fija el eje X como categórico ANTES de añadir vlines/anotaciones: si no,
    # Plotly resuelve esas posiciones contra un eje aún no tipado y las coloca
    # todas al inicio (bug ya visto con la línea roja de "Fecha Corte").
    fig_trend.update_xaxes(type="category", categoryorder="array", categoryarray=periodos)

    # Etiquetas con el valor final de cada indicador (el TCPI muestra el valor
    # REAL aunque la línea se haya recortado visualmente). Se separan con un
    # gap mínimo, igual que en las lupas, para que no se superpongan cuando
    # dos indicadores terminan con valores muy parecidos.
    etiquetas_finales = sorted([
        ("SPI", hist_spi[-1], hist_spi[-1], "#1E3A8A"),
        ("CPI", hist_cpi[-1], hist_cpi[-1], "#EAB308"),
        ("TCPI", hist_tcpi[-1], hist_tcpi_graf[-1], "#14B8A6"),
    ], key=lambda t: t[2])
    gap_min_final = (y_max_t - y_min_t) * 0.07
    for i in range(1, len(etiquetas_finales)):
        nombre_i, valor_i, pos_i, color_i = etiquetas_finales[i]
        pos_prev = etiquetas_finales[i - 1][2]
        if pos_i - pos_prev < gap_min_final:
            etiquetas_finales[i] = (nombre_i, valor_i, pos_prev + gap_min_final, color_i)
    for nombre, valor_real, pos_etiqueta, color in etiquetas_finales:
        fuera_de_escala = valor_real is not None and valor_real > tope_visible
        texto = f"<b>{nombre}:{valor_real:.2f}{' ⚠' if fuera_de_escala else ''}</b>".replace(".", ",")
        fig_trend.add_annotation(x=periodos[-1], y=pos_etiqueta, xanchor="left", xshift=8,
                                  text=texto, showarrow=False, font=dict(color=color, size=12))

    # Línea vertical de "Fecha Corte" en el corte elegido por el usuario
    fig_trend.add_vline(x=periodos[idx_marcado], line_width=2, line_color="#DC2626")
    fig_trend.add_annotation(x=periodos[idx_marcado], y=y_max_t * 0.98, yanchor="top",
                              text=f"<b>FECHA CORTE<br>({fecha_marcada})</b>", showarrow=False,
                              textangle=-90, font=dict(color="#DC2626", size=10))

    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[y_min_t, y_max_t], dtick=0.1, showgrid=True, gridcolor="rgba(255,255,255,0.7)", zeroline=False),
        xaxis=dict(showgrid=False),
        height=400, margin=dict(l=20, r=90, t=30, b=40),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=13))
    )

    c_trend_graf, c_trend_tabla = st.columns([2.5, 1])
    with c_trend_graf:
        st.plotly_chart(fig_trend, width="stretch")
        st.markdown(
            "<div style='text-align:center'><b style='font-size:1.1em'>Trazabilidad</b><br>"
            "Indicadores de estado del proyecto</div>",
            unsafe_allow_html=True
        )
    with c_trend_tabla:
        st.markdown(f"**Valores en {corte_trend_sel}**")
        tcpi_marcado = hist_tcpi[idx_marcado]
        if tcpi_marcado is None:
            valor_tcpi_txt = "N/D"
        elif tcpi_marcado > tope_visible:
            valor_tcpi_txt = f"{tcpi_marcado:.2f} ⚠ (meta BAC inalcanzable)"
        else:
            valor_tcpi_txt = f"{tcpi_marcado:.2f}"
        df_trend_valores = pd.DataFrame({
            "Indicador": ["SPI", "CPI", "TCPI"],
            "Valor": [
                f"{hist_spi[idx_marcado]:.2f}",
                f"{hist_cpi[idx_marcado]:.2f}",
                valor_tcpi_txt,
            ]
        })
        st.dataframe(df_trend_valores, hide_index=True, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 2: SEGUIMIENTO DEL ALCANCE Y EDT
# ------------------------------------------------------------------------------
with tab_edt:
    _panel_control_cortes("corte_sel_edt", "edt")
    st.subheader(f"Seguimiento y Control del Alcance (EDT) - {corte_seleccionado}")
    
    # Progreso de las 3 fases
    c_f1, c_f2, c_f3 = st.columns(3)
    p_f1 = df_edt_master[df_edt_master["Codigo"] == "1.0"][col_activa].values[0]
    p_f2 = df_edt_master[df_edt_master["Codigo"] == "2.0"][col_activa].values[0]
    p_f3 = df_edt_master[df_edt_master["Codigo"] == "3.0"][col_activa].values[0]

    c_f1.metric("1. Inicio y Planeación", f"{p_f1}%", delta="100% Aprobado" if p_f1==100 else "En curso")
    c_f2.metric("2. Diagnóstico y Estrategia", f"{p_f2}%", delta="Completado" if p_f2==100 else "En progreso")
    c_f3.metric("3. Piloto y Cierre", f"{p_f3}%", delta="Ejecutando" if p_f3>0 else "No iniciado")

    st.markdown("---")
    c_edt_t, c_edt_g = st.columns([1.3, 1])

    with c_edt_t:
        st.markdown("**Detalle de Paquetes de Trabajo (EDT Semaforizada)**")
        df_show_edt = df_edt_master[["Codigo", "Nombre", "Pto", col_activa]].copy()
        df_show_edt.columns = ["Código", "Paquete de Trabajo", "Presupuesto ($)", "Avance Real (%)"]
        df_show_edt["Estado"] = df_show_edt["Avance Real (%)"].apply(lambda x: "Finalizado 🟢" if x == 100 else "En Ejecución 🟡" if x > 0 else "No Iniciado ⚪")
        st.dataframe(df_show_edt, hide_index=True, use_container_width=True)

    with c_edt_g:
        st.markdown("**Comparativa de Avance por Paquete de Trabajo**")
        fig_bar_edt = px.bar(
            df_show_edt[~df_show_edt["Código"].isin(["1.0", "2.0", "3.0"])],
            x="Avance Real (%)", y="Código", orientation="h",
            color="Avance Real (%)", color_continuous_scale="Blues",
            hover_data=["Paquete de Trabajo", "Presupuesto ($)"]
        )
        fig_bar_edt.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_bar_edt, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 3: GESTIÓN DE RIESGOS
# ------------------------------------------------------------------------------
with tab_riesgos:
    _panel_control_cortes("corte_sel_riesgos", "riesgos")
    st.subheader(f"Evaluación de Riesgos y Reserva de Contingencia - {corte_seleccionado}")

    rk1, rk2, rk3 = st.columns(3)
    rk1.metric("Valor Monetario Esperado (VME)", f"${VME_val/1e6:.2f} M COP", delta=f"{((VME_val/56030654)-1)*100:.1f}% vs C1")
    rk2.metric("Valor Tiempo Esperado (VTE)", f"{VTE_val} Días", delta=f"+{VTE_val-58} días de desvío")
    rk3.metric("Riesgos Críticos Activos", "3 Materializados / 3 Críticos", delta_color="inverse")

    c_r_heat, c_r_list = st.columns([1.2, 1])

    with c_r_heat:
        st.markdown("**Mapa de Calor de Riesgos (Probabilidad vs. Impacto)**")
        # Gráfico interactivo que simula el mapa de calor de la guía
        col_p = "P_C5" if col_activa == "C5" else "P_C1"
        col_i = "I_C5" if col_activa == "C5" else "I_C1"
        
        fig_rf = px.scatter(
            df_riesgos_master, x=col_i, y=col_p, text="ID", color="Estado_C5",
            size=[14]*len(df_riesgos_master), hover_data=["Nombre"],
            color_discrete_map={"Cerrado 🟢": "#10B981", "Monitoreado 🟡": "#F59E0B", "Crítico 🔴": "#DC2626", "Materializado 🔴": "#7F1D1D", "Latente 🟢": "#3B82F6"}
        )
        fig_rf.update_layout(
            xaxis=dict(title="Nivel de Impacto (1-5)", range=[0.5, 5.5]),
            yaxis=dict(title="Probabilidad de Ocurrencia", range=[0.0, 1.0]),
            height=380, margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_rf, width="stretch")

    with c_r_list:
        st.markdown("**Registro de Riesgos Más Significativos**")
        st.dataframe(
            df_riesgos_master[["ID", "Nombre", col_p, col_i, "Estado_C5"]].rename(
                columns={col_p: "Probabilidad", col_i: "Impacto", "Estado_C5": "Estado Actual"}
            ),
            hide_index=True, use_container_width=True
        )

# ------------------------------------------------------------------------------
# PESTAÑA 4: CONTROL DE CALIDAD
# ------------------------------------------------------------------------------
with tab_calidad:
    _panel_control_cortes("corte_sel_calidad", "calidad")
    st.subheader(f"Seguimiento y Control de Calidad (Requisitos CAL) - {corte_seleccionado}")

    cal_prom = datos_corte["cal_global"]
    cumplidos_cal = int((df_calidad_master[col_activa] == 100).sum())
    total_cal = len(df_calidad_master)
    en_progreso_cal = int(((df_calidad_master[col_activa] > 0) & (df_calidad_master[col_activa] < 100)).sum())
    no_iniciados_cal = int((df_calidad_master[col_activa] == 0).sum())

    # --- Fila de KPIs ejecutivos ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Cumplimiento Global", f"{cal_prom:.1f}%", delta=f"Corte {col_activa}")
    k2.metric("Requisitos Cumplidos", f"{cumplidos_cal} / {total_cal}")
    k3.metric("En Progreso", f"{en_progreso_cal}")
    k4.metric("No Iniciados", f"{no_iniciados_cal}", delta=f"-{no_iniciados_cal}" if no_iniciados_cal else None, delta_color="inverse")

    st.markdown("---")
    c_gauge_cal, c_pendientes = st.columns([1, 1.6])

    with c_gauge_cal:
        st.markdown("**Índice de Cumplimiento (Semáforo Gerencial)**")
        fig_gauge_cal = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cal_prom,
            number={"suffix": "%", "font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0F172A"},
                "steps": [
                    {"range": [0, 50], "color": "#FCA5A5"},
                    {"range": [50, 85], "color": "#FDE68A"},
                    {"range": [85, 100], "color": "#86EFAC"},
                ],
            }
        ))
        fig_gauge_cal.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_gauge_cal, width="stretch")

    with c_pendientes:
        st.markdown("**⚠️ Entregables Críticos Pendientes para Gerencia**")
        df_pendientes = df_calidad_master[df_calidad_master[col_activa] < 100].sort_values(col_activa)
        if df_pendientes.empty:
            st.success("Todos los requisitos de calidad están al 100% en este corte.")
        else:
            for _, fila in df_pendientes.iterrows():
                pct = fila[col_activa]
                calif = CALIFICACIONES_REALES.get((fila["ID"], col_activa), "No Iniciado ⚪" if pct == 0 else "En Progreso 🟡")
                obs = OBSERVACIONES_REALES.get((fila["ID"], col_activa), "No aplica para este corte. Entregable en estado \"No Iniciado\".")
                st.markdown(f"**{fila['ID']} · {fila['Requisito']}** — {pct}% · {calif}")
                st.caption(obs)

    st.markdown("---")
    c_cal_t, c_cal_chart = st.columns([1.3, 1])

    with c_cal_t:
        st.markdown("**Matriz de Trazabilidad Evolutiva por Requisito**")

        def _calificacion_real(id_req, pct, estado_final):
            # CAL 08-11 cambian de calificación entre cortes (dato real del
            # PDF de trazabilidad); el resto permanece fijo en su Estado.
            return CALIFICACIONES_REALES.get((id_req, col_activa), estado_final if pct == 100 else "No Iniciado ⚪")

        df_cal_view = df_calidad_master[["ID", "Requisito", col_activa, "Estado"]].copy()
        df_cal_view["Estado"] = [
            _calificacion_real(id_req, pct, estado)
            for id_req, pct, estado in zip(df_cal_view["ID"], df_cal_view[col_activa], df_cal_view["Estado"])
        ]
        df_cal_view.columns = ["ID", "Requisito de Calidad", "% Cumplimiento", "Calificación"]

        def _color_fila_calidad(row):
            pct = row["% Cumplimiento"]
            if pct == 100:
                color = "background-color: #DCFCE7"
            elif pct == 0:
                color = "background-color: #F1F5F9"
            else:
                color = "background-color: #FEF9C3"
            return [color] * len(row)

        st.dataframe(df_cal_view.style.apply(_color_fila_calidad, axis=1), hide_index=True, width="stretch")

    with c_cal_chart:
        st.markdown("**Recuperación de Entregables Críticos (CAL 08, 09, 10, 11)**")
        # Serie de tendencia de entregables clave extraída del PDF
        cortes_eje = ["Corte 1", "Corte 2", "Corte 3", "Corte 4", "Corte 5"]
        cal08_vals = [53, 95, 100, 100, 100]
        cal09_vals = [0, 35, 91, 100, 100]
        cal10_vals = [0, 0, 25, 100, 100]
        cal11_vals = [0, 0, 0, 0, 30]

        fig_cal_trend = go.Figure()
        fig_cal_trend.add_trace(go.Scatter(x=cortes_eje, y=cal08_vals, name="CAL 08 (Causas Raíz)", line=dict(color="#2563EB", width=2.5)))
        fig_cal_trend.add_trace(go.Scatter(x=cortes_eje, y=cal09_vals, name="CAL 09 (Línea Base)", line=dict(color="#F59E0B", width=2.5)))
        fig_cal_trend.add_trace(go.Scatter(x=cortes_eje, y=cal10_vals, name="CAL 10 (Diseño Estrategia)", line=dict(color="#8B5CF6", width=2.5)))
        fig_cal_trend.add_trace(go.Scatter(x=cortes_eje, y=cal11_vals, name="CAL 11 (Prueba Piloto)", line=dict(color="#EF4444", width=2.5)))

        fig_cal_trend.update_layout(
            height=360, margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(title="% Aprobación", range=[0, 110]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_cal_trend, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 5: STORYTELLING Y PRESENTACIONES CON IA
# ------------------------------------------------------------------------------
with tab_ia:
    st.subheader("Automatización de Storytelling Ejecutivo con IA")
    col_ai1, col_ai2 = st.columns(2)

    with col_ai1:
        st.markdown("**1. Redacción de Memorando Estratégico (Gemini)**")
        st.write("Genera una síntesis técnica conectando EVM, EDT, Riesgos y Calidad.")
        
        if st.button("Generar Memorando Integral", type="primary"):
            if not GEMINI_KEY:
                st.error("Configura tu GEMINI_API_KEY en el archivo .env")
            else:
                with st.spinner("Sintetizando información ejecutiva del proyecto..."):
                    prompt = f"""
                    Actúa como Director del Proyecto de Grado de la Maestría en Gerencia de Proyectos.
                    Elabora un Memorando Ejecutivo de Seguimiento y Control para el Comité Directivo de Acerías Paz del Río
                    con base en los siguientes datos REALES del {corte_seleccionado}:

                    1. VALOR GANADO (EVM):
                       - BAC: ${BAC:,.0f} COP
                       - PV: ${PV:,.0f} | EV: ${EV:,.0f} | AC: ${AC:,.0f}
                       - SPI: {SPI:.2f} | CPI: {CPI:.2f}
                       - Variación Costo (CV): ${CV:,.0f} COP | Variación Cronograma (SV): ${SV:,.0f} COP
                       - Pronóstico de Cierre: EAC = ${EAC:,.0f} COP | VAC = ${VAC:,.0f} COP
                    
                    2. ALCANCE (EDT):
                       - Fase 1 (Planeación): {p_f1}%
                       - Fase 2 (Diagnóstico y Estrategia): {p_f2}%
                       - Fase 3 (Prueba Piloto): {p_f3}%
                    
                    3. GESTIÓN DE RIESGOS:
                       - Reserva de Contingencia Monetaria (VME): ${VME_val:,.0f} COP
                       - Reserva de Tiempo (VTE): {VTE_val} días
                       - Eventos críticos: R10 (Reasignación de personal), R11 (Disponibilidad de equipo) y R14 (Permisos).
                    
                    4. CALIDAD:
                       - Avance acumulado de requisitos: {cal_prom}%
                       - Estado de CAL 11 (Prueba Piloto): 30% con observaciones en ventanas operativas y HSE.

                    ESTRUCTURA DEL INFORME:
                    1. **Diagnóstico Integral del Proyecto:** Resumen de salud general y estado contractual.
                    2. **Análisis Cruzado Causa-Efecto:** Conecta cómo los riesgos (R10/R11) y la calidad (CAL 11) impactaron el CPI/SPI.
                    3. **Impacto Financiero y Proyección al Cierre:** Interpretación del sobrecosto proyectado (EAC/VAC).
                    4. **3 Decisiones Estratégicas Inmediatas:** Medidas correctivas requeridas para la prueba piloto.
                    """
                    
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_KEY}"
                    res = None
                    error_msg = None
                    for intento in range(2):  # 1 reintento ante fallas transitorias de red
                        try:
                            res = requests.post(gen_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=45)
                            error_msg = None
                            break
                        except requests.exceptions.RequestException as e:
                            error_msg = str(e)
                            res = None

                    if res is not None and res.status_code == 200:
                        st.session_state.memo_paz = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                        st.success("¡Memorando generado exitosamente con Gemini!")
                    elif res is not None:
                        st.error(f"Gemini respondió con error {res.status_code}: {res.text[:300]}")
                    else:
                        st.error(f"Error de conexión con IA tras 2 intentos: {error_msg}")

        if "memo_paz" in st.session_state:
            st.info(st.session_state.memo_paz)

    with col_ai2:
        st.markdown("**2. Exportar Diapositivas a Gamma**")
        st.write("Genera una baraja de diapositivas en Gamma con las métricas consolidadas.")
        
        if st.button("Exportar Presentación Ejecutiva"):
            if not GAMMA_KEY:
                st.error("Configura tu GAMMA_API_KEY en el archivo .env")
            else:
                texto_gamma = st.session_state.get("memo_paz", (
                    f"Informe de Control Integrado - Acerías Paz del Río. {corte_seleccionado}. "
                    f"BAC: ${BAC/1e6:.1f}M COP, EV: ${EV/1e6:.1f}M, AC: ${AC/1e6:.1f}M, "
                    f"CPI: {CPI:.2f}, SPI: {SPI:.2f}, EAC: ${EAC/1e6:.1f}M, VME: ${VME_val/1e6:.1f}M."
                ))
                with st.spinner("Creando presentación en Gamma..."):
                    try:
                        res = requests.post(
                            "https://public-api.gamma.app/v1.0/generations",
                            headers={"X-API-KEY": GAMMA_KEY, "Content-Type": "application/json"},
                            json={"inputText": texto_gamma, "textMode": "generate", "format": "presentation", "numCards": 6}
                        )
                        if res.status_code in [200, 201]:
                            st.success("¡Presentación enviada a Gamma! Revisa tu cuenta de Gamma.")
                    except Exception as e:
                        st.error(f"Error al conectar con Gamma: {e}")