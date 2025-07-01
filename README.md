Real Time Crime Data Analysis and Visualization

Overview

This project analyzes and visualizes crime data from the UK Police API (data.police.uk) or local CSV files, producing interactive maps with crime hotspots and detailed graphs (pie charts, bar graphs) when hotspots are clicked. It supports filtering by police force, year, month, and crime type.

Setup
Install Python 3.8+: Ensure Python is installed.
Install VS Code: Download from code.visualstudio.com.
Install Dependencies: Run pip install -r requirements.txt in the project root.
Data Directory: Place CSV files in the data/ folder with the structure:

data/
├── 2022-4/
│   ├── 2022-4-btp-street.csv
│   ├── 2022-4-metropolitan-street.csv
│   └── ...
├── 2022-5/
└── ... (up to 2025-3)

Each CSV should have columns: Crime ID, Month, Reported by, Crime type, Latitude, Longitude, Last outcome category.
API Key: The provided API key (IPaSRFcihM2DDpWwcgJ4GzvZpI8nBcPtJ1hxtyrL) is used for data.police.uk. If the API fails, the system falls back to CSV files.

Running the Project
Open the project in VS Code.
Run python src/main.py to start the Flask server.
Open http://127.0.0.1:5000 in a browser to access the web interface.
Select a police force, year, month, and crime type, then click "Fetch Data" to view the hotspot map.
Click a hotspot marker to display pie charts and bar graphs.

Features
Data Sources: Fetches data from the UK Police API or local CSV files.
Interactive Map: Displays crime hotspots using Folium, with heatmap and clickable markers.
Graphs: Pie charts (crime type distribution) and bar graphs (crimes by month) for selected hotspots.
Filtering: Filter by police force, year, month, and crime type.

Dependencies
Flask: Web framework
pandas, numpy: Data processing
folium, geopandas: Map visualization
matplotlib, seaborn, plotly: Graph generation
requests: API calls

Notes
If the API key is invalid or the API is down, the system automatically uses CSV files.
CSV files must follow the naming convention YYYY-MM-force-street.csv.
Visualizations are saved as PNG images and embedded in the web interface.
The project assumes the British National Grid (EPSG:27700) for accurate spatial analysis.

Output Locations
Map: Displayed in the browser at /.



Graphs: Generated on-demand and displayed below the map when a hotspot is clicked.



Logs: Printed to the console for debugging.

Limitations
The API may have rate limits or downtime, relying on CSV files as a fallback.
Missing or invalid coordinates are filtered out during data cleaning.
The project assumes the data structure matches the UK Police API format.

References
UK Police Data: data.police.uk
Folium Documentation: folium.readthedocs.io