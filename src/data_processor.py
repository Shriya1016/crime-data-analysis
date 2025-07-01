import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import logging

class DataProcessor:
    def __init__(self):
        """Initialize DataProcessor."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess crime data.
        
        Args:
            df (pd.DataFrame): Raw crime data
        
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        if df.empty:
            logging.warning("Empty DataFrame received for cleaning")
            return df
        
        # Drop rows with missing lat/lon
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # Convert month to datetime
        df['month'] = pd.to_datetime(df['month'], errors='coerce')
        
        # Remove invalid coordinates
        df = df[(df['latitude'].between(49, 61)) & (df['longitude'].between(-8, 2))]
        
        # Standardize crime categories
        df['category'] = df['category'].str.lower().str.replace('-', ' ')
        logging.info(f"Cleaned DataFrame: {len(df)} records remaining")
        return df

    def create_geodataframe(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        """
        Convert DataFrame to GeoDataFrame for spatial analysis.
        
        Args:
            df (pd.DataFrame): Cleaned DataFrame with lat/lon
        
        Returns:
            gpd.GeoDataFrame: GeoDataFrame with point geometries
        """
        if df.empty:
            logging.warning("Empty DataFrame received for GeoDataFrame creation")
            return gpd.GeoDataFrame()
        
        geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        # Convert to British National Grid for accurate spatial analysis
        gdf = gdf.to_crs(epsg=27700)
        logging.info("Created GeoDataFrame with British National Grid CRS")
        return gdf

    def aggregate_hotspots(self, gdf: gpd.GeoDataFrame, grid_size: float = 1000) -> gpd.GeoDataFrame:
        """
        Aggregate crime data into grid cells for hotspot detection.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame with crime points
            grid_size (float): Size of grid cells in meters
        
        Returns:
            gpd.GeoDataFrame: Aggregated grid with crime counts
        """
        if gdf.empty:
            logging.warning("Empty GeoDataFrame received for hotspot aggregation")
            return gdf
        
        # Create a grid
        xmin, ymin, xmax, ymax = gdf.total_bounds
        x = np.arange(np.floor(xmin), np.ceil(xmax), grid_size)
        y = np.arange(np.floor(ymin), np.ceil(ymax), grid_size)
        grid_cells = []
        for xi in x:
            for yi in y:
                grid_cells.append(Polygon([(xi, yi), (xi+grid_size, yi), (xi+grid_size, yi+grid_size), (xi, yi+grid_size)]))
        
        grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs=gdf.crs)
        # Spatial join to count crimes per grid cell
        joined = gpd.sjoin(gdf, grid, how='left', predicate='within')
        grid['crime_count'] = joined.groupby(joined.index_right).size()
        grid['crime_count'] = grid['crime_count'].fillna(0)
        
        # Add centroid for hotspot markers
        grid['centroid'] = grid['geometry'].centroid
        logging.info(f"Aggregated {len(grid[grid['crime_count'] > 0])} hotspot grid cells")
        return grid