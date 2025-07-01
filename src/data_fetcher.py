import os
import pandas as pd
import requests
from datetime import datetime
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    def __init__(self, api_key: str, data_dir: str = "../data"):
        """
        Initialize DataFetcher with API key and data directory.
        
        Args:
            api_key (str): API key for data.police.uk
            data_dir (str): Directory containing CSV files
        """
        self.api_key = api_key
        self.data_dir = data_dir
        self.base_url = "https://data.police.uk/api/crimes-street/all-crime"
        self.police_forces = [
            "Avon and Somerset Constabulary", "Bedfordshire Police", "British Transport Police",
            # ... (all other forces as listed in the prompt)
            "Wiltshire Police"
        ]

    def fetch_api_data(self, force: str, year: int, month: int) -> Optional[pd.DataFrame]:
        """
        Fetch crime data from the UK Police API for a specific force, year, and month.
        
        Args:
            force (str): Police force name
            year (int): Year of data
            month (int): Month of data
        
        Returns:
            Optional[pd.DataFrame]: DataFrame with crime data or None if failed
        """
        try:
            # Format force name for API (lowercase, hyphenated)
            force_slug = force.lower().replace(" ", "-").replace("&", "and")
            params = {
                "date": f"{year}-{month:02d}",
                "force": force_slug,
                "key": self.api_key
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                logging.warning(f"No data returned for {force} {year}-{month:02d}")
                return None
            df = pd.DataFrame(data)
            df['force'] = force
            logging.info(f"Fetched {len(df)} records from API for {force} {year}-{month:02d}")
            return df
        except Exception as e:
            logging.error(f"API fetch failed for {force} {year}-{month:02d}: {str(e)}")
            return None

    def load_csv_data(self, year: int, month: int) -> pd.DataFrame:
        """
        Load crime data from CSV files for a specific year and month.
        
        Args:
            year (int): Year of data
            month (int): Month of data
        
        Returns:
            pd.DataFrame: Combined DataFrame from all CSV files
        """
        folder = os.path.join(self.data_dir, f"{year}-{month}")
        if not os.path.exists(folder):
            logging.warning(f"Data folder {folder} does not exist")
            return pd.DataFrame()
        
        dfs = []
        for force in self.police_forces:
            file_name = f"{year}-{month}-{force.lower().replace(' ', '-')}-street.csv"
            file_path = os.path.join(folder, file_name)
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                    df['force'] = force
                    dfs.append(df)
                    logging.info(f"Loaded {len(df)} records from {file_path}")
                except Exception as e:
                    logging.error(f"Failed to load {file_path}: {str(e)}")
            else:
                logging.warning(f"File {file_path} not found")
        
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def get_data(self, forces: List[str], years: List[int], months: List[int], crime_types: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetch data from API or CSV files, prioritizing API.
        
        Args:
            forces (List[str]): List of police forces
            years (List[int]): List of years
            months (List[int]): List of months
            crime_types (Optional[List[str]]): List of crime types to filter
        
        Returns:
            pd.DataFrame: Combined crime data
        """
        dfs = []
        for year in years:
            for month in months:
                for force in forces:
                    # Try API first
                    df = self.fetch_api_data(force, year, month)
                    if df is None or df.empty:
                        # Fallback to CSV
                        df = self.load_csv_data(year, month)
                    if not df.empty:
                        dfs.append(df)
        
        if not dfs:
            logging.error("No data retrieved from API or CSV")
            return pd.DataFrame()
        
        combined_df = pd.concat(dfs, ignore_index=True)
        if crime_types:
            combined_df = combined_df[combined_df['category'].isin(crime_types)]
        
        # Standardize column names
        combined_df = self._standardize_columns(combined_df)
        logging.info(f"Total records after combining: {len(combined_df)}")
        return combined_df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize DataFrame columns for consistency.
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: Standardized DataFrame
        """
        # Expected columns: crime_id, month, force, category, location (lat, lon), outcome_status
        rename_map = {
            'Crime ID': 'crime_id',
            'Month': 'month',
            'Reported by': 'force',
            'Crime type': 'category',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Last outcome category': 'outcome_status'
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        # Ensure lat/lon are numeric
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        return df