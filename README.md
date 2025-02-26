# SatAsAService - Análisis de Datos Satelitales con Google Earth Engine

Este proyecto combina imágenes de **Sentinel-2** y datos climáticos de **ECMWF ERA5-Land** para la extracción de índices de vegetación y humedad del suelo. Se implementa en **Google Earth Engine (GEE)** y permite la visualización y análisis de datos geoespaciales en áreas específicas.

## **Descripción del Proyecto**
El sistema permite:
- 📡 **Procesar imágenes satelitales de Sentinel-2** y aplicar máscaras de nubes.
- 📊 **Extraer series temporales** de índices como **NDVI, NDMI, NDWI, NDSI**.
- 🌱 **Analizar humedad del suelo** desde ERA5-Land en diferentes capas de profundidad.
- 🗺️ **Visualizar datos en un mapa interactivo** con soporte para múltiples capas.

---

## **Estructura del Proyecto**
```bash
├── 📂 src
│   ├── 🛰️ auth.py            # Autenticación de Google Earth Engine
│   ├── 🛰️ config.py          # Configuración de AOI, fechas y parámetros de visualización
│   ├── 🛰️ main.py            # Script principal para ejecutar el flujo completo
│   ├── 🛰️ processing.py      # Procesamiento de imágenes y cálculo de índices
│   ├── 🛰️ time_series_extraction.py  # Extracción de datos temporales
│   ├── 🛰️ point_extraction.py        # Extracción de valores en puntos específicos
│   ├── 🛰️ visualization.py   # Creación del mapa interactivo
│   ├── 🛰️ plot_time_series.py # Visualización de series temporales con Plotly
│   ├── 🛰️ requirements.txt   # Dependencias necesarias para ejecutar el proyecto