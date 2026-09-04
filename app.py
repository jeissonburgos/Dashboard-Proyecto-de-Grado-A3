import os
import time
import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import statsmodels.api as sm
from streamlit_echarts import st_echarts
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

# ==============================================================================
# BARRA LATERAL (SELECTOR DE CORTE)
# ==============================================================================
st.sidebar.header("🎛️ Control de Cortes")
corte_seleccionado = st.sidebar.selectbox("Seleccionar Hito de Control:", list(datos_cortes_evm.keys()), index=4)

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

# Mapeo de estado en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Presupuesto (BAC):** `${BAC/1e6:.2f} M COP`")
st.sidebar.markdown(f"**Reserva Contingencia (VME):** `${VME_val/1e6:.2f} M`")
st.sidebar.markdown(f"**Reserva Tiempo (VTE):** `{VTE_val} Días`")
st.sidebar.markdown(f"**Salud Contractual:** {'🟢 En meta' if (SPI>=1.0 and CPI>=0.95) else '🟡 Alerta' if (SPI>=0.9 or CPI>=0.85) else '🔴 Crítico'}")

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
    st.subheader(f"Seguimiento y Control de Costos (EVM) - {corte_seleccionado}")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Valor Planificado (PV)", f"${PV/1e6:.1f} M")
    k2.metric("Valor Ganado (EV)", f"${EV/1e6:.1f} M")
    k3.metric("Costo Real (AC)", f"${AC/1e6:.1f} M")
    k4.metric("Variación Costo (CV)", f"${CV/1e6:.1f} M", delta=f"{CV/1e6:.1f} M")
    k5.metric("Variación Cronograma (SV)", f"${SV/1e6:.1f} M", delta=f"{SV/1e6:.1f} M")

    c_curva, c_gauges = st.columns([2.3, 1])

    with c_curva:
        fig_s = go.Figure()
        # Curva Base PV
        fig_s.add_trace(go.Scatter(x=meses_evm, y=pv_master, mode='lines+markers', name='PV (Planificado)', line=dict(color='#10B981', width=3.5, shape='spline')))
        # Curva Real EV
        fig_s.add_trace(go.Scatter(x=meses_evm[:idx_corte+1], y=ev_master[:idx_corte+1], mode='lines+markers', name='EV (Valor Ganado)', line=dict(color='#2563EB', width=3.5, shape='spline')))
        # Curva Real AC
        fig_s.add_trace(go.Scatter(x=meses_evm[:idx_corte+1], y=ac_master[:idx_corte+1], mode='lines+markers', name='AC (Costo Real)', line=dict(color='#F59E0B', width=3.5, shape='spline')))
        
        # BAC y Líneas de corte
        fig_s.add_hline(y=BAC, line_dash="solid", line_color="#0F172A", line_width=1.5, annotation_text=f"BAC ${BAC/1e6:.1f}M", annotation_position="top left")
        
        if corte_seleccionado == "Comparativa Global":
            hitos = [("Mar/26", "Corte 1"), ("Abr/26", "Corte 2"), ("May/26", "Corte 3-4"), ("Ago/26", "Corte 5")]
            for m, lbl in hitos:
                fig_s.add_vline(x=m, line_width=1.5, line_dash="dash", line_color="#DC2626")
                fig_s.add_annotation(x=m, y=BAC*0.85, text=lbl, showarrow=False, textangle=-90, font=dict(color="#DC2626", size=10))
        else:
            fig_s.add_vline(x=datos_corte["mes"], line_width=2.5, line_color="#DC2626")
            fig_s.add_annotation(x=datos_corte["mes"], y=BAC*0.85, text=f"CORTE: {datos_corte['mes']}", showarrow=False, textangle=-90, font=dict(color="#DC2626", size=11))

        fig_s.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248, 250, 252, 0.7)",
            yaxis=dict(tickformat="$,.0f", showgrid=True, gridcolor="#E2E8F0"),
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
            margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_s, width="stretch")

