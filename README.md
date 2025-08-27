# 🔋 Battery Dashboard

A comprehensive battery analysis tool with web-based dashboard for advanced battery data visualization, Google Drive integration, and real-time analysis capabilities. Features enhanced column detection, temperature analysis, SOC plotting, and automated data processing.

## ✨ Key Features

### 🎯 **Advanced Data Analysis**
- **Smart Column Detection**: Automatically detects thermocouple, temperature, SOC, and voltage columns
- **Multi-Temperature Analysis**: Support for 30+ temperature sensors (LH-/RH- thermocouples, BMS sensors)
- **SOC vs Temperature Plots**: Interactive analysis with heatmaps and statistical summaries
- **Voltage Analysis**: Cell voltage monitoring and balancing status
- **Real-time Efficiency Metrics**: Energy efficiency and round-trip calculations

### 🌐 **Seamless Integration**
- **Google Drive Integration**: Direct access to battery test data folders
- **Smart Caching**: Intelligent data caching for faster load times
- **Automatic File Detection**: Discovers CSV files across entire folder structures
- **Background Processing**: Preloads popular files for instant access

### 📊 **Interactive Dashboard**
- **Multi-Plot Support**: Overview, temperature heatmaps, voltage analysis, and more
- **Dynamic File Selection**: Easy file browsing with cache status indicators
- **Real-time Statistics**: Live data points, test duration, and efficiency metrics
- **Export Capabilities**: Download processed data and analysis results

### 🔧 **Enhanced User Experience**
- **One-Click Installation**: Automated installer with desktop shortcut
- **Auto-Launch**: Browser opens automatically to dashboard
- **Responsive UI**: Works on desktop and tablet devices
- **Debug Logging**: Comprehensive logging for troubleshooting

## 📋 Prerequisites

- Python 3.8 or higher
- Git installed on your system
- Google Drive API credentials (see setup instructions below)

## 🛠️ Installation Methods

### Method 1: Quick Install (Recommended for Windows)

1. **Download and run the installer:**
   ```cmd
   curl -o installer.bat https://raw.githubusercontent.com/harisankar99ola/battery_dashboard/main/installer.bat
   installer.bat
   ```

2. **Or download manually:**
   - Download `installer.bat` from the repository
   - Double-click to run the installer
   - Follow prompts to set up Google Drive credentials
   - Desktop shortcut "Battery Dashboard" will be created

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
   start.bat
   ```
   Or manually:
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

**Installed via installer:**
- Double-click "Battery Dashboard" desktop shortcut
- Or run `start.bat` from installation folder

**Manual installation:**
```cmd
start.bat
```
Or:
```cmd
python src/main.py
```

The application will:
- Start the backend server (port 8000)
- Start the frontend dashboard (port 8050)
- Automatically open your browser to http://localhost:8050

### Using the Dashboard

1. **Select Files**: Click "📂 Open File Selector" to browse battery test files
   - 🏎️ Cached files load instantly
   - 📡 Non-cached files download on demand
   
2. **Choose Analysis Type**: Select from available plot types:
   - **📊 Data Overview**: Basic statistics and data preview
   - **🌡️ Temperature Analysis**: Multi-sensor temperature plots
   - **🔥 Temperature Heatmap**: Spatial temperature distribution
   - **⚡ Voltage Analysis**: Cell voltage monitoring
   - **🔋 Current Analysis**: Current flow visualization
   - **🔋 SOC vs Temperature**: State of charge correlation analysis

3. **Configure Parameters**: 
   - Select specific temperature columns for detailed analysis
   - Choose data preprocessing options
   - Set resampling rates for performance

4. **View Results**: Interactive plots with:
   - Real-time statistics (data points, test duration, efficiency)
   - Downloadable analysis results
   - Export capabilities for further processing

### Column Detection Features

The dashboard automatically detects and categorizes:

- **Thermocouple Sensors**: `LH-C1-Busbar-T22_avg`, `RH-C2-Cell1-T94_avg`
- **BMS Temperature**: `BMS00_Pack_Temperature_01_avg` through `BMS00_Pack_Temperature_06_avg`
- **Battery Stats**: `Battery_Temperature_Max_00_avg`, `Effective_Battery_Temperature_00_avg`
- **SOC Data**: `Pack_SOC_00_avg`, `Pack_SoH_avg`
- **Cell Voltages**: `Cell_Voltage_Cell_1_avg` through `Cell_Voltage_Cell_14_avg`
- **Current/Power**: Automatically identified current and power measurements

### Available Endpoints

- **Frontend Dashboard**: http://localhost:8050
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
battery_dashboard/
├── src/
│   ├── main.py                    # Application entry point & launcher
│   ├── backend/                   # FastAPI backend services
│   │   ├── main_simple.py        # Main backend server (recommended)
│   │   ├── main.py              # Alternative backend server
│   │   ├── cache_manager.py     # Data caching system
│   │   ├── data_processor.py    # Enhanced column detection & analysis
│   │   ├── drive_handler.py     # Google Drive integration
│   │   └── ...
│   └── frontend/                 # Dash frontend application
│       ├── app.py               # Main dashboard interface
│       ├── components/          # Dashboard components
│       │   └── plots.py        # Plot generation & visualization
│       └── ...
├── start.bat                     # Windows application launcher
├── stop.bat                      # Stop all services
├── installer.bat                 # Automated Windows installer
├── setup_credentials.bat         # Google Drive credential setup
├── requirements.txt              # Project dependencies
├── .gitignore                   # Git ignore rules (protects sensitive data)
└── README.md                    # This documentation
```

