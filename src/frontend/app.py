import dash
from dash import dcc, html, Input, Output, State, dash_table, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
from plotly.subplots import make_subplots

from components.plots import BatteryPlots

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Battery Data Dashboard"

# Initialize plot generator
plot_generator = BatteryPlots()

# API base URL
API_BASE_URL = "http://localhost:8000"

# Layout components
def create_header():
    return dbc.NavbarSimple(
        brand="🔋 Battery Data Dashboard",
        brand_href="#",
        color="dark",
        dark=True,
        className="mb-4"
    )

def create_file_selector():
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.Span("📁 Data Selection", className="me-auto"),
                dbc.Badge(id="cache-status-badge", children="Checking cache...", color="secondary", className="ms-2")
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            html.Div([
                # Status indicator
                dbc.Alert(
                    id="file-status-alert",
                    children="Ready to load files",
                    color="info",
                    is_open=True,
                    dismissable=False,
                    className="mb-3"
                ),
                html.Label("Select CSV Files:", className="fw-bold mb-2"),
                html.P([
                    "All CSV files from the entire folder structure are shown below. ",
                    dbc.Badge("🏎️", color="success", className="me-1"),
                    "Cached files load instantly. ",
                    dbc.Badge("📡", color="warning", className="me-1"), 
                    "Non-cached files are downloaded on demand."
                ], className="text-muted small mb-3"),
                
                # File selection display and button
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="selected-files-display", children=[
                                html.P("No files selected", className="text-muted mb-0")
                            ], style={"minHeight": "50px", "maxHeight": "150px", "overflowY": "auto"})
                        ], style={"padding": "10px"})
                    ], style={"marginBottom": "10px"}),
                    dbc.Button(
                        "📂 Open File Selector", 
                        id="open-file-selector-btn", 
                        color="primary", 
                        size="sm",
                        className="mb-3"
                    )
                ]),
                
                # Hidden dropdown for compatibility (still needed for callbacks)
                dcc.Dropdown(
                    id="file-dropdown",
                    placeholder="Loading all CSV files...",
                    multi=True,
                    className="mb-2",
                    style={"display": "none"}  # Hide the dropdown
                ),
                html.Label("Select Columns to Load:", className="fw-bold"),
                dcc.Dropdown(
                    id="column-dropdown",
                    placeholder="Select files first to see columns...",
                    multi=True,
                    className="mb-2",
                    style={"fontSize": "12px"}
                ),
                dbc.Button(
                    "✅ Select All Columns", 
                    id="select-all-columns-btn", 
                    color="secondary", 
                    size="sm",
                    className="mb-3"
                )
            ])
        ])
    ], className="mb-4")

def create_plot_controls():
    return dbc.Card([
        dbc.CardHeader("📊 Plot Controls"),
        dbc.CardBody([
            html.Div([
                html.Label("Plot Type:", className="fw-bold"),
                dcc.Dropdown(
                    id="plot-type-dropdown",
                    options=[],  # Will be populated dynamically
                    placeholder="Load data to see available plot types...",
                    className="mb-3"
                ),
                html.Label("Temperature Columns (for SOC analysis):", className="fw-bold"),
                dcc.Dropdown(
                    id="temp-columns-dropdown",
                    placeholder="Select temperature columns...",
                    multi=True,
                    className="mb-2"
                ),
                dbc.Button(
                    "✅ Select All Temperature Columns", 
                    id="select-all-temp-btn", 
                    color="secondary", 
                    size="sm",
                    className="mb-2"
                ),
                dbc.Button(
                    "📥 Download SOC vs Temperature Data", 
                    id="download-soc-analysis-btn", 
                    color="success", 
                    size="sm",
                    className="mb-3",
                    style={"display": "none"}  # Initially hidden
                ),
                dcc.Download(id="download-soc-analysis"),
                dbc.Row([
                    dbc.Col([
                        dbc.Checklist(
                            options=[{"label": "Preprocess Data", "value": "preprocess"}],
                            value=["preprocess"],
                            id="preprocess-check",
                            className="mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Resample Rate:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id="resample-dropdown",
                            options=[
                                {"label": "No Resampling", "value": ""},
                                {"label": "1 Second", "value": "1S"},
                                {"label": "10 Seconds", "value": "10S"},
                                {"label": "1 Minute", "value": "1T"}
                            ],
                            value="1S"
                        )
                    ], width=6)
                ])
            ])
        ])
    ], className="mb-4")

