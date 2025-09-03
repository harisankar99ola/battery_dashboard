from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import Optional
import pandas as pd
import os
from dotenv import load_dotenv

from drive_handler import GoogleDriveHandler
from data_processor import BatteryDataProcessor
from cache_manager import DataCacheManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Battery Dashboard API",
    description="API for battery data analysis and visualization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers - will be set during startup
drive_handler = None
data_processor = BatteryDataProcessor()
cache_manager = DataCacheManager()

# Configuration
DRIVE_FOLDER_ID = "1Ixvo_rJZ_9jni3R6HdAJnL_gvEF4tI5l"

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global drive_handler
    print("🚀 Battery Dashboard API starting up...")
    
    try:
        # Look for credentials in parent directory
        current_dir = os.getcwd()
        parent_dir = os.path.join(current_dir, '..', '..')
        credentials_path = os.path.join(parent_dir, 'credentials.json')
        
        if os.path.exists(credentials_path):
            # Change to parent directory temporarily for authentication
            original_dir = os.getcwd()
            os.chdir(parent_dir)
            drive_handler = GoogleDriveHandler()
            os.chdir(original_dir)
            
            # Test Google Drive connection
            folders = drive_handler.get_battery_test_folders(DRIVE_FOLDER_ID)
            print(f"✅ Connected to Google Drive folder: {DRIVE_FOLDER_ID}")
            print(f"🗂️ Found {len(folders)} battery test folders")
            
            # Clear expired cache entries
            cache_manager.clear_expired_cache()
            
            # Get popular files for preloading
            try:
                all_files = drive_handler.get_all_csv_files_recursive(DRIVE_FOLDER_ID)
                if all_files:
                    print(f"📁 Found {len(all_files)} CSV files total")
                    
                    # Sort by modification time (most recent first) and size (reasonable size files first)
                    popular_files = sorted(all_files, 
                                         key=lambda x: (x.get('modifiedTime', ''), -int(x.get('size', 0))))
                    
                    # Start background preloading of first 10 files
                    import asyncio
                    asyncio.create_task(cache_manager.preload_popular_files(drive_handler, popular_files, max_files=10))
                    print("🔄 Started background preloading of popular files...")
                    
            except Exception as e:
                print(f"⚠️ Could not start preloading: {e}")
            
        else:
            print(f"❌ Credentials file not found at: {credentials_path}")
            print("⚠️  API will run in limited mode without Google Drive access")
            
    except Exception as e:
        print(f"❌ Error connecting to Google Drive: {e}")
        print("⚠️  API will run in limited mode without Google Drive access")
        drive_handler = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Battery Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "battery-dashboard-api"}

