"""
utils/forecasting.py
====================
Bloque 1 – Validación académica (train/test split + métricas)
Bloque 2 – Proyección a futuro y generación de consejos comerciales

La compuerta de confianza (precisión >= 80 %) vive aquí como constante
UMBRAL_CONFIANZA para que la lógica y la UI compartan la misma fuente.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import matplotlib
matplotlib.use("Agg")          # backend sin GUI para Streamlit
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pmdarima as pm
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────
UMBRAL_CONFIANZA: float = 80.0   # % de precisión mínima para mostrar consejos
N_FORECAST: int = 3              # meses a proyectar hacia el futuro
UMBRAL_VARIACION: float = 3.0    # % de cambio para considerar alza/baja


# ─────────────────────────────────────────────────────────
# Dataclasses de resultado
# ─────────────────────────────────────────────────────────

@dataclass
class ResultadoValidacion:
    """Resultado del Bloque 1 (validación académica)."""
    mae: float
    mape: float
    precision: float          # = 100 - mape
    tipo_modelo: str          # "SARIMA (Estacional)" | "ARIMA (Tendencia)"
    orden: tuple
    orden_estacional: tuple
    n_train: int
    n_test: int
    # Series para graficar
    serie_train: pd.Series
    serie_test: pd.Series
    pred_validacion: pd.Series
    confiable: bool = field(init=False)

    def __post_init__(self):
        self.confiable = self.precision >= UMBRAL_CONFIANZA


@dataclass
class ResultadoProyeccion:
    """Resultado del Bloque 2 (proyección a futuro)."""
    precio_actual: float
    precio_mes1: float
    precio_mes2: float
    precio_mes3: float
    variacion_pct: float
    tendencia: str            # "ALZA" | "BAJA" | "ESTABLE"
    emoji: str
    consejo_productor: str
    consejo_consumidor: str
    pronostico: pd.Series


# ─────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────

def _detectar_tipo_modelo(modelo: pm.ARIMA) -> str:
    return (
        "SARIMA (Estacional)"
        if modelo.seasonal_order[3] > 0
        else "ARIMA (Tendencia)"
    )


def _entrenar_modelo(serie: pd.Series) -> pm.ARIMA:
    """Entrena auto_arima con parámetros adaptativos según la longitud de la serie."""
    n = len(serie)
    estacional = n >= 20
    modelo = pm.auto_arima(
        serie,
        seasonal=estacional,
        m=12,
        max_p=3, max_q=3,
        max_P=2, max_Q=2,
        stepwise=True,
        suppress_warnings=True,
        error_action="ignore",
    )
    return modelo


# ─────────────────────────────────────────────────────────
# Bloque 1: Validación académica
# ─────────────────────────────────────────────────────────

def validar_modelo(serie: pd.Series) -> ResultadoValidacion:
    """
    Realiza un split dinámico train/test, entrena auto_arima y calcula
    MAE y MAPE sobre el conjunto de prueba.

    Regla de split:
      - Si len(serie) > 24 → test = últimos 6 meses
      - Si len(serie) <= 24 → test = 20 % de los datos (mínimo 2)
    """
    n_total = len(serie)
    n_test = 6 if n_total > 24 else max(2, int(n_total * 0.20))
    n_train = n_total - n_test

    train = serie.iloc[:n_train]
    test  = serie.iloc[n_train:]

    modelo = _entrenar_modelo(train)
    pred_arr = modelo.predict(n_periods=n_test)
    pred_validacion = pd.Series(pred_arr, index=test.index)

    mae  = mean_absolute_error(test, pred_validacion)
    mape = mean_absolute_percentage_error(test, pred_validacion) * 100

    return ResultadoValidacion(
        mae=mae,
        mape=mape,
        precision=100.0 - mape,
        tipo_modelo=_detectar_tipo_modelo(modelo),
        orden=modelo.order,
        orden_estacional=modelo.seasonal_order,
        n_train=n_train,
        n_test=n_test,
        serie_train=train,
        serie_test=test,
        pred_validacion=pred_validacion,
    )


# ─────────────────────────────────────────────────────────
# Bloque 2: Proyección y consejos
# ─────────────────────────────────────────────────────────

def proyectar_y_aconsejar(serie: pd.Series) -> ResultadoProyeccion:
    """
    Entrena un modelo sobre TODA la serie y proyecta N_FORECAST meses.
    Genera consejos específicos para Productor y Consumidor.
    """
    modelo = _entrenar_modelo(serie)
    pred_arr = modelo.predict(n_periods=N_FORECAST)

    # Índice de fechas futuras
    ultima_fecha = serie.index[-1]
    fechas_futuras = pd.date_range(
        start=ultima_fecha + pd.DateOffset(months=1),
        periods=N_FORECAST,
        freq="MS",
    )
    pronostico = pd.Series(pred_arr, index=fechas_futuras)

    precio_actual = float(serie.iloc[-1])
    precio_mes1   = float(pronostico.iloc[0])
    precio_mes2   = float(pronostico.iloc[1]) if N_FORECAST >= 2 else precio_mes1
    precio_mes3   = float(pronostico.iloc[2]) if N_FORECAST >= 3 else precio_mes1
    variacion     = ((precio_mes1 - precio_actual) / precio_actual) * 100.0

    if variacion > UMBRAL_VARIACION:
        tendencia = "ALZA"
        emoji = "📈"
        consejo_productor = (
            "⚠️ **NO VENDA TODAVÍA.** El precio proyectado para el próximo mes es superior al actual. "
            "Si puede almacenar su producto de forma segura, espere para mejorar su margen de ganancia."
        )
        consejo_consumidor = (
            "🚨 **COMPRE YA.** El precio está subiendo. Abastézcase cuanto antes antes de que el "
            "incremento afecte su presupuesto."
        )
    elif variacion < -UMBRAL_VARIACION:
        tendencia = "BAJA"
        emoji = "📉"
        consejo_productor = (
            "🚨 **VENDA LO ANTES POSIBLE.** La oferta en el mercado está aumentando y el precio "
            "continuará bajando. Liquidar hoy le evita pérdidas mayores."
        )
        consejo_consumidor = (
            "✅ **ESPERE PARA COMPRAR.** El precio caerá en los próximos días. "
            "Sea paciente y obtendrá un precio más favorable para su bolsillo."
        )
    else:
        tendencia = "ESTABLE"
        emoji = "⚖️"
        consejo_productor = (
            "👍 **PRECIO JUSTO.** El mercado se encuentra en equilibrio. "
            "Puede vender con tranquilidad; no se esperan cambios bruscos."
        )
        consejo_consumidor = (
            "👍 **PRECIO ESTABLE.** Compre lo que necesite; el mercado está en equilibrio "
            "y no hay urgencia ni para adelantar ni para postergar la compra."
        )

    return ResultadoProyeccion(
        precio_actual=precio_actual,
        precio_mes1=precio_mes1,
        precio_mes2=precio_mes2,
        precio_mes3=precio_mes3,
        variacion_pct=variacion,
        tendencia=tendencia,
        emoji=emoji,
        consejo_productor=consejo_productor,
        consejo_consumidor=consejo_consumidor,
        pronostico=pronostico,
    )


# ─────────────────────────────────────────────────────────
# Gráficas (retornan fig de matplotlib)
# ─────────────────────────────────────────────────────────

def grafica_validacion(
    rv: ResultadoValidacion,
    producto: str,
    mercado: str,
) -> plt.Figure:
    """Gráfica del backtesting: entrenamiento, realidad y predicción de validación."""
    fig, ax = plt.subplots(figsize=(11, 4.5))

    # Mostrar solo los últimos 24 meses de entrenamiento para claridad
    train_plot = rv.serie_train.tail(24)
    ax.plot(train_plot.index, train_plot.values,
            label="Entrenamiento", color="#1a3a5c", linewidth=1.8, alpha=0.85)
    ax.plot(rv.serie_test.index, rv.serie_test.values,
            label="Realidad (oculto)", color="#2e7d32",
            marker="o", linewidth=2, markersize=5)
    ax.plot(rv.pred_validacion.index, rv.pred_validacion.values,
            label="Predicción del modelo", color="#c62828",
            linestyle="--", marker="x", linewidth=2, markersize=6)

    ax.set_title(
        f"Validación de Precisión — {producto}\n{mercado}",
        fontsize=12, fontweight="bold", pad=10,
    )
    ax.set_ylabel("Precio por Kg ($COP)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=35)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    return fig


def grafica_proyeccion(
    serie: pd.Series,
    rp: ResultadoProyeccion,
    producto: str,
    mercado: str,
) -> plt.Figure:
    """Gráfica de proyección: histórico reciente + 3 meses de pronóstico."""
    fig, ax = plt.subplots(figsize=(11, 4.5))

    historico_plot = serie.tail(24)
    ax.plot(historico_plot.index, historico_plot.values,
            label="Histórico (últimos 24 meses)", color="#1a3a5c",
            linewidth=1.8, marker="o", markersize=3)

    # Conectar el último punto del histórico con el primero del pronóstico
    puente_idx = [serie.index[-1], rp.pronostico.index[0]]
    puente_val = [float(serie.iloc[-1]), float(rp.pronostico.iloc[0])]
    ax.plot(puente_idx, puente_val, color="#c62828", linestyle="--", linewidth=1.5)

    color_tendencia = {"ALZA": "#c62828", "BAJA": "#1565c0", "ESTABLE": "#558b2f"}
    ax.plot(rp.pronostico.index, rp.pronostico.values,
            label=f"Pronóstico ({rp.tendencia} {rp.emoji})",
            color=color_tendencia.get(rp.tendencia, "#c62828"),
            linestyle="--", marker="s", linewidth=2.5, markersize=7)

    ax.set_title(
        f"Proyección de Precios — {producto}\n{mercado}",
        fontsize=12, fontweight="bold", pad=10,
    )
    ax.set_ylabel("Precio por Kg ($COP)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=35)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    return fig