def create_stats_cards():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("0", id="files-count", className="text-primary"),
                        html.P("Files Loaded", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("0", id="data-points", className="text-success"),
                        html.P("Data Points", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("0h", id="duration", className="text-info"),
                        html.P("Test Duration", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("-", id="efficiency", className="text-warning"),
                        html.P("Efficiency", className="card-text")
                    ])
                ])
            ], width=3)
        ])
    ], className="mb-4")

# Main layout
app.layout = dbc.Container([
    create_header(),
    
    # Loading indicator
    dcc.Loading(
        id="loading",
        children=[html.Div(id="loading-output")],
        type="default",
    ),
    
    # Data stores
    dcc.Store(id="folders-store"),
    dcc.Store(id="files-store"),
    dcc.Store(id="current-data-store"),
    dcc.Store(id="combined-data-store"),
    
    # File selector modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("📂 Select CSV Files")),
        dbc.ModalBody([
            html.Div([
                html.P("Select the CSV files you want to analyze:", className="mb-3"),
                html.Div(id="file-checkboxes-container", children=[
                    html.P("Loading files...", className="text-muted")
                ], style={"maxHeight": "400px", "overflowY": "auto"}),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("✅ Select All", id="modal-select-all-btn", color="primary", size="sm"),
                    ], width=6),
                    dbc.Col([
                        dbc.Button("❌ Clear All", id="modal-clear-all-btn", color="secondary", size="sm"),
                    ], width=6)
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="modal-cancel-btn", color="secondary", className="me-2"),
            dbc.Button("Apply Selection", id="modal-apply-btn", color="primary")
        ])
    ], id="file-selector-modal", size="lg", is_open=False),
    
    # Main content with better spacing
    dbc.Row([
        dbc.Col([
            create_file_selector(),
            create_plot_controls()
        ], width=4),
        dbc.Col([
            create_stats_cards(),
            dbc.Card([
                dbc.CardHeader("📈 Data Visualization"),
                dbc.CardBody([
                    dcc.Graph(
                        id="main-plot",
                        figure={},
                        style={"height": "700px", "width": "100%"}
                    )
                ], style={"padding": "20px"})
            ], className="mb-4")
        ], width=8)
    ], className="g-4"),  # Add gutters for better spacing
    
    # Data table section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📋 Data Table"),
                dbc.CardBody([
                    html.Div(id="data-table-container")
                ])
            ])
        ], width=12)
    ], className="mt-4"),
    
    # Interval component for periodic updates
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    )
], fluid=True)

# Callbacks

@app.callback(
    Output("plot-type-dropdown", "options"),
    Output("plot-type-dropdown", "value"),
    Input("current-data-store", "data"),
    Input("combined-data-store", "data")
)
def update_plot_options(current_data, combined_data):
    """Update available plot types based on loaded data column types"""
    data_source = combined_data if combined_data else current_data
    
    if not data_source or not data_source.get("statistics", {}).get("column_types"):
        return [], None
    
    column_types = data_source["statistics"]["column_types"]
    options = []
    default_value = None
    
    print(f"🔍 DEBUG: Available column types: {list(column_types.keys())}")
    
    # Basic plots that work with any data
    options.append({"label": "📊 Data Overview", "value": "overview"})
    if not default_value:
        default_value = "overview"
    
    # Temperature plots - check for both old and new format keys
    temp_cols = []
    temp_keys = ["temperature_columns", "thermocouple", "temp_sensors", "temp_stats", "temp_cols", "temperature"]
    for key in temp_keys:
        temp_cols.extend(column_types.get(key, []))
    
    if temp_cols:
        options.append({"label": "🌡️ Temperature Analysis", "value": "temperature"})
        options.append({"label": "🔥 Temperature Heatmap", "value": "temp_heatmap"})
        print(f"✅ Added temperature plot options. Found {len(temp_cols)} temperature columns")
    else:
        print(f"❌ No temperature columns found in: {list(column_types.keys())}")
    
    # Voltage plots - check for both old and new format keys
    voltage_cols = column_types.get("voltage_columns", []) + column_types.get("cell_voltages", [])
    if voltage_cols:
        options.append({"label": "⚡ Voltage Analysis", "value": "voltage"})
        print(f"✅ Added voltage plot option. Found {len(voltage_cols)} voltage columns")
    
    # Current plots - check for both old and new format keys  
    current_cols = column_types.get("current_columns", []) + column_types.get("current", [])
    if current_cols:
        options.append({"label": "🔋 Current Analysis", "value": "current"})
        print(f"✅ Added current plot option. Found {len(current_cols)} current columns")
    
    # SOC analysis - check for both old and new format keys
    soc_cols = column_types.get("soc_columns", []) + column_types.get("soc_soh", [])
    if temp_cols and soc_cols:
        options.append({"label": "🔋 SOC vs Temperature", "value": "soc_temp"})
        print(f"✅ Added SOC vs Temperature option. Found {len(soc_cols)} SOC columns")
    
    print(f"🎯 Final plot options: {[opt['label'] for opt in options]}")
    return options, default_value

