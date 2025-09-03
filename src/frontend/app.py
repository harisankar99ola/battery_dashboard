"""Simplified overview-only Dash app."""

import dash
from dash import dcc, html, Input, Output, State, dash_table, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import requests
from plotly.subplots import make_subplots

API_BASE_URL = "http://localhost:8000"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Battery Dashboard (Overview Only)"

def create_header():
    return dbc.NavbarSimple(brand="🔋 Battery Dashboard (Overview Only)", color="dark", dark=True, className="mb-4")

def create_file_selector():
    return dbc.Card([
        dbc.CardHeader("📁 Data Selection"),
        dbc.CardBody([
            dbc.Alert(id="file-status-alert", children="Ready to load files", color="info", is_open=True, dismissable=False, className="mb-3"),
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="selected-files-display", children=[html.P("No files selected", className="text-muted mb-0")], style={"minHeight":"50px","maxHeight":"150px","overflowY":"auto"})
                    ], style={"padding":"10px"})
                ], style={"marginBottom":"10px"}),
                dbc.Button("📂 Open File Selector", id="open-file-selector-btn", color="primary", size="sm", className="mb-3")
            ]),
            dcc.Dropdown(id="file-dropdown", placeholder="Loading all CSV files...", multi=True, className="mb-2", style={"display":"none"}),
            html.Label("Select Columns to Load:", className="fw-bold"),
            dcc.Dropdown(id="column-dropdown", placeholder="Select files first to see columns...", multi=True, className="mb-2", style={"fontSize":"12px"}),
            dbc.Button("✅ Select All Columns", id="select-all-columns-btn", color="secondary", size="sm", className="mb-3"),
            dbc.Badge(id="cache-status-badge", children="Checking cache...", color="secondary")
        ])
    ], className="mb-4")

def create_stats_cards():
    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("0", id="files-count", className="text-primary"), html.P("Files Loaded")])) , width=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("0", id="data-points", className="text-success"), html.P("Data Points")])) , width=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("0h", id="duration", className="text-info"), html.P("Test Duration")])) , width=4)
        ])
    ], className="mb-4")

# Main layout
app.layout = dbc.Container([
    create_header(),
    dcc.Loading(id="loading", children=[html.Div(id="loading-output")], type="default"),
    dcc.Store(id="files-store"),
    dcc.Store(id="current-data-store"),
    dcc.Store(id="combined-data-store"),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("📂 Select CSV Files")),
        dbc.ModalBody([
            html.Div([
                html.P("Select the CSV files you want to analyze:", className="mb-3"),
                html.Div(id="file-checkboxes-container", children=[html.P("Loading files...", className="text-muted")], style={"maxHeight":"400px","overflowY":"auto"}),
                html.Hr(),
                dbc.Row([
                    dbc.Col(dbc.Button("✅ Select All", id="modal-select-all-btn", color="primary", size="sm"), width=6),
                    dbc.Col(dbc.Button("❌ Clear All", id="modal-clear-all-btn", color="secondary", size="sm"), width=6)
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="modal-cancel-btn", color="secondary", className="me-2"),
            dbc.Button("Apply Selection", id="modal-apply-btn", color="primary")
        ])
    ], id="file-selector-modal", size="lg", is_open=False),
    dbc.Row([
        dbc.Col([create_file_selector()], width=4),
        dbc.Col([
            create_stats_cards(),
            dbc.Card([
                dbc.CardHeader("📈 Data Overview"),
                dbc.CardBody([dcc.Graph(id="main-plot", figure={}, style={"height":"700px","width":"100%"})], style={"padding":"20px"})
            ], className="mb-4")
        ], width=8)
    ], className="g-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📋 Data Table"),
                dbc.CardBody([html.Div(id="data-table-container")])
            ])
        ], width=12)
    ], className="mt-4"),
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)
], fluid=True)

# Callbacks

