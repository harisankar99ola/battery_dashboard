from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Optional, Any
import pandas as pd
import os
from dotenv import load_dotenv
import json

from drive_handler import GoogleDriveHandler
from data_processor import BatteryDataProcessor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Battery Data Dashboard API",
    description="API for battery testing data analysis and visualization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
drive_handler = GoogleDriveHandler()
data_processor = BatteryDataProcessor()

# Configuration
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1Ixvo_rJZ_9jni3R6HdAJnL_gvEF4tI5l")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Battery Dashboard API starting up...")
    print(f"📁 Connected to Google Drive folder: {DRIVE_FOLDER_ID}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Battery Data Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "battery-dashboard-api"}

# Simple endpoints for frontend compatibility
@app.get("/folders")
async def get_folders():
    """Get all battery test folders (simplified)"""
    try:
        folders = drive_handler.get_battery_test_folders(DRIVE_FOLDER_ID)
        return folders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching folders: {str(e)}")

@app.get("/files/{folder_id}")
async def get_files_in_folder(folder_id: str):
    """Get CSV files in a specific folder (simplified)"""
    try:
        files = drive_handler.get_csv_files_in_folder(folder_id)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")

@app.get("/columns/{file_id}")
async def get_file_columns(file_id: str):
    """Get available columns in a CSV file"""
    try:
        # Get file content to analyze columns
        content = drive_handler.download_file_content(file_id)
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
    resample: Optional[str] = Query(None, description="Resample rate")
):
    """Get processed data from a CSV file"""
    try:
        content = drive_handler.download_file_content(file_id)
        df = data_processor.process_csv_content(content)
        
        # Filter columns if specified
        if selected_columns:
            cols = [col.strip() for col in selected_columns.split(',')]
            # Only include columns that exist in the dataframe
            valid_cols = [col for col in cols if col in df.columns]
            if valid_cols:
                df = df[valid_cols]
        
        # Apply preprocessing if requested
        if preprocess:
            df = data_processor.apply_preprocessing(df)
        
        # Apply resampling if requested  
        if resample:
            df = data_processor.resample_data(df, resample)
        
        # Get column types and statistics
        column_types = data_processor.identify_column_types(df)
        stats = data_processor.calculate_statistics(df)
        
        return {
            "data": df.to_dict('records'),
            "index": df.index.tolist() if hasattr(df.index, 'tolist') else list(df.index),
            "columns": df.columns.tolist(),
            "statistics": {
                "shape": df.shape,
                "column_types": column_types,
                **stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

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
            content = drive_handler.download_file_content(file_id_list[0])
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

@app.get("/api/folders")
async def get_battery_test_folders():
    """Get all battery test folders from Google Drive"""
    try:
        folders = drive_handler.get_battery_test_folders(DRIVE_FOLDER_ID)
        return {
            "success": True,
            "folders": folders,
            "count": len(folders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching folders: {str(e)}")

@app.get("/api/folder/{folder_path:path}")
async def get_folder_structure(folder_path: str):
    """Get folder structure for a specific path"""
    try:
        # This would need to be implemented to navigate to specific folder paths
        structure = drive_handler.get_folder_structure(DRIVE_FOLDER_ID)
        return {
            "success": True,
            "structure": structure
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching folder structure: {str(e)}")

@app.get("/api/files")
async def get_csv_files(
    folder_id: Optional[str] = Query(None, description="Specific folder ID to search"),
    search_pattern: Optional[str] = Query(None, description="Search pattern for file names")
):
    """Get CSV files from Google Drive"""
    try:
        if search_pattern:
            files = drive_handler.search_files(search_pattern, folder_id or DRIVE_FOLDER_ID)
        elif folder_id:
            files = drive_handler.get_csv_files_in_folder(folder_id)
        else:
            files = drive_handler.get_csv_files_in_folder(DRIVE_FOLDER_ID)
        
        # Filter only CSV files
        csv_files = [f for f in files if f.get('name', '').lower().endswith('.csv')]
        
        return {
            "success": True,
            "files": csv_files,
            "count": len(csv_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")

@app.get("/api/data/{file_id}")
async def get_file_data(
    file_id: str,
    preprocess: bool = Query(True, description="Whether to preprocess the data"),
    resample: Optional[str] = Query(None, description="Resampling frequency (e.g., '1S', '10S')"),
    selected_columns: Optional[str] = Query(None, description="Comma-separated list of columns to load")
):
    """Get data from a specific CSV file with optional column selection"""
    try:
        # Download and read CSV file
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found or could not be read")
        
        # Get column types before any filtering
        column_types = data_processor.identify_column_types(df)
        
        # Filter columns if specified
        if selected_columns:
            requested_cols = [col.strip() for col in selected_columns.split(',')]
            # Always include time column if available
            time_cols = column_types.get('time', [])
            if time_cols:
                requested_cols.extend(time_cols)
            
            # Filter to only existing columns
            available_cols = [col for col in requested_cols if col in df.columns]
            if available_cols:
                df = df[available_cols]
        
        # Preprocess if requested
        if preprocess:
            df = data_processor.preprocess_dataframe(df)
            
            if resample:
                df = data_processor.resample_data(df, resample)
        
        # Recalculate column types after filtering
        column_types = data_processor.identify_column_types(df)
        
        # Calculate basic statistics
        stats = {
            "shape": df.shape,
            "columns": list(df.columns),
            "column_types": column_types,
            "time_range": {
                "start": float(df.index.min()) if len(df) > 0 else None,
                "end": float(df.index.max()) if len(df) > 0 else None,
                "duration": float(df.index.max() - df.index.min()) if len(df) > 0 else None
            }
        }
        
        return {
            "success": True,
            "data": df.to_dict('records'),
            "index": df.index.tolist(),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file data: {str(e)}")

@app.get("/api/columns/{file_id}")
async def get_file_columns(file_id: str):
    """Get available columns from a CSV file"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        column_types = data_processor.identify_column_types(df)
        
        return {
            "success": True,
            "columns": list(df.columns),
            "column_types": column_types,
            "total_columns": len(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting columns: {str(e)}")

@app.post("/api/download/processed-data")
async def download_processed_data(
    file_ids: List[str],
    selected_columns: Optional[List[str]] = None,
    x_axis: str = "time",
    filters: Optional[Dict] = None
):
    """Download processed data with selected columns and filters"""
    try:
        if not file_ids:
            raise HTTPException(status_code=400, detail="No file IDs provided")
        
        combined_data = []
        
        for file_id in file_ids:
            df = drive_handler.get_csv_as_dataframe(file_id)
            if df is not None:
                df = data_processor.preprocess_dataframe(df)
                
                # Apply column selection
                if selected_columns:
                    # Always include time and x_axis columns
                    columns_to_include = selected_columns.copy()
                    column_types = data_processor.identify_column_types(df)
                    time_cols = column_types.get('time', [])
                    if time_cols and time_cols[0] not in columns_to_include:
                        columns_to_include.append(time_cols[0])
                    
                    if x_axis != "time" and x_axis in df.columns and x_axis not in columns_to_include:
                        columns_to_include.append(x_axis)
                    
                    available_cols = [col for col in columns_to_include if col in df.columns]
                    if available_cols:
                        df = df[available_cols]
                
                # Apply filters if specified
                if filters:
                    for column, filter_range in filters.items():
                        if column in df.columns and 'min' in filter_range and 'max' in filter_range:
                            df = df[(df[column] >= filter_range['min']) & (df[column] <= filter_range['max'])]
                
                combined_data.append(df)
        
        if not combined_data:
            raise HTTPException(status_code=404, detail="No valid data found")
        
        # Combine all dataframes
        final_df = data_processor.combine_datasets(combined_data)
        
        return {
            "success": True,
            "data": final_df.to_dict('records'),
            "columns": list(final_df.columns),
            "shape": final_df.shape,
            "csv_data": final_df.to_csv(index=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing download: {str(e)}")

@app.post("/api/data/combine")
async def combine_datasets(
    request: Dict[str, Any]
):
    """Combine multiple datasets"""
    try:
        file_ids = request.get("file_ids", [])
        labels = request.get("labels", [])
        selected_columns = request.get("selected_columns", [])
        
        if not file_ids:
            raise HTTPException(status_code=400, detail="No file IDs provided")
        
        # Download all datasets
        dataframes = []
        actual_labels = []
        
        for i, file_id in enumerate(file_ids):
            df = drive_handler.get_csv_as_dataframe(file_id)
            if df is not None:
                df = data_processor.preprocess_dataframe(df)
                
                # Apply column selection if specified
                if selected_columns:
                    column_types = data_processor.identify_column_types(df)
                    columns_to_include = selected_columns.copy()
                    # Always include time columns
                    time_cols = column_types.get('time', [])
                    if time_cols:
                        columns_to_include.extend(time_cols)
                    
                    available_cols = [col for col in columns_to_include if col in df.columns]
                    if available_cols:
                        df = df[available_cols]
                
                dataframes.append(df)
                label = labels[i] if labels and i < len(labels) else f"Dataset_{i+1}"
                actual_labels.append(label)
        
        if not dataframes:
            raise HTTPException(status_code=404, detail="No valid datasets found")
        
        # Combine datasets
        combined_df = data_processor.combine_datasets(dataframes, actual_labels)
        
        # Get combined statistics
        column_types = data_processor.identify_column_types(combined_df)
        
        stats = {
            "shape": combined_df.shape,
            "datasets_count": len(dataframes),
            "column_types": column_types,
            "datasets": list(combined_df['Dataset'].unique()) if 'Dataset' in combined_df.columns else actual_labels
        }
        
        return {
            "success": True,
            "data": combined_df.to_dict('records'),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining datasets: {str(e)}")

@app.get("/api/analysis/temperature-stats/{file_id}")
async def get_temperature_statistics(file_id: str):
    """Get temperature statistics for a dataset"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = data_processor.preprocess_dataframe(df)
        temp_stats = data_processor.calculate_temperature_statistics(df)
        
        # Convert Series to dict for JSON serialization
        stats_dict = {}
        for key, series in temp_stats.items():
            stats_dict[key] = {
                "data": series.tolist(),
                "index": series.index.tolist(),
                "mean": float(series.mean()),
                "max": float(series.max()),
                "min": float(series.min()),
                "std": float(series.std())
            }
        
        return {
            "success": True,
            "temperature_statistics": stats_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating temperature statistics: {str(e)}")

@app.get("/api/analysis/voltage-stats/{file_id}")
async def get_voltage_statistics(file_id: str):
    """Get voltage statistics for a dataset"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = data_processor.preprocess_dataframe(df)
        voltage_stats = data_processor.calculate_voltage_statistics(df)
        
        # Convert Series to dict for JSON serialization
        stats_dict = {}
        for key, series in voltage_stats.items():
            stats_dict[key] = {
                "data": series.tolist(),
                "index": series.index.tolist(),
                "mean": float(series.mean()),
                "max": float(series.max()),
                "min": float(series.min()),
                "std": float(series.std())
            }
        
        return {
            "success": True,
            "voltage_statistics": stats_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating voltage statistics: {str(e)}")

@app.post("/api/analysis/soc-temperature")
async def derive_soc_temperature_relationship(
    file_id: str,
    temperature_columns: Optional[List[str]] = None
):
    """Derive SOC vs temperature relationship"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = data_processor.preprocess_dataframe(df)
        soc_temp_df = data_processor.derive_soc_temperature_relationship(
            df, temperature_columns
        )
        
        return {
            "success": True,
            "data": soc_temp_df.to_dict('records'),
            "index": soc_temp_df.index.tolist(),
            "columns": list(soc_temp_df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deriving SOC-temperature relationship: {str(e)}")

@app.get("/api/analysis/phases/{file_id}")
async def detect_test_phases(file_id: str):
    """Detect test phases (charge, discharge, rest)"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = data_processor.preprocess_dataframe(df)
        phases = data_processor.detect_test_phases(df)
        
        return {
            "success": True,
            "phases": phases,
            "phase_count": {phase: len(intervals) for phase, intervals in phases.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting test phases: {str(e)}")

@app.get("/api/analysis/efficiency/{file_id}")
async def calculate_energy_efficiency(file_id: str):
    """Calculate energy efficiency metrics"""
    try:
        df = drive_handler.get_csv_as_dataframe(file_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = data_processor.preprocess_dataframe(df)
        efficiency = data_processor.calculate_energy_efficiency(df)
        
        return {
            "success": True,
            "efficiency_metrics": efficiency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating efficiency: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