@app.callback(
    [Output("file-dropdown", "options"),
     Output("file-dropdown", "placeholder"),
     Output("cache-status-badge", "children"),
     Output("cache-status-badge", "color"),
     Output("files-store", "data")],
    Input("interval-component", "n_intervals")
)
def load_all_csv_files(n_intervals):
    """Load all CSV files from the entire folder structure with cache status"""
    try:
        response = requests.get(f"{API_BASE_URL}/all-csv-files")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            cached_count = data.get('cached_count', 0)
            total_count = data.get('total_count', 0)
            
            if files:
                options = []
                for file in files:
                    # Create display label with folder path and file info
                    size_info = f" ({file['size_mb']} MB)" if file.get('size_mb') else ""
                    cache_icon = "🏎️" if file.get('cached') else "📡"
                    row_info = f" | {file['row_count']} rows" if file.get('row_count') else ""
                    
                    display_name = file.get('path', file['name'])
                    if display_name.startswith('/'):
                        display_name = display_name[1:]  # Remove leading slash
                    
                    label = f"{cache_icon} {display_name}{size_info}{row_info}"
                    
                    options.append({
                        'label': label,
                        'value': file['id']
                    })
                
                # Cache status for badge
                cache_badge_text = f"{cached_count}/{total_count} cached"
                cache_badge_color = "success" if cached_count > 0 else "warning"
                
                placeholder = f"Select from {len(files)} CSV files (🏎️ = cached, 📡 = download)"
                
                # Prepare files data for the modal
                files_store_data = {
                    'success': True,
                    'files': [
                        {
                            'id': file['id'],
                            'display_name': file.get('path', file['name']),
                            'cached': file.get('cached', False),
                            'size_mb': file.get('size_mb'),
                            'row_count': file.get('row_count')
                        }
                        for file in files
                    ],
                    'cached_count': cached_count,
                    'total_count': total_count
                }
                
                return options, placeholder, cache_badge_text, cache_badge_color, files_store_data
            else:
                return [], "No CSV files found", "No files", "secondary", {'success': False, 'files': []}
        else:
            return [], "Error loading files", "Error", "danger", {'success': False, 'files': []}
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return [], "Error loading files", "Error", "danger", {'success': False, 'files': []}

