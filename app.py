import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
import numpy as np
from datetime import datetime, timedelta
import os
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Set page configuration
st.set_page_config(
    page_title="Social Determinants of Health (SDOH) Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Census API Configuration
CENSUS_API_KEY = None  # Census API can work without key for basic queries
CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs1"

# SDOH Metrics Configuration
SDOH_METRICS = {
    "Median Household Income": {
        "variable": "DP03_0062E",
        "endpoint": "profile",
        "positive": True,
        "description": "Median household income in the past 12 months (in 2022 inflation-adjusted dollars)"
    },
    "Poverty Rate": {
        "variable": "DP03_0119PE", 
        "endpoint": "profile",
        "positive": False,
        "description": "Percentage of population below poverty level"
    },
    "Educational Attainment (Bachelor's+)": {
        "variable": "DP02_0065PE",
        "endpoint": "profile",
        "positive": True,
        "description": "Percentage of population 25+ with bachelor's degree or higher"
    },
    "Unemployment Rate": {
        "variable": "DP03_0005PE",
        "endpoint": "profile",
        "positive": False,
        "description": "Unemployment rate for population 16 years and over"
    },
    "Health Insurance Coverage": {
        "variable": "DP03_0096PE",
        "endpoint": "profile",
        "positive": True,
        "description": "Percentage of population with health insurance coverage"
    }
}

# State FIPS to abbreviation mapping
FIPS_TO_ABBREV = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY",
    # Also include non-zero padded versions for consistency
    "1": "AL", "2": "AK", "4": "AZ", "5": "AR", "6": "CA", "8": "CO", "9": "CT"
}