## 🔧 Recent Improvements (Latest Release)

### ✨ Enhanced Column Detection
- **Smart Pattern Matching**: Detects DMD extractor output with `_avg` suffixes
- **Comprehensive Coverage**: Identifies 30+ temperature sensors, 14 voltage cells, SOC data
- **Debug Logging**: Detailed column detection feedback for troubleshooting

### 🐛 Bug Fixes
- **SOC Temperature Plots**: Fixed legend itemwidth error (now supports 30+ sensors)
- **File Name Display**: Proper file names shown in selection interface
- **Duration Calculation**: Enhanced time column detection and test duration display
- **UI Responsiveness**: Improved file selection and data loading experience

### 🛡️ Security Enhancements
- **Enhanced .gitignore**: Protects cache files, tokens, and sensitive data
- **Credential Safety**: Automatic exclusion of Google Drive credentials from version control
- **Data Privacy**: Local caching with no cloud storage of sensitive battery data

### 🚀 Performance Optimizations
- **Smart Caching**: Instant loading of previously accessed files
- **Background Preloading**: Popular files cached automatically
- **Efficient Column Processing**: Optimized detection algorithms

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

1. **"Only 1 column found" Error:**
   - **Cause**: Column detection patterns not matching your data format
   - **Solution**: Check that column names follow expected patterns (see Column Detection section)
   - **Debug**: Look for column detection debug output in terminal

2. **SOC vs Temperature Plot Error:**
   - **Cause**: Legend configuration issue (fixed in latest version)
   - **Solution**: Update to latest version or ensure itemwidth ≥ 30 in plot configuration

3. **File names not displaying:**
   - **Cause**: Missing display_name field (fixed in latest version)
   - **Solution**: Update to latest version for proper file name display

4. **Test duration shows "0h":**
   - **Cause**: Time column not detected properly
   - **Solution**: Ensure your data has a "Time" column or check debug logs for time detection

5. **Port already in use:**
   ```
   Error: [Errno 48] Address already in use
   ```
   **Solution**: 
   ```cmd
   stop.bat
   start.bat
   ```
   Or manually kill processes on ports 8000/8050

6. **Google API credentials error:**
   ```
   Error: The file credentials.json was not found
   ```
   **Solution**: Run `setup_credentials.bat` or ensure `credentials.json` is in project root

7. **Module import errors:**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Solution**: Run `pip install -r requirements.txt`

### Debug Mode

Run with debug logging:
```cmd
python src/main.py --debug
```

Or check terminal output for detailed column detection information:
```
🔍 Column detection debug:
  Total columns: 64
  Sample columns: ['Time', 'LH-C1-Busbar-T22_avg', ...]
  Thermocouple columns: 24 - ['LH-C1-Busbar-T22_avg', ...]
  Temp stats columns: 3 - ['Battery_Temperature_Max_00_avg', ...]
  SOC/SOH columns: 2 - ['Pack_SOC_00_avg', 'Pack_SoH_avg']
```

## 📊 Data Formats

### Supported File Types
- **CSV files**: Primary format for battery test data (from DMD extractor)
- **Excel files**: .xlsx, .xls formats supported
- **Google Drive**: Direct integration with shared folders

### Expected Data Columns

The system automatically detects columns with these patterns:

