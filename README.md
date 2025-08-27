# 🔋 Battery Dashboard

A comprehensive battery analysis tool with web-based dashboard for SOC (State of Charge) analysis, Google Drive integration, and real-time data visualization.

## 🚀 Features

- **Interactive Dashboard**: Web-based interface for battery data analysis
- **Google Drive Integration**: Seamless file upload and management
- **SOC Analysis**: State of Charge vs Temperature plotting and analysis
- **Real-time Visualization**: Dynamic plots with efficiency metrics
- **Batch Processing**: Automated data extraction and processing
- **Export Capabilities**: Download results in various formats

## 📋 Prerequisites

- Python 3.8 or higher
- Git installed on your system
- Google Drive API credentials (see setup instructions below)

## 🛠️ Installation Methods

### Method 1: Quick Install (Recommended)

1. **Download and run the installer:**
   ```cmd
   curl -o installer.bat https://raw.githubusercontent.com/harisankar99ola/battery_dashboard/main/installer.bat
   installer.bat
   ```

2. **Or download manually:**
   - Download `installer.bat` from the repository
   - Double-click to run the installer

### Method 2: Manual Installation

1. **Clone the repository:**
   ```cmd
   git clone https://github.com/harisankar99ola/battery_dashboard.git
   cd battery_dashboard
   ```

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Setup Google Drive credentials** (see below)

4. **Run the application:**
   ```cmd
   python src/main.py
   ```

## 🔑 Google Drive API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it

### Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Download the credentials JSON file
5. Rename it to `credentials.json` and place in project root

### Step 3: First Run Authentication

1. Run the application: `python src/main.py`
2. Browser will open for Google authentication
3. Grant permissions to access Google Drive
4. `token.json` will be created automatically

## 🚀 Usage

### Starting the Application

```cmd
python src/main.py
```

The application will:
- Start the backend server (port 8000)
- Start the frontend dashboard (port 8050)
- Automatically open your browser to http://localhost:8050

### Using the Dashboard

1. **Upload Files**: Use the file upload component to upload battery data
2. **Select Analysis**: Choose SOC analysis or other available options
3. **View Results**: Interactive plots and metrics will be displayed
4. **Download Results**: Use download buttons to save analysis results

### Available Endpoints

- **Frontend Dashboard**: http://localhost:8050
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
battery_dashboard/
├── src/
│   ├── main.py                 # Application entry point
│   ├── backend/               # FastAPI backend
│   │   ├── main.py           # Backend server
│   │   ├── upload_handler.py # File upload logic
│   │   ├── soc_analyzer.py   # SOC analysis
│   │   └── ...
│   └── frontend/             # Dash frontend
│       ├── app.py           # Frontend application
│       ├── components/      # Dash components
│       └── ...
├── requirements.txt          # Project dependencies
├── installer.bat            # Windows installer script
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## � Configuration

### Environment Variables

Create a `.env` file in the project root for custom configuration:

```env
BACKEND_PORT=8000
FRONTEND_PORT=8050
UPLOAD_FOLDER=uploads
DEBUG=False
```

### Custom Settings

Modify `src/main.py` to change:
- Server ports
- Auto-browser launch behavior
- Credential file locations
## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```
   Error: [Errno 48] Address already in use
   ```
   **Solution**: Kill processes on ports 8000/8050 or change ports in configuration

2. **Google API credentials error:**
   ```
   Error: The file credentials.json was not found
   ```
   **Solution**: Ensure `credentials.json` is in project root and properly configured

3. **Browser doesn't open automatically:**
   - Manually navigate to http://localhost:8050
   - Check firewall settings

4. **Module import errors:**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Solution**: Run `pip install -r requirements.txt`

### Debug Mode

Run with debug logging:
```cmd
python src/main.py --debug
```

## 📊 Data Formats

### Supported File Types
- CSV files with battery test data
- Excel files (.xlsx, .xls)
- JSON formatted battery data

### Expected Data Columns
- Time/Timestamp
- Voltage
- Current
- Temperature
- SOC (State of Charge)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Harisankar Suresh** - *Initial work* - [harisankar99ola](https://github.com/harisankar99ola)

## 🙏 Acknowledgments

- PyBAMM community for battery modeling frameworks
- Plotly/Dash for excellent visualization tools
- FastAPI for the robust backend framework

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing [GitHub Issues](https://github.com/harisankar99ola/battery_dashboard/issues)
3. Create a new issue with detailed description

## 🔄 Updates

Check for updates regularly:
```cmd
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Happy Battery Analysis! 🔋⚡**

### Data Access
- `GET /api/folders` - List available test folders
- `GET /api/files` - Get CSV files from folders
- `GET /api/data/{file_id}` - Load and process data file
- `POST /api/data/combine` - Combine multiple datasets

### Analysis
- `GET /api/analysis/temperature-stats/{file_id}` - Temperature statistics
- `GET /api/analysis/voltage-stats/{file_id}` - Voltage statistics  
- `POST /api/analysis/soc-temperature` - SOC-temperature relationships
- `GET /api/analysis/phases/{file_id}` - Test phase detection
- `GET /api/analysis/efficiency/{file_id}` - Energy efficiency metrics

## 🛠️ Development

### Adding New Plot Types

1. **Backend**: Add analysis endpoints in `backend/main.py`
2. **Data Processing**: Extend `data_processor.py` with new analysis functions
3. **Frontend**: Add plot generation in `frontend/components/plots.py`
4. **UI**: Update plot type dropdown in `frontend/app.py`

### Custom Data Processing

Extend the `BatteryDataProcessor` class to add new analysis capabilities:

```python
def custom_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
    """Add your custom analysis here"""
    # Your analysis logic
    return results
```

### Adding Authentication

For production deployment, implement Google OAuth:

1. Configure OAuth credentials
2. Add authentication middleware
3. Implement domain restrictions
4. Add user session management

## 🔧 Configuration

### Environment Variables
- `DRIVE_FOLDER_ID`: Google Drive folder ID for data access
- `API_HOST`/`API_PORT`: Backend server configuration
- `DASH_HOST`/`DASH_PORT`: Dashboard server configuration

### Google Drive Setup
1. Create Google Cloud Project
2. Enable Google Drive API
3. Create service account credentials
4. Share your data folder with the service account email

## 📈 Performance Optimization

- **Data Sampling**: Large datasets are automatically sampled for visualization
- **Chunked Loading**: Files are loaded in chunks to prevent memory issues
- **Caching**: Processed data is cached to improve response times
- **Async Processing**: Backend uses async operations for better performance

## 🐛 Troubleshooting

### Common Issues

1. **"No folders found"**: Check Google Drive credentials and folder permissions
2. **"Import errors"**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **"Connection refused"**: Verify backend is running on port 8000
4. **"Empty plots"**: Check data format and column naming conventions

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

**Built with ❤️ for advanced battery data analysis**