# Modal file selector callbacks
@app.callback(
    Output('file-selector-modal', 'is_open'),
    [Input('open-file-selector-btn', 'n_clicks'),
     Input('modal-cancel-btn', 'n_clicks'),
     Input('modal-apply-btn', 'n_clicks')],
    [State('file-selector-modal', 'is_open')]
)
def toggle_file_modal(open_clicks, cancel_clicks, apply_clicks, is_open):
    """Toggle the file selector modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'open-file-selector-btn':
        return True
    elif button_id in ['modal-cancel-btn', 'modal-apply-btn']:
        return False
    
    return is_open

@app.callback(
    Output('file-checkboxes-container', 'children'),
    Input('files-store', 'data')
)
def update_file_checkboxes(files_data):
    """Populate the modal with file checkboxes"""
    if not files_data or not files_data.get('success'):
        return [html.P("No files available", className="text-muted")]
    
    files = files_data.get('files', [])
    if not files:
        return [html.P("No files found", className="text-muted")]
    
    checkboxes = []
    for file_info in files:
        file_id = file_info['id']
        display_name = file_info['display_name']
        is_cached = file_info.get('cached', False)
        
        # Add cache indicator
        icon = "🏎️" if is_cached else "📡"
        label = f"{icon} {display_name}"
        
        checkbox = dbc.Checkbox(
            id={'type': 'file-checkbox', 'index': file_id},
            label=label,
            value=False,
            className="mb-2"
        )
        checkboxes.append(checkbox)
    
    return checkboxes

@app.callback(
    [Output({'type': 'file-checkbox', 'index': ALL}, 'value'),
     Output('file-dropdown', 'value', allow_duplicate=True),
     Output('selected-files-display', 'children')],
    [Input('modal-select-all-btn', 'n_clicks'),
     Input('modal-clear-all-btn', 'n_clicks'),
     Input('modal-apply-btn', 'n_clicks'),
     Input({'type': 'file-checkbox', 'index': ALL}, 'value')],
    [State({'type': 'file-checkbox', 'index': ALL}, 'id'),
     State('files-store', 'data')],
    prevent_initial_call=True
)
def handle_modal_file_selection(select_all_clicks, clear_all_clicks, apply_clicks, checkbox_values, checkbox_ids, files_data):
    """Handle file selection in the modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id']
    
    # Initialize variables
    new_checkbox_values = checkbox_values or []
    selected_file_ids = []
    display_children = []
    
    if 'modal-select-all-btn' in button_id and select_all_clicks:
        # Select all checkboxes
        new_checkbox_values = [True] * len(checkbox_ids)
    elif 'modal-clear-all-btn' in button_id and clear_all_clicks:
        # Clear all checkboxes
        new_checkbox_values = [False] * len(checkbox_ids)
    elif 'modal-apply-btn' in button_id and apply_clicks:
        # Apply current selection to dropdown
        selected_file_ids = [
            checkbox_ids[i]['index'] for i, selected in enumerate(checkbox_values or [])
            if selected and i < len(checkbox_ids)
        ]
    else:
        # Handle individual checkbox changes
        new_checkbox_values = checkbox_values or []
    
    # Update selected files display
    if files_data and files_data.get('files'):
        files_dict = {f['id']: f for f in files_data['files']}
        current_selected = [
            checkbox_ids[i]['index'] for i, selected in enumerate(new_checkbox_values)
            if selected and i < len(checkbox_ids)
        ]
        
        if current_selected:
            display_children = [
                html.Div([
                    html.Span(f"🗂️ {len(current_selected)} file(s) selected:", className="fw-bold mb-2 d-block"),
                    html.Ul([
                        html.Li(f"{'🏎️' if files_dict.get(file_id, {}).get('cached', False) else '📡'} {files_dict.get(file_id, {}).get('display_name', file_id)}")
                        for file_id in current_selected[:5]  # Show first 5
                    ] + ([html.Li(f"... and {len(current_selected) - 5} more")] if len(current_selected) > 5 else []),
                    className="mb-0", style={"fontSize": "12px"})
                ])
            ]
        else:
            display_children = [html.P("No files selected", className="text-muted mb-0")]
    else:
        display_children = [html.P("No files available", className="text-muted mb-0")]
    
    # Return appropriate values based on the trigger
    if 'modal-apply-btn' in button_id:
        return new_checkbox_values, selected_file_ids, display_children
    else:
        return new_checkbox_values, dash.no_update, display_children

@app.callback(
    Output('column-dropdown', 'options'),
    Output('column-dropdown', 'placeholder'),
    Input('file-dropdown', 'value')
)
def update_columns(selected_files):
    if not selected_files:
        return [], "Select files first to see columns..."
    
    # Get columns from the first file
    try:
        file_id = selected_files[0] if isinstance(selected_files, list) else selected_files
        response = requests.get(f"{API_BASE_URL}/columns/{file_id}")
        if response.status_code == 200:
            columns_data = response.json()
            options = []
            
            # Add "Select All" option
            all_columns = []
            for cols in columns_data.values():
                all_columns.extend(cols)
            
            if all_columns:
                options.append({'label': '✅ SELECT ALL COLUMNS', 'value': '__SELECT_ALL__'})
                options.append({'label': '---', 'value': '__DIVIDER__', 'disabled': True})
            
            # Group columns by type for better organization
            for col_type, cols in columns_data.items():
                if cols:
                    # Create readable category names
                    category_names = {
                        'temp_stats': 'TEMPERATURE STATISTICS',
                        'temp_cols': 'BMS TEMPERATURE SENSORS', 
                        'thermocouple': 'THERMOCOUPLE SENSORS',
                        'cell_voltages': 'CELL VOLTAGES',
                        'soc_soh': 'SOC & SOH',
                        'current': 'CURRENT',
                        'power': 'POWER',
                        'time': 'TIME'
                    }
                    category_name = category_names.get(col_type, col_type.upper())
                    
                    options.append({'label': f"--- {category_name} ---", 'value': f"__{col_type}__", 'disabled': True})
                    for col in cols:
                        options.append({'label': f"  {col}", 'value': col})
            
            total_columns = len(all_columns)
            placeholder = f"Select columns to load (found {total_columns} columns)..."
            return options, placeholder
    except Exception as e:
        print(f"Error fetching columns: {e}")
    
    return [], "Error loading columns"

