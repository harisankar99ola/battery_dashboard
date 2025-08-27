import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

class BatteryPlots:
    """
    Create various battery data visualizations
    """
    
    def __init__(self):
        self.default_template = "plotly_white"
        self.color_palette = px.colors.qualitative.Set3
    
    def create_temperature_overview(self, df: pd.DataFrame, column_types: Dict[str, List[str]]) -> go.Figure:
        """Create comprehensive temperature overview plot"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Thermocouple Temperatures', 'BMS Temperature Sensors', 
                          'Temperature Statistics', 'Temperature Distribution'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Thermocouple data
        if column_types.get('thermocouple'):
            for i, col in enumerate(column_types['thermocouple']):  # Show all thermocouple columns
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[col], 
                        name=col,  # Use actual column name
                        line=dict(color=self.color_palette[i % len(self.color_palette)]),
                        opacity=0.7
                    ),
                    row=1, col=1
                )
        
        # BMS temperature sensors
        if column_types.get('temp_sensors'):
            for i, col in enumerate(column_types['temp_sensors']):  # Show all BMS sensors
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[col],
                        name=col,  # Use actual column name
                        line=dict(color=self.color_palette[i % len(self.color_palette)])
                    ),
                    row=1, col=2
                )
        
        # Temperature statistics (if available)
        temp_cols = column_types.get('thermocouple', []) + column_types.get('temp_sensors', [])
        if temp_cols:
            temp_data = df[temp_cols]
            temp_mean = temp_data.mean(axis=1)
            temp_max = temp_data.max(axis=1)
            temp_min = temp_data.min(axis=1)
            
            fig.add_trace(
                go.Scatter(x=df.index, y=temp_mean, name='Mean Temp', 
                          line=dict(color='red', width=2)),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=temp_max, name='Max Temp',
                          line=dict(color='orange', dash='dash')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=temp_min, name='Min Temp',
                          line=dict(color='blue', dash='dash')),
                row=2, col=1
            )
            
            # Temperature distribution
            fig.add_trace(
                go.Histogram(x=temp_mean, name='Temp Distribution',
                           marker_color='lightblue', opacity=0.7),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Battery Temperature Analysis",
            template=self.default_template,
            showlegend=True
        )
        
        return fig
    
    def create_voltage_analysis(self, df: pd.DataFrame, column_types: Dict[str, List[str]]) -> go.Figure:
        """Create comprehensive voltage analysis plot"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Individual Cell Voltages', 'Voltage Statistics', 
                          'Voltage vs Time', 'Voltage Distribution'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        voltage_cols = column_types.get('cell_voltages', [])
        
        if voltage_cols:
            # Individual cell voltages (show all cells)
            for i, col in enumerate(voltage_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[col],
                        name=col,  # Use actual column name instead of Cell_1, Cell_2
                        line=dict(color=self.color_palette[i % len(self.color_palette)]),
                        opacity=0.6
                    ),
                    row=1, col=1
                )
            
            # Voltage statistics
            voltage_data = df[voltage_cols]
            voltage_mean = voltage_data.mean(axis=1)
            voltage_max = voltage_data.max(axis=1)
            voltage_min = voltage_data.min(axis=1)
            voltage_std = voltage_data.std(axis=1)
            
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_mean, name='Mean Voltage',
                          line=dict(color='green', width=2)),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_max, name='Max Voltage',
                          line=dict(color='red', dash='dash')),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_min, name='Min Voltage',
                          line=dict(color='blue', dash='dash')),
                row=1, col=2
            )
            
            # Voltage range over time
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_max - voltage_min, 
                          name='Voltage Range',
                          line=dict(color='purple', width=2)),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_std, 
                          name='Voltage Std Dev',
                          line=dict(color='orange', width=2)),
                row=2, col=1
            )
            
            # Voltage distribution
            fig.add_trace(
                go.Histogram(x=voltage_mean, name='Voltage Distribution',
                           marker_color='lightgreen', opacity=0.7),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Battery Voltage Analysis",
            template=self.default_template,
            showlegend=True
        )
        
        return fig
    
    def create_soc_temperature_plot(self, soc_temp_data: dict) -> go.Figure:
        """Create SOC vs Temperature relationship plot from analysis data"""
        try:
            print(f"Creating SOC temperature plot with data keys: {soc_temp_data.keys() if soc_temp_data else 'None'}")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['SOC vs Temperature (Line Chart)', 'SOC vs Temperature (Heatmap)', 
                              'Temperature Distribution by SOC', 'SOC Range Summary'],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Check if the response structure is correct
            if not soc_temp_data or not soc_temp_data.get('success', False):
                print("SOC analysis was not successful")
                fig.add_annotation(
                    text="SOC vs Temperature analysis failed.<br>Please check your data selection.",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16), align="center"
                )
                return fig
            
            # Extract data from the correct structure
            analysis_data = soc_temp_data.get('data', {})
            if 'temperature_data' not in analysis_data:
                print("No temperature_data found in SOC analysis data")
                fig.add_annotation(
                    text="No SOC vs Temperature data available.<br>Please select temperature columns and try again.",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16), align="center"
                )
                return fig
            
            soc_points = analysis_data.get('soc_points', [])
            temp_data = analysis_data.get('temperature_data', {})
            
            print(f"SOC points: {len(soc_points)} points")
            print(f"Temperature sensors: {len(temp_data)} sensors")
            
            if not soc_points or not temp_data:
                fig.add_annotation(
                    text="Insufficient data for SOC vs Temperature analysis.<br>Please check your data selection.",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16), align="center"
                )
                return fig
            
            # 1. Line chart - SOC vs Temperature for each sensor
            colors = px.colors.qualitative.Set3
            heatmap_data = []
            sensor_names = []
            
            for i, (sensor, temps) in enumerate(temp_data.items()):
                # Filter out None values for line plot
                valid_indices = [j for j, temp in enumerate(temps) if temp is not None]
                valid_soc = [soc_points[j] for j in valid_indices]
                valid_temps = [temps[j] for j in valid_indices]
                
                if valid_temps:
                    # Create shorter name for legend
                    if 'LH-' in sensor or 'RH-' in sensor:
                        parts = sensor.split('-')
                        if len(parts) >= 3:
                            legend_name = f"{parts[0]}-{parts[1]}-{parts[2]}"
                        else:
                            legend_name = sensor.replace('_avg', '')
                    else:
                        legend_name = sensor.replace('_avg', '').replace('Temperature', 'Temp')
                    
                    fig.add_trace(
                        go.Scatter(
                            x=valid_soc, y=valid_temps,
                            mode='lines+markers',
                            name=legend_name,
                            line=dict(color=colors[i % len(colors)]),
                            marker=dict(size=4),
                            legendgroup="temperature"
                        ),
                        row=1, col=1
                    )
                
                # Prepare data for heatmap (include None as NaN)
                heatmap_data.append(temps)
                # Create very short sensor names for heatmap y-axis
                if 'LH-' in sensor or 'RH-' in sensor:
                    parts = sensor.split('-')
                    if len(parts) >= 4:
                        # Format: LH-C1-Cell1 or RH-C2-Cell3
                        short_name = f"{parts[0]}-{parts[1]}-{parts[2]}"
                    else:
                        short_name = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else sensor[:10]
                elif 'Pack_Temperature' in sensor:
                    # Extract number: BMSXX_Pack_Temperature_XX_avg -> PackTemp_XX
                    if 'Pack_Temperature_' in sensor:
                        temp_num = sensor.split('Pack_Temperature_')[1].split('_')[0]
                        short_name = f"PackTemp_{temp_num}"
                    else:
                        short_name = "PackTemp"
                elif 'Battery_Temperature' in sensor:
                    if 'Min' in sensor:
                        short_name = "BattTempMin"
                    elif 'Max' in sensor:
                        short_name = "BattTempMax"
                    else:
                        short_name = "BattTemp"
                elif 'Effective_Battery_Temperature' in sensor:
                    short_name = "EffBattTemp"
                else:
                    short_name = sensor.replace('_avg', '')[:12]
                
                sensor_names.append(short_name)            # 2. Heatmap - SOC vs Temperature
            if heatmap_data:
                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data,
                        x=soc_points,
                        y=sensor_names,
                        colorscale='Viridis',
                        showscale=True,
                        hoverongaps=False,
                        hovertemplate='SOC: %{x}%<br>Sensor: %{y}<br>Temp: %{z:.1f}°C<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. Temperature distribution by SOC ranges
            if temp_data:
                # Group SOC into ranges: 0-25%, 25-50%, 50-75%, 75-100%
                soc_ranges = ['0-25%', '25-50%', '50-75%', '75-100%']
                
                for sensor, temps in list(temp_data.items())[:5]:  # First 5 sensors for clarity
                    range_temps = [
                        [temps[j] for j in range(0, 6) if temps[j] is not None],      # 0-25%
                        [temps[j] for j in range(5, 11) if temps[j] is not None],    # 25-50%
                        [temps[j] for j in range(10, 16) if temps[j] is not None],   # 50-75%
                        [temps[j] for j in range(15, 21) if temps[j] is not None]    # 75-100%
                    ]
                    
                    for k, (soc_range, range_temps_list) in enumerate(zip(soc_ranges, range_temps)):
                        if range_temps_list:
                            fig.add_trace(
                                go.Box(
                                    y=range_temps_list,
                                    name=f"{sensor[:15]}...",  # Truncated name
                                    x=[soc_range] * len(range_temps_list),
                                    boxpoints='all',
                                    jitter=0.3,
                                    pointpos=-1.8
                                ),
                                row=2, col=1
                            )
                    break  # Only show one sensor for box plot clarity
            
            # 4. Summary statistics
            if temp_data:
                summary_text = []
                for sensor, temps in temp_data.items():
                    valid_temps = [t for t in temps if t is not None]
                    if valid_temps:
                        min_temp = min(valid_temps)
                        max_temp = max(valid_temps)
                        avg_temp = sum(valid_temps) / len(valid_temps)
                        summary_text.append(f"{sensor[:20]}: {min_temp:.1f}-{max_temp:.1f}°C (avg: {avg_temp:.1f}°C)")
                
                fig.add_annotation(
                    text="<br>".join(summary_text[:10]),  # First 10 sensors
                    xref="x4", yref="y4",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=10),
                    align="left"
                )
            
            # 2. Heatmap - SOC vs Temperature
            if heatmap_data:
                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data,
                        x=soc_points,
                        y=sensor_names,
                        colorscale='Viridis',
                        showscale=True,
                        hoverongaps=False,
                        hovertemplate='SOC: %{x}%<br>Sensor: %{y}<br>Temp: %{z:.1f}°C<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. Temperature distribution by SOC ranges
            if temp_data:
                # Group SOC into ranges: 0-25%, 25-50%, 50-75%, 75-100%
                soc_ranges = ['0-25%', '25-50%', '50-75%', '75-100%']
                
                for sensor, temps in list(temp_data.items())[:5]:  # First 5 sensors for clarity
                    range_temps = [
                        [temps[j] for j in range(0, 6) if temps[j] is not None],      # 0-25%
                        [temps[j] for j in range(5, 11) if temps[j] is not None],    # 25-50%
                        [temps[j] for j in range(10, 16) if temps[j] is not None],   # 50-75%
                        [temps[j] for j in range(15, 21) if temps[j] is not None]    # 75-100%
                    ]
                    
                    for k, (soc_range, range_temps_list) in enumerate(zip(soc_ranges, range_temps)):
                        if range_temps_list:
                            fig.add_trace(
                                go.Box(
                                    y=range_temps_list,
                                    name=f"{sensor[:15]}...",  # Truncated name
                                    x=[soc_range] * len(range_temps_list),
                                    boxpoints='all',
                                    jitter=0.3,
                                    pointpos=-1.8
                                ),
                                row=2, col=1
                            )
                    break  # Only show one sensor for box plot clarity
            
            # 4. Summary statistics
            if temp_data:
                summary_text = []
                for sensor, temps in temp_data.items():
                    valid_temps = [t for t in temps if t is not None]
                    if valid_temps:
                        min_temp = min(valid_temps)
                        max_temp = max(valid_temps)
                        avg_temp = sum(valid_temps) / len(valid_temps)
                        summary_text.append(f"{sensor[:20]}: {min_temp:.1f}-{max_temp:.1f}°C (avg: {avg_temp:.1f}°C)")
                
                fig.add_annotation(
                    text="<br>".join(summary_text[:10]),  # First 10 sensors
                    xref="x4", yref="y4",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=10),
                    align="left"
                )
            
            fig.update_layout(
                height=800,
                title_text="SOC vs Temperature Analysis",
                template=self.default_template,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=10),
                    itemsizing="constant",
                    itemwidth=30
                ),
                margin=dict(l=150, r=200, t=80, b=80)  # Increase left and right margins
            )
            
            # Update axes labels with better spacing
            fig.update_xaxes(title_text="SOC (%)", row=1, col=1)
            fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
            fig.update_xaxes(title_text="SOC (%)", row=1, col=2)
            fig.update_yaxes(
                title_text="Sensors", 
                row=1, col=2,
                tickfont=dict(size=9),  # Smaller font for sensor names
                automargin=True
            )
            fig.update_xaxes(title_text="SOC Range", row=2, col=1)
            fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
            
            return fig
        
        except Exception as e:
            print(f"Error creating SOC temperature plot: {e}")
            error_fig = go.Figure()
            error_fig.add_annotation(
                text=f"Error creating SOC vs Temperature plot:<br>{str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16), align="center"
            )
            return error_fig

    def create_3d_temperature_voltage_plot(self, df: pd.DataFrame, column_types: Dict[str, List[str]]) -> go.Figure:
        """Create 3D plot of temperature vs voltage vs time"""
        voltage_cols = column_types.get('cell_voltages', [])
        temp_cols = column_types.get('thermocouple', []) + column_types.get('temp_sensors', [])
        
        if not voltage_cols or not temp_cols:
            return go.Figure()
        
        # Calculate mean values
        voltage_mean = df[voltage_cols].mean(axis=1)
        temp_mean = df[temp_cols].mean(axis=1)
        time_normalized = (df.index - df.index.min()) / (df.index.max() - df.index.min())
        
        fig = go.Figure(data=[go.Scatter3d(
            x=time_normalized,
            y=voltage_mean,
            z=temp_mean,
            mode='markers+lines',
            marker=dict(
                size=3,
                color=temp_mean,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Temperature (°C)")
            ),
            line=dict(color='darkblue', width=2),
            text=[f'Time: {t:.1f}s<br>Voltage: {v:.3f}V<br>Temp: {temp:.1f}°C' 
                  for t, v, temp in zip(df.index, voltage_mean, temp_mean)],
            hovertemplate='%{text}<extra></extra>',
            name='Battery State'
        )])
        
        fig.update_layout(
            title='3D Battery State Evolution: Temperature vs Voltage vs Time',
            scene=dict(
                xaxis_title='Normalized Time',
                yaxis_title='Average Voltage (V)',
                zaxis_title='Average Temperature (°C)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            template=self.default_template,
            height=700
        )
        
        return fig
    
    def create_3d_crate_analysis(self, df: pd.DataFrame, column_types: Dict[str, List[str]], 
                                c_rate_data: pd.Series = None) -> go.Figure:
        """Create 3D plot with C-rate, SOC, and Temperature"""
        temp_cols = column_types.get('thermocouple', []) + column_types.get('temp_sensors', [])
        soc_cols = column_types.get('soc_soh', [])
        
        if not all([temp_cols, soc_cols]):
            return go.Figure().add_annotation(
                text="Missing required data for 3D C-Rate analysis",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
        
        # Calculate mean temperature
        temp_mean = df[temp_cols].mean(axis=1)
        
        # Get SOC data
        soc_col = [col for col in soc_cols if 'soc' in col.lower()]
        if not soc_col:
            return go.Figure().add_annotation(
                text="No SOC data found",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
        
        soc_data = df[soc_col[0]]
        
        # Use provided C-rate or estimate from current
        if c_rate_data is not None:
            c_rate = c_rate_data
        else:
            current_cols = column_types.get('current', [])
            if current_cols:
                current_data = df[current_cols[0]]
                c_rate = abs(current_data) / 3.5  # Assuming 3.5Ah capacity
            else:
                c_rate = pd.Series(np.ones(len(df)), index=df.index)  # Default to 1C
        
        # Sample data for plotting (to avoid too many points)
        sample_size = min(1000, len(df))
        sample_indices = np.linspace(0, len(df)-1, sample_size, dtype=int)
        
        soc_sample = soc_data.iloc[sample_indices]
        temp_sample = temp_mean.iloc[sample_indices]
        c_rate_sample = c_rate.iloc[sample_indices]
        
        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=soc_sample,
            y=temp_sample,
            z=c_rate_sample,
            mode='markers',
            marker=dict(
                size=8,
                color=temp_sample,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Temperature (°C)"),
                opacity=0.8
            ),
            text=[f'SOC: {s:.1f}%<br>Temp: {t:.1f}°C<br>C-Rate: {c:.2f}C' 
                  for s, t, c in zip(soc_sample, temp_sample, c_rate_sample)],
            hovertemplate='%{text}<extra></extra>',
            name='Battery Operating Points'
        )])
        
        fig.update_layout(
            title='3D Battery Analysis: SOC vs Temperature vs C-Rate',
            scene=dict(
                xaxis_title='SOC (%)',
                yaxis_title='Temperature (°C)',
                zaxis_title='C-Rate',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            ),
            template=self.default_template,
            height=700
        )
        
        return fig
    
    def create_heatmap_plot(self, df: pd.DataFrame, column_types: Dict[str, List[str]], 
                           plot_type: str = 'temperature') -> go.Figure:
        """Create heatmap for temperature or voltage data"""
        if plot_type == 'temperature':
            cols = column_types.get('thermocouple', []) + column_types.get('temp_sensors', [])
            title = "Temperature Heatmap Over Time"
            colorbar_title = "Temperature (°C)"
        else:
            cols = column_types.get('cell_voltages', [])
            title = "Voltage Heatmap Over Time"
            colorbar_title = "Voltage (V)"
        
        if not cols:
            return go.Figure()
        
        # Sample data for better performance (every 10th point)
        sample_df = df[cols].iloc[::10]
        
        # Create shortened but meaningful labels for y-axis
        y_labels = []
        for col in cols:
            if 'thermocouple' in plot_type.lower() or plot_type == 'temperature':
                # For temperature columns, extract meaningful parts
                if 'LH-' in col or 'RH-' in col:
                    # Extract like "LH-C1-Cell3" from "LH-C1-Cell3-T27_avg"
                    parts = col.split('-')
                    if len(parts) >= 3:
                        y_labels.append(f"{parts[0]}-{parts[1]}-{parts[2]}")
                    else:
                        y_labels.append(col.replace('_avg', ''))
                elif 'BMS' in col:
                    # Extract like "BMS-Temp01" from "BMS00_Pack_Temperature_01_avg"
                    if 'Temperature' in col:
                        temp_num = col.split('_')[-2]
                        y_labels.append(f"BMS-T{temp_num}")
                    else:
                        y_labels.append(col.replace('_avg', ''))
                else:
                    y_labels.append(col.replace('_avg', ''))
            else:
                y_labels.append(col.replace('_avg', ''))
        
        fig = go.Figure(data=go.Heatmap(
            z=sample_df.T.values,
            x=sample_df.index,
            y=y_labels,
            colorscale='Viridis',
            colorbar=dict(title=colorbar_title),
            hoverongaps=False,
            hovertemplate='Time: %{x}<br>Column: %{y}<br>Value: %{z:.2f}<br>Full Name: %{customdata}<extra></extra>',
            customdata=cols  # Show full column name on hover
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Temperature Sensors",
            template=self.default_template,
            height=600,
            yaxis=dict(tickmode='linear')
        )
        
        return fig
    
    def create_phase_analysis_plot(self, df: pd.DataFrame, phases: Dict[str, List], 
                                  column_types: Dict[str, List[str]]) -> go.Figure:
        """Create plot showing different test phases"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=['Current vs Time', 'Voltage vs Time', 'Temperature vs Time'],
            shared_xaxes=True,
            vertical_spacing=0.08
        )
        
        # Current plot
        current_cols = column_types.get('current', [])
        if current_cols:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[current_cols[0]],
                          name='Current', line=dict(color='blue')),
                row=1, col=1
            )
        
        # Voltage plot
        voltage_cols = column_types.get('cell_voltages', [])
        if voltage_cols:
            voltage_mean = df[voltage_cols].mean(axis=1)
            fig.add_trace(
                go.Scatter(x=df.index, y=voltage_mean,
                          name='Avg Voltage', line=dict(color='green')),
                row=2, col=1
            )
        
        # Temperature plot
        temp_cols = column_types.get('thermocouple', []) + column_types.get('temp_sensors', [])
        if temp_cols:
            temp_mean = df[temp_cols].mean(axis=1)
            fig.add_trace(
                go.Scatter(x=df.index, y=temp_mean,
                          name='Avg Temperature', line=dict(color='red')),
                row=3, col=1
            )
        
        # Add phase annotations
        colors = {'charge': 'rgba(0,255,0,0.2)', 'discharge': 'rgba(255,0,0,0.2)', 'rest': 'rgba(128,128,128,0.2)'}
        
        for phase, intervals in phases.items():
            for start_idx, end_idx in intervals:
                if start_idx < len(df) and end_idx < len(df):
                    start_time = df.index[start_idx]
                    end_time = df.index[end_idx]
                    
                    for row in [1, 2, 3]:
                        fig.add_vrect(
                            x0=start_time, x1=end_time,
                            fillcolor=colors.get(phase, 'rgba(0,0,0,0.1)'),
                            opacity=0.3,
                            line_width=0,
                            row=row, col=1
                        )
        
        fig.update_layout(
            height=800,
            title_text="Battery Test Phases Analysis",
            template=self.default_template,
            showlegend=True
        )
        
        fig.update_yaxes(title_text="Current (A)", row=1, col=1)
        fig.update_yaxes(title_text="Voltage (V)", row=2, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=3, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        return fig
