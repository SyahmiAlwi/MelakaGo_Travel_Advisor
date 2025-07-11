# ==============================================================================
# app.py - MelakaGo: Modern Streamlit Dashboard with Fixed Light Mode & Clock
# ==============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime, date
import time
from streamlit_geolocation import streamlit_geolocation  # <-- New Import

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MelakaGo - Smart Travel Advisory",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- DYNAMIC CSS BASED ON THEME ---
def get_theme_css(dark_mode=False):
    if dark_mode:
        bg_primary = "#181c20"
        bg_secondary = "#23272f"
        text_primary = "#f3f4f6"
        text_secondary = "#b0b3b8"
        card_bg = "#23272f"
        border_color = "#23272f"
        sidebar_bg = "#181c20"
        sidebar_text = "#f3f4f6"
        input_bg = "#23272f"
        input_text = "#f3f4f6"
        button_bg = "#23272f"
        button_text = "#f3f4f6"
    else:
        bg_primary = "#f8fafc"
        bg_secondary = "#ffffff"
        text_primary = "#1a202c"
        text_secondary = "#4a5568"
        card_bg = "#ffffff"
        border_color = "#e2e8f0"
        sidebar_bg = "#f8fafc"
        sidebar_text = "#1a202c"
        input_bg = "#ffffff"
        input_text = "#1a202c"
        button_bg = "#f1f5f9"
        button_text = "#1a202c"
    return f"""
<style>
    :root {{
        --malacca-blue: #1e40af;
        --malacca-red: #dc2626;
        --malacca-yellow: #fbbf24;
        --malacca-white: #ffffff;
        --malacca-light-blue: #dbeafe;
        --malacca-light-red: #fee2e2;
        --malacca-light-yellow: #fef3c7;
        --bg-primary: {bg_primary};
        --bg-secondary: {bg_secondary};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --card-bg: {card_bg};
        --border-color: {border_color};
        --sidebar-bg: {sidebar_bg};
        --sidebar-text: {sidebar_text};
        --input-bg: {input_bg};
        --input-text: {input_text};
        --button-bg: {button_bg};
        --button-text: {button_text};
    }}
    body, .stApp {{
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif;
    }}
    .stSidebar, .css-1d391kg, .css-1cypcdb, .css-17eq0hr, .css-1lcbmhc, .css-1wivap2 {{
        background: var(--sidebar-bg) !important;
        color: var(--sidebar-text) !important;
    }}
    .main-header {{
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(90deg, var(--malacca-blue) 0%, var(--malacca-red) 100%);
        border-radius: 18px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.10);
        border: none;
    }}
    .main-title {{
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.10);
        color: var(--malacca-white);
    }}
    .main-subtitle {{
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.95;
        color: var(--malacca-light-yellow);
    }}
    .digital-clock {{
        background: linear-gradient(135deg, var(--malacca-blue), var(--malacca-red));
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(30, 64, 175, 0.10);
        border: 3px solid var(--malacca-yellow);
    }}
    .clock-time {{
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        margin-bottom: 0.3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.10);
    }}
    .clock-date {{
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.08);
    }}
    .metric-card {
        background: var(--card-bg);
        padding: 2rem 1.5rem;
        border-radius: 18px;
        box-shadow: 0 2px 16px rgba(30, 64, 175, 0.08);
        border: none;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
        width: 100%;
        min-width: 250px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }
    .metric-card:hover {{
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.12);
        transform: translateY(-2px);
    }}
    .advisory-header {{
        background: linear-gradient(90deg, var(--malacca-blue) 0%, var(--malacca-red) 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 18px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 24px rgba(30, 64, 175, 0.10);
        border: none;
    }}
    .recommendation-card, .data-source, .selected-time, .footer, .metric-container {{
        background: var(--card-bg);
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(30, 64, 175, 0.06);
        border: none;
        color: var(--text-primary);
        margin: 1rem 0;
    }}
    .footer {{
        margin-top: 2rem;
        text-align: center;
    }}
    .stButton > button {{
        background-color: var(--button-bg) !important;
        color: var(--button-text) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0 2px 8px rgba(30, 64, 175, 0.08) !important;
        border: none !important;
    }}
    .stButton > button:hover {{
        background-color: var(--malacca-blue) !important;
        color: #fff !important;
    }}
    .stSlider > div > div > div > div {{
        background-color: var(--malacca-blue) !important;
    }}
    .stDateInput > div > div > input {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
    }}
</style>
"""

