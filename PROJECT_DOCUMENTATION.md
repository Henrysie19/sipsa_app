# Documentación del Proyecto SIPSA

Este documento describe cómo se creó el proyecto, su estructura de carpetas y el propósito de cada componente. Está pensado como referencia para cualquier usuario que quiera recrear o entender el proyecto.

## 1. Visión general

Este proyecto es una aplicación de Streamlit para analizar precios mayoristas agrícolas en Colombia usando un modelo estadístico de series de tiempo.

La idea principal es separar la interfaz de usuario de la lógica de negocio:

- `app.py`: solo maneja la interfaz y el flujo de la aplicación.
- `utils/`: contiene la lógica de carga de datos, preparación de series y forecasting.
- `data/`: contiene el dataset principal en formato `parquet`.

## 2. Estructura de carpetas

```
sipsa_app/
├── app.py
├── data/
│   └── sipsa_consolidado_2025.parquet
├── requirements.txt
├── README.md
├── PROJECT_DOCUMENTATION.md
└── utils/
    ├── __init__.py
    ├── data_processing.py
    └── forecasting.py
```

### `app.py`

Este archivo es el punto de entrada de Streamlit.

Funciones:

- Configura la página de Streamlit.
- Carga el dataset usando `utils.cargar_dataset()`.
- Presenta los controles de la barra lateral para seleccionar producto y mercado.
- Ejecuta el flujo de análisis cuando el usuario pulsa el botón.
- Muestra los resultados, gráficos y mensajes de error.

Importancia:

- Separa claramente la UI de la lógica de datos.
- Facilita cambios en la presentación sin tocar los modelos.

### `data/`

Contiene el dataset en formato `parquet`.

Archivo clave:

- `sipsa_consolidado_2025.parquet`

Importancia:

- El análisis se basa en datos históricos reales.
- `parquet` es un formato eficiente para cargas grandes con pandas.
- Mantener los datos en `data/` evita mezclar código y datos.

### `requirements.txt`

Lista las dependencias del proyecto.

Ejemplo:

- `streamlit`
- `pandas`
- `pmdarima`
- `scikit-learn`
- `matplotlib`

Importancia:

- Permite recrear el entorno de Python fácilmente.
- Asegura que quien ejecute el proyecto use las librerías correctas.

### `README.md`

Explica cómo ejecutar el proyecto, su estructura y dependencias.

Importancia:

- Documenta al usuario final cómo iniciar la aplicación.
- Sirve como guía rápida para colaboradores.

### `utils/`

Este paquete agrupa la lógica del proyecto.

Archivos:

- `__init__.py`: expone las funciones públicas del paquete.
- `data_processing.py`: carga y prepara los datos.
- `forecasting.py`: entrena los modelos y genera las predicciones.

Importancia:

- Permite reutilizar funciones desde `app.py` de forma limpia.
- Facilita pruebas unitarias y mantenimiento.
- Evita duplicación de código.

## 3. Cómo se creó el proyecto paso a paso

### 1. Crear el entorno

1. Abrir una terminal en la carpeta del proyecto.
2. Crear un entorno virtual:

```bash
python -m venv .venv
```

3. Activarlo:

- Windows PowerShell:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```

### 2. Instalar dependencias

Crear `requirements.txt` con las librerías necesarias y ejecutar:

```bash
pip install -r requirements.txt
```

### 3. Organizar el proyecto

1. Crear la carpeta `data/`.
2. Copiar el dataset `sipsa_consolidado_2025.parquet` dentro de `data/`.
3. Crear la carpeta `utils/`.
4. Añadir los archivos de lógica en `utils/data_processing.py` y `utils/forecasting.py`.
5. Añadir `utils/__init__.py` para exportar las funciones públicas.

### 4. Crear la aplicación Streamlit

1. En `app.py`, importar las funciones necesarias de `utils`.
2. Configurar la página con `st.set_page_config()`.
3. Cargar datos con `cargar_dataset()`.
4. Crear controles en la barra lateral.
5. Implementar el flujo de análisis y las visualizaciones.

### 5. Probar y ajustar

1. Ejecutar:

```bash
streamlit run app.py
```

2. Verificar que el dataset se cargue correctamente.
3. Probar la selección de productos y mercados.
4. Ajustar la lógica del modelo si es necesario.

## 4. Por qué esta división de carpetas es útil

- `app.py` se enfoca solo en la interfaz.
- `utils/` mantiene la lógica de negocio separada.
- `data/` mantiene los datos aislados.
- `requirements.txt` documenta dependencias.
- `README.md` y este documento guían a nuevos usuarios.

## 5. Recomendaciones para recrear el proyecto

1. Mantén la separación entre UI y lógica.
2. Usa un paquete (`utils/`) para agrupar funciones reutilizables.
3. Deja los datos en un directorio separado.
4. Documenta la estructura y los pasos de ejecución.
5. Prioriza nombres claros para archivos y funciones.

---

Este archivo es solo para información de quien quiera entender cómo se construyó el proyecto y cómo recrearlo desde cero.