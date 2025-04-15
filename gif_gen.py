import imageio
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

from auth import reconnect_gee

def create_colorbar(width, height, ramp, font=None):
    """
    Genera una imagen (PIL) con un gradiente vertical basado en 'ramp',
    lista de tuplas (valor_float, color_hex). Etiqueta los valores a la derecha.
    """
    colorbar = Image.new('RGBA', (width * 3 + 8, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(colorbar)

    min_val, _ = ramp[0]
    max_val, _ = ramp[-1]
    val_range = max_val - min_val

    def interpolate_color(c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    # Convertir hex a RGB y guardarlo en ramp_rgb
    ramp_rgb = []
    for val, hexcolor in ramp:
        rgb = tuple(int(hexcolor[i:i+2], 16) for i in (1, 3, 5))
        ramp_rgb.append((rgb, val))

    # Crear el gradiente en vertical
    for row in range(height):
        frac = row / float(height - 1)
        current_val = min_val + frac * val_range

        color_row = (0, 0, 0)
        for i in range(len(ramp_rgb) - 1):
            val_i = ramp_rgb[i][1]
            val_ip1 = ramp_rgb[i+1][1]
            if val_i <= current_val <= val_ip1:
                local_frac = (current_val - val_i) / (val_ip1 - val_i)
                c1 = ramp_rgb[i][0]
                c2 = ramp_rgb[i+1][0]
                color_row = interpolate_color(c1, c2, local_frac)
                break
        else:
            # Si está fuera del rango, ajustamos al extremo
            if current_val < ramp_rgb[0][1]:
                color_row = ramp_rgb[0][0]
            elif current_val > ramp_rgb[-1][1]:
                color_row = ramp_rgb[-1][0]

        for col in range(width):
            colorbar.putpixel((col, height - 1 - row), color_row)

    if not font:
        try:
            font = ImageFont.truetype("arialbd.ttf", 4)  # Fuente de la leyenda
        except IOError:
            font = ImageFont.load_default()

    # Dibujar etiquetas a la derecha de la barra
    text_x = width + 5
    for val, hexcolor in ramp:
        frac_label = (val - min_val) / val_range
        label_row = height - int(frac_label * (height - 1))
        label_str = f"{val:g}"

        # Definir offset vertical dinámico
        if -0.5 < val < 0 or val > 0.5:
            # Desplaza más abajo
            y_offset = 1
        elif 0.5 > val > 0:
            # Desplaza más arriba
            y_offset = -10
        elif val < -0.5:
            y_offset = -15
        else:
            # Para cero, centrado
            y_offset = 0

        # Ahora dibujamos el texto aplicando el offset
        draw.text((text_x, label_row + y_offset), label_str, fill="black", font=font)

    return colorbar

def draw_marker(draw, point, aoi_info, image_size, marker_color="red", marker_radius=5, text="Localidad"):
    """
    Dibuja un marcador (círculo) en la imagen usando las coordenadas de la localización.

    :param draw: Objeto ImageDraw de Pillow.
    :param point: Tupla (lon, lat) de la localización.
    :param aoi_info: Información del AOI obtenida con getInfo() (diccionario).
    :param image_size: Tupla (ancho, alto) de la imagen en píxeles.
    :param marker_color: Color del marcador.
    :param marker_radius: Radio del marcador en píxeles.
    :param text: Texto a dibujar sobre el marcador.
    """
    # Suponiendo que aoi_info es un polígono, extraemos sus coordenadas.
    # En EE, para un rectángulo generalmente la estructura es:
    # {"type": "Polygon", "coordinates": [[ [xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin] ]]}
    coords = aoi_info["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    xmin, xmax = min(lons), max(lons)
    ymin, ymax = min(lats), max(lats)

    width_px, height_px = image_size
    lon, lat = point
    # Convertir a coordenadas de pixel:
    x_pixel = (lon - xmin) / (xmax - xmin) * width_px
    y_pixel = (ymax - lat) / (ymax - ymin) * height_px

    # Dibujar un círculo (elipse) centrado en (x_pixel, y_pixel)
    draw.ellipse(
        [(x_pixel - marker_radius, y_pixel - marker_radius),
         (x_pixel + marker_radius, y_pixel + marker_radius)],
        fill=marker_color
    )

    # Cargar una fuente para el texto
    try:
        font = ImageFont.truetype("arialbd.ttf", 12)  # Fuente en negrita de tamaño 12
    except IOError:
        font = ImageFont.load_default()

    # Calcular el tamaño del texto para centrarlo horizontalmente
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    # Posicionar el texto encima del marcador
    # Se centra horizontalmente, y verticalmente se coloca unos 5 píxeles arriba del marcador
    x_text = x_pixel - text_width / 2
    y_text = y_pixel - marker_radius - 5 - (bbox[3] - bbox[1])

    draw.text((x_text, y_text), text, fill=marker_color, font=font)

def download_thumbnail(url, timeout=60, check_interval=0.5):
    """
    Intenta descargar la imagen desde 'url', esperando hasta 'timeout' segundos a que esté disponible,
    comprobando cada 'check_interval' segundos.

    :param url: URL de la imagen.
    :param timeout: Tiempo máximo en segundos a esperar.
    :param check_interval: Intervalo en segundos entre comprobaciones.
    :return: La respuesta si se descarga correctamente o None en caso de timeout.
    """
    start_time = time.time()
    reconnect_done = False
    while True:
        try:
            response = requests.get(url)
            # Si all está OK, devolvemos la respuesta.
            if response.status_code == 200:
                return response
            # Si se recibe error 401 y aún no se intentó reconectar
            elif response.status_code == 401 and not reconnect_done:
                print(f"\nError 401 detectado en {url}. Intentando re-autenticar y reconectar a EE...")
                if reconnect_gee():
                    reconnect_done = True
                else:
                    print("No se pudo reconectar a EE.")
            # Si se recibe otro error, simplemente se imprime (se puede extender la lógica si se requiere).
            else:
                print(f"\nError descargando imagen de: {url} (Código {response.status_code})")

            # Comprobar timeout
            if time.time() - start_time > timeout:
                print(f"\nTimeout alcanzado intentando descargar la imagen de: {url}")
                return None
            time.sleep(check_interval)
        except Exception as e:
            print(f"\nExcepción al intentar descargar {url}: {e}")
            if time.time() - start_time > timeout:
                print(f"\nTimeout alcanzado (excepción) intentando descargar {url}")
                return None
            time.sleep(check_interval)

def create_gif_from_urls(urls, dates, legend_palette, aoi, output_filename='laguna_gallocanta_evolucion.gif', duration=1):
    """
    Descarga imágenes a partir de una lista de URLs y crea un GIF animado.

    :param urls: Lista de URLs de las imágenes.
    :param dates: Lista de fechas (string) correspondientes a cada imagen.
    :param legend_palette: Identificador de la capa del satélite utilizado.
    :param aoi: Area of interest selected
    :param output_filename: Nombre del GIF de salida.
    :param duration: Tiempo (en segundos) que se muestra cada frame.
    """
    if legend_palette == "ndmi":
        legend_items = [
            (-0.8, '#800000'),  # Rojo oscuro (baja humedad)
            (-0.24, '#ff0000'),  # Rojo brillante (zona seca)
            (-0.032, '#ffff00'),  # Amarillo (transición a humedad)
            (0.032, '#00ffff'),  # Cian (humedad moderada)
            (0.24, '#0000ff'),  # Azul brillante (humedad alta)
            (0.8, '#000080')  # Azul oscuro (máxima humedad)
        ]
    else:
        legend_items = [
            (0.0, '#ffffcc'),  # Rojo oscuro (baja humedad)
            (0.2, '#c2e699'),  # Rojo brillante (zona seca)
            (0.4, '#78c679'),  # Amarillo (transición a humedad)
            (0.6, '#31a354'),  # Cian (humedad moderada)
            (0.8, '#006837'),  # Azul brillante (humedad alta)
        ]

    images = []
    counter = 0
    total = len(urls)

    # Generar la barra de color continua (por ejemplo 20px ancho x 200px alto).
    colorbar_width = 20
    colorbar_height = 100

    try:
        font_bar = ImageFont.truetype("arialbd.ttf", 15)
    except IOError:
        font_bar = ImageFont.load_default()

    legend_img = create_colorbar(colorbar_width, colorbar_height, legend_items, font=font_bar)

    marker_point = (-1.501846, 40.971332)
    aoi_info = aoi.getInfo()

    for url, date_text in zip(urls, dates):
        response = download_thumbnail(url, timeout=20)
        if response is not None:
            # Leer la imagen desde los datos binarios
            img_array = imageio.v2.imread(BytesIO(response.content))
            pil_img = Image.fromarray(img_array)
            draw = ImageDraw.Draw(pil_img)

            try:
                font = ImageFont.truetype("arialbd.ttf", 20)
            except IOError:
                font = ImageFont.load_default()

            # Calcular el tamaño del texto y su posición en la esquina inferior derecha.
            text = date_text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            width, height = pil_img.size
            x_date = width - text_width - 5  # 5 píxeles del borde derecho
            y_date = height - text_height - 5  # 5 píxeles del borde inferior

            draw.text((x_date, y_date), text, fill="black", font=font)

            pil_draw_resized = ImageDraw.Draw(pil_img)
            w2, h2 = pil_img.size

            # Pegar la leyenda (colorbar) en la esquina superior derecha.
            # Asegúrate de que la barra no sea más grande que la imagen final.
            # Su ancho + 5 píxeles de margen => x_bar.
            x_bar = w2 - legend_img.width - 5
            y_bar = 5

            # Pegar la barra.
            pil_img.paste(legend_img, (x_bar, y_bar), legend_img)  # 3er param => usar alpha

            # Dibujar el marcador en la localización especificada
            draw_marker(draw, marker_point, aoi_info, pil_img.size, marker_color="black", marker_radius=3, text="Laguna de Gallocanta")

            # Convertir la imagen anotada de vuelta a un array de NumPy.
            annotated_array = np.array(pil_img)
            images.append(annotated_array)
        else:
            print(f"Fallo definitivo descargando imagen de: {url}")
        counter += 1

        progress = counter / total
        bar_length = 50 # Total length of the bar
        filled_length = int(bar_length * progress)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        print(f"\rProgreso: [{bar}] {progress*100:6.2f}%", end="", flush=True)

    print(f"\n")
    # Crear el GIF
    imageio.mimsave(output_filename, images, duration=duration)
    print(f"GIF creado y guardado como {output_filename}")

def merge_gifs(gif1_path, gif2_path, output_path, duration=0.1):
    """
    Une dos GIFs consecutivamente en uno solo.

    :param gif1_path: Ruta del primer GIF.
    :param gif2_path: Ruta del segundo GIF.
    :param output_path: Ruta de salida para el GIF resultante.
    :param duration: Duración (en segundos) de cada frame en el GIF final.
    """
    # Leer los GIFs y obtener los cuadros
    frames_gif1 = imageio.mimread(gif1_path)
    frames_gif2 = imageio.mimread(gif2_path)

    # Concatenar los frames
    all_frames = frames_gif1 + frames_gif2

    # Guardar el GIF resultante
    imageio.mimsave(output_path, all_frames, duration=duration)
    print(f"GIF unido guardado en {output_path}")