# --- LOAD MODELS AND DATA ---
@st.cache_resource
def load_models_and_data():
    try:
        model_jam = joblib.load('model_jam_classifier.joblib')
        model_peak = joblib.load('model_peak_classifier.joblib')
        preprocessor = joblib.load('preprocessor.joblib')
        df_historical = pd.read_csv('dashboard_data.csv')
        df_historical['datetime'] = pd.to_datetime(df_historical['datetime'])
        return model_jam, model_peak, preprocessor, df_historical
    except FileNotFoundError:
        st.error("❌ Error: Model or data files not found. Please check your file paths.")
        st.stop()

model_jam, model_peak, preprocessor, df_historical = load_models_and_data()

# --- WEATHER API FUNCTION ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_weather_forecast(lat, lon, target_date):
    """Fetches hourly weather forecast for a specific date from the Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "start_date": target_date,
        "end_date": target_date,
        "timezone": "Asia/Singapore"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast_df = pd.DataFrame(data['hourly'])
        forecast_df['datetime'] = pd.to_datetime(forecast_df['time'])
        forecast_df = forecast_df.rename(columns={
            'weather_code': 'weathercode',
            'wind_speed_10m': 'windspeed_10m'
        })
        return forecast_df
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch weather data: {e}")
        return None

# --- HELPER FUNCTIONS ---
def get_weather_icon_and_desc(weather_code):
    """Return weather icon and description based on weather code."""
    if weather_code >= 61:
        return "🌧️", "Rainy", "#dc2626"
    elif weather_code >= 51:
        return "🌦️", "Drizzle", "#6b7280"
    elif weather_code >= 3:
        return "☁️", "Cloudy", "#9ca3af"
    else:
        return "☀️", "Clear", "#fbbf24"

def get_traffic_status_style(traffic_level):
    """Return CSS class for traffic level."""
    if traffic_level == "Peak":
        return "status-danger"
    elif traffic_level == "Shoulder":
        return "status-warning"
    else:
        return "status-good"

def get_jam_status_style(is_jam):
    """Return CSS class for jam status."""
    return "status-danger" if is_jam else "status-good"

# --- REAL-TIME CLOCK FUNCTION ---
def display_digital_clock():
    """Display a real-time digital clock using Streamlit's st.empty() for live updates."""
    import time as _time
    clock_placeholder = st.empty()
    for _ in range(1):  # Only run once per rerun, but user can call this in a loop if needed
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %d-%m-%Y")
        clock_placeholder.markdown(f"""
        <div class="digital-clock">
            <div class="clock-time">🕐 {current_time}</div>
            <div class="clock-date">{current_date}</div>
        </div>
        """, unsafe_allow_html=True)
        _time.sleep(1)

