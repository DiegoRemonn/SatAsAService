import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_indices_per_point(csv_filename):
    """
    Generates time-series plots for each geographic point showing the evolution of all indices.

    :param csv_filename: str
        Path to the CSV file containing the extracted time-series data.
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

def plot_points_per_index(csv_filename):
    """
    Generates time-series plots for each index showing its evolution across different locations.

    :param csv_filename: str
        Path to the CSV file containing the extracted time-series data.
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