**Temperature Sensors:**
- `LH-C{X}-{Location}-T{XX}_avg` (Left side thermocouples)
- `RH-C{X}-{Location}-T{XX}_avg` (Right side thermocouples)  
- `BMS00_Pack_Temperature_{XX}_avg` (BMS temperature sensors)
- `Battery_Temperature_{Min/Max}_{XX}_avg` (Battery statistics)
- `Effective_Battery_Temperature_{XX}_avg` (Calculated temperatures)

**Electrical Data:**
- `Cell_Voltage_Cell_{X}_avg` (Individual cell voltages)
- `Pack_SOC_{XX}_avg` (State of charge)
- `Pack_SoH_avg` (State of health)
- `{X}_Current_{XX}_avg` (Current measurements)
- `{X}_Power_{XX}_avg` (Power measurements)

**Time Data:**
- `Time` (Primary time column, typically in seconds)
- Any column containing "time" or "timestamp"

### DMD Extractor Compatibility

This dashboard is designed to work with data processed by the DMD extraction automator, which:
- Adds `_avg` suffixes to all columns
- Rounds time values and groups by second intervals
- Processes thermocouples, BMS data, cell voltages, and SOC information
- Creates filtered datasets with only relevant battery parameters

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

## 🔄 Updates & Changelog

### Latest Release (v2.0) - August 2025

**🎯 Major Enhancements:**
- Enhanced column detection for 30+ temperature sensors
- Smart pattern matching for DMD extractor output
- SOC vs Temperature correlation analysis with statistical summaries
- Comprehensive data caching system for faster loading

**🐛 Critical Fixes:**
- Fixed SOC temperature plot legend itemwidth error
- Resolved file name display issues in UI
- Enhanced test duration calculation and display
- Improved startup script reliability

**🛡️ Security:**
- Enhanced .gitignore protection for sensitive data
- Automatic exclusion of cache files and credentials
- Secure handling of Google Drive authentication tokens

**📊 Performance:**
- Intelligent caching reduces load times by 80%
- Background preloading of popular files
- Optimized column detection algorithms
- Enhanced memory management for large datasets

### Upgrading

To get the latest version:
```cmd
git pull origin master
pip install -r requirements.txt --upgrade
```

Check for updates regularly as we continuously improve the analysis capabilities and add new battery data processing features.

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes and test thoroughly**
4. **Follow the coding standards**:
   - Add debug logging for new features
   - Update column detection patterns if needed
   - Test with real battery data
   - Update documentation
5. **Submit a pull request** with detailed description

### Development Setup

```cmd
git clone https://github.com/harisankar99ola/battery_dashboard.git
cd battery_dashboard
pip install -r requirements.txt
# Set up your development environment
start.bat
```

### Adding New Analysis Features

1. **Backend**: Add analysis endpoints in `src/backend/main_simple.py`
2. **Data Processing**: Extend `data_processor.py` with new analysis functions
3. **Frontend**: Add plot generation in `src/frontend/components/plots.py`
4. **UI**: Update plot type dropdown in `src/frontend/app.py`

## 👥 Authors & Contributors

- **Harisankar Suresh** - *Initial development* - [harisankar99ola](https://github.com/harisankar99ola)
- **Battery Analysis Team** - *Requirements and testing*

## 🙏 Acknowledgments

- **PyBAMM Community** - Battery modeling frameworks and best practices
- **Plotly/Dash** - Excellent visualization tools for interactive dashboards
- **FastAPI** - High-performance backend framework
- **Google Drive API** - Seamless cloud integration
- **AutoLion/DMD Tools** - Battery data extraction and processing workflows

## 📞 Support

For issues and questions:

1. **Check this README** - Most common issues are covered above
2. **Search existing issues**: [GitHub Issues](https://github.com/harisankar99ola/battery_dashboard/issues)
3. **Create a new issue** with:
   - Detailed error description
   - Steps to reproduce
   - Column detection debug output (if applicable)
   - Your data format/column names
   - System information (Windows version, Python version)

## 📈 Performance Tips

- **Large Files**: Use data sampling for files >100MB
- **Multiple Files**: Select fewer files for faster analysis
- **Memory**: Close other applications when processing large datasets
- **Network**: Ensure stable internet for Google Drive access
- **Cache**: Let popular files cache for instant subsequent access

---

**🔋 Built with ❤️ for Advanced Battery Data Analysis ⚡**

*Enabling data-driven insights for battery research, development, and testing teams worldwide.*

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
