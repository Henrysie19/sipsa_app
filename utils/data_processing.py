"""
utils/data_processing.py
========================
Carga, limpieza y preparación del dataset SIPSA.
Todos los accesos al dataset deben pasar por este módulo.
"""

import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/sipsa_consolidado_2025.parquet")
MIN_MONTHS_REQUIRED = 10


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def _limpiar_texto(texto: str) -> str:
    """Normaliza texto: quita acentos, pasa a mayúsculas, elimina espacios laterales."""
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto.strip().upper()


# ─────────────────────────────────────────────────────────
# Carga principal (cacheada para Streamlit)
# ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Cargando dataset SIPSA…")
def cargar_dataset() -> pd.DataFrame:
    """
    Lee el parquet, aplica limpieza básica y retorna el DataFrame maestro.
    Usa st.cache_data para no recargar en cada interacción.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de datos: {DATA_PATH}. "
            "Asegúrate de que el dataset exista en la carpeta `data/` y que "
            "estés ejecutando Streamlit desde el directorio del proyecto.")

    df = pd.read_parquet(DATA_PATH)

    # Normalización de texto
    for col in ["grupo", "producto", "mercado"]:
        df[col] = df[col].apply(_limpiar_texto)

    # Tipos y filtros de calidad
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["precio_kg"] = pd.to_numeric(df["precio_kg"], errors="coerce")
    df = df.dropna(subset=["fecha", "precio_kg", "producto"])
    df = df[df["precio_kg"] > 0]

    # Eliminar outliers extremos (precio > 10× mediana del producto)
    mediana_producto = df.groupby("producto")["precio_kg"].transform("median")
    df = df[df["precio_kg"] < mediana_producto * 10]

    return df.sort_values("fecha").reset_index(drop=True)


# ─────────────────────────────────────────────────────────
# Selectors para la UI
# ─────────────────────────────────────────────────────────


def obtener_productos(df: pd.DataFrame) -> list[str]:
    """Retorna lista ordenada de productos únicos."""
    return sorted(df["producto"].unique().tolist())


def obtener_mercados(df: pd.DataFrame, producto: str) -> list[str]:
    """Retorna mercados disponibles para un producto específico."""
    mercados = (
        df[df["producto"] == producto]["mercado"]
        .unique()
        .tolist()
    )
    return sorted(mercados)


# ─────────────────────────────────────────────────────────
# Preparación de serie temporal
# ─────────────────────────────────────────────────────────


def preparar_serie(df: pd.DataFrame, producto: str, mercado: str) -> pd.Series | None:
    """
    Filtra por producto y mercado, resamplea a frecuencia mensual (MS)
    y rellena huecos con forward-fill.

    Returns
    -------
    pd.Series con índice DatetimeIndex o None si hay datos insuficientes.
    """
    df_local = df[(df["producto"] == producto) & (df["mercado"] == mercado)].copy()

    if df_local.empty:
        return None

    serie = (
        df_local
        .set_index("fecha")["precio_kg"]
        .resample("MS")
        .mean()
        .ffill()
    )

    return serie if len(serie) >= MIN_MONTHS_REQUIRED else None


def resumen_cobertura(df: pd.DataFrame, producto: str, mercado: str) -> dict:
    """Devuelve un dict con estadísticas básicas de cobertura para un par producto-mercado."""
    df_local = df[(df["producto"] == producto) & (df["mercado"] == mercado)]
    if df_local.empty:
        return {"meses": 0, "fecha_inicio": None, "fecha_fin": None}
    serie = (
        df_local
        .set_index("fecha")["precio_kg"]
        .resample("MS")
        .mean()
    )
    return {
        "meses": len(serie),
        "fecha_inicio": serie.index.min(),
        "fecha_fin": serie.index.max(),
    }
