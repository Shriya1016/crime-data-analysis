import folium
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import logging

class Visualizer:
    def __init__(self):
        """Initialize Visualizer."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def create_hotspot_map(self, gdf: gpd.GeoDataFrame, hotspot_gdf: gpd.GeoDataFrame) -> folium.Map:
        """
        Create an interactive map with crime hotspots.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame with crime points
            hotspot_gdf (gpd.GeoDataFrame): GeoDataFrame with hotspot grid
        
        Returns:
            folium.Map: Interactive map object
        """
        # Initialize map centered on UK
        m = folium.Map(location=[54.0, -2.0], zoom_start=6, tiles="OpenStreetMap")
        
        # Add heatmap
        heat_data = [[point.y, point.x] for point in gdf.geometry]
        folium.plugins.HeatMap(heat_data, radius=15).add_to(m)
        
        # Add hotspot markers
        for idx, row in hotspot_gdf.iterrows():
            if row['crime_count'] > 0:
                folium.Marker(
                    location=[row['centroid'].y, row['centroid'].x],
                    popup=folium.Popup(f"Crimes: {int(row['crime_count'])}", max_width=200),
                    icon=folium.Icon(color='red' if row['crime_count'] > 10 else 'orange')
                ).add_to(m)
        
        logging.info("Created hotspot map")
        return m

    def generate_graphs(self, df: pd.DataFrame, centroid: tuple, radius: float = 1000) -> dict:
        """
        Generate pie chart and bar graph for crimes near a hotspot.
        
        Args:
            df (pd.DataFrame): Crime data
            centroid (tuple): (x, y) coordinates of hotspot centroid
            radius (float): Radius in meters for filtering crimes
        
        Returns:
            dict: Dictionary with base64-encoded plot images
        """
        # Filter crimes near centroid
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['latitude']), crs="EPSG:4326")
        gdf = gdf.to_crs(epsg=27700)
        centroid_point = Point(centroid)
        buffer = centroid_point.buffer(radius)
        nearby_crimes = gdf[gdf.geometry.within(buffer)]
        
        if nearby_crimes.empty:
            logging.warning("No crimes found near hotspot")
            return {}
        
        # Pie chart for crime types
        crime_counts = nearby_crimes['category'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(crime_counts, labels=crime_counts.index, autopct='%1.1f%%')
        ax.set_title("Crime Type Distribution")
        pie_buffer = BytesIO()
        fig.savefig(pie_buffer, format='png')
        pie_base64 = base64.b64encode(pie_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        # Bar graph for crime counts by month
        nearby_crimes['month_str'] = nearby_crimes['month'].dt.strftime('%Y-%m')
        monthly_counts = nearby_crimes['month_str'].value_counts().sort_index()
        fig, ax = plt.subplots()
        sns.barplot(x=monthly_counts.index, y=monthly_counts.values, ax=ax)
        ax.set_title("Crimes by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Crime Count")
        plt.xticks(rotation=45)
        bar_buffer = BytesIO()
        fig.savefig(bar_buffer, format='png')
        bar_base64 = base64.b64encode(bar_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        logging.info("Generated pie chart and bar graph")
        return {'pie_chart': pie_base64, 'bar_graph': bar_base64}