class CensusDataManager:
    def __init__(self):
        self.cache_file = "census_data_cache.csv"
        self.cache_duration = timedelta(weeks=1)  # Cache for 1 week
        # Use separate state and county cache files to avoid column conflicts
        self.state_cache_file = "census_state_cache.csv"
        self.county_cache_file = "census_county_cache.csv"
        
    def load_cache(self):
        """Load cached data from separate state and county files"""
        cache_data = {}
        
        # Load state cache
        if os.path.exists(self.state_cache_file):
            try:
                df = pd.read_csv(self.state_cache_file, dtype={'fips': str})
                if not df.empty:
                    cache_time = datetime.fromisoformat(df['timestamp'].iloc[0])
                    if datetime.now() - cache_time < self.cache_duration:
                        for key in df['cache_key'].unique():
                            key_data = df[df['cache_key'] == key].copy()
                            key_data = key_data.drop(['cache_key', 'timestamp'], axis=1, errors='ignore')
                            if 'fips' in key_data.columns:
                                key_data['fips'] = key_data['fips'].astype(str).str.zfill(2)
                            cache_data[key] = key_data.to_dict('records')
            except Exception as e:
                st.warning(f"Error loading state cache: {e}")
        
        # Load county cache
        if os.path.exists(self.county_cache_file):
            try:
                df = pd.read_csv(self.county_cache_file, dtype={'county_fips': str, 'state_fips': str})
                if not df.empty:
                    cache_time = datetime.fromisoformat(df['timestamp'].iloc[0])
                    if datetime.now() - cache_time < self.cache_duration:
                        for key in df['cache_key'].unique():
                            key_data = df[df['cache_key'] == key].copy()
                            key_data = key_data.drop(['cache_key', 'timestamp'], axis=1, errors='ignore')
                            cache_data[key] = key_data.to_dict('records')
            except Exception as e:
                st.warning(f"Error loading county cache: {e}")
                
        return cache_data
    
    def save_cache(self, data):
        """Save data to separate cache files for state and county data"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Load existing cache
            existing_data = self.load_cache()
            existing_data.update(data)
            
            # Separate state and county data
            state_data = {}
            county_data = {}
            
            for cache_key, records in existing_data.items():
                if cache_key.endswith('_state'):
                    state_data[cache_key] = records
                else:
                    county_data[cache_key] = records
            
            # Save state data
            if state_data:
                state_rows = []
                for cache_key, records in state_data.items():
                    for record in records:
                        row = {'cache_key': cache_key, 'timestamp': timestamp}
                        row.update(record)
                        state_rows.append(row)
                
                if state_rows:
                    df = pd.DataFrame(state_rows)
                    df.to_csv(self.state_cache_file, index=False)
            
            # Save county data
            if county_data:
                county_rows = []
                for cache_key, records in county_data.items():
                    for record in records:
                        row = {'cache_key': cache_key, 'timestamp': timestamp}
                        row.update(record)
                        county_rows.append(row)
                
                if county_rows:
                    df = pd.DataFrame(county_rows)
                    df.to_csv(self.county_cache_file, index=False)
                    
        except Exception as e:
            st.warning(f"Error saving cache: {e}")
    
    def fetch_census_data(self, metric_key, geography_level="state"):
        """Fetch data from Census API"""
        cache_key = f"{metric_key}_{geography_level}"
        cached_data = self.load_cache()
        
        if cache_key in cached_data:
            return cached_data[cache_key]
        
        metric_config = SDOH_METRICS[metric_key]
        variable = metric_config["variable"]
        endpoint = metric_config["endpoint"]
        
        try:
            if geography_level == "state":
                # Fetch state-level data
                url = f"{CENSUS_BASE_URL}/{endpoint}"
                params = {
                    "get": f"{variable},NAME",
                    "for": "state:*"
                }
            else:
                # Fetch county-level data for a specific state
                state_fips = geography_level  # Expecting state FIPS code
                url = f"{CENSUS_BASE_URL}/{endpoint}"
                params = {
                    "get": f"{variable},NAME",
                    "for": f"county:*",
                    "in": f"state:{state_fips}"
                }
            
            if CENSUS_API_KEY:
                params["key"] = CENSUS_API_KEY
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the data
            if len(data) > 1:  # First row is headers
                rows = data[1:]
                
                processed_data = []
                for row in rows:
                    try:
                        value = float(row[0]) if row[0] not in [None, '', '-'] else None
                        name = row[1]
                        
                        if geography_level == "state":
                            fips = row[2]
                            # Normalize FIPS code to 2-digit zero-padded format
                            fips = fips.zfill(2)
                            # Skip Puerto Rico and other territories for US state maps
                            if fips not in FIPS_TO_ABBREV:
                                continue
                            processed_data.append({
                                'name': name,
                                'fips': fips,
                                'value': value
                            })
                        else:
                            state_fips = row[2].zfill(2)
                            county_fips = row[3].zfill(3)
                            processed_data.append({
                                'name': name,
                                'county_fips': county_fips,
                                'state_fips': state_fips,
                                'value': value
                            })
                    except (ValueError, IndexError):
                        continue
                
                # Update cache
                cached_data[cache_key] = processed_data
                self.save_cache(cached_data)
                
                return processed_data
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Request failed: {e}")
            return []
        except Exception as e:
            st.error(f"Error processing data: {e}")
            return []
        
        return []

def create_choropleth_map(data, metric_key, title_suffix=""):
    """Create a choropleth map using Plotly"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    if df.empty or 'value' not in df.columns:
        return None
    
    # Remove rows with null values and filter out territories
    df = df.dropna(subset=['value'])
    df = df[df['fips'].isin(FIPS_TO_ABBREV.keys())]
    
    if df.empty:
        return None
    
    metric_config = SDOH_METRICS[metric_key]
    is_positive = metric_config["positive"]
    
    # Choose color scale based on metric type
    color_scale = 'Greens' if is_positive else 'Reds'
    
    # Convert FIPS to state abbreviations
    df['abbrev'] = df['fips'].map(FIPS_TO_ABBREV)
    # Remove any rows where mapping failed
    df = df.dropna(subset=['abbrev'])
    
    # Create the choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=df['abbrev'],
        z=df['value'],
        locationmode='USA-states',
        colorscale=color_scale,
        text=df['name'],
        zmin=df['value'].min(),
        zmax=df['value'].max(),
        hovertemplate='<b>%{text}</b><br>' + f'{metric_key}: %{{z:,.2f}}<extra></extra>',
        colorbar=dict(title=metric_key),
        showscale=True
    ))
    
    fig.update_layout(
        title=f"{metric_key} by State{title_suffix}",
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='albers usa',
            scope='usa'
        ),
        height=600
    )
    
    return fig

