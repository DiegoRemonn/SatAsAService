# SatAsAService - Análisis de Datos Satelitales con Google Earth Engine

> #### ⚠️ IMPORTANTE:
> Este proyecto combina imágenes de **Sentinel-2** y datos climáticos de **ECMWF ERA5-Land** para la extracción de índices de vegetación y humedad del suelo. Se implementa en **Google Earth Engine (GEE)** y permite la visualización y análisis de datos geoespaciales en áreas específicas.

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

### Procedimiento del análisis satelital

El proceso de análisis satelital en este proyecto sigue los siguientes pasos:

1. **Descarga de datos satelitales**  
   - Se obtienen imágenes ópticas de **Sentinel-2** y datos climáticos de **ERA5-Land** desde **Google Earth Engine (GEE)**.  
   - Se aplican filtros de fecha y región de interés.

2. **Aplicación de máscaras de nubes**  
   - Se usa la **banda QA60** de Sentinel-2 para eliminar píxeles afectados por nubes y cirros.

3. **Cálculo de índices espectrales (Sentinel-2)**  
   Se calculan varios índices para analizar la vegetación y la humedad:
   - **NDVI** (Índice de Vegetación), **NDMI** (Índice de Humedad de la Vegetación), **NDWI** (Índice de Agua), **NDSI** (Índice de Nieve).

4. **Extracción de humedad del suelo (ERA5-Land)**  
   Se obtienen datos de humedad en diferentes profundidades:
   - **0-7 cm (superficial)**, **7-28 cm**, **28-100 cm**, **100-289 cm (capa profunda)**.

5. **Extracción de datos en puntos de interés**  
   - Se obtiene la información en ubicaciones específicas de **Zaragoza**.  
   - Se extraen valores en un punto exacto y en una ventana de **100x100 m** alrededor.  

6. **Generación de series temporales**  
   - Se extraen datos semanales (14 días/2 semanas) y se guardan en archivos CSV.  
   - Se registra la evolución de los índices en el tiempo para cada punto.

7. **Creación de mapas interactivos**  
   - Se generan mapas en **HTML** con geemap.  
   - Se superponen capas de **Sentinel-2** y **ERA5-Land** para la exploración visual.

8. **Visualización y análisis de resultados**  
   - Se crean gráficos dinámicos con **Plotly**.  
   - Se comparan índices de vegetación y humedad en distintos puntos.

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
- **0-7 cm** *(capa superficial).*
- **7-28 cm.**
- **28-100 cm.**
- **100-289 cm** *(capa profunda).*

> ### 📝 NOTA:
> Este proyecto usa Google Earth Engine y requiere una cuenta autorizada para acceder a los datos.

> ### 🚨 WARNING:
> Los datos de Sentinel-2 están disponibles desde 2017, mientras que ERA5-Land tiene datos desde 1950.