# Callback to handle "Select All" functionality
@app.callback(
    Output('column-dropdown', 'value'),
    Input('column-dropdown', 'value'),
    Input('select-all-columns-btn', 'n_clicks'),
    State('column-dropdown', 'options'),
    prevent_initial_call=True
)
def handle_select_all(selected_values, select_all_clicks, options):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return selected_values or []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle Select All button click
    if trigger_id == 'select-all-columns-btn' and select_all_clicks:
        # Get all actual column values (exclude special options)
        all_columns = [opt['value'] for opt in options 
                      if not opt['value'].startswith('__') and not opt.get('disabled', False)]
        return all_columns
    
    # Handle dropdown changes (including __SELECT_ALL__ option)
    if selected_values and '__SELECT_ALL__' in selected_values:
        # Get all actual column values (exclude special options)
        all_columns = [opt['value'] for opt in options 
                      if not opt['value'].startswith('__') and not opt.get('disabled', False)]
        return all_columns
    
    return selected_values or []

# Auto-preview callback for quick data exploration
@app.callback(
    Output("current-data-store", "data", allow_duplicate=True),
    Output("files-count", "children", allow_duplicate=True),
    Output("data-points", "children", allow_duplicate=True),
    Output("duration", "children", allow_duplicate=True),
    Output("efficiency", "children", allow_duplicate=True),
    Output("file-status-alert", "children"),
    Output("file-status-alert", "color"),
    Input("file-dropdown", "value"),
    prevent_initial_call=True
)
def auto_preview_data(selected_files):
    """Automatically load data when files are selected (full load, not just preview)"""
    if not selected_files:
        return {}, "0", "0", "0h", "-", "Ready to load files", "info"
    
    try:
        # Update status to loading
        file_count = len(selected_files) if isinstance(selected_files, list) else 1
        
        # Convert to list if single file
        file_list = selected_files if isinstance(selected_files, list) else [selected_files]
        
        # Load full data from first file (not just preview - this was the issue!)
        first_file = file_list[0]
        
        # Request full data with basic preprocessing
        params = {
            "preprocess": True,
            "resample": "1S"  # Light resampling for better performance
        }
        
        response = requests.get(f"{API_BASE_URL}/data/{first_file}", params=params)
        
        if response.status_code == 200:
            full_data = response.json()
            
            # Extract basic statistics  
            stats = full_data.get('statistics', {})
            data_points = stats.get('total_rows', 0)
            if 'shape' in stats:
                data_points = stats['shape'][0]
            
            # Calculate duration if time data is available
            duration = "0h"
            if 'duration_hours' in stats:
                hours = stats['duration_hours']
                if hours < 1:
                    duration = f"{int(hours * 60)}m"
                else:
                    duration = f"{hours:.1f}h"
            elif 'time_range' in stats:
                time_range = stats['time_range']
                duration_sec = time_range.get('duration', 0)
                hours = duration_sec / 3600
                if hours < 1:
                    duration = f"{int(hours * 60)}m"
                else:
                    duration = f"{hours:.1f}h"
            
            # Calculate efficiency placeholder
            efficiency = "-"
            if stats.get('efficiency_percent'):
                efficiency = f"{stats['efficiency_percent']:.1f}%"
            
            # Success status
            success_msg = f"✅ Data loaded: {data_points:,} data points from {file_count} file(s)"
            
            print(f"✅ Auto-loaded full data with column types: {list(stats.get('column_types', {}).keys())}")
            
            return full_data, str(file_count), f"{data_points:,}", duration, efficiency, success_msg, "success"
        else:
            error_msg = f"❌ Failed to load data (Status: {response.status_code})"
            return {}, "0", "0", "0h", "-", error_msg, "danger"
        
    except Exception as e:
        print(f"Error in auto-preview: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        error_msg = f"❌ Error loading data: {str(e)[:50]}..."
        return {}, "0", "0", "0h", "-", error_msg, "warning"

# Callback for temperature columns "Select All" button
@app.callback(
    Output('temp-columns-dropdown', 'value'),
    Input('select-all-temp-btn', 'n_clicks'),
    State('temp-columns-dropdown', 'options'),
    prevent_initial_call=True
)
def select_all_temp_columns(n_clicks, temp_options):
    if not n_clicks or not temp_options:
        return []
    
    # Get all temperature column values
    all_temp_columns = [opt['value'] for opt in temp_options]
    return all_temp_columns

# Separate callback specifically for updating temperature columns dropdown
@app.callback(
    Output("temp-columns-dropdown", "options"),
    Input("current-data-store", "data")
)
def update_temperature_columns_dropdown(current_data):
    """Update temperature columns dropdown when data is loaded"""
    if not current_data or not current_data.get("statistics"):
        return []
    
    # Extract all temperature column types - use the actual keys from backend
    column_types = current_data.get("statistics", {}).get("column_types", {})
    temp_cols = []
    
    # Backend uses these keys, so check for both old and new formats
    possible_temp_keys = [
        "temperature_columns",  # New backend format
        "thermocouple", "temp_sensors", "temp_stats", "temp_cols", "temperature"  # Old format
    ]
    
    for col_type in possible_temp_keys:
        if col_type in column_types:
            temp_cols.extend(column_types.get(col_type, []))
    
    # Remove duplicates and sort
    temp_cols = sorted(list(set(temp_cols)))
    
    # Create options
    temp_options = [{"label": col, "value": col} for col in temp_cols]
    
    print(f"✅ Updated temperature dropdown with {len(temp_cols)} columns: {temp_cols[:3]}...")
    print(f"   Available column types: {list(column_types.keys())}")
    return temp_options

@app.callback(
    Output("main-plot", "figure"),
    Input("plot-type-dropdown", "value"),
    Input("current-data-store", "data"),
    Input("combined-data-store", "data"),
    State("temp-columns-dropdown", "value"),
    State("file-dropdown", "value")
)
def update_main_plot(plot_type, current_data, combined_data, selected_temp_cols, selected_files):
    """Update main plot based on selection"""
    print("🎯 DEBUG: update_main_plot called with:")
    print(f"  plot_type: {plot_type}")
    print(f"  current_data: {type(current_data)} - {bool(current_data)}")
    if isinstance(current_data, dict):
        print(f"  current_data keys: {list(current_data.keys())}")
        print(f"  current_data has 'data': {'data' in current_data}")
    print(f"  combined_data: {type(combined_data)} - {bool(combined_data)}")
    print(f"  selected_temp_cols: {selected_temp_cols}")
    print(f"  selected_files: {selected_files}")
    
    # Use combined data if available, otherwise current data
    data_source = combined_data if combined_data else current_data
    
    if not data_source or not data_source.get("data"):
        print("❌ No data source available")
        return go.Figure()
    
    print(f"✅ Data source available with keys: {data_source.keys()}")
    
    try:
        # Convert data to DataFrame
        df_data = data_source["data"]
        if "index" in data_source:
            df = pd.DataFrame(df_data, index=data_source["index"])
        else:
            df = pd.DataFrame(df_data)
        
        print(f"✅ DataFrame created: {df.shape}")
        print(f"  Columns: {list(df.columns[:5])}...")  # Show first 5 columns
        
        # Get column types
        column_types = data_source.get("statistics", {}).get("column_types", {})
        
        # Generate plot based on type
        if plot_type == "overview":
            result_fig = create_data_overview_plot(df)
            return result_fig
        
        elif plot_type == "temperature":
            # Filter to only show selected temperature columns if any are selected
            if selected_temp_cols:
                # Get all temperature columns from both old and new formats
                all_temp_cols = []
                temp_keys = ["temperature_columns", "thermocouple", "temp_sensors", "temp_stats", "temp_cols", "temperature"]
                for key in temp_keys:
                    all_temp_cols.extend(column_types.get(key, []))
                
                # Create filtered column types with only selected columns
                filtered_column_types = column_types.copy()
                for key in temp_keys:
                    if key in filtered_column_types:
                        filtered_column_types[key] = [col for col in column_types.get(key, []) if col in selected_temp_cols]
                
                return plot_generator.create_temperature_overview(df, filtered_column_types)
            else:
                return plot_generator.create_temperature_overview(df, column_types)
        
        elif plot_type == "voltage":
            return plot_generator.create_voltage_analysis(df, column_types)
        
        elif plot_type == "current":
            return create_current_analysis_plot(df, column_types)
        
        elif plot_type == "soc_temp":
            if selected_temp_cols and selected_files:
                # Get SOC-temperature relationship
                file_id = selected_files[0] if isinstance(selected_files, list) else selected_files
                payload = {
                    "file_id": file_id,
                    "temperature_columns": selected_temp_cols
                }
                print(f"Requesting SOC vs temperature analysis with payload: {payload}")
                response = requests.post(f"{API_BASE_URL}/api/analysis/soc-temperature", json=payload)
                print(f"SOC analysis response status: {response.status_code}")
                if response.status_code == 200:
                    soc_temp_data = response.json()
                    print(f"SOC analysis data keys: {soc_temp_data.keys()}")
                    # The new endpoint returns analysis data, not raw dataframe data
                    return plot_generator.create_soc_temperature_plot(soc_temp_data)
                else:
                    print(f"SOC analysis failed: {response.text}")
            return go.Figure()
        
        elif plot_type == "temp_heatmap":
            # Filter to only show selected temperature columns if any are selected
            if selected_temp_cols:
                # Get all temperature columns from both old and new formats
                all_temp_cols = []
                temp_keys = ["temperature_columns", "thermocouple", "temp_sensors", "temp_stats", "temp_cols", "temperature"]
                for key in temp_keys:
                    all_temp_cols.extend(column_types.get(key, []))
                
                # Create filtered column types with only selected columns
                filtered_column_types = column_types.copy()
                for key in temp_keys:
                    if key in filtered_column_types:
                        filtered_column_types[key] = [col for col in column_types.get(key, []) if col in selected_temp_cols]
                
                return plot_generator.create_heatmap_plot(df, filtered_column_types, "temperature")
            else:
                return plot_generator.create_heatmap_plot(df, column_types, "temperature")
        
    except Exception as e:
        print(f"❌ Error creating plot: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return go.Figure()


def create_data_overview_plot(df: pd.DataFrame) -> go.Figure:
    """Create a simple overview plot showing the first few columns over time"""
    cell_voltages_cols = [col for col in df.columns if 'Cell_Voltage_Cell' in col]
    temp_cols = [col for col in df.columns if 'BMS00_Pack_' in col if '02' not in col and '05' not in col]
    thermocouple_cols = [col for col in df.columns if 'RH' in col or 'LH' in col]
    cell_balancing_cols = [col for col in df.columns if '_Balancing_Status_' in col]
    pdu_temp_cols = [col for col in df.columns if 'BMS00_PDU_Temperature_' in col] 
    soc_soh_cols = [col for col in df.columns if 'Pack_S' in col]
    fig = make_subplots(rows=3, cols=2, shared_xaxes=True, subplot_titles=('Cell Voltages Over Time','BMS temperature sensor data' ,'Current Over Time','Thermocouple Data', 'SoC and SoH Over Time', 'Cell Balancing Status'))
    for col in cell_voltages_cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col), row=1, col=1)
    for col in temp_cols+pdu_temp_cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col), row=1, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=df['Battery_Current_00_avg'], mode='lines', name='Battery Current'), row=2, col=1)
    for col in thermocouple_cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col), row=2, col=2)
    for col in soc_soh_cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col), row=3, col=1)
    for col in cell_balancing_cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col), row=3, col=2)
    fig.update_layout(height=800, width=1100, title_text="Data Overview", template='plotly_white')
    
    return fig