def create_county_map(data, metric_key, state_name):
    """Create a county-level choropleth map"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    if df.empty or 'value' not in df.columns:
        return None
    
    # Remove rows with null values
    df = df.dropna(subset=['value'])
    
    if df.empty:
        return None
    
    # Create FIPS codes for counties (state + county)
    df['full_fips'] = df['state_fips'] + df['county_fips']

    
    metric_config = SDOH_METRICS[metric_key]
    is_positive = metric_config["positive"]
    
    # Choose color scale based on metric type
    color_scale = 'Greens' if is_positive else 'Reds'
    
    # Add note about data availability
    st.info(f"🗺️ Showing {len(df)} counties with available data. Counties with insufficient population (<65,000) appear uncolored.")

    # Create choropleth map using geojson
    try:
        fig = px.choropleth(
            df,
            geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations='full_fips',
            color='value',
            color_continuous_scale=color_scale,
            # color_continuous_scale='Viridis',
            range_color=[df['value'].min(), df['value'].max()],
            scope="usa",
            title=f"{metric_key} by County in {state_name}",
            hover_name='name',
            hover_data={'full_fips': False, 'value': ':.2f'},
            labels={'value': metric_key}
        )
        
        # Focus on the selected state
        fig.update_geos(fitbounds="locations", visible=False)

        fig.update_layout(
            title_x=0.5,
            height=600
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Could not create county choropleth map: {e}")
        
        # Fallback to bar chart if choropleth fails
        df_sorted = df.sort_values('value', ascending=False)
        bar_color = '#2E8B57' if is_positive else '#DC143C'
        
        fig = go.Figure(data=go.Bar(
            x=df_sorted['value'],
            y=df_sorted['name'],
            orientation='h',
            marker_color=bar_color,
            hovertemplate='<b>%{y}</b><br>' + f'{metric_key}: %{{x:,.2f}}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{metric_key} by County in {state_name}",
            title_x=0.5,
            xaxis_title=metric_key,
            yaxis_title="Counties",
            height=max(400, len(df) * 25),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig

def export_data_to_csv(data, filename=None):
    """Export data to CSV format"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return csv_buffer.getvalue()

