#!/usr/bin/env python3

import sys
import traceback
sys.path.append('.')

from drive_handler import GoogleDriveHandler
from data_processor import BatteryDataProcessor

def test_data_loading():
    print("Testing data loading...")
    
    try:
        # Initialize handlers
        drive_handler = GoogleDriveHandler()
        data_processor = BatteryDataProcessor()
        
        # Test file ID from the user's selection
        file_id = "1xjwrWod6t32nwKyV44UthMa_n8MDofWk"
        
        print(f"1. Downloading file {file_id}...")
        content = drive_handler.download_file_to_memory(file_id)
        print(f"   Downloaded {len(content)} bytes")
        
        print("2. Processing CSV content...")
        df = data_processor.process_csv_content(content)
        print(f"   Processed DataFrame shape: {df.shape}")
        print(f"   Columns: {list(df.columns[:5])}...")  # First 5 columns
        
        print("3. Identifying column types...")
        column_types = data_processor.identify_column_types(df)
        print(f"   Column types: {column_types}")
        
        print("4. Calculating statistics...")
        stats = data_processor.calculate_statistics(df)
        print(f"   Stats keys: {list(stats.keys())}")
        
        print("✅ All steps completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading()
