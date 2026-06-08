# 🌾 SIPSA Predictor: Inteligencia de Datos para el Agro Colombiano

## 🖼️ Demo
(

https://github.com/user-attachments/assets/ed1c34cb-373f-4549-83a7-c037d24c8f3c

) 


[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

### 🚀 Optimización de la toma de decisiones en mercados mayoristas mediante analítica predictiva.

## 📝 Contexto y Objetivo
En el sector agropecuario colombiano, la volatilidad de los precios mayoristas (datos SIPSA-DANE) genera una alta incertidumbre. Este proyecto nace para cerrar la brecha de información entre productores y comercializadores. 

**El objetivo:** Proporcionar una herramienta técnica que no solo visualice datos históricos, sino que proyecte tendencias a corto plazo (3 meses) utilizando modelos robustos de series de tiempo, permitiendo una planificación estratégica basada en datos y no en suposiciones.

---

## 🛠️ Características Principales
- **Motor Adaptativo:** Selección automática entre modelos **ARIMA y SARIMA** según la densidad y estacionalidad de los datos.
- **Compuerta de Confianza:** El sistema evalúa su propia precisión (MAPE). Si la fiabilidad es menor al 80%, el sistema bloquea los consejos comerciales para proteger financieramente al usuario.
- **Análisis Regional:** Consultas dinámicas cruzando +600,000 registros por producto y central de abastos específica.
- **Interfaz Intuitiva:** Despliegue profesional mediante Streamlit para una experiencia de usuario fluida.

---

## 🧠 Arquitectura y Lógica
El sistema sigue un pipeline de ingeniería de datos riguroso:

1. **ETL:** Limpieza y normalización de datos del SIPSA (2013-2025).
2. **Validación Académica:** Backtesting dinámico que divide la serie en entrenamiento y prueba.
3. **Métricas Técnicas:** Cálculo de MAE, RMSE y MAPE para cada consulta individual.
4. **Dashboard:** Traducción de métricas estadísticas a "Consejos para el Productor/Consumidor".

---

## 📁 Estructura del Proyecto

```
sipsa_app/
│
├── app.py                          # UI principal de Streamlit (solo interfaz)
├── requirements.txt                # Dependencias exactas
├── README.md
│
├── data/
│   └── sipsa_consolidado_2025.parquet   # Dataset limpio (721 k registros)
│
└── utils/
    ├── __init__.py                 # Exportaciones públicas del paquete
    ├── data_processing.py          # ETL, carga y preparación de series
    └── forecasting.py              # Validación académica + proyección + consejos
```

> Todos los módulos de lógica de negocio residen en el paquete `utils/`. No hay archivos duplicados `data_processing.py` o `forecasting.py` en la raíz del proyecto.

---

## 🚀 Ejecución Local

### 1. Clonar / descomprimir el proyecto

```bash
cd sipsa_app
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
# Con venv
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
.venv\Scripts\activate             # Windows PowerShell

# O con conda
conda create -n sipsa python=3.11
conda activate sipsa
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> ⚠️ `pmdarima` requiere un compilador C. En Windows instala primero
> [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
> En Ubuntu/Debian: `sudo apt-get install build-essential`

### 4. Lanzar la aplicación

```bash
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501`.

---

## 🧠 Lógica de la Aplicación

```
Usuario selecciona Producto + Mercado
         │
         ▼
  preparar_serie()  ──► ¿< 10 meses? ──► st.error (datos insuficientes)
         │
         ▼
  validar_modelo()  ──► Backtesting dinámico
  (Bloque 1)              Train: N - test meses
                          Test:  6 meses (o 20 % si < 24 meses)
         │
         ▼
  ¿Precisión ≥ 80%?
    │              │
   SÍ              NO
    │              │
    ▼              ▼
proyectar_y_     st.error — Compuerta cerrada
aconsejar()      Gráfica referencial (opcional)
(Bloque 2)
    │
    ▼
Gráfica + Métricas + Consejos
(st.success / st.info / st.warning)
```

---

## 📦 Dependencias Clave

| Librería | Uso |
|---|---|
| `streamlit` | Interfaz web interactiva |
| `pmdarima` | `auto_arima` — selección automática ARIMA/SARIMA |
| `pandas` | Manipulación de series temporales |
| `scikit-learn` | Métricas MAE y MAPE |
| `matplotlib` | Gráficas de validación y proyección |
| `pyarrow` | Lectura eficiente del dataset `.parquet` |

---

## 🔬 Notas Académicas

- La **precisión** se define como `100% − MAPE`.
- El umbral de confianza del **80 %** es configurable en `utils/forecasting.py → UMBRAL_CONFIANZA`.
- El split dinámico adapta la ventana de prueba a la longitud real de cada serie,
  evitando errores en mercados con pocos datos.
- `auto_arima` selecciona automáticamente entre **ARIMA** (productos con tendencia de
  costos, ej. procesados) y **SARIMA** (productos con ciclos de cosecha, ej. papa, hortalizas).

  ---

## 🔬 Rigor Académico
- **Precisión:** Definida como `100% − MAPE`.
- **Detección de Estacionalidad:** Uso de `auto_arima` con criterios de información de Akaike (AIC).
- **Tratamiento de Datos:** Imputación técnica de vacíos mediante *forward-fill* para mantener la integridad cronológica.

---

✉️ **Contacto:** Henry Sierra - linkedin.com/in/henry-sierra