def create_current_analysis_plot(df: pd.DataFrame, column_types: dict) -> go.Figure:
    """Create current analysis plot"""
    fig = go.Figure()
    
    current_cols = column_types.get('current', [])
    if not current_cols:
        return fig
    
    # Get time data
    x_data = df.index if hasattr(df.index, 'tolist') else range(len(df))
    
    colors = px.colors.qualitative.Set3
    for i, col in enumerate(current_cols[:3]):  # Limit to 3 current columns
        fig.add_trace(go.Scatter(
            x=x_data,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig.update_layout(
        title="Current Analysis",
        xaxis_title="Time",
        yaxis_title="Current (A)",
        template="plotly_white",
        height=600
    )
    
    return fig

@app.callback(
    Output("data-table-container", "children"),
    Input("current-data-store", "data"),
    Input("combined-data-store", "data")
)
def update_data_table(current_data, combined_data):
    """Update data table display"""
    data_source = combined_data if combined_data else current_data
    
    if not data_source or not data_source.get("data"):
        return html.P("No data available")
    
    try:
        df_data = data_source["data"]
        df = pd.DataFrame(df_data)
        
        # Show all selected columns (not just first 10)
        # Limit to first 100 rows for performance
        display_df = df.head(100)
        
        return dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": col, "id": col} for col in display_df.columns],
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left', 
                'padding': '8px',
                'fontSize': '11px',
                'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)', 
                'fontWeight': 'bold',
                'fontSize': '12px'
            },
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in display_df.to_dict('records')
            ],
            tooltip_duration=None
        )
    except Exception as e:
        return html.P(f"Error displaying data: {e}")

