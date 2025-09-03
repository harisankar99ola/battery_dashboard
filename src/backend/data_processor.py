import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from sklearn.preprocessing import StandardScaler
import re

class BatteryDataProcessor:
    """
    Process battery data following the same methodology as dmd_extractor.py
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def clean_for_json(self, obj):
        """
        Clean data for JSON serialization by handling NaN, inf, and -inf values
        """
        if isinstance(obj, dict):
            return {k: self.clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.clean_for_json(v) for v in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return [self.clean_for_json(x) for x in obj.tolist()]
        elif isinstance(obj, (float, int)):
            if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            return obj
        else:
            return obj
    
    def process_csv_content(self, content: bytes, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Process CSV content from bytes and return a pandas DataFrame
        """
        try:
            # Convert bytes to string
            csv_string = content.decode('utf-8')
            
            # Read CSV from string
            df = pd.read_csv(pd.io.common.StringIO(csv_string))
            
            # If sample_size is specified, return only a sample
            if sample_size and len(df) > sample_size:
                df = df.head(sample_size)
                
            return df
            
        except Exception as e:
            raise Exception(f"Error processing CSV content: {str(e)}")
    
    def identify_column_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Identify column types based on naming patterns from dmd_extractor
        Updated to match the exact methodology from dmd_extraction_automator.py
        """
        column_types = {
            'temp_stats': [],
            'soc_soh': [],
            'cell_voltages': [],
            'temp_cols': [],
            'thermocouple': [],
            'cell_balancing': [],
            'time': [],
            'current': [],
            'power': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            # Remove _avg suffix for pattern matching (since DMD extractor adds this)
            col_base = col_lower.replace('_avg', '')
            
            # Temperature statistics - Battery_Temperature_M or Effective_Battery
            if 'battery_temperature_m' in col_base or 'effective_battery' in col_base:
                column_types['temp_stats'].append(col)
            
            # SOC and SOH - Pack_S columns (broader pattern to match Pack_SOC, Pack_SoH, etc.)
            elif 'pack_s' in col_base:
                column_types['soc_soh'].append(col)
            
            # Cell voltages - Cell_Voltage_Cell
            elif 'cell_voltage_cell' in col_base:
                column_types['cell_voltages'].append(col)
            
            # BMS temperature sensors - BMS00_Pack_ columns (broader pattern)
            elif 'bms00_pack_' in col_base:
                column_types['temp_cols'].append(col)
            
            # Thermocouples - RH or LH columns (exact match to DMD extractor)
            # Updated patterns to match actual column names like LH-C1-Busbar-T22_avg, RH-C2-Cell1-T94_avg
            elif ('lh-' in col_lower and 't' in col_lower) or ('rh-' in col_lower and 't' in col_lower):
                column_types['thermocouple'].append(col)
            
            # Cell balancing - _Balancing_Status_
            elif '_balancing_status_' in col_base:
                column_types['cell_balancing'].append(col)
            
            # Time columns
            elif col_lower in ['time', 'timestamp', 'index'] or 'time' in col_lower:
                column_types['time'].append(col)
            
            # Current - also look for patterns that might include current measurements
            elif 'current' in col_lower or 'amp' in col_lower or 'battery_current' in col_base:
                column_types['current'].append(col)
            
            # Power
            elif 'power' in col_lower or 'watt' in col_lower or 'battery_power' in col_base:
                column_types['power'].append(col)
        
        # Combine all temperature columns for unified temperature analysis
        all_temp_columns = column_types['temp_stats'] + column_types['temp_cols'] + column_types['thermocouple']
        column_types['temperature'] = all_temp_columns
        
        # Debug output to see what columns are being detected
        print("🔍 Column detection debug:")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Sample columns: {list(df.columns)[:10]}")
        print(f"  Thermocouple columns: {len(column_types['thermocouple'])} - {column_types['thermocouple'][:3]}...")
        print(f"  Temp stats columns: {len(column_types['temp_stats'])} - {column_types['temp_stats'][:3]}...")
        print(f"  Temp cols: {len(column_types['temp_cols'])} - {column_types['temp_cols'][:3]}...")
        print(f"  SOC/SOH columns: {len(column_types['soc_soh'])} - {column_types['soc_soh'][:3]}...")
        print(f"  Cell voltage columns: {len(column_types['cell_voltages'])} - {column_types['cell_voltages'][:3]}...")
        print(f"  Total temperature columns: {len(all_temp_columns)}")
        
        return column_types
    
    def extract_cell_numbers(self, cell_columns: List[str]) -> List[int]:
        """Extract cell numbers from column names"""
        cell_numbers = []
        for col in cell_columns:
            # Extract numbers from column names
            numbers = re.findall(r'\d+', col)
            if numbers:
                cell_numbers.append(int(numbers[-1]))  # Take the last number
        return sorted(list(set(cell_numbers)))
    
    def apply_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply preprocessing to the dataframe
        """
        return self.preprocess_dataframe(df)
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess dataframe similar to dmd_extractor methodology
        """
        # Make a copy
        processed_df = df.copy()
        
        # Identify time column
        time_cols = self.identify_column_types(df)['time']
        if time_cols:
            time_col = time_cols[0]
            if time_col != 'Time':
                processed_df = processed_df.rename(columns={time_col: 'Time'})
            
            # Set time as index if not already
            if 'Time' in processed_df.columns:
                processed_df['Time'] = pd.to_numeric(processed_df['Time'], errors='coerce')
                processed_df = processed_df.set_index('Time')
        
        # Remove any non-numeric columns except time
        numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
        processed_df = processed_df[numeric_cols]
        
        # Remove any completely null columns
        processed_df = processed_df.dropna(axis=1, how='all')
        
        # Forward fill missing values (common in time series data)
        processed_df = processed_df.ffill().bfill()
        
        return processed_df
    
    def resample_data(self, df: pd.DataFrame, frequency: str = '1S') -> pd.DataFrame:
        """
        Resample data to specified frequency (similar to dmd_extractor rounding and grouping)
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            # If index is numeric (seconds), convert to datetime-like resampling
            df_resampled = df.groupby(df.index.round(0)).mean()
        else:
            df_resampled = df.resample(frequency).mean()
        
        return df_resampled
    
    
    def calculate_c_rate(self, df: pd.DataFrame, battery_capacity: float = 3.5) -> pd.Series:
        """
        Calculate C-rate from current data
        battery_capacity in Ah (default 3.5Ah for typical cell)
        """
        column_types = self.identify_column_types(df)
        current_columns = column_types['current']
        
        if not current_columns:
            return pd.Series(dtype=float)
        
        current_col = current_columns[0]
        current_data = df[current_col]
        
        # C-rate = Current(A) / Capacity(Ah)
        c_rate = current_data / battery_capacity
        return c_rate
    
    def combine_datasets(self, file_ids: List[str], drive_handler, 
                        labels: List[str] = None) -> Dict[str, Any]:
        """
        Combine multiple datasets from file IDs with proper labeling
        """
        if not file_ids:
            return {"data": [], "summary": "No files provided"}
        
        dataframes = []
        file_names = []
        
        # Download and process each file
        for file_id in file_ids:
            try:
                content = drive_handler.download_file_to_memory(file_id)
                df = self.process_csv_content(content)
                dataframes.append(df)
                
                # Get file name for labeling
                file_info = drive_handler.get_file_info(file_id)
                file_names.append(file_info.get('name', f'File_{file_id}'))
                
            except Exception as e:
                print(f"Error processing file {file_id}: {e}")
                continue
        
        if not dataframes:
            return {"data": [], "summary": "No valid files processed"}
        
        # Combine the dataframes
        combined_df = self._combine_dataframes(dataframes, file_names)
        
        return {
            "data": combined_df.to_dict('records'),
            "columns": combined_df.columns.tolist(),
            "summary": f"Combined {len(dataframes)} files with {len(combined_df)} total rows"
        }
    
    def _combine_dataframes(self, dataframes: List[pd.DataFrame], 
                           labels: List[str] = None) -> pd.DataFrame:
        """
        Internal method to combine multiple DataFrames with proper labeling
        """
        if not dataframes:
            return pd.DataFrame()
        
        combined_parts = []
        
        for i, df in enumerate(dataframes):
            df_copy = df.copy()
            
            # Add dataset label
            label = labels[i] if labels and i < len(labels) else f"Dataset_{i+1}"
            df_copy['Dataset'] = label
            
            # Reset index to make time a column, then add relative time
            if isinstance(df_copy.index, pd.DatetimeIndex):
                df_copy['Absolute_Time'] = df_copy.index
                df_copy['Relative_Time'] = (df_copy.index - df_copy.index[0]).total_seconds()
            else:
                df_copy['Relative_Time'] = df_copy.index
                df_copy['Absolute_Time'] = df_copy.index
            
            combined_parts.append(df_copy)
        
        # Concatenate all parts
        combined_df = pd.concat(combined_parts, ignore_index=True)
        return combined_df
    
    # Removed advanced analysis methods (temperature/voltage statistics, SOC-temperature relationships,
    # phase detection, and energy efficiency) as the frontend now only needs basic overview data.
    # Retrieve previous versions from git history if reintroduction is required.
    
    def calculate_statistics(self, df):
        """Calculate basic statistics for the dataframe"""
        try:
            # Basic statistics
            stats = {
                'shape': df.shape,
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()},
                'memory_usage': int(df.memory_usage(deep=True).sum()),
                'null_counts': df.isnull().sum().to_dict(),
                'numeric_stats': {}
            }
            
            # Get numeric columns for additional stats
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # Convert numpy values to Python native types for JSON serialization
                mean_vals = df[numeric_cols].mean()
                std_vals = df[numeric_cols].std()
                min_vals = df[numeric_cols].min()
                max_vals = df[numeric_cols].max()
                
                stats['numeric_stats'] = {
                    'mean': {col: float(val) if pd.notna(val) else None for col, val in mean_vals.items()},
                    'std': {col: float(val) if pd.notna(val) else None for col, val in std_vals.items()},
                    'min': {col: float(val) if pd.notna(val) else None for col, val in min_vals.items()},
                    'max': {col: float(val) if pd.notna(val) else None for col, val in max_vals.items()}
                }
            
            # Time range calculation - handle Time column properly
            time_cols = [col for col in df.columns if col.lower() in ['time', 'timestamp'] or 'time' in col.lower()]
            duration_hours = 0
            
            print(f"🕐 Time column detection: found {len(time_cols)} time columns: {time_cols}")
            
            if time_cols:
                time_col = time_cols[0]
                print(f"🕐 Using time column: {time_col}, dtype: {df[time_col].dtype}")
                try:
                    if pd.api.types.is_datetime64_any_dtype(df[time_col]):
                        duration_seconds = (df[time_col].max() - df[time_col].min()).total_seconds()
                        duration_hours = duration_seconds / 3600
                        print(f"🕐 Datetime column: duration = {duration_hours:.2f} hours")
                        stats['time_range'] = {
                            'start': df[time_col].min().isoformat() if hasattr(df[time_col].min(), 'isoformat') else str(df[time_col].min()),
                            'end': df[time_col].max().isoformat() if hasattr(df[time_col].max(), 'isoformat') else str(df[time_col].max()),
                            'duration_seconds': float(duration_seconds),
                            'duration_hours': float(duration_hours)
                        }
                    else:
                        # Handle numeric time columns (seconds from start)
                        time_values = pd.to_numeric(df[time_col], errors='coerce').dropna()
                        if len(time_values) > 0:
                            duration_seconds = float(time_values.max() - time_values.min())
                            duration_hours = duration_seconds / 3600
                            print(f"🕐 Numeric time column: range {time_values.min():.1f} to {time_values.max():.1f}, duration = {duration_hours:.2f} hours")
                            stats['time_range'] = {
                                'start': float(time_values.min()),
                                'end': float(time_values.max()),
                                'duration_seconds': duration_seconds,
                                'duration_hours': duration_hours
                            }
                except Exception as e:
                    print(f"❌ Error processing time column {time_col}: {e}")
            else:
                print("❌ No time columns detected")
            
            # Always include duration_hours for frontend
            stats['duration_hours'] = duration_hours
            
            return stats
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'shape': df.shape,
                'dtypes': {},
                'memory_usage': 0,
                'null_counts': {},
                'numeric_stats': {}
            }
