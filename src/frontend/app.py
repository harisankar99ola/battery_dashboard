import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests

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
        dbc.CardHeader("📁 Data Selection"),
        dbc.CardBody([
            html.Div([
                html.Label("Select CSV Files:", className="fw-bold mb-2"),
                html.P("All CSV files from the entire folder structure are shown below. Select multiple files to load and analyze.", 
                       className="text-muted small mb-3"),
                dcc.Dropdown(
                    id="file-dropdown",
                    placeholder="Loading all CSV files...",
                    multi=True,
                    className="mb-3",
                    style={"fontSize": "12px", "maxHeight": "200px"}
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
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "🔄 Load Selected Files", 
                            id="load-data-btn", 
                            color="primary", 
                            disabled=True,
                            className="me-2",
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        html.A(
                            dbc.Button(
                                "💾 Download Data", 
                                id="download-data-btn", 
                                color="info", 
                                disabled=True,
                                size="sm"
                            ),
                            id="download-link",
                            href="",
                            download="battery_data.csv"
                        )
                    ], width=6)
                ])
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
    
    # Basic plots that work with any data
    options.append({"label": "📊 Data Overview", "value": "overview"})
    if not default_value:
        default_value = "overview"
    
    # Temperature plots - only if temperature columns exist
    temp_cols = (column_types.get("thermocouple", []) + 
                 column_types.get("temp_sensors", []) + 
                 column_types.get("temp_stats", []) +
                 column_types.get("temperature", []))
    if temp_cols:
        options.append({"label": "🌡️ Temperature Analysis", "value": "temperature"})
        options.append({"label": "🔥 Temperature Heatmap", "value": "temp_heatmap"})
        if not default_value:
            default_value = "temperature"
    
    # Voltage plots - only if voltage columns exist  
    voltage_cols = column_types.get("cell_voltages", [])
    if voltage_cols:
        options.append({"label": "⚡ Voltage Analysis", "value": "voltage"})
        if not default_value:
            default_value = "voltage"
    
    # Current plots - only if current columns exist
    current_cols = column_types.get("current", [])
    if current_cols:
        options.append({"label": "🔋 Current Analysis", "value": "current"})
    
    # SOC analysis - only if both temperature and SOC columns exist
    soc_cols = column_types.get("soc_soh", [])
    if temp_cols and soc_cols:
        options.append({"label": "🔋 SOC vs Temperature", "value": "soc_temp"})
    
    return options, default_value

@app.callback(
    Output("file-dropdown", "options"),
    Output("file-dropdown", "placeholder"),
    Input("interval-component", "n_intervals")
)
def load_all_csv_files(n_intervals):
    """Load all CSV files from the entire folder structure"""
    try:
        response = requests.get(f"{API_BASE_URL}/all-csv-files")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if files:
                options = []
                for file in files:
                    # Create display label with folder path and file info
                    label = f"📄 {file['display_name']}"
                    if file.get('size_mb', 0) > 0:
                        label += f" ({file['size_mb']} MB)"
                    
                    options.append({
                        'label': label,
                        'value': file['id']
                    })
                
                placeholder = f"Select from {len(files)} CSV files (scroll to see all)..."
                return options, placeholder
            else:
                return [], "No CSV files found"
        else:
            return [], "Error loading files"
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return [], "Error loading files"

@app.callback(
    Output('column-dropdown', 'options'),
    Output('column-dropdown', 'placeholder'),
    Output('load-data-btn', 'disabled'),
    Input('file-dropdown', 'value')
)
def update_columns(selected_files):
    if not selected_files:
        return [], "Select files first to see columns...", True
    
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
            return options, placeholder, False
    except Exception as e:
        print(f"Error fetching columns: {e}")
    
    return [], "Error loading columns", True

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

@app.callback(
    Output("current-data-store", "data"),
    Output("temp-columns-dropdown", "options"),
    Output("files-count", "children"),
    Output("data-points", "children"),
    Output("duration", "children"),
    Output("download-data-btn", "disabled"),
    Input("load-data-btn", "n_clicks"),
    State("file-dropdown", "value"),
    State("column-dropdown", "value"),
    State("preprocess-check", "value"),
    State("resample-dropdown", "value")
)
def load_selected_files(n_clicks, selected_files, selected_columns, preprocess_options, resample_rate):
    """Load and process selected CSV files"""
    if not n_clicks or not selected_files:
        return {}, [], "0", "0", "0h", True
    
    global data_store
    data_store = {}
    
    try:
        # Ensure selected_files is a list
        file_list = selected_files if isinstance(selected_files, list) else [selected_files]
        
        # Load data for all selected files
        for file_id in file_list:
            params = {
                "preprocess": "preprocess" in (preprocess_options or []),
                "resample": resample_rate if resample_rate else None
            }
            
            # Add selected columns to params
            if selected_columns:
                # Filter out disabled options (group headers) and remove duplicates
                valid_columns = list(set([col for col in selected_columns if not col.startswith('__')]))
                if valid_columns:
                    params["selected_columns"] = ','.join(valid_columns)
            
            response = requests.get(f"{API_BASE_URL}/data/{file_id}", params=params)
            
            if response.status_code == 200:
                file_data = response.json()
                data_store[file_id] = file_data
        
        if data_store:
            # If multiple files, combine them automatically
            if len(file_list) > 1:
                # Use the backend combine functionality
                try:
                    payload = {"file_ids": file_list}
                    response = requests.post(f"{API_BASE_URL}/combine", json=payload)
                    if response.status_code == 200:
                        combined_data = response.json()
                        # Use combined data for analysis
                        main_data = combined_data
                    else:
                        # Fallback to first file
                        main_data = list(data_store.values())[0]
                except Exception as e:
                    # Fallback to first file if combine fails
                    print(f"Combine failed, using first file: {e}")
                    main_data = list(data_store.values())[0]
            else:
                main_data = list(data_store.values())[0]
            
            # Extract temperature column options
            column_types = main_data.get("statistics", {}).get("column_types", {})
            temp_cols = column_types.get("thermocouple", []) + column_types.get("temp_sensors", [])
            temp_options = [{"label": col, "value": col} for col in temp_cols]
            
            # Calculate combined stats
            if len(file_list) > 1:
                total_points = sum(data.get("statistics", {}).get("shape", [0, 0])[0] for data in data_store.values())
            else:
                total_points = main_data.get("statistics", {}).get("shape", [0, 0])[0]
            
            file_count = len(file_list)
            
            # Get duration from new endpoint
            try:
                file_id = file_list[0]  # Use first file for duration
                duration_response = requests.get(f"{API_BASE_URL}/api/analysis/duration/{file_id}")
                if duration_response.status_code == 200:
                    duration_data = duration_response.json()
                    duration_hours = f"{duration_data.get('duration_hours', 0):.1f}h"
                else:
                    # Fallback to time_range from statistics
                    time_range = main_data.get("statistics", {}).get("time_range", {})
                    duration = time_range.get("duration", 0)
                    duration_hours = f"{duration/3600:.1f}h" if duration else "0h"
            except Exception as e:
                print(f"Error getting duration: {e}")
                duration_hours = "0h"
            
            return main_data, temp_options, str(file_count), f"{total_points:,}", duration_hours, False
        
    except Exception as e:
        print(f"Error loading data: {e}")
    
    return {}, [], "0", "0", "0h", True

# Add download callback
@app.callback(
    Output("download-link", "href"),
    Input("load-data-btn", "n_clicks"),
    State("file-dropdown", "value"),
    State("column-dropdown", "value")
)
def update_download_link(n_clicks, selected_files, selected_columns):
    """Update download link for processed data"""
    if not n_clicks or not selected_files:
        return ""
    
    try:
        params = {}
        if selected_columns:
            valid_columns = [col for col in selected_columns if not col.startswith('__')]
            if valid_columns:
                params["selected_columns"] = ','.join(valid_columns)
        
        # Build download URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        file_ids = ','.join(selected_files) if isinstance(selected_files, list) else selected_files
        download_url = f"{API_BASE_URL}/download/processed-data?file_ids={file_ids}"
        if query_string:
            download_url += f"&{query_string}"
        
        return download_url
        
    except Exception as e:
        print(f"Error generating download link: {e}")
    
    return ""

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
    # Use combined data if available, otherwise current data
    data_source = combined_data if combined_data else current_data
    
    if not data_source or not data_source.get("data"):
        return go.Figure()
    
    try:
        # Convert data to DataFrame
        df_data = data_source["data"]
        if "index" in data_source:
            df = pd.DataFrame(df_data, index=data_source["index"])
        else:
            df = pd.DataFrame(df_data)
        
        # Get column types
        column_types = data_source.get("statistics", {}).get("column_types", {})
        
        # Generate plot based on type
        if plot_type == "overview":
            return create_data_overview_plot(df, column_types)
        
        elif plot_type == "temperature":
            # Filter to only show selected temperature columns if any are selected
            if selected_temp_cols:
                filtered_column_types = column_types.copy()
                # Only show selected temperature columns
                filtered_column_types['thermocouple'] = [col for col in column_types.get('thermocouple', []) if col in selected_temp_cols]
                filtered_column_types['temp_sensors'] = [col for col in column_types.get('temp_sensors', []) if col in selected_temp_cols]
                filtered_column_types['temp_stats'] = [col for col in column_types.get('temp_stats', []) if col in selected_temp_cols]
                filtered_column_types['temperature'] = [col for col in column_types.get('temperature', []) if col in selected_temp_cols]
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
                filtered_column_types = column_types.copy()
                # Only show selected temperature columns
                filtered_column_types['thermocouple'] = [col for col in column_types.get('thermocouple', []) if col in selected_temp_cols]
                filtered_column_types['temp_sensors'] = [col for col in column_types.get('temp_sensors', []) if col in selected_temp_cols]
                filtered_column_types['temp_stats'] = [col for col in column_types.get('temp_stats', []) if col in selected_temp_cols]
                return plot_generator.create_heatmap_plot(df, filtered_column_types, "temperature")
            else:
                return plot_generator.create_heatmap_plot(df, column_types, "temperature")
        
    except Exception as e:
        print(f"Error creating plot: {e}")
    
    return go.Figure()


def create_data_overview_plot(df: pd.DataFrame, column_types: dict) -> go.Figure:
    """Create a simple overview plot showing the first few columns over time"""
    fig = go.Figure()
    
    # Get time column if available
    time_col = None
    if df.index.name and 'time' in df.index.name.lower():
        x_data = df.index
        x_title = df.index.name
    elif 'time' in df.columns[0].lower():
        time_col = df.columns[0]
        x_data = df[time_col]
        x_title = time_col
    else:
        x_data = df.index
        x_title = "Index"
    
    # Plot first few numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    plot_cols = numeric_cols[:5]  # Limit to first 5 columns
    
    colors = px.colors.qualitative.Set3
    for i, col in enumerate(plot_cols):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig.update_layout(
        title="Data Overview - Selected Columns",
        xaxis_title=x_title,
        yaxis_title="Values",
        template="plotly_white",
        height=600
    )
    
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