@app.callback(
    Output("efficiency", "children"),
    Input("current-data-store", "data"),
    State("file-dropdown", "value")
)
def update_efficiency(current_data, selected_files):
    """Update efficiency metric"""
    if not current_data or not selected_files:
        return "-"
    
    try:
        file_id = selected_files[0] if isinstance(selected_files, list) else selected_files
        response = requests.get(f"{API_BASE_URL}/api/analysis/efficiency/{file_id}")
        if response.status_code == 200:
            efficiency_data = response.json()
            efficiency = efficiency_data.get("efficiency_metrics", {}).get("round_trip_efficiency", 0)
            return f"{efficiency*100:.1f}%"
    except Exception as e:
        print(f"Error calculating efficiency: {e}")
    
    return "-"

# Callback to show/hide download button based on plot type
@app.callback(
    Output("download-soc-analysis-btn", "style"),
    Input("plot-type-dropdown", "value")
)
def toggle_download_button(plot_type):
    """Show download button only for SOC vs Temperature analysis"""
    if plot_type == "soc_temp":
        return {"display": "block"}
    return {"display": "none"}

# Callback to handle SOC analysis data download
@app.callback(
    Output("download-soc-analysis", "data"),
    Input("download-soc-analysis-btn", "n_clicks"),
    State("file-dropdown", "value"),
    State("temp-columns-dropdown", "value"),
    prevent_initial_call=True
)
def download_soc_analysis(n_clicks, selected_files, selected_temp_cols):
    """Download SOC vs Temperature analysis data as CSV"""
    if not n_clicks or not selected_files or not selected_temp_cols:
        return None
    
    try:
        file_id = selected_files[0] if isinstance(selected_files, list) else selected_files
        payload = {
            "file_id": file_id,
            "temperature_columns": selected_temp_cols
        }
        response = requests.post(f"{API_BASE_URL}/api/analysis/soc-temperature", json=payload)
        if response.status_code == 200:
            soc_temp_response = response.json()
            
            # Check if analysis was successful
            if not soc_temp_response.get('success', False):
                print("SOC analysis failed for download")
                return None
            
            # Extract data from the correct structure
            analysis_data = soc_temp_response.get('data', {})
            soc_points = analysis_data.get('soc_points', [])
            temp_data = analysis_data.get('temperature_data', {})
            
            if not soc_points or not temp_data:
                print("No data available for download")
                return None
            
            # Convert the analysis data to a downloadable CSV format
            download_data = []
            
            # Create rows for each SOC point
            for i, soc in enumerate(soc_points):
                row = {'SOC_Percent': soc}
                for sensor, temps in temp_data.items():
                    row[f"{sensor}_Temperature_C"] = temps[i] if i < len(temps) and temps[i] is not None else "NA"
                download_data.append(row)
            
            df_download = pd.DataFrame(download_data)
            
            # Generate filename with timestamp
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SOC_vs_Temperature_Analysis_{timestamp}.csv"
            
            return dcc.send_data_frame(df_download.to_csv, filename, index=False)
    
    except Exception as e:
        print(f"Error creating download: {e}")
    
    return None

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
