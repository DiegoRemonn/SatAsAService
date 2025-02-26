# SatAsAService - Análisis de Datos Satelitales con Google Earth Engine

> [!IMPORTANT]
> Este proyecto combina imágenes de **Sentinel-2** y datos climáticos de **ECMWF ERA5-Land** para la extracción de índices de vegetación y humedad del suelo. Se implementa en **Google Earth Engine (GEE)** y permite la visualización y análisis de datos geoespaciales en áreas específicas._

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
```

## **Instalación y Configuración**
### **1. Clonar el repositorio**
```bash
git clone https://gitlab.i3a.es/howlab/software/python/satellite/satasaservice.git
cd satasaservice
```
### **2. Crear un entorno virtual y activar dependencias**
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# En Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Uso del Proyecto

### Ejecutar el Script Principal
```bash
python main.py
```

## 📊 **Visualización de Series Temporales**
Los gráficos generados por **Plotly** permiten:

- **Visualizar la evolución de índices de vegetación** en cada punto.
- **Comparar la humedad del suelo** en diferentes capas de **ERA5-Land**.
- **Guardar gráficos como archivos `.html` y `.png`** para su análisis.

### **Índices de Vegetación (Sentinel-2)**
**Índices disponibles**:
- **NDVI** (*Índice de Vegetación Normalizado*) 🌿
- **NDMI** (*Índice de Humedad de la Vegetación*) 💧
- **NDWI** (*Índice de Agua Normalizado*) 💦
- **NDSI** (*Índice de Nieve Diferencial*) ❄️

### **Humedad del Suelo (ERA5-Land)**
**Capas de humedad del suelo**:
- **0-7 cm** *(capa superficial)*
- **7-28 cm**
- **28-100 cm**
- **100-289 cm** *(capa profunda)*

[!NOTE]
Este proyecto usa Google Earth Engine y requiere una cuenta autorizada para acceder a los datos.

[!WARNING]
Los datos de Sentinel-2 están disponibles desde 2017, mientras que ERA5-Land tiene datos desde 1950.