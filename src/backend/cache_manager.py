import os
import json
import pandas as pd
import pickle
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
import hashlib
import logging

@dataclass
class CacheEntry:
    """Represents a cached data entry"""
    file_id: str
    file_name: str
    file_path: str
    last_updated: datetime
    file_size: int
    columns: List[str]
    column_types: Dict[str, str]
    data_preview: Dict[str, Any]  # Small preview of the data
    
class DataCacheManager:
    """Manages caching of battery data for faster access"""
    
    def __init__(self, cache_dir: str = "cache", max_cache_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_cache_age = timedelta(hours=max_cache_age_hours)
        self.cache_index_file = os.path.join(cache_dir, "cache_index.json")
        self.data_cache_dir = os.path.join(cache_dir, "data")
        self.metadata_cache_dir = os.path.join(cache_dir, "metadata")
        
        # Create cache directories
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(self.data_cache_dir, exist_ok=True)
        os.makedirs(self.metadata_cache_dir, exist_ok=True)
        
        # Cache index (file_id -> CacheEntry metadata)
        self.cache_index: Dict[str, Dict] = self._load_cache_index()
        
        # In-memory cache for frequently accessed data
        self.memory_cache: Dict[str, pd.DataFrame] = {}
        self.memory_cache_max_size = 5  # Maximum files to keep in memory
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_cache_index(self) -> Dict[str, Dict]:
        """Load the cache index from disk"""
        if os.path.exists(self.cache_index_file):
            try:
                with open(self.cache_index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache index: {e}")
        return {}
    
    def _save_cache_index(self):
        """Save the cache index to disk"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save cache index: {e}")
    
    def _get_cache_key(self, file_id: str) -> str:
        """Generate a safe cache key for a file ID"""
        return hashlib.md5(file_id.encode()).hexdigest()
    
    def _is_cache_valid(self, file_id: str) -> bool:
        """Check if cached data is still valid"""
        if file_id not in self.cache_index:
            return False
        
        cached_time_str = self.cache_index[file_id].get('last_updated')
        if not cached_time_str:
            return False
        
        try:
            cached_time = datetime.fromisoformat(cached_time_str)
            return datetime.now() - cached_time < self.max_cache_age
        except Exception:
            return False
    
    def get_cached_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get cached file metadata (columns, types, preview) without loading full data"""
        if not self._is_cache_valid(file_id):
            return None
        
        cache_key = self._get_cache_key(file_id)
        metadata_file = os.path.join(self.metadata_cache_dir, f"{cache_key}.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata for {file_id}: {e}")
        
        return None
    
    def get_cached_data(self, file_id: str) -> Optional[pd.DataFrame]:
        """Get cached DataFrame"""
        # Check memory cache first
        if file_id in self.memory_cache:
            self.logger.info(f"Cache hit (memory): {file_id}")
            return self.memory_cache[file_id]
        
        # Check if cache is valid
        if not self._is_cache_valid(file_id):
            return None
        
        # Load from disk cache
        cache_key = self._get_cache_key(file_id)
        cache_file = os.path.join(self.data_cache_dir, f"{cache_key}.pkl")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    df = pickle.load(f)
                
                # Add to memory cache
                self._add_to_memory_cache(file_id, df)
                self.logger.info(f"Cache hit (disk): {file_id}")
                return df
            except Exception as e:
                self.logger.warning(f"Failed to load cached data for {file_id}: {e}")
        
        return None
    
    def cache_data(self, file_id: str, file_name: str, df: pd.DataFrame, 
                   drive_handler=None) -> bool:
        """Cache DataFrame and metadata"""
        try:
            cache_key = self._get_cache_key(file_id)
            
            # Cache the actual data
            cache_file = os.path.join(self.data_cache_dir, f"{cache_key}.pkl")
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
            
            # Generate metadata
            from data_processor import BatteryDataProcessor
            processor = BatteryDataProcessor()
            
            # Get column types
            column_types_dict = processor.identify_column_types(df)
            
            # Extract specific column lists
            time_cols = column_types_dict.get('time', [])
            voltage_cols = column_types_dict.get('cell_voltages', [])
            current_cols = column_types_dict.get('current', [])
            temp_cols = column_types_dict.get('temp_cols', []) + column_types_dict.get('thermocouple', []) + column_types_dict.get('temp_stats', [])
            soc_cols = column_types_dict.get('soc_soh', [])
            other_cols = []
            
            # Create simplified column types mapping
            column_types = {}
            for col in df.columns:
                if col in time_cols:
                    column_types[col] = 'time'
                elif col in voltage_cols:
                    column_types[col] = 'voltage'
                elif col in current_cols:
                    column_types[col] = 'current'
                elif col in temp_cols:
                    column_types[col] = 'temperature'
                elif col in soc_cols:
                    column_types[col] = 'soc'
                else:
                    column_types[col] = 'other'
                    other_cols.append(col)
            
            # Create data preview (first and last few rows)
            preview_data = {
                'head': df.head(3).to_dict('records'),
                'tail': df.tail(3).to_dict('records'),
                'shape': df.shape,
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            # Cache metadata
            metadata = {
                'file_id': file_id,
                'file_name': file_name,
                'last_updated': datetime.now().isoformat(),
                'columns': df.columns.tolist(),
                'column_types': column_types,
                'data_preview': preview_data,
                'row_count': len(df),
                'column_count': len(df.columns)
            }
            
            metadata_file = os.path.join(self.metadata_cache_dir, f"{cache_key}.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            # Update cache index
            self.cache_index[file_id] = {
                'file_name': file_name,
                'last_updated': datetime.now().isoformat(),
                'cache_key': cache_key,
                'row_count': len(df),
                'column_count': len(df.columns)
            }
            self._save_cache_index()
            
            # Add to memory cache
            self._add_to_memory_cache(file_id, df)
            
            self.logger.info(f"Cached data for {file_name} ({len(df)} rows, {len(df.columns)} columns)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cache data for {file_id}: {e}")
            return False
    
    def _add_to_memory_cache(self, file_id: str, df: pd.DataFrame):
        """Add DataFrame to memory cache with size management"""
        # Remove oldest entries if cache is full
        while len(self.memory_cache) >= self.memory_cache_max_size:
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        # Add new entry
        self.memory_cache[file_id] = df
    
    def get_all_cached_files_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all cached files"""
        cached_files = []
        
        for file_id, index_entry in self.cache_index.items():
            if self._is_cache_valid(file_id):
                metadata = self.get_cached_file_metadata(file_id)
                if metadata:
                    # Combine index and metadata
                    file_info = {
                        'file_id': file_id,
                        'file_name': index_entry['file_name'],
                        'last_updated': index_entry['last_updated'],
                        'row_count': index_entry['row_count'],
                        'column_count': index_entry['column_count'],
                        'columns': metadata.get('columns', []),
                        'column_types': metadata.get('column_types', {}),
                        'data_preview': metadata.get('data_preview', {}),
                        'cached': True
                    }
                    cached_files.append(file_info)
        
        return cached_files
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        expired_files = []
        
        for file_id in list(self.cache_index.keys()):
            if not self._is_cache_valid(file_id):
                expired_files.append(file_id)
        
        for file_id in expired_files:
            self.remove_from_cache(file_id)
        
        if expired_files:
            self.logger.info(f"Removed {len(expired_files)} expired cache entries")
    
    def remove_from_cache(self, file_id: str):
        """Remove a file from cache"""
        try:
            # Remove from memory cache
            if file_id in self.memory_cache:
                del self.memory_cache[file_id]
            
            # Remove from disk cache
            if file_id in self.cache_index:
                cache_key = self.cache_index[file_id]['cache_key']
                
                cache_file = os.path.join(self.data_cache_dir, f"{cache_key}.pkl")
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                
                metadata_file = os.path.join(self.metadata_cache_dir, f"{cache_key}.json")
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
                
                del self.cache_index[file_id]
                self._save_cache_index()
            
            self.logger.info(f"Removed {file_id} from cache")
            
        except Exception as e:
            self.logger.error(f"Failed to remove {file_id} from cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_cached = len(self.cache_index)
        valid_cached = sum(1 for file_id in self.cache_index if self._is_cache_valid(file_id))
        memory_cached = len(self.memory_cache)
        
        # Calculate disk usage
        disk_usage = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                disk_usage += os.path.getsize(os.path.join(root, file))
        
        return {
            'total_cached_files': total_cached,
            'valid_cached_files': valid_cached,
            'memory_cached_files': memory_cached,
            'cache_disk_usage_mb': round(disk_usage / 1024 / 1024, 2),
            'cache_directory': self.cache_dir
        }
    
    async def preload_popular_files(self, drive_handler, file_list: List[Dict], max_files: int = 10):
        """Preload popular/recent files into cache"""
        self.logger.info(f"Starting preload of up to {max_files} files...")
        
        preloaded = 0
        for file_info in file_list[:max_files]:
            file_id = file_info['id']
            file_name = file_info['name']
            
            # Skip if already cached and valid
            if self._is_cache_valid(file_id):
                self.logger.info(f"Skipping {file_name} - already cached")
                continue
            
            try:
                self.logger.info(f"Preloading {file_name}...")
                
                # Download and process the file
                content = drive_handler.download_file_to_memory(file_id)
                
                # Process CSV content using data processor
                from data_processor import BatteryDataProcessor
                processor = BatteryDataProcessor()
                df = processor.process_csv_content(content)
                
                # Validate that we got a DataFrame
                if not isinstance(df, pd.DataFrame):
                    self.logger.error(f"Expected DataFrame but got {type(df)} for {file_name}")
                    continue
                
                if df is not None and not df.empty:
                    success = self.cache_data(file_id, file_name, df, drive_handler)
                    if success:
                        preloaded += 1
                        self.logger.info(f"✅ Preloaded {file_name}")
                    else:
                        self.logger.warning(f"❌ Failed to cache {file_name}")
                else:
                    self.logger.warning(f"❌ Failed to process {file_name}")
                
            except Exception as e:
                self.logger.error(f"Error preloading {file_name}: {e}")
                import traceback
                self.logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Add small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)
        
        self.logger.info(f"Preloading complete: {preloaded} files cached")
        return preloaded