# --- MAIN APP ---
def main():
    # Apply theme CSS
    st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Theme Toggle Button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        theme_text = "Dark" if not st.session_state.dark_mode else "Light"
        if st.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    # Header with Malacca Flag Colors
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🏛️ MelakaGo</div>
        <div class="main-subtitle">Smart Travel Advisory for Historic Malacca</div>
    </div>
    """, unsafe_allow_html=True)

    # Get current hour for default value
    current_hour = datetime.now().hour

    # Sidebar for inputs
    with st.sidebar:
        # Real-time Digital Clock
        display_digital_clock()
        
        st.markdown("### 🕐 Select Your Travel Time")
        st.markdown("*Plan your journey through historic Malacca*")
        
        # --- NEW: GEOLOCATION COMPONENT ---
        st.header("Get Your Location")
        location = streamlit_geolocation()
        lat = location.get('latitude', 2.19)
        lon = location.get('longitude', 102.24)
        st.write(f"Current Coordinates: {lat:.4f}, {lon:.4f}")
        if 'latitude' not in location:
            st.caption("Showing data for central Malacca. Click the map icon above to use your current location.")
        
        # Date and time selection
        selected_date = st.date_input("📅 Date", date.today())
        selected_hour = st.slider("⏰ Hour (24-hour format)", 0, 23, current_hour)  # Default to current hour
        
        # Show selected time with Malacca colors
        st.markdown(f"""
        <div class="selected-time">
            <strong>🎯 Selected Journey Time</strong><br>
            <div style="font-size: 1.1rem; margin-top: 0.5rem;">
                {selected_date.strftime('%A, %d-%m-%Y')}<br>
                {selected_hour:02d}:00
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Process input and get data
    user_selected_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour)
    input_data_row = None
    data_source_info = ""

    # --- Use dynamic coordinates for weather forecast ---
    if selected_date >= date.today():
        data_source_info = f"Fetching live forecast for your location..."
        forecast_df = get_weather_forecast(lat, lon, selected_date.strftime('%Y-%m-%d'))
        if forecast_df is not None:
            input_data_row = forecast_df[forecast_df['datetime'].dt.hour == selected_hour].iloc[0:1]
    else:
        data_source_info = f"📊 Historical weather data from {selected_date.strftime('%d-%m-%Y')}"
        input_data_row = df_historical[
            (df_historical['datetime'].dt.date == selected_date) & 
            (df_historical['datetime'].dt.hour == selected_hour)
        ].iloc[0:1]

    # Display data source
    st.markdown(f'<div class="data-source">📡 Data Source: {data_source_info}</div>', unsafe_allow_html=True)

    if input_data_row is None or input_data_row.empty:
        st.warning("⚠️ No weather data could be found for the selected date and hour. Please try another time.")
        return

    # Prepare input data for prediction
    X_live = pd.DataFrame(index=pd.RangeIndex(1))
    X_live['hour'] = selected_hour
    X_live['day_of_week'] = user_selected_dt.strftime('%A')
    X_live['month'] = user_selected_dt.strftime('%B')
    X_live['is_weekend'] = (user_selected_dt.weekday() >= 5)
    
    # Holiday data
    is_holiday = df_historical[df_historical['datetime'].dt.date == selected_date]
    X_live['is_holiday_mlk'] = False if is_holiday.empty else is_holiday['is_holiday_mlk'].iloc[0]
    
    # Weather data
    X_live['temperature_2m'] = input_data_row['temperature_2m'].values[0]
    X_live['relative_humidity_2m'] = input_data_row['relative_humidity_2m'].values[0]
    X_live['weathercode'] = input_data_row['weathercode'].values[0]
    X_live['windspeed_10m'] = input_data_row['windspeed_10m'].values[0]
    
    # Create cyclical features
    X_live['hour_sin'] = np.sin(2 * np.pi * X_live['hour'] / 24)
    X_live['hour_cos'] = np.cos(2 * np.pi * X_live['hour'] / 24)
    month_map = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 
                 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    X_live['month_num'] = X_live['month'].map(month_map)
    X_live['month_sin'] = np.sin(2 * np.pi * X_live['month_num'] / 12)
    X_live['month_cos'] = np.cos(2 * np.pi * X_live['month_num'] / 12)
    X_live = X_live.drop(['hour', 'month', 'month_num'], axis=1)

    # Make predictions
    X_live_processed = preprocessor.transform(X_live)
    prediction_jam = model_jam.predict(X_live_processed)[0]
    prediction_peak = model_peak.predict(X_live_processed)[0]
    jam_label = 'Jam Likely' if prediction_jam else 'No Jam'

    # Advisory Header with Malacca Flag Design
    st.markdown(f"""
    <div class="advisory-header">
        <h2>🎯 Travel Advisory for Historic Malacca</h2>
        <h3>{selected_date.strftime('%A, %d-%m-%Y')} at {selected_hour:02d}:00</h3>
    </div>
    """, unsafe_allow_html=True)

    # Main prediction cards
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚦 Congestion Risk")
        jam_class = get_jam_status_style(prediction_jam)
        st.markdown(f'<div class="{jam_class}">{jam_label}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Traffic Level")
        traffic_class = get_traffic_status_style(prediction_peak)
        st.markdown(f'<div class="{traffic_class}">{prediction_peak} Hour</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🌤️ Weather Forecast")
        weather_code_val = input_data_row['weathercode'].values[0]
        weather_icon, weather_desc, weather_color = get_weather_icon_and_desc(weather_code_val)
        temp = input_data_row['temperature_2m'].values[0]
        
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <span class="weather-icon">{weather_icon}</span>
            <div>
                <div style="font-weight: 600; color: {weather_color};">{weather_desc}</div>
                <div style="color: #1e40af;">{temp:.1f}°C</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Travel Recommendations
    st.markdown("## 🎯 Travel Recommendations for Malacca")

    # Determine recommendations
    if input_data_row['weathercode'].values[0] >= 61:
        vehicle_rec = "🚗 A car is recommended for safety due to rain in Malacca's narrow streets."
        vehicle_icon = "🚗"
        consequence_text = "⚠️ **Risk Warning:** Motorcycle travel during rain can be dangerous on Malacca's historic cobblestone areas."
        risk_class = "risk-warning"
    elif jam_label == "Jam Likely" or prediction_peak == "Peak":
        vehicle_rec = "🏍️ A motorcycle is recommended to navigate through Malacca's busy heritage areas."
        vehicle_icon = "🏍️"
        consequence_text = "⚠️ **Risk Warning:** Cars may face significant delays in Malacca's narrow heritage streets during peak hours."
        risk_class = "risk-warning"
    elif prediction_peak == "Shoulder":
        vehicle_rec = "🚗🏍️ Both vehicles are suitable for exploring Malacca comfortably."
        vehicle_icon = "🚗🏍️"
        consequence_text = "✅ **Outlook:** Good time to visit Malacca's attractions with moderate traffic."
        risk_class = "risk-good"
    else:
        vehicle_rec = "🚗 Perfect time for a comfortable car journey through historic Malacca."
        vehicle_icon = "🚗"
        consequence_text = "✅ **Outlook:** Excellent conditions for sightseeing in Malacca's heritage sites."
        risk_class = "risk-good"

    # Display recommendations
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="recommendation-card">
            <h4>🚙 Recommended Vehicle for Malacca</h4>
            <div style="display: flex; align-items: center; margin-top: 1rem;">
                <span class="vehicle-icon">{vehicle_icon}</span>
                <div style="font-size: 1.1rem; font-weight: 500;">{vehicle_rec}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="{risk_class}">
            <h4>📋 Travel Outlook & Consequences</h4>
            <div style="margin-top: 1rem; font-size: 1.1rem;">{consequence_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Additional insights
    st.markdown("---")
    st.markdown("## 📈 Weather & Travel Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("🌡️ Temperature", f"{temp:.1f}°C")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        humidity = input_data_row['relative_humidity_2m'].values[0]
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("💧 Humidity", f"{humidity:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        windspeed = input_data_row['windspeed_10m'].values[0]
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("💨 Wind Speed", f"{windspeed:.1f} km/h")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        is_weekend_text = "Yes" if X_live['is_weekend'].values[0] else "No"
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("📅 Weekend", is_weekend_text)
        st.markdown('</div>', unsafe_allow_html=True)

    # Refresh button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Malacca Forecast", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Footer with Malacca theme
    st.markdown("""
    <div class="footer">
        <h4 style="color: #1e40af; margin-bottom: 1rem;">🏛️ MelakaGo - Smart Travel Advisory</h4>
        <p style="color: #dc2626; font-weight: 500;">Navigating Historic Malacca with Intelligence 🚗🏍️</p>
        <p style="color: #1e40af; font-size: 0.9rem;">Powered by AI • Inspired by Malacca's Heritage</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()