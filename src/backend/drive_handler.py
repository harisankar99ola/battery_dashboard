import os
import io
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from pathlib import Path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Google Drive scope for read access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveHandler:
    def __init__(self, credentials_file: str = None, token_file: str = 'token.json'):
        self.credentials_file = credentials_file or 'client_secret_1022800559354-pa9vaklj5tco6oag3t9v1837nijlrt8l.apps.googleusercontent.com (1).json'
        self.token_file = token_file
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate and build Google Drive service"""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)

    def list_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """List all files and folders in a Google Drive folder"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, parents)",
                pageSize=1000
            ).execute()
            
            items = results.get('files', [])
            return items
        except Exception as e:
            print(f"Error listing folder contents: {e}")
            return []

    def get_folder_structure(self, folder_id: str, path: str = "") -> Dict[str, Any]:
        """Get hierarchical folder structure"""
        items = self.list_folder_contents(folder_id)
        structure = {
            'folders': [],
            'files': [],
            'path': path
        }
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                folder_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'path': f"{path}/{item['name']}" if path else item['name']
                }
                # Recursively get subfolder structure
                folder_info['contents'] = self.get_folder_structure(
                    item['id'], 
                    folder_info['path']
                )
                structure['folders'].append(folder_info)
            else:
                file_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'mimeType': item['mimeType'],
                    'size': item.get('size'),
                    'modifiedTime': item.get('modifiedTime'),
                    'path': f"{path}/{item['name']}" if path else item['name']
                }
                structure['files'].append(file_info)
        
        return structure

    def download_file_to_memory(self, file_id: str) -> bytes:
        """Download file content to memory"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_io.seek(0)
            return file_io.getvalue()
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get file information by file ID"""
        try:
            file_metadata = self.service.files().get(fileId=file_id, fields='id,name,size,modifiedTime').execute()
            return {
                'id': file_metadata.get('id'),
                'name': file_metadata.get('name'),
                'size': file_metadata.get('size'),
                'modified': file_metadata.get('modifiedTime')
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {'id': file_id, 'name': f'Unknown_{file_id}'}

    def get_csv_as_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """Download CSV file and return as pandas DataFrame"""
        try:
            file_content = self.download_file_to_memory(file_id)
            if file_content:
                df = pd.read_csv(io.BytesIO(file_content))
                return df
            return None
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def search_files(self, query: str, folder_id: str = None) -> List[Dict[str, Any]]:
        """Search files by name pattern"""
        try:
            search_query = f"name contains '{query}' and trashed=false"
            if folder_id:
                search_query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=search_query,
                fields="files(id, name, mimeType, size, modifiedTime, parents)",
                pageSize=1000
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error searching files: {e}")
            return []

    def get_csv_files_in_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get all CSV files in a specific folder"""
        items = self.list_folder_contents(folder_id)
        csv_files = []
        
        for item in items:
            # Check for CSV files by extension and MIME type
            if (item.get('name', '').lower().endswith('.csv') or 
                item.get('mimeType') == 'application/vnd.ms-excel' and 
                item.get('name', '').lower().endswith('.csv')):
                csv_files.append(item)
        
        return csv_files

    def get_subfolders(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get immediate subfolders of a folder"""
        items = self.list_folder_contents(folder_id)
        subfolders = []
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                subfolders.append({
                    'id': item['id'],
                    'name': item['name']
                })
        
        return subfolders

    def get_all_csv_files_recursive(self, root_folder_id: str) -> List[Dict[str, Any]]:
        """Get ALL CSV files from root folder and all subfolders recursively"""
        all_csv_files = []
        
        def scan_folder_for_csv(folder_id: str, folder_path: str = ""):
            try:
                items = self.list_folder_contents(folder_id)
                
                for item in items:
                    if item['mimeType'] == 'application/vnd.google-apps.folder':
                        # Recursively scan subfolders
                        subfolder_path = f"{folder_path}/{item['name']}" if folder_path else item['name']
                        scan_folder_for_csv(item['id'], subfolder_path)
                    
                    elif (item.get('name', '').lower().endswith('.csv') or 
                          item.get('mimeType') == 'application/vnd.ms-excel' and 
                          item.get('name', '').lower().endswith('.csv')):
                        # This is a CSV file
                        file_path = f"{folder_path}/{item['name']}" if folder_path else item['name']
                        
                        file_info = {
                            'id': item['id'],
                            'name': item['name'],
                            'full_path': file_path,
                            'folder_path': folder_path or "Root",
                            'size': item.get('size', 0),
                            'modified': item.get('modifiedTime', ''),
                            'mimeType': item.get('mimeType', '')
                        }
                        all_csv_files.append(file_info)
                        
            except Exception as e:
                print(f"Error scanning folder {folder_id}: {e}")
        
        # Start recursive scan from root folder
        scan_folder_for_csv(root_folder_id)
        
        # Sort files by folder path and then by name for better organization
        all_csv_files.sort(key=lambda x: (x['folder_path'], x['name']))
        
        return all_csv_files

    def get_battery_test_folders(self, root_folder_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Get battery test folders (folders containing CSV files) including subfolders"""
        test_folders = []
        
        def scan_folder_recursive(folder_id: str, path: str = "", depth: int = 0):
            if depth > max_depth:
                return
                
            items = self.list_folder_contents(folder_id)
            folders = [item for item in items if item['mimeType'] == 'application/vnd.google-apps.folder']
            
            # Check current folder for CSV files
            csv_files = self.get_csv_files_in_folder(folder_id)
            if csv_files:
                display_name = path.split('/')[-1] if path else "Root"
                # Truncate long names for better display
                if len(display_name) > 50:
                    display_name = display_name[:47] + "..."
                
                test_folders.append({
                    'id': folder_id,
                    'name': display_name,
                    'full_path': path,
                    'csv_files': csv_files,
                    'file_count': len(csv_files),
                    'depth': depth
                })
            
            # Recursively scan subfolders
            for folder in folders:
                folder_path = f"{path}/{folder['name']}" if path else folder['name']
                scan_folder_recursive(folder['id'], folder_path, depth + 1)
        
        scan_folder_recursive(root_folder_id)
        return test_folders
