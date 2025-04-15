import pandas as pd
import plotly.graph_objects as go
import webbrowser
import os

def plot_indices_per_point(csv_filename, save_figures=True):
    """
    Generates time-series plots for each geographic point, showing the evolution of all indices.

    This function loads the CSV file containing extracted time-series data, identifies the available index columns
    (excluding "Date", "Latitude", and "Longitude"), and then plots each index for each unique geographic point.

    Args:
        csv_filename (str): Path to the CSV file containing the time-series data.
        save_figures (bool): If True, saves each figure as an HTML file.

    Returns:
        None
    """
    df = pd.read_csv(csv_filename)

    # Determine the index columns (exclude 'Date', 'Latitude', 'Longitude')
    available_indices = [col for col in df.columns if col not in ["Date", "Latitude", "Longitude"]]

    if not available_indices:
        print(f"⚠️ No valid indices found in {csv_filename}. Skipping plot.")
        return

    # Determine dataset name for title display based on file name
    satellite = "Sentinel_2" if "sentinel" in csv_filename.lower() else "ERA5"

    # Get unique geographic points from the CSV data.
    unique_points = df[['Latitude', 'Longitude']].drop_duplicates().values.tolist()

    for lat, lon in unique_points:
        df_point = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]
        fig = go.Figure()

        # Plot each available index for the current point.
        for index in available_indices:
            if index in df_point.columns:
                fig.add_trace(go.Scatter(
                    x=df_point["Date"], y=df_point[index], mode='lines+markers', name=index
                ))

        fig.update_layout(
            title = f"{satellite} - Index Evolution at ({lat}, {lon})",
            xaxis_title = "Date",
            yaxis_title = "Index Value",
            template = "plotly_dark"
        )

        fig.show()

        # Save the figure as an HTML file if enabled.
        if save_figures:
            save_figure(fig, f"{satellite}_time_series_point_{lat}_{lon}", open_in_browser=False)

def plot_points_per_index(csv_filename, save_figures=True):
    """
    Generates time-series plots for each index, showing its evolution across different locations.

    This function loads the CSV file containing the time-series data, identifies the index columns
    (excluding "Date", "Latitude", and "Longitude"), and then creates a plot for each index
    where each location's time series is plotted.

    Args:
        csv_filename (str): Path to the CSV file containing the time-series data.
        save_figures (bool): If True, saves each figure as an HTML file.

    Returns:
        None
    """
    df = pd.read_csv(csv_filename)

    available_indices = [col for col in df.columns if col not in ["Date", "Latitude", "Longitude"]]

    if not available_indices:
        print(f"⚠️ No valid indices found in {csv_filename}. Skipping plot.")
        return

    satellite = "Sentinel_2" if "sentinel" in csv_filename.lower() else "ERA5"

    for index in available_indices:
        fig = go.Figure()
        unique_points = df[['Latitude', 'Longitude']].drop_duplicates().values.tolist()

        for lat, lon in unique_points:
            df_point = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]
            if index in df_point.columns:  # Ensure the index exists for the point
                fig.add_trace(go.Scatter(
                    x=df_point["Date"], y=df_point[index], mode='lines+markers', name=f"({lat}, {lon})"
                ))

        fig.update_layout(
            title = f"{satellite} - Evolution of {index} Across Locations",
            xaxis_title = "Date",
            yaxis_title = f"{index} Value",
            template = "plotly_dark"
        )

        fig.show()

        if save_figures:
            save_figure(fig, f"{satellite}_time_series_index_{index}", open_in_browser=False)

def save_figure(fig, filename, open_in_browser=True):
    """
    Saves a Plotly figure in HTML format and optionally opens it in the default web browser.

    Args:
        fig (plotly.graph_objects.Figure): The figure to be saved.
        filename (str): Base filename (without extension) to use when saving the figure.
        open_in_browser (bool): If True, opens the saved HTML file in the default browser.

    Returns:
        None
    """
    # Sanitize the filename to ensure compatibility with the file system.
    filename = filename.replace(".", "_").replace(",", "").replace(" ", "_")

    # Save as HTML (interactive)
    html_path = os.path.abspath(f"{filename}.html")
    fig.write_html(html_path)

    print(f"Saved: {filename}.html")

    # Open in browser if enabled
    if open_in_browser:
        webbrowser.open(f"file://{html_path}")
        print(f"Opened {filename}.html in browser.")