## Plot type selection removed – always overview

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
        response = requests.get(f"{API_BASE_URL}/api/columns/{file_id}")
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
    Output("file-status-alert", "children"),
    Output("file-status-alert", "color"),
    Input("file-dropdown", "value"),
    prevent_initial_call=True
)
def auto_preview_data(selected_files):
    """Automatically load data when files are selected (full load, not just preview)"""
    if not selected_files:
        return {}, "0", "0", "0h", "Ready to load files", "info"

    try:
        file_count = len(selected_files) if isinstance(selected_files, list) else 1
        file_list = selected_files if isinstance(selected_files, list) else [selected_files]
        first_file = file_list[0]

        params = {"preprocess": True, "resample": "1S"}
        response = requests.get(f"{API_BASE_URL}/api/data/{first_file}", params=params)

        if response.status_code != 200:
            error_msg = f"❌ Failed to load data (Status: {response.status_code})"
            return {}, "0", "0", "0h", error_msg, "danger"

        full_data = response.json()
        stats = full_data.get('statistics', {})
        data_points = stats.get('total_rows', 0)
        if 'shape' in stats:
            data_points = stats['shape'][0]

        duration = "0h"
        if 'duration_hours' in stats:
            hours = stats['duration_hours']
            duration = f"{int(hours * 60)}m" if hours < 1 else f"{hours:.1f}h"
        elif 'time_range' in stats:
            time_range = stats['time_range']
            duration_sec = time_range.get('duration', 0)
            hours = duration_sec / 3600
            duration = f"{int(hours * 60)}m" if hours < 1 else f"{hours:.1f}h"

        success_msg = f"✅ Data loaded: {data_points:,} data points from {file_count} file(s)"
        print(f"✅ Auto-loaded full data with column types: {list(stats.get('column_types', {}).keys())}")
        return full_data, str(file_count), f"{data_points:,}", duration, success_msg, "success"

    except Exception as e:
        import traceback
        print(f"Error in auto-preview: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        error_msg = f"❌ Error loading data: {str(e)[:50]}..."
        return {}, "0", "0", "0h", error_msg, "warning"

# Callback for temperature columns "Select All" button
## Temperature selection removed

@app.callback(
    Output("main-plot", "figure"),
    Input("current-data-store", "data"),
    Input("combined-data-store", "data")
)
def update_main_plot(current_data, combined_data):
    data_source = combined_data if combined_data else current_data
    if not data_source or not data_source.get("data"):
        return go.Figure()
    try:
        df_data = data_source["data"]
        if "index" in data_source:
            df = pd.DataFrame(df_data, index=data_source["index"])
        else:
            df = pd.DataFrame(df_data)
        return create_data_overview_plot(df)
    except Exception:
        return go.Figure()


def create_data_overview_plot(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=3, cols=2, shared_xaxes=True, subplot_titles=(
        'Cell Voltages','BMS Temps','Current','Thermocouples','SOC/SOH','Balancing'))
    def pick(pred, limit=None):
        cols=[c for c in df.columns if pred(c)]
        return cols if limit is None else cols[:limit]
    volt = pick(lambda c: 'Cell_Voltage_Cell' in c, 12)
    bms = pick(lambda c: 'BMS00_Pack_' in c and '02' not in c and '05' not in c, 8)
    pdu = pick(lambda c: 'BMS00_PDU_Temperature_' in c, 4)
    thermo = pick(lambda c: 'RH' in c or 'LH' in c, 8)
    soc = pick(lambda c: 'Pack_S' in c, 4)
    bal = pick(lambda c: '_Balancing_Status_' in c, 6)
    current_col = next((c for c in df.columns if 'Battery_Current' in c), None)
    for c in volt:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'), row=1, col=1)
    for c in bms + pdu:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'), row=1, col=2)
    if current_col:
        fig.add_trace(go.Scatter(x=df.index, y=df[current_col], name=current_col, mode='lines'), row=2, col=1)
    for c in thermo:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'), row=2, col=2)
    for c in soc:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'), row=3, col=1)
    for c in bal:
        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'), row=3, col=2)
    fig.update_layout(height=800, template='plotly_white', title_text='Data Overview')
    return fig


## Removed other analysis plots

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

## Efficiency removed

## SOC temperature download removed

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
