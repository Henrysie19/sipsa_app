"""
app.py  –  Aplicación principal SIPSA
======================================
Sistema Predictivo de Precios Mayoristas Agrícolas — Colombia
Proyecto de Especialización | Streamlit UI

Este archivo SOLO maneja la interfaz de usuario.
Toda la lógica de negocio vive en utils/.
"""

import streamlit as st

from utils import (
    UMBRAL_CONFIANZA,
    MIN_MONTHS_REQUIRED,
    cargar_dataset,
    grafica_proyeccion,
    grafica_validacion,
    obtener_mercados,
    obtener_productos,
    preparar_serie,
    proyectar_y_aconsejar,
    resumen_cobertura,
    validar_modelo,
)

# ─────────────────────────────────────────────────────────
# Configuración de página
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIPSA · Predictor de Precios",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CSS mínimo para mejorar legibilidad
# ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .metric-card {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-label  { font-size: 0.78rem; color: #555; margin-bottom: 4px; }
    .metric-value  { font-size: 1.5rem; font-weight: 700; color: #1a3a5c; }
    .metric-delta  { font-size: 0.85rem; margin-top: 4px; }
    .section-title { font-size: 1.1rem; font-weight: 600; color: #1a3a5c;
                     border-left: 4px solid #1a7a4a; padding-left: 10px;
                     margin: 18px 0 8px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────
# Header principal
# ─────────────────────────────────────────────────────────
st.title("🌾 SIPSA · Sistema Predictivo de Precios Mayoristas")
st.caption(
    "Fuente: DANE — Sistema de Información de Precios y Abastecimiento del Sector Agropecuario "
    "| Datos 2013–2025 | Modelos ARIMA / SARIMA con validación académica"
)
st.divider()


# ─────────────────────────────────────────────────────────
# Carga del dataset (cacheado)
# ─────────────────────────────────────────────────────────
try:
    df = cargar_dataset()
except FileNotFoundError as exc:
    st.error(
        "❌ No se pudo cargar el dataset de precios. "
        "Verifica que el archivo `data/sipsa_consolidado_2025.parquet` exista "
        "en la carpeta del proyecto y vuelve a ejecutar.",
        icon="🚨",
    )
    st.markdown(
        "<small>Si no tienes el dataset, coloca el archivo en `data/sipsa_consolidado_2025.parquet` "
        "o consulta el README del proyecto para obtener instrucciones.</small>",
        unsafe_allow_html=True,
    )
    st.stop()
except Exception as exc:
    st.error(
        f"❌ Error inesperado al cargar el dataset: `{exc}`",
        icon="🚨",
    )
    st.stop()


# ─────────────────────────────────────────────────────────
# Sidebar — Selección de parámetros
# ─────────────────────────────────────────────────────────
with st.sidebar:
    # Usamos la ruta local de tu archivo
    st.image(
        "ai-assistant.gif",
        width=100
    )
    st.write("Modelo Predictivo") # Opcional: un texto pequeño debajo
    st.markdown("## ⚙️ Parámetros de Análisis")
    st.markdown("Selecciona el producto y el mercado que deseas analizar.")
    st.divider()

    productos = obtener_productos(df)
    producto_sel = st.selectbox(
        "🥕 Producto",
        productos,
        index=productos.index("PAPA ICA-HUILA") if "PAPA ICA-HUILA" in productos else 0,
        help="Lista de productos reportados por el SIPSA.",
    )

    mercados = obtener_mercados(df, producto_sel)
    mercado_sel = st.selectbox(
        "🏪 Mercado / Central de Abastos",
        mercados,
        help="Mercados mayoristas con datos para el producto seleccionado.",
    )

    cobertura = resumen_cobertura(df, producto_sel, mercado_sel)
    st.markdown(
        f"""
        **Cobertura de datos:**
        - 📅 Desde: `{cobertura['fecha_inicio'].strftime('%b %Y') if cobertura['fecha_inicio'] else '—'}`
        - 📅 Hasta: `{cobertura['fecha_fin'].strftime('%b %Y') if cobertura['fecha_fin'] else '—'}`
        - 📊 Meses disponibles: `{cobertura['meses']}`
        """
    )

    st.divider()
    ejecutar = st.button(
        "🚀 Ejecutar Análisis",
        type="primary",
        use_container_width=True,
    )

    st.markdown("---")
    st.caption(
        f"ℹ️ **Umbral de confianza:** {UMBRAL_CONFIANZA:.0f}%  \n"
        f"Datos insuficientes si < {MIN_MONTHS_REQUIRED} meses."
    )


# ─────────────────────────────────────────────────────────
# Estado inicial (antes de ejecutar)
# ─────────────────────────────────────────────────────────
if not ejecutar:
    st.info(
        "👈 **Selecciona un Producto y un Mercado** en el panel izquierdo "
        "y pulsa **Ejecutar Análisis** para comenzar.",
        icon="ℹ️",
    )
    st.markdown(
        """
        ### ¿Qué hace esta aplicación?
        1. **Valida** el modelo estadístico (ARIMA / SARIMA) con datos históricos reales
           y calcula la **precisión** mediante backtesting.
        2. Si la precisión supera el **80 %**, **proyecta** el precio a 3 meses y genera
           **recomendaciones** para el Productor y el Consumidor.
        3. Si la precisión es inferior al umbral, se advierte que los consejos
           comerciales **no son seguros** para ese mercado.

        > _Los modelos SARIMA capturan ciclos de cosecha; los ARIMA capturan tendencias
        > de costos (productos procesados, industriales)._
        """,
    )
    st.stop()


# ─────────────────────────────────────────────────────────
# Pipeline principal
# ─────────────────────────────────────────────────────────
serie = preparar_serie(df, producto_sel, mercado_sel)

if serie is None:
    st.error(
        f"⛔ **Datos insuficientes** para **{producto_sel}** en **{mercado_sel}**.  \n"
        f"Se requieren al menos **{MIN_MONTHS_REQUIRED} meses** de registros mensuales "
        f"y solo se encontraron {cobertura['meses']}.  \n\n"
        "Prueba con otro mercado o producto que tenga mayor cobertura histórica.",
        icon="🚨",
    )
    st.stop()

# ── Bloque 1: Validación académica ──────────────────────
with st.spinner("🔬 Validando modelo (backtesting)…"):
    try:
        rv = validar_modelo(serie)
    except Exception as exc:
        st.error(
            f"❌ Error durante la validación del modelo: `{exc}`  \n"
            "Intenta con un producto / mercado con más datos históricos.",
            icon="🚨",
        )
        st.stop()

# ─────────────────────────────────────────────────────────
# Sección 1: Resultado de la validación
# ─────────────────────────────────────────────────────────
st.markdown(f'<p class="section-title">📐 Bloque 1 — Validación Académica del Modelo</p>',
            unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4)

precision_color = "#2e7d32" if rv.confiable else "#c62828"
precision_label = "✅ CONFIABLE" if rv.confiable else "⚠️ BAJA CONFIANZA"

col_a.markdown(
    f"""<div class="metric-card">
        <div class="metric-label">Precisión del Modelo</div>
        <div class="metric-value" style="color:{precision_color}">{rv.precision:.1f}%</div>
        <div class="metric-delta">{precision_label}</div>
    </div>""",
    unsafe_allow_html=True,
)
col_b.markdown(
    f"""<div class="metric-card">
        <div class="metric-label">Error Promedio (MAE)</div>
        <div class="metric-value">${rv.mae:,.0f}</div>
        <div class="metric-delta">pesos / Kg</div>
    </div>""",
    unsafe_allow_html=True,
)
col_c.markdown(
    f"""<div class="metric-card">
        <div class="metric-label">Tipo de Modelo</div>
        <div class="metric-value" style="font-size:1.05rem">{rv.tipo_modelo.split(" ")[0]}</div>
        <div class="metric-delta">{" ".join(rv.tipo_modelo.split(" ")[1:])}</div>
    </div>""",
    unsafe_allow_html=True,
)
col_d.markdown(
    f"""<div class="metric-card">
        <div class="metric-label">Parámetros del Modelo</div>
        <div class="metric-value" style="font-size:1.0rem">({rv.orden[0]},{rv.orden[1]},{rv.orden[2]})</div>
        <div class="metric-delta">orden (p,d,q) · estacional m={rv.orden_estacional[3]}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.write("")
fig_val = grafica_validacion(rv, producto_sel, mercado_sel)
st.pyplot(fig_val, use_container_width=True)

with st.expander("ℹ️ ¿Cómo se calculó esta validación?"):
    st.markdown(
        f"""
        Se realizó un **split dinámico** de la serie:

        | Conjunto | Meses | Rol |
        |---|---|---|
        | **Entrenamiento** | {rv.n_train} | El modelo aprende de estos datos |
        | **Prueba (oculto)** | {rv.n_test} | Se compara la predicción con la realidad |

        La **Precisión** se calcula como `100% − MAPE` (Mean Absolute Percentage Error).
        Un valor ≥ {UMBRAL_CONFIANZA:.0f}% indica que el modelo puede usarse para tomar
        decisiones comerciales con confianza razonable.
        """
    )

st.divider()


# ─────────────────────────────────────────────────────────
# Sección 2: Proyección + Compuerta de Confianza
# ─────────────────────────────────────────────────────────
if rv.confiable:
    # ── Bloque 2: Proyección ────────────────────────────
    with st.spinner("📡 Generando proyección…"):
        try:
            rp = proyectar_y_aconsejar(serie)
        except Exception as exc:
            st.error(f"❌ Error durante la proyección: `{exc}`", icon="🚨")
            st.stop()

    st.markdown(
        f'<p class="section-title">🔮 Bloque 2 — Proyección y Recomendaciones '
        f'({rp.tendencia} {rp.emoji})</p>',
        unsafe_allow_html=True,
    )

    # Métricas de precio
    variacion_str = f"{rp.variacion_pct:+.1f}%"
    delta_color = (
        "normal" if rp.tendencia == "ESTABLE"
        else ("inverse" if rp.tendencia == "BAJA" else "normal")
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Precio Actual", f"${rp.precio_actual:,.0f}", help="Último mes disponible en el histórico")
    c2.metric("📅 Mes 1",  f"${rp.precio_mes1:,.0f}", delta=variacion_str)
    c3.metric("📅 Mes 2",  f"${rp.precio_mes2:,.0f}")
    c4.metric("📅 Mes 3",  f"${rp.precio_mes3:,.0f}")

    st.write("")
    fig_proy = grafica_proyeccion(serie, rp, producto_sel, mercado_sel)
    st.pyplot(fig_proy, use_container_width=True)

    st.write("")

    # Consejos
    col_prod, col_cons = st.columns(2, gap="large")

    with col_prod:
        st.markdown("#### 👨‍🌾 Consejo para el Productor")
        if rp.tendencia == "ALZA":
            st.warning(rp.consejo_productor, icon="⚠️")
        elif rp.tendencia == "BAJA":
            st.error(rp.consejo_productor, icon="🚨")
        else:
            st.success(rp.consejo_productor, icon="👍")

    with col_cons:
        st.markdown("#### 🛒 Consejo para el Consumidor")
        if rp.tendencia == "ALZA":
            st.error(rp.consejo_consumidor, icon="🚨")
        elif rp.tendencia == "BAJA":
            st.info(rp.consejo_consumidor, icon="✅")
        else:
            st.success(rp.consejo_consumidor, icon="👍")

    # Nota de contexto
    st.markdown(
        f"""
        <small>
        ⚡ Proyección basada en <strong>{rv.tipo_modelo}</strong> con una precisión
        histórica del <strong>{rv.precision:.1f}%</strong>.
        La variación proyectada entre el precio actual y el Mes 1 es
        <strong>{rp.variacion_pct:+.1f}%</strong>.
        Estos consejos son orientativos y no constituyen asesoría financiera.
        </small>
        """,
        unsafe_allow_html=True,
    )

else:
    # ── Compuerta cerrada: precisión < 80 % ─────────────
    st.error(
        f"🔒 **Compuerta de Confianza CERRADA**  \n\n"
        f"La precisión del modelo para **{producto_sel}** en **{mercado_sel}** "
        f"es de solo **{rv.precision:.1f}%**, por debajo del umbral mínimo "
        f"requerido de **{UMBRAL_CONFIANZA:.0f}%**.  \n\n"
        "Esto puede deberse a:\n"
        "- Alta **volatilidad** en los precios de este mercado.\n"
        "- **Datos escasos** o discontinuos en el historial.\n"
        "- **Choques externos** (paros, sequías) que alteraron los patrones normales.\n\n"
        "⚠️ **Los consejos comerciales han sido ocultados para este mercado** "
        "porque podrían inducir decisiones económicas incorrectas.",
        icon="🚨",
    )

    with st.expander("📊 Ver gráfica de proyección (solo referencial, no confiable)"):
        st.warning(
            "Esta proyección se muestra únicamente con fines exploratorios. "
            "**No debe usarse para tomar decisiones comerciales.**",
            icon="⚠️",
        )
        with st.spinner("Generando proyección referencial…"):
            try:
                rp_ref = proyectar_y_aconsejar(serie)
                fig_proy_ref = grafica_proyeccion(serie, rp_ref, producto_sel, mercado_sel)
                st.pyplot(fig_proy_ref, use_container_width=True)
            except Exception:
                st.info("No fue posible generar la proyección referencial para este mercado.")

    st.info(
        "💡 **Sugerencia:** Prueba con otro mercado del mismo producto que tenga "
        "mayor cobertura histórica. Los mercados con más de 48 meses de datos "
        "suelen superar el umbral de confianza.",
        icon="💡",
    )


# ─────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🇨🇴 Proyecto de Especialización · Sistema SIPSA · "
    "Modelos de Series de Tiempo (ARIMA / SARIMA) · "
    "Datos DANE Colombia 2013–2025"
)
