import pandas as pd
import plotly.graph_objects as go
import webbrowser
import os

def plot_indices_per_point(csv_filename, save_figures=True):
    """
    Generates time-series plots for each geographic point showing the evolution of all indices.

    :param csv_filename: str
        Path to the CSV file containing the extracted time-series data.
    :param save_figures: bool
        If True, saves the figures as HTML and PNG.
    """
    df = pd.read_csv(csv_filename)

    # Get unique points (latitude, longitude)
    unique_points = df[['Latitude', 'Longitude']].drop_duplicates().values.tolist()

    for lat, lon in unique_points:
        df_point = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]

        fig = go.Figure()

        for index in ["NDVI", "NDMI", "NDWI", "NDSI"]:
            fig.add_trace(go.Scatter(
                x = df_point["Date"], y = df_point[index], mode = 'lines+markers', name = index
            ))

        fig.update_layout(
            title = f"Index Evolution at ({lat}, {lon})",
            xaxis_title = "Date",
            yaxis_title = "Index Value",
            template = "plotly_dark"
        )

        fig.show()

        # Save the figure if enabled
        if save_figures:
            save_figure(fig, f"time_series_point_{lat}_{lon}", open_in_browser=False)

def plot_points_per_index(csv_filename, save_figures=True):
    """
    Generates time-series plots for each index showing its evolution across different locations.

    :param csv_filename: str
        Path to the CSV file containing the extracted time-series data.
    :param save_figures: bool
        If True, saves the figures as HTML and PNG.
    """
    df = pd.read_csv(csv_filename)

    for index in ["NDVI", "NDMI", "NDWI", "NDSI"]:
        fig = go.Figure()

        unique_points = df[['Latitude', 'Longitude']].drop_duplicates().values.tolist()

        for lat, lon in unique_points:
            df_point = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]

            fig.add_trace(go.Scatter(
                x = df_point["Date"], y = df_point[index], mode = 'lines+markers', name = f"({lat}, {lon})"
            ))

        fig.update_layout(
            title = f"Evolution of {index} Across Locations",
            xaxis_title = "Date",
            yaxis_title = f"{index} Value",
            template = "plotly_dark"
        )
        fig.show()

        # Save the figure if enabled
        if save_figures:
            save_figure(fig, f"time_series_index_{index}", open_in_browser=False)

def save_figure(fig, filename, open_in_browser=True):
    """
    Saves a Plotly figure in HTML and PNG format and optionally opens it in a web browser.

    :param fig: plotly.graph_objects.Figure
        The figure to be saved.
    :param filename: str
        The base filename (without extension) for saving the figure.
    :param open_in_browser: bool, optional
        If True, opens the saved HTML file in the default web browser (default: True).
    """
    # Ensure filename is safe for filesystem
    filename = filename.replace(".", "_").replace(",", "").replace(" ", "_")

    # Save as HTML (interactive)
    html_path = os.path.abspath(f"{filename}.html")
    fig.write_html(html_path)

    # Save as PNG using Kaleido
    #fig.write_image(f"{filename}.png", engine="kaleido")

    print(f"Saved: {filename}.html and {filename}.png")

    # Open in browser if enabled
    if open_in_browser:
        webbrowser.open(f"file://{html_path}")
        print(f"Opened {filename}.html in browser.")