@app.get("/all-csv-files")
async def get_all_csv_files():
    """Get ALL CSV files from the entire folder structure (with cache support)"""
    if drive_handler is None:
        raise HTTPException(status_code=503, detail="Google Drive service not available. Please check credentials and restart the application.")
        
    try:
        # Get cached files first
        cached_files = cache_manager.get_all_cached_files_metadata()
        
        # Get all files from Drive
        all_files = drive_handler.get_all_csv_files_recursive(DRIVE_FOLDER_ID)
        
        # Format files with additional info for the frontend
        formatted_files = []
        for file in all_files:
            # Check if file is cached
            cached_info = next((cf for cf in cached_files if cf['file_id'] == file['id']), None)
            
            # Calculate file size in MB
            size_mb = 0
            if file.get('size'):
                try:
                    size_mb = int(file['size']) / (1024 * 1024)
                except (ValueError, TypeError):
                    size_mb = 0
            
            formatted_file = {
                'id': file['id'],
                'name': file['name'],
                'display_name': file['name'],  # Add display_name for frontend
                'size': file.get('size', '0'),
                'size_mb': round(size_mb, 2),
                'modifiedTime': file.get('modifiedTime', ''),
                'path': file.get('full_path', file['name']),
                'folder_path': file.get('folder_path', 'Root'),
                'parents': file.get('parents', []),
                'cached': cached_info is not None,
                'column_count': cached_info['column_count'] if cached_info else None,
                'row_count': cached_info['row_count'] if cached_info else None,
                'columns': cached_info['columns'] if cached_info else [],
                'column_types': cached_info['column_types'] if cached_info else {}
            }
            formatted_files.append(formatted_file)
        
        # Sort by cached status (cached first), then by modification time
        formatted_files.sort(key=lambda x: (not x['cached'], x.get('modifiedTime', '')), reverse=True)
        
        cache_stats = cache_manager.get_cache_stats()
        
        return {
            "files": formatted_files,
            "total_count": len(formatted_files),
            "cached_count": len(cached_files),
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        print(f"Error in get_all_csv_files: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching CSV files: {str(e)}")

@app.get("/folders")
async def get_folders():
    """Get all battery test folders with hierarchy info - DEPRECATED, use /all-csv-files instead"""
    try:
        folders = drive_handler.get_battery_test_folders(DRIVE_FOLDER_ID)
        # Add hierarchy information
        structured_folders = []
        for folder in folders:
            # Check if folder has subfolders
            subfolders = drive_handler.get_subfolders(folder['id'])
            folder_info = {
                'id': folder['id'],
                'name': folder['name'],
                'full_path': folder.get('full_path', ''),
                'csv_count': len(folder.get('csv_files', [])),
                'has_subfolders': len(subfolders) > 0,
                'subfolders': subfolders
            }
            structured_folders.append(folder_info)
        
        return structured_folders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching folders: {str(e)}")

@app.get("/subfolders/{folder_id}")
async def get_subfolders(folder_id: str):
    """Get subfolders of a specific folder"""
    try:
        subfolders = drive_handler.get_subfolders(folder_id)
        # Add CSV file count for each subfolder
        structured_subfolders = []
        for subfolder in subfolders:
            csv_files = drive_handler.get_csv_files_in_folder(subfolder['id'])
            subfolder_info = {
                'id': subfolder['id'],
                'name': subfolder['name'],
                'csv_count': len(csv_files)
            }
            structured_subfolders.append(subfolder_info)
        
        return structured_subfolders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subfolders: {str(e)}")

@app.get("/files/{folder_id}")
async def get_files_in_folder(folder_id: str):
    """Get CSV files in a specific folder"""
    try:
        csv_files = drive_handler.get_csv_files_in_folder(folder_id)
        # Format files with folder name for frontend compatibility
        formatted_files = []
        for file in csv_files:
            file_info = {
                'id': file['id'],
                'name': file['name'],
                'size': file.get('size', 0),
                'modified': file.get('modifiedTime', ''),
                'folder_name': file.get('name', 'Unknown')  # Add folder_name that frontend expects
            }
            formatted_files.append(file_info)
        
        return formatted_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")

@app.get("/columns/{file_id}")
async def get_file_columns(file_id: str):
    """Get available columns in a CSV file"""
    try:
        content = drive_handler.download_file_to_memory(file_id)
        df = data_processor.process_csv_content(content, sample_size=10)
        column_types = data_processor.identify_column_types(df)
        return column_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing columns: {str(e)}")

@app.get("/data/{file_id}")
async def get_file_data(
    file_id: str,
    selected_columns: Optional[str] = Query(None, description="Comma-separated list of columns"),
    preprocess: bool = Query(False, description="Apply preprocessing"),
    resample: Optional[str] = Query(None, description="Resample rate"),
    preview_only: bool = Query(False, description="Load only preview data for quick stats"),
    max_rows: Optional[int] = Query(None, description="Maximum number of rows to load")
):
    """Get processed data from a CSV file (with cache support)"""
    try:
        # Try to get from cache first
        df = cache_manager.get_cached_data(file_id)
        
        if df is None:
            # Not in cache, download from Drive
            if drive_handler is None:
                raise HTTPException(status_code=503, detail="Google Drive service not available")
            
            print(f"Cache miss for {file_id}, downloading from Google Drive...")
            
            # Download and process the file
            content = drive_handler.download_file_to_memory(file_id)
            df = data_processor.process_csv_content(content)
            
            if df is None or df.empty:
                raise HTTPException(status_code=404, detail="File not found or empty")
            
            # Cache the downloaded data
            try:
                file_info = drive_handler.get_file_info(file_id)
                file_name = file_info.get('name', f'file_{file_id}')
                cache_manager.cache_data(file_id, file_name, df, drive_handler)
                print(f"✅ Cached data for {file_name}")
            except Exception as e:
                print(f"⚠️ Failed to cache data: {e}")
        else:
            print(f"Cache hit for {file_id}")
        
        # Make a copy for processing to avoid modifying cached data
        df_processed = df.copy()
        
        # For preview mode, limit rows early for performance
        if preview_only and max_rows:
            df_processed = df_processed.head(max_rows)
        
        # Filter columns if specified
        if selected_columns:
            cols = [col.strip() for col in selected_columns.split(',')]
            valid_cols = [col for col in cols if col in df_processed.columns]
            if valid_cols:
                df_processed = df_processed[valid_cols]
        
        # Apply preprocessing if requested (skip for preview mode for speed)
        if preprocess and not preview_only:
            df_processed = data_processor.apply_preprocessing(df_processed)
        
        # Apply resampling if requested  
        if resample and not preview_only:
            df_processed = data_processor.resample_data(df_processed, resample)
        
        # Get column types and statistics
        column_types_dict = data_processor.identify_column_types(df_processed)
        
        # Extract specific column lists (matching the cache manager approach)
        time_cols = column_types_dict.get('time', [])
        voltage_cols = column_types_dict.get('cell_voltages', [])
        current_cols = column_types_dict.get('current', [])
        temp_cols = (column_types_dict.get('temp_cols', []) + 
                    column_types_dict.get('thermocouple', []) + 
                    column_types_dict.get('temp_stats', []))
        soc_cols = column_types_dict.get('soc_soh', [])
        
        # Build other_cols list
        categorized_cols = set(time_cols + voltage_cols + current_cols + temp_cols + soc_cols)
        other_cols = [col for col in df_processed.columns if col not in categorized_cols]
        
        # Create response format column types - include both old and new format for compatibility
        column_types = {
            "time_columns": time_cols,
            "voltage_columns": voltage_cols,
            "current_columns": current_cols,
            "temperature_columns": temp_cols,
            "soc_columns": soc_cols,
            "other_columns": other_cols,
            # Also include individual categories for frontend plot detection
            "thermocouple": column_types_dict.get('thermocouple', []),
            "temp_stats": column_types_dict.get('temp_stats', []),
            "temp_cols": column_types_dict.get('temp_cols', []),
            "cell_voltages": column_types_dict.get('cell_voltages', []),
            "soc_soh": column_types_dict.get('soc_soh', []),
            "temperature": column_types_dict.get('temperature', [])
        }
        stats = data_processor.calculate_statistics(df_processed)
        
        # For preview mode, return minimal data
        if preview_only:
            preview_data = {
                "data": df_processed.head(100).to_dict('records'),  # Only first 100 rows
                "index": df_processed.head(100).index.tolist() if hasattr(df_processed.index, 'tolist') else list(df_processed.head(100).index),
                "columns": df_processed.columns.tolist(),
                "statistics": {
                    "shape": df_processed.shape,
                    "column_types": column_types,
                    "total_rows": len(df),  # Original full count for stats
                    **stats
                },
                "preview_mode": True
            }
            # Clean data for JSON serialization
            return data_processor.clean_for_json(preview_data)
        
        full_data = {
            "data": df.to_dict('records'),
            "index": df.index.tolist() if hasattr(df.index, 'tolist') else list(df.index),
            "columns": df.columns.tolist(),
            "statistics": {
                "shape": df.shape,
                "column_types": column_types,
                **stats
            }
        }
        # Clean data for JSON serialization
        return data_processor.clean_for_json(full_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ---------------------------------------------------------------------------
# Alias endpoints for new /api/* path used by simplified frontend
# ---------------------------------------------------------------------------
@app.get("/api/columns/{file_id}")
async def api_get_file_columns(file_id: str):
    """Alias of /columns for backward/forward compatibility."""
    return await get_file_columns(file_id)  # Reuse existing logic

@app.get("/api/data/{file_id}")
async def api_get_file_data(
    file_id: str,
    selected_columns: Optional[str] = Query(None, description="Comma-separated list of columns"),
    preprocess: bool = Query(False, description="Apply preprocessing"),
    resample: Optional[str] = Query(None, description="Resample rate"),
    preview_only: bool = Query(False, description="Load only preview data for quick stats"),
    max_rows: Optional[int] = Query(None, description="Maximum number of rows to load")
):
    """Alias of /data for backward/forward compatibility."""
    return await get_file_data(
        file_id=file_id,
        selected_columns=selected_columns,
        preprocess=preprocess,
        resample=resample,
        preview_only=preview_only,
        max_rows=max_rows
    )

@app.post("/combine")
async def combine_files(request: dict):
    """Combine multiple CSV files"""
    try:
        file_ids = request.get("file_ids", [])
        if len(file_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 files required for combining")
        
        combined_data = data_processor.combine_datasets(file_ids, drive_handler)
        return combined_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining files: {str(e)}")

@app.get("/download/processed-data")
async def download_processed_data(
    file_ids: str = Query(..., description="Comma-separated file IDs"),
    selected_columns: Optional[str] = Query(None, description="Comma-separated column names")
):
    """Download processed data as CSV"""
    try:
        file_id_list = file_ids.split(',')
        
        if len(file_id_list) == 1:
            # Single file download
            content = drive_handler.download_file_to_memory(file_id_list[0])
            df = data_processor.process_csv_content(content)
        else:
            # Multiple files - combine them
            combined_data = data_processor.combine_datasets(file_id_list, drive_handler)
            df = pd.DataFrame(combined_data["data"])
        
        # Filter columns if specified
        if selected_columns:
            cols = [col.strip() for col in selected_columns.split(',')]
            valid_cols = [col for col in cols if col in df.columns]
            if valid_cols:
                df = df[valid_cols]
        
        # Convert to CSV
        csv_content = df.to_csv(index=False)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=battery_data.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading data: {str(e)}")

@app.post("/api/analysis/soc-temperature")
async def analyze_soc_temperature(request: dict):
    """Analyze SOC vs Temperature relationship"""
    try:
        file_id = request.get("file_id")
        temperature_columns = request.get("temperature_columns", [])
        
        if not file_id or not temperature_columns:
            raise HTTPException(status_code=400, detail="Missing file_id or temperature_columns")
        
        # Download and process the file
        content = drive_handler.download_file_to_memory(file_id)
        df = data_processor.process_csv_content(content)
        
        # Get SOC column
        column_types = data_processor.identify_column_types(df)
        soc_columns = column_types.get('soc_soh', [])
        soc_col = None
        
        for col in soc_columns:
            if 'soc' in col.lower():
                soc_col = col
                break
        
        if not soc_col:
            raise HTTPException(status_code=400, detail="No SOC column found in data")
        
        # Create SOC bins (0-100% in 5% increments)
        soc_bins = list(range(0, 101, 5))  # [0, 5, 10, ..., 95, 100]
        
        # Initialize result data
        result_data = {
            "soc_points": soc_bins,
            "temperature_data": {}
        }
        
        # For each temperature column, find average temperature at each SOC point
        for temp_col in temperature_columns:
            if temp_col not in df.columns:
                continue
                
            temp_at_soc = []
            for soc_point in soc_bins:
                # Find data points within ±2.5% of target SOC
                soc_mask = (df[soc_col] >= soc_point - 2.5) & (df[soc_col] <= soc_point + 2.5)
                
                if soc_mask.any():
                    avg_temp = df.loc[soc_mask, temp_col].mean()
                    temp_at_soc.append(float(avg_temp))
                else:
                    temp_at_soc.append(None)  # NA for unavailable SOC points
            
            result_data["temperature_data"][temp_col] = temp_at_soc
        
        return {
            "success": True,
            "data": result_data,
            "soc_column": soc_col,
            "message": f"SOC vs Temperature analysis for {len(temperature_columns)} sensors"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in SOC-Temperature analysis: {str(e)}")

@app.get("/api/analysis/efficiency/{file_id}")
async def get_efficiency_analysis(file_id: str):
    """Calculate battery efficiency metrics"""
    try:
        content = drive_handler.download_file_to_memory(file_id)
        df = data_processor.process_csv_content(content)
        
        # Look for current and voltage columns to calculate efficiency
        current_cols = [col for col in df.columns if 'current' in col.lower() or 'pack_current' in col.lower()]
        voltage_cols = [col for col in df.columns if 'pack_voltage' in col.lower() or 'voltage_pack' in col.lower()]
        soc_cols = [col for col in df.columns if 'soc' in col.lower() and 'pack' in col.lower()]
        
        efficiency_metrics = {"round_trip_efficiency": 0.0}
        
        if current_cols and voltage_cols and soc_cols:
            current_col = current_cols[0]
            voltage_col = voltage_cols[0] 
            # Note: soc_col available for future efficiency calculations
            
            # Calculate energy during charge and discharge
            df_with_power = df.copy()
            df_with_power['power'] = df_with_power[current_col] * df_with_power[voltage_col]
            
            # Separate charge and discharge based on current direction
            charge_mask = df_with_power[current_col] > 0
            discharge_mask = df_with_power[current_col] < 0
            
            if charge_mask.any() and discharge_mask.any():
                # Calculate energy (integrate power over time)
                time_diff = 1  # Assuming 1-second intervals
                charge_energy = (df_with_power.loc[charge_mask, 'power'] * time_diff).sum() / 3600  # Wh
                discharge_energy = abs((df_with_power.loc[discharge_mask, 'power'] * time_diff).sum()) / 3600  # Wh
                
                if charge_energy > 0:
                    efficiency = discharge_energy / charge_energy
                    efficiency_metrics["round_trip_efficiency"] = min(efficiency, 1.0)  # Cap at 100%
        
        return {
            "success": True,
            "efficiency_metrics": efficiency_metrics,
            "message": "Efficiency analysis completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating efficiency: {str(e)}")

@app.get("/api/analysis/duration/{file_id}")
async def get_test_duration(file_id: str):
    """Calculate test duration from timestamp data"""
    try:
        content = drive_handler.download_file_to_memory(file_id)
        df = data_processor.process_csv_content(content)
        
        # Look for time columns
        time_cols = [col for col in df.columns if 'time' in col.lower()]
        
        if not time_cols:
            return {
                "success": False,
                "duration_hours": 0,
                "message": "No time column found"
            }
        
        time_col = time_cols[0]
        
        # Try to convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            try:
                df[time_col] = pd.to_datetime(df[time_col])
            except Exception:
                # If datetime conversion fails, assume it's in seconds from start
                if df[time_col].dtype in ['int64', 'float64']:
                    duration_seconds = df[time_col].max() - df[time_col].min()
                    duration_hours = duration_seconds / 3600
                    return {
                        "success": True,
                        "duration_hours": float(duration_hours),
                        "message": f"Duration calculated from numeric time: {duration_hours:.2f}h"
                    }
                else:
                    return {
                        "success": False,
                        "duration_hours": 0,
                        "message": "Could not parse time column"
                    }
        
        # Calculate duration from datetime
        duration = df[time_col].max() - df[time_col].min()
        duration_hours = duration.total_seconds() / 3600
        
        return {
            "success": True,
            "duration_hours": float(duration_hours),
            "start_time": df[time_col].min().isoformat() if hasattr(df[time_col].min(), 'isoformat') else str(df[time_col].min()),
            "end_time": df[time_col].max().isoformat() if hasattr(df[time_col].max(), 'isoformat') else str(df[time_col].max()),
            "message": f"Test duration: {duration_hours:.2f} hours"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating duration: {str(e)}")

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics and performance metrics"""
    try:
        stats = cache_manager.get_cache_stats()
        cached_files = cache_manager.get_all_cached_files_metadata()
        
        # Add more detailed stats
        stats['cached_files'] = []
        for file_info in cached_files:
            file_stats = {
                'file_id': file_info['file_id'],
                'file_name': file_info['file_name'],
                'row_count': file_info['row_count'],
                'column_count': file_info['column_count'],
                'last_updated': file_info['last_updated'],
                'memory_usage_mb': file_info['data_preview'].get('memory_usage_mb', 0)
            }
            stats['cached_files'].append(file_stats)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@app.post("/cache/clear")
async def clear_cache():
    """Clear expired cache entries"""
    try:
        cache_manager.clear_expired_cache()
        stats = cache_manager.get_cache_stats()
        return {
            "message": "Cache cleared successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
