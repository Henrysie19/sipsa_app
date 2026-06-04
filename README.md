# 🌾 SIPSA · Sistema Predictivo de Precios Mayoristas Agrícolas

Proyecto de Especialización — Colombia  
Modelos ARIMA / SARIMA con validación académica y compuerta de confianza.

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