def export_data_to_pdf(data, metric_key, title):
    """Export data to PDF format"""
    if not data:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_para = Paragraph(f"<b>{title}</b>", styles['Title'])
    story.append(title_para)
    story.append(Spacer(1, 12))
    
    # Metric description
    metric_desc = SDOH_METRICS[metric_key]['description']
    desc_para = Paragraph(f"<b>Metric:</b> {metric_desc}", styles['Normal'])
    story.append(desc_para)
    story.append(Spacer(1, 12))
    
    # Data timestamp
    timestamp_para = Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    story.append(timestamp_para)
    story.append(Spacer(1, 12))
    
    # Data summary
    df = pd.DataFrame(data)
    if not df.empty and 'value' in df.columns:
        clean_df = df.dropna(subset=['value'])
        if not clean_df.empty:
            stats_para = Paragraph(
                f"<b>Data Summary:</b><br/>"
                f"Total locations: {len(clean_df)}<br/>"
                f"Average: {clean_df['value'].mean():.2f}<br/>"
                f"Minimum: {clean_df['value'].min():.2f}<br/>"
                f"Maximum: {clean_df['value'].max():.2f}",
                styles['Normal']
            )
            story.append(stats_para)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.title("🏥 Social Determinants of Health (SDOH) Dashboard")
    st.markdown("### Exploring Health Equity Across the United States")
    
    # Initialize data manager
    data_manager = CensusDataManager()
    
    # Sidebar for controls
    st.sidebar.header("📊 Dashboard Controls")
    
    # Metric selection
    selected_metric = st.sidebar.selectbox(
        "Select SDOH Metric:",
        list(SDOH_METRICS.keys()),
        help="Choose a Social Determinant of Health metric to visualize"
    )
    
    # Display metric description
    metric_info = SDOH_METRICS[selected_metric]
    st.sidebar.info(f"**Description:** {metric_info['description']}")
    
    # Data source information
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📋 Data Source Information**")
    st.sidebar.markdown("""
    - **Source:** U.S. Census Bureau American Community Survey (ACS)
    - **Year:** 2022
    - **Coverage:** All 50 states + DC
    - **Update Frequency:** Annual
    """)
    
    with st.sidebar:
        st.markdown('---')
        st.markdown("### 🎯 Key Features")
        st.markdown("""
        - **Real-time Data:** Live Census API integration
        - **Interactive Maps:** Click states for county details
        - **Smart Caching:** Reduced API calls
        - **Data Export:** CSV and PDF formats
        - **Color Coding:** Green (positive) / Red (negative)
        """)
    
    # Main content area
    col1, col2 = st.columns([10, 1])
    
    with col1:
        # Load and display national map
        with st.spinner(f"Loading {selected_metric} data..."):
            state_data = data_manager.fetch_census_data(selected_metric, "state")
        
        if state_data:
            # st.write(pd.DataFrame(state_data).head())
            # st.write(state_data)

            fig = create_choropleth_map(state_data, selected_metric)
            if fig:
                # Display the national map with click detection
                clicked_data = st.plotly_chart(
                    fig, 
                    use_container_width=True, 
                    key="national_map",
                    on_select="rerun"
                )
                
                # Handle state selection
                st.markdown("### 🔍 State Drill-Down")
                
                # Initialize session state for selected state
                if "selected_state_name" not in st.session_state:
                    st.session_state.selected_state_name = ""
                
                # Check for map clicks
                selected_state = ""
                if clicked_data and "selection" in clicked_data:
                    points = clicked_data["selection"].get("points", [])
                    if points:
                        # Get the state from the clicked point
                        point = points[0]
                        if "location" in point:
                            # Convert abbreviation back to full name
                            abbrev = point["location"]
                            for item in state_data:
                                if item['fips'] in FIPS_TO_ABBREV and FIPS_TO_ABBREV[item['fips']] == abbrev:
                                    selected_state = item['name']
                                    st.session_state.selected_state_name = selected_state
                                    break
                
                # Create selectbox with current selection
                state_names = sorted([item['name'] for item in state_data if item['value'] is not None])
                selected_state = st.selectbox(
                    "Select a state to view county-level data (or click on the map above):",
                    [""] + state_names,
                    index=state_names.index(st.session_state.selected_state_name) + 1 if st.session_state.selected_state_name in state_names else 0,
                    key="state_dropdown"
                )
                
                # Update session state if dropdown changed
                if selected_state != st.session_state.selected_state_name:
                    st.session_state.selected_state_name = selected_state
                
                # Show county data if a state is selected
                if st.session_state.selected_state_name:
                    # Find state FIPS code
                    state_fips = None
                    for item in state_data:
                        if item['name'] == st.session_state.selected_state_name:
                            state_fips = item['fips']
                            break
                    
                    if state_fips:
                        st.markdown(f"#### 📍 {st.session_state.selected_state_name} Counties")
                        
                        with st.spinner(f"Loading county data for {st.session_state.selected_state_name}..."):
                            county_data = data_manager.fetch_census_data(selected_metric, state_fips)
                        
                        if county_data:
                            county_fig = create_county_map(county_data, selected_metric, st.session_state.selected_state_name)
                            if county_fig:
                                st.plotly_chart(county_fig, use_container_width=True)
                                
                                # County data summary
                                df = pd.DataFrame(county_data)
                                clean_df = df.dropna(subset=['value'])
                                if not clean_df.empty:
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Counties", len(clean_df))
                                    with col2:
                                        st.metric("Average", f"{clean_df['value'].mean():.2f}")
                                    with col3:
                                        st.metric("Minimum", f"{clean_df['value'].min():.2f}")
                                    with col4:
                                        st.metric("Maximum", f"{clean_df['value'].max():.2f}")
                        else:
                            st.warning(f"No county data available for {st.session_state.selected_state_name}")
                else:
                    st.info("💡 Click on a state in the map above or select from the dropdown to view county-level data.")
            else:
                st.error("Unable to create map visualization")
        else:
            st.error("Unable to load state data. Please check your internet connection and try again.")
    
    # Export functionality
    st.markdown("---")
    st.markdown("### 📥 Data Export")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📊 Export State Data (CSV)"):
            if state_data:
                csv_data = export_data_to_csv(state_data, f"sdoh_{selected_metric}_states.csv")
                if csv_data:
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"sdoh_{selected_metric.lower().replace(' ', '_')}_states.csv",
                        mime="text/csv"
                    )
    
    with export_col2:
        if st.button("📄 Export State Data (PDF)"):
            if state_data:
                pdf_data = export_data_to_pdf(
                    state_data, 
                    selected_metric, 
                    f"SDOH Report: {selected_metric} by State"
                )
                if pdf_data:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name=f"sdoh_{selected_metric.lower().replace(' ', '_')}_report.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()