with c_gauges:
    st.markdown("**Eficiencia en Costos (CPI / IRC)**")
    st_echarts(options={
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0.5,
            "max": 1.5,
            "radius": "95%",
            "center": ["50%", "70%"],
            "axisLine": {"lineStyle": {"width": 12, "color": [[0.4, "#EF4444"], [0.5, "#F59E0B"], [1.0, "#10B981"]]}},
            "pointer": {"length": "55%", "width": 4, "itemStyle": {"color": "#1E293B"}},
            "axisTick": {"show": False},
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "detail": {"formatter": "{value}", "fontSize": 20, "fontWeight": "bold", "offsetCenter": [0, "-20%"], "color": "#0F172A"},
            "title": {"offsetCenter": [0, "20%"], "fontSize": 12, "color": "#64748B"},
            "data": [{"value": round(CPI, 2), "name": "CPI"}]
        }]
    }, height="150px")

    st.markdown("**Eficiencia en Plazo (SPI / IRP)**")
    st_echarts(options={
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0.5,
            "max": 1.5,
            "radius": "95%",
            "center": ["50%", "70%"],
            "axisLine": {"lineStyle": {"width": 12, "color": [[0.4, "#EF4444"], [0.5, "#F59E0B"], [1.0, "#10B981"]]}},
            "pointer": {"length": "55%", "width": 4, "itemStyle": {"color": "#1E293B"}},
            "axisTick": {"show": False},
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "detail": {"formatter": "{value}", "fontSize": 20, "fontWeight": "bold", "offsetCenter": [0, "-20%"], "color": "#0F172A"},
            "title": {"offsetCenter": [0, "20%"], "fontSize": 12, "color": "#64748B"},
            "data": [{"value": round(SPI, 2), "name": "SPI"}]
        }]
    }, height="150px")

    # Índices en el tiempo y Regresión OLS
    col_t1, col_t2 = st.columns([1.5, 1])
    with col_t1:
        st.markdown("**Evolución de Índices SPI y CPI**")
        hist_spi = [round(ev_master[i]/pv_master[i], 2) for i in range(idx_corte + 1)]
        hist_cpi = [round(ev_master[i]/ac_master[i], 2) for i in range(idx_corte + 1)]
        fig_idx = go.Figure()
        fig_idx.add_trace(go.Scatter(x=meses_evm[:idx_corte+1], y=hist_spi, name="SPI (Cronograma)", line=dict(color="#2563EB", width=2.5)))
        fig_idx.add_trace(go.Scatter(x=meses_evm[:idx_corte+1], y=hist_cpi, name="CPI (Costo)", line=dict(color="#F59E0B", width=2.5)))
        fig_idx.add_hline(y=1.0, line_dash="dot", line_color="#10B981", annotation_text="Meta (1.0)")
        fig_idx.update_layout(height=230, margin=dict(l=20, r=20, t=25, b=20), yaxis=dict(range=[0.5, 1.4]))
        st.plotly_chart(fig_idx, width="stretch")

    with col_t2:
        st.markdown("**Pronóstico Estadístico de Cierre (EAC vs BAC)**")
        st.info(
            f"- **Presupuesto Inicial (BAC):** ${BAC:,.0f} COP\n"
            f"- **Estimado a la Conclusión (EAC):** ${EAC:,.0f} COP\n"
            f"- **Variación al Cierre (VAC):** ${VAC:,.0f} COP ({'Sobrecosto financiero' if VAC < 0 else 'Ahorro'})\n"
            f"- **Costo del Trabajo Restante (ETC):** ${ETC:,.0f} COP"
        )

# ------------------------------------------------------------------------------
# PESTAÑA 2: SEGUIMIENTO DEL ALCANCE Y EDT
# ------------------------------------------------------------------------------
with tab_edt:
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
    st.subheader(f"Seguimiento y Control de Calidad (Requisitos CAL) - {corte_seleccionado}")

    # KPIs de calidad
    cal_prom = datos_corte["cal_global"]
    st.metric("Avance Acumulado de Requisitos de Calidad", f"{cal_prom}%", delta=f"Corte {col_activa}")

    c_cal_t, c_cal_chart = st.columns([1.3, 1])

    with c_cal_t:
        st.markdown("**Matriz de Trazabilidad Evolutiva por Requisito**")
        df_cal_view = df_calidad_master[["ID", "Requisito", col_activa, "Estado"]].copy()
        df_cal_view.columns = ["ID", "Requisito de Calidad", "% Cumplimiento", "Calificación"]
        st.dataframe(df_cal_view, hide_index=True, use_container_width=True)

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
                    try:
                        res = requests.post(gen_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
                        if res.status_code == 200:
                            st.session_state.memo_paz = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                            st.success("¡Memorando generado exitosamente con Gemini!")
                    except Exception as e:
                        st.error(f"Error de conexión con IA: {e}")

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