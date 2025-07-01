from flask import Flask, render_template, request, jsonify
from data_fetcher import DataFetcher
from data_processor import DataProcessor
from visualizer import Visualizer
import folium
import logging
import numpy as np

app = Flask(__name__)
fetcher = DataFetcher(api_key="IPaSRFcihM2DDpWwcgJ4GzvZpI8nBcPtJ1hxtyrL")
processor = DataProcessor()
visualizer = Visualizer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    """Render the main page."""
    forces = fetcher.police_forces
    years = [2022, 2023, 2024, 2025]
    months = list(range(1, 13))
    # Sample crime types (update based on actual data)
    crime_types = ['all crime', 'violent crime', 'burglary', 'vehicle crime', 'anti social behaviour']
    return render_template('index.html', forces=forces, years=years, months=months, crime_types=crime_types)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    """Fetch and visualize crime data based on user input."""
    force = request.form['force']
    year = int(request.form['year'])
    month = int(request.form['month'])
    crime_type = request.form['crime_type'] or None
    
    # Fetch data
    df = fetcher.get_data(
        forces=[force],
        years=[year],
        months=[month],
        crime_types=[crime_type] if crime_type and crime_type != 'all crime' else None
    )
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Process data
    df_clean = processor.clean_data(df)
    gdf = processor.create_geodataframe(df_clean)
    hotspot_gdf = processor.aggregate_hotspots(gdf)
    
    # Create map
    m = visualizer.create_hotspot_map(gdf, hotspot_gdf)
    map_html = m._repr_html_()
    
    return jsonify({'map_html': map_html})

@app.route('/get_graphs', methods=['POST'])
def get_graphs():
    """Generate graphs for a specific hotspot."""
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])
    
    # Fetch recent data (simplified for demo; in practice, cache or re-fetch)
    df = fetcher.get_data(
        forces=fetcher.police_forces,
        years=[2022, 2023, 2024, 2025],
        months=list(range(1, 13))
    )
    df_clean = processor.clean_data(df)
    
    # Convert lat/lng to British National Grid
    point_gdf = gpd.GeoDataFrame(geometry=[Point(lng, lat)], crs="EPSG:4326")
    point_gdf = point_gdf.to_crs(epsg=27700)
    centroid = (point_gdf.geometry.x[0], point_gdf.geometry.y[0])
    
    # Generate graphs
    graphs = visualizer.generate_graphs(df_clean, centroid)
    return jsonify(graphs)

if __name__ == '__main__':
    app.run(debug=True)