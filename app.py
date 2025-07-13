# ==============================================================================
# app.py - MelakaGo: Modern Streamlit Dashboard with Fixed Light Mode & Clock
# ==============================================================================
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime, date, timezone, timedelta
import time
import json
import base64


# --- CONSTANTS ---
DEFAULT_MALACCA_LAT = 2.19
DEFAULT_MALACCA_LON = 102.24
WEATHER_API_TTL = 3600  # 1 hour cache
RADAR_HEIGHT = 450
CHART_HEIGHT = 400

# Function to encode image to base64
@st.cache_data
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Function to get Malaysia time (UTC+8)
def get_malaysia_time():
    """Get current time in Malaysia timezone (UTC+8)"""
    malaysia_tz = timezone(timedelta(hours=8))
    return datetime.now(malaysia_tz)


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MelakaGo",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state - default to dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

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
        background: transparent !important;
        color: var(--sidebar-text) !important;
    }}
    
    /* Make sidebar content container transparent with subtle backdrop */
    .stSidebar > div:first-child {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem;
        padding: 1rem;
    }}
    .main-header {{
        text-align: center;
        padding: 2rem 1.5rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px rgba(30, 64, 175, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .main-header:hover {{
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 60px rgba(30, 64, 175, 0.25);
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 30%, #3b82f6 60%, #60a5fa 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        pointer-events: none;
        transition: all 0.4s ease;
    }}
    .main-header:hover::before {{
        background: linear-gradient(45deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
    }}
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.1;
        transition: all 0.3s ease;
    }}
    .main-header:hover .main-title {{
        transform: scale(1.05);
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: 0px;
    }}
    .main-subtitle {{
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.9;
        color: #e0f2fe;
        margin-top: 0.5rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }}
    .main-header:hover .main-subtitle {{
        opacity: 1;
        transform: translateY(-2px);
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    .analog-clock {{
        background: linear-gradient(135deg, var(--malacca-blue), var(--malacca-red));
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(30, 64, 175, 0.10);
        border: 3px solid var(--malacca-yellow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }}
    .analog-clock:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(30, 64, 175, 0.2);
        background: linear-gradient(135deg, #1e40af, #dc2626);
        border: 3px solid #fbbf24;
    }}
    .clock-container {{
        width: 100px;
        height: 100px;
        border: 3px solid white;
        border-radius: 50%;
        margin: 0 auto 1rem auto;
        position: relative;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .clock-center {{
        width: 8px;
        height: 8px;
        background: #dc2626;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
    }}
    .clock-hand {{
        position: absolute;
        background: #1f2937;
        transform-origin: bottom center;
        border-radius: 1px;
    }}
    .hour-hand {{
        width: 3px;
        height: 25px;
        top: 25px;
        left: 50%;
        margin-left: -1.5px;
        z-index: 2;
    }}
    .minute-hand {{
        width: 2px;
        height: 35px;
        top: 15px;
        left: 50%;
        margin-left: -1px;
        z-index: 3;
    }}
    .clock-time {{
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    .clock-date {{
        color: white;
        font-size: 1rem;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    .metric-card {{
        background: var(--card-bg);
        padding: 2rem 1.5rem;
        border-radius: 18px;
        box-shadow: 0 2px 16px rgba(30, 64, 175, 0.08);
        border: none;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
    }}
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
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }}
    .recommendation-card:hover, .data-source:hover, .selected-time:hover, .metric-container:hover {{
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 25px rgba(30, 64, 175, 0.12);
        border: 1px solid rgba(30, 64, 175, 0.1);
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
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stButton > button:hover {{
        background-color: var(--malacca-blue) !important;
        color: #fff !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.2) !important;
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
@st.cache_data(ttl=WEATHER_API_TTL, show_spinner=False)
def get_weather_forecast(lat: float, lon: float, target_date: str):
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
def safe_get_value(data_row, column, default_value=None):
    """Safely get value from DataFrame with fallback."""
    try:
        if data_row is not None and not data_row.empty and column in data_row.columns:
            values = data_row[column].values
            if len(values) > 0:
                return values[0]
    except (IndexError, KeyError, AttributeError):
        pass
    return default_value

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

# --- ANALOG CLOCK DISPLAY ---

def display_animated_background():
    """Display animated background using CSS animations"""
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        background-attachment: fixed;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(251, 191, 36, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
        animation: backgroundPulse 10s ease-in-out infinite;
    }
    @keyframes backgroundPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_analog_clock():
    """Display analog clock emoji showing current time visually."""
    now = get_malaysia_time()
    current_date = now.strftime("%d %B")
    
    # Create a simple clock emoji representation based on hour
    hour = now.hour % 12
    clock_emojis = {
        0: "🕛", 1: "🕐", 2: "🕑", 3: "🕒", 4: "🕓", 5: "🕔",
        6: "🕕", 7: "🕖", 8: "🕗", 9: "🕘", 10: "🕙", 11: "🕚"
    }
    clock_emoji = clock_emojis.get(hour, "🕐")
    
    # Use simple HTML that Streamlit can handle reliably
    clock_html = f"""
    <div style="
        text-align: center;
        margin-bottom: 2rem;
    ">
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.8rem;
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--text-primary);
        ">
            <span style="font-size: 2rem;">{clock_emoji}</span>
            <span>{current_date}</span>
        </div>
    </div>
    """
    
    st.markdown(clock_html, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # Apply theme CSS
    st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Create beautiful animated CSS background
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        position: relative;
        overflow: hidden;
    }
    
    /* Animated gradient background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -999;
        background: 
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.4) 0%, transparent 60%),
            radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.3) 0%, transparent 60%),
            radial-gradient(circle at 40% 40%, rgba(251, 191, 36, 0.25) 0%, transparent 60%);
        animation: backgroundPulse 1.5s ease-in-out infinite;
    }
    
    /* Moving wave patterns */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 200%;
        z-index: -998;
        background: 
            linear-gradient(45deg, transparent 20%, rgba(59, 130, 246, 0.15) 40%, transparent 60%),
            linear-gradient(-45deg, transparent 20%, rgba(220, 38, 38, 0.12) 40%, transparent 60%),
            linear-gradient(90deg, transparent 30%, rgba(251, 191, 36, 0.1) 50%, transparent 70%);
        animation: backgroundWave 2s linear infinite;
    }
    
    @keyframes backgroundPulse {
        0%, 100% { 
            opacity: 0.6;
            transform: scale(1) rotate(0deg);
        }
        33% { 
            opacity: 0.9;
            transform: scale(1.1) rotate(120deg);
        }
        66% { 
            opacity: 0.7;
            transform: scale(0.95) rotate(240deg);
        }
    }
    
    @keyframes backgroundWave {
        0% { transform: translateX(-50%) translateY(-50%) rotate(0deg); }
        100% { transform: translateX(-50%) translateY(-50%) rotate(360deg); }
    }
    
    /* Floating animated elements */
    .floating-elements {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -997;
        pointer-events: none;
    }
    
    .floating-circle {
        position: absolute;
        border-radius: 50%;
        animation: float 2.5s ease-in-out infinite;
    }
    
    .floating-circle:nth-child(1) {
        width: 120px;
        height: 120px;
        top: 15%;
        left: 10%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 70%, transparent 100%);
        animation-delay: 0s;
    }
    
    .floating-circle:nth-child(2) {
        width: 80px;
        height: 80px;
        top: 60%;
        left: 75%;
        background: radial-gradient(circle, rgba(220, 38, 38, 0.18) 0%, rgba(220, 38, 38, 0.04) 70%, transparent 100%);
        animation-delay: 0.5s;
    }
    
    .floating-circle:nth-child(3) {
        width: 150px;
        height: 150px;
        top: 75%;
        left: 15%;
        background: radial-gradient(circle, rgba(251, 191, 36, 0.15) 0%, rgba(251, 191, 36, 0.03) 70%, transparent 100%);
        animation-delay: 1s;
    }
    
    .floating-circle:nth-child(4) {
        width: 100px;
        height: 100px;
        top: 25%;
        left: 70%;
        background: radial-gradient(circle, rgba(16, 185, 129, 0.16) 0%, rgba(16, 185, 129, 0.04) 70%, transparent 100%);
        animation-delay: 1.5s;
    }
    
    .floating-circle:nth-child(5) {
        width: 60px;
        height: 60px;
        top: 45%;
        left: 35%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.05) 70%, transparent 100%);
        animation-delay: 2s;
    }
    
    @keyframes float {
        0%, 100% { 
            transform: translateY(0px) translateX(0px) rotate(0deg) scale(1);
            opacity: 0.6;
        }
        25% { 
            transform: translateY(-30px) translateX(20px) rotate(90deg) scale(1.1);
            opacity: 0.8;
        }
        50% { 
            transform: translateY(-15px) translateX(-15px) rotate(180deg) scale(0.9);
            opacity: 1;
        }
        75% { 
            transform: translateY(25px) translateX(10px) rotate(270deg) scale(1.05);
            opacity: 0.7;
        }
    }
    
    /* Particle effect */
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(59, 130, 246, 0.6);
        border-radius: 50%;
        animation: particle 4s linear infinite;
    }
    
    .particle:nth-child(6) {
        left: 10%;
        animation-delay: 0s;
        background: rgba(220, 38, 38, 0.5);
    }
    
    .particle:nth-child(7) {
        left: 30%;
        animation-delay: 0.8s;
        background: rgba(251, 191, 36, 0.6);
    }
    
    .particle:nth-child(8) {
        left: 50%;
        animation-delay: 1.6s;
        background: rgba(16, 185, 129, 0.5);
    }
    
    .particle:nth-child(9) {
        left: 70%;
        animation-delay: 2.4s;
        background: rgba(139, 92, 246, 0.6);
    }
    
    .particle:nth-child(10) {
        left: 90%;
        animation-delay: 3.2s;
        background: rgba(59, 130, 246, 0.4);
    }
    
    @keyframes particle {
        0% {
            transform: translateY(100vh) scale(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
            transform: translateY(90vh) scale(1);
        }
        90% {
            opacity: 1;
            transform: translateY(10vh) scale(1);
        }
        100% {
            transform: translateY(0) scale(0);
            opacity: 0;
        }
    }
    
    /* Ensure all Streamlit content is above the background */
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    
    .main-content {
        position: relative;
        z-index: 100;
    }
    </style>
    
    <div class="floating-elements">
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content container
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Initialize session state for info button
    if 'show_info' not in st.session_state:
        st.session_state.show_info = False
    
    # Main header with info button at top right
    col_header, col_info = st.columns([10, 1])
    
    with col_header:
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-start;
            margin-bottom: 1.5rem;
        ">
            <div style="
                background: linear-gradient(90deg, var(--malacca-blue) 0%, var(--malacca-red) 50%, var(--malacca-yellow) 100%);
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                box-shadow: 0 4px 12px rgba(30, 64, 175, 0.1);
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.8rem;
                color: white;
            ">
                <img src="data:image/png;base64,{get_image_base64('Picture4.png') or ''}" style="width: 24px; height: 24px; object-fit: contain;" alt="MelakaGo Logo">
                <div>
                    <span style="font-size: 1.3rem; font-weight: 700; margin-right: 0.4rem;">MelakaGo</span>
                    <span style="font-size: 0.85rem; opacity: 0.9; font-weight: 500;">Smart Travel Advisory</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info:
        st.markdown('<div style="margin-top: 0.5rem;">', unsafe_allow_html=True)
        if st.button("ℹ️", key="info_button", help="Click to see prediction explanations"):
            st.session_state.show_info = not st.session_state.show_info
        st.markdown('</div>', unsafe_allow_html=True)

    # Get current hour for default value
    current_hour = get_malaysia_time().hour

    # Sidebar for inputs
    with st.sidebar:
        # Analog Clock
        display_analog_clock()
        

        
        # --- LOCATION INPUT ---
        melaka_locations = {
            "Ayer Keroh": (2.2760, 102.2921),
            "Bandar Hilir": (2.1935, 102.2496),
            "Bukit Katil": (2.2234, 102.2915),
            "Alor Gajah": (2.3817, 102.2089),
            "Jasin": (2.3084, 102.4381),
            "Melaka Tengah": (2.2008, 102.2487),
        }
        selected_location_name = st.selectbox("📍 Choose your location:", list(melaka_locations.keys()))
        MALACCA_LAT, MALACCA_LON = melaka_locations[selected_location_name]
        
        st.markdown(f"""
        <div style="
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            <span style="font-size: 1.2rem;">📍</span>
            <div>
                <span style="color: #059669; font-weight: 500; font-size: 0.9rem;">You are viewing:</span>
                <div style="color: var(--text-primary); font-weight: 600; font-size: 1rem; margin-top: 0.2rem;">{selected_location_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🕐 Select Your Travel Time")
        
        # Date and time selection
        selected_date = st.date_input("📅 Date", date.today())
        
        # Better time picker with 12-hour format display
        st.markdown("### ⏰ Select Travel Time")
        
        # Create time options with both 12-hour and 24-hour format
        time_options = []
        time_labels = []
        for hour in range(24):
            time_options.append(hour)
            if hour == 0:
                time_labels.append("12:00 AM (00:00)")
            elif hour < 12:
                time_labels.append(f"{hour}:00 AM ({hour:02d}:00)")
            elif hour == 12:
                time_labels.append("12:00 PM (12:00)")
            else:
                time_labels.append(f"{hour-12}:00 PM ({hour:02d}:00)")
        
        # Use selectbox for better time selection
        selected_time_index = st.selectbox(
            "",
            options=range(len(time_options)),
            index=current_hour,
            format_func=lambda x: time_labels[x]
        )
        selected_hour = time_options[selected_time_index]
        
        # Show selected time with Malacca colors and DD/MM/YYYY format
        st.markdown(f"""
        <div class="selected-time">
            <strong>🎯 Selected Journey Time</strong><br>
            <div style="font-size: 1.1rem; margin-top: 0.5rem;">
                {selected_date.strftime('%d/%m/%Y')}<br>
                {time_labels[selected_time_index].split(' (')[0]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        


    # Process input and get data
    user_selected_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour)
    input_data_row = None
    data_source_info = ""

    # Determine data source with failover
    if selected_date >= date.today():
        data_source_info = f"🔴 Live weather forecast for {selected_date.strftime('%d/%m/%Y')}"
        forecast_df = get_weather_forecast(MALACCA_LAT, MALACCA_LON, selected_date.strftime('%Y-%m-%d'))
        
        if forecast_df is not None and not forecast_df.empty:
            hourly_data = forecast_df[forecast_df['datetime'].dt.hour == selected_hour]
            if not hourly_data.empty:
                input_data_row = hourly_data.iloc[0:1]
            else:
                input_data_row = None
        else:
            # Failover: Use historical data pattern
            st.warning("⚠️ Live forecast unavailable. Using historical weather pattern.")
            data_source_info = f"📊 Historical weather pattern (forecast unavailable)"
            input_data_row = df_historical[
                (df_historical['datetime'].dt.hour == selected_hour)
            ].tail(1)  # Get recent similar hour
    else:
        data_source_info = f"📊 Historical weather data from {selected_date.strftime('%d/%m/%Y')}"
        historical_data = df_historical[
            (df_historical['datetime'].dt.date == selected_date) & 
            (df_historical['datetime'].dt.hour == selected_hour)
        ]
        if not historical_data.empty:
            input_data_row = historical_data.iloc[0:1]
        else:
            # Fallback to similar hour pattern
            input_data_row = df_historical[
                df_historical['datetime'].dt.hour == selected_hour
            ].tail(1)



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
    X_live['is_holiday_mlk'] = False
    if not is_holiday.empty and 'is_holiday_mlk' in is_holiday.columns:
        try:
            X_live['is_holiday_mlk'] = bool(is_holiday['is_holiday_mlk'].iloc[0])
        except:
            X_live['is_holiday_mlk'] = False
    
    # Weather data - using safe access methods
    X_live['temperature_2m'] = safe_get_value(input_data_row, 'temperature_2m', 25.0)
    X_live['relative_humidity_2m'] = safe_get_value(input_data_row, 'relative_humidity_2m', 70.0)
    X_live['weathercode'] = safe_get_value(input_data_row, 'weathercode', 0)
    X_live['windspeed_10m'] = safe_get_value(input_data_row, 'windspeed_10m', 5.0)
    
    # Create cyclical features
    X_live['hour_sin'] = np.sin(2 * np.pi * X_live['hour'] / 24)
    X_live['hour_cos'] = np.cos(2 * np.pi * X_live['hour'] / 24)
    month_map = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 
                 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    X_live['month_num'] = X_live['month'].apply(lambda x: month_map.get(x, 1))
    X_live['month_sin'] = np.sin(2 * np.pi * X_live['month_num'] / 12)
    X_live['month_cos'] = np.cos(2 * np.pi * X_live['month_num'] / 12)
    X_live = X_live.drop(['hour', 'month', 'month_num'], axis=1)

    # Make predictions
    X_live_processed = preprocessor.transform(X_live)
    prediction_jam = model_jam.predict(X_live_processed)[0]
    prediction_peak = model_peak.predict(X_live_processed)[0]
    
    # Create labels with emojis
    jam_label = '🚨 Jam Likely' if prediction_jam else '✅ No Jam'
    
    # Add emojis to traffic levels
    if prediction_peak == "Peak":
        traffic_label = "🔴 Peak Hour"
    elif prediction_peak == "Shoulder":
        traffic_label = "🟡 Shoulder Hour"
    else:
        traffic_label = "🟢 Off-Peak Hour"

    # Minimalist Advisory Header
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    ">
        <div style="
            display: flex;
            align-items: center;
        ">
            <div>
                <div style="
                    font-size: 1.1rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 0.2rem;
                ">
                    {selected_location_name} • Historic Malacca
                </div>
                <div style="
                    font-size: 0.85rem;
                    color: var(--text-secondary);
                    opacity: 0.8;
                ">
                    Traffic & Weather Conditions
                </div>
            </div>
        </div>
        <div style="
            text-align: right;
            background: rgba(30, 64, 175, 0.1);
            padding: 0.6rem 1rem;
            border-radius: 8px;
            border: 1px solid rgba(30, 64, 175, 0.2);
        ">
            <div style="
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--malacca-blue);
                margin-bottom: 0.1rem;
            ">
                {selected_date.strftime('%d %b %Y')}
            </div>
            <div style="
                font-size: 1.1rem;
                font-weight: 700;
                color: var(--text-primary);
            ">
                {selected_hour:02d}:00
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main prediction cards with improved layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        jam_status_color = "#dc2626" if prediction_jam else "#22c55e"
        jam_bg_color = "rgba(220, 38, 38, 0.1)" if prediction_jam else "rgba(34, 197, 94, 0.1)"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="display: flex; align-items: center; margin-bottom: 1.5rem; color: var(--text-primary);">
                <span style="font-size: 1.8rem; margin-right: 0.8rem;">🚦</span>
                <span>Congestion Risk</span>
            </h3>
                         <div style="text-align: center; padding: 1.5rem; background: {jam_bg_color}; border-radius: 12px; border: 2px solid {jam_status_color}; min-height: 80px; display: flex; flex-direction: column; justify-content: center;">
                 <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">{"🚨" if prediction_jam else "✅"}</div>
                 <div style="font-size: 1.1rem; font-weight: 700; color: {jam_status_color}; margin-bottom: 0.3rem;">{"Jam Likely" if prediction_jam else "No Jam"}</div>
                 <div style="font-size: 1.2rem; font-weight: 600; color: {jam_status_color};">{"High Risk" if prediction_jam else "Clear Roads"}</div>
             </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if prediction_peak == "Peak":
            traffic_color = "#dc2626"
            traffic_bg = "rgba(220, 38, 38, 0.1)"
        elif prediction_peak == "Shoulder":
            traffic_color = "#f59e0b"
            traffic_bg = "rgba(245, 158, 11, 0.1)"
        else:
            traffic_color = "#22c55e"
            traffic_bg = "rgba(34, 197, 94, 0.1)"
            
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="display: flex; align-items: center; margin-bottom: 1.5rem; color: var(--text-primary);">
                <span style="font-size: 1.8rem; margin-right: 0.8rem;">📊</span>
                <span>Traffic Level</span>
            </h3>
                         <div style="text-align: center; padding: 1.5rem; background: {traffic_bg}; border-radius: 12px; border: 2px solid {traffic_color}; min-height: 80px; display: flex; flex-direction: column; justify-content: center;">
                 <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">{"🔴" if prediction_peak == "Peak" else "🟡" if prediction_peak == "Shoulder" else "🟢"}</div>
                 <div style="font-size: 1.1rem; font-weight: 700; color: {traffic_color}; margin-bottom: 0.3rem;">{prediction_peak} Hour</div>
                 <div style="font-size: 1.2rem; font-weight: 600; color: {traffic_color};">{"Heavy Traffic" if prediction_peak == "Peak" else "Moderate Flow" if prediction_peak == "Shoulder" else "Light Traffic"}</div>
             </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        weather_code_val = safe_get_value(input_data_row, 'weathercode', 0)
        weather_icon, weather_desc, weather_color = get_weather_icon_and_desc(weather_code_val)
        temp = safe_get_value(input_data_row, 'temperature_2m', 25.0)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; color: var(--text-primary);">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.8rem; margin-right: 0.8rem;">🌤️</span>
                    <span>Weather Forecast</span>
                </div>
            </h3>
            <div style="text-align: center; padding: 1.5rem; background: rgba(59, 130, 246, 0.1); border-radius: 12px; border: 2px solid #3b82f6; min-height: 80px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">{weather_icon}</div>
                <div style="font-weight: 700; color: {weather_color}; font-size: 1.1rem; margin-bottom: 0.3rem;">{weather_desc}</div>
                <div style="color: #1e40af; font-size: 1.2rem; font-weight: 600;">{temp:.1f}°C</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Info explanation cards (controlled by top-right button)
    if st.session_state.show_info:
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem;">What do these predictions mean?</h4>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">We analyze traffic patterns and road conditions to give you 6 possible scenarios:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create cards in a grid layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                border-left: 4px solid #ef4444;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #dc2626; margin-bottom: 0.5rem;">
                    🔴 Peak Hour + Jam Likely
                </div>
                <div style="color: #991b1b; font-weight: 600; margin-bottom: 0.3rem;">
                    → Avoid if possible!
                </div>
                <div style="color: #7f1d1d; font-size: 0.9rem;">
                    Heavy traffic with complete standstill<br>
                    Travel time: 2-3x longer than normal
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fef3c7, #fde68a);
                border-left: 4px solid #f59e0b;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #d97706; margin-bottom: 0.5rem;">
                    🟡 Peak Hour + No Jam
                </div>
                <div style="color: #b45309; font-weight: 600; margin-bottom: 0.3rem;">
                    → Plan extra time
                </div>
                <div style="color: #92400e; font-size: 0.9rem;">
                    Heavy but moving traffic<br>
                    Travel time: 1.5-2x longer than normal
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fed7aa, #fdba74);
                border-left: 4px solid #f97316;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #ea580c; margin-bottom: 0.5rem;">
                    🟠 Shoulder Hour + Jam Likely
                </div>
                <div style="color: #c2410c; font-weight: 600; margin-bottom: 0.3rem;">
                    → Check traffic news
                </div>
                <div style="color: #9a3412; font-size: 0.9rem;">
                    Unexpected incident causing delays<br>
                    Travel time: 2x longer than normal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #dcfce7, #bbf7d0);
                border-left: 4px solid #22c55e;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #16a34a; margin-bottom: 0.5rem;">
                    🟢 Shoulder Hour + No Jam
                </div>
                <div style="color: #15803d; font-weight: 600; margin-bottom: 0.3rem;">
                    → Good to go
                </div>
                <div style="color: #166534; font-size: 0.9rem;">
                    Moderate traffic, manageable delays<br>
                    Travel time: Slightly longer than normal
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                border-left: 4px solid #ef4444;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #dc2626; margin-bottom: 0.5rem;">
                    🔴 Off-Peak Hour + Jam Likely
                </div>
                <div style="color: #991b1b; font-weight: 600; margin-bottom: 0.3rem;">
                    → Major incident!
                </div>
                <div style="color: #7f1d1d; font-size: 0.9rem;">
                    Serious emergency or road closure<br>
                    Travel time: Unpredictable, find alternate route
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #d1fae5, #a7f3d0);
                border-left: 4px solid #10b981;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 1.1rem; font-weight: bold; color: #059669; margin-bottom: 0.5rem;">
                    ✅ Off-Peak Hour + No Jam
                </div>
                <div style="color: #047857; font-weight: 600; margin-bottom: 0.3rem;">
                    → Perfect timing!
                </div>
                <div style="color: #065f46; font-size: 0.9rem;">
                    Clear roads, smooth journey<br>
                    Travel time: Normal or faster
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #eff6ff, #dbeafe);
            border: 1px solid #3b82f6;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: center;
        ">
            <div style="color: #1d4ed8; font-weight: 600;">
                💡 <strong>Tip:</strong> Green predictions are your best bet for comfortable travel!
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Travel Recommendations
    st.markdown("## 🎯 Travel Recommendations for Malacca")

    # Determine recommendations
    weather_code_for_rec = safe_get_value(input_data_row, 'weathercode', 0)
    weather_code_for_rec = weather_code_for_rec if weather_code_for_rec is not None else 0
    if weather_code_for_rec >= 61:
        vehicle_rec = "A car is recommended for safety due to rain in Malacca's narrow streets."
        vehicle_icon = "🚗"
        consequence_text = "Risk Warning: Motorcycle travel during rain can be dangerous on Malacca's historic cobblestone areas."
        consequence_icon = "⚠️"
        risk_class = "risk-warning"
    elif jam_label == "Jam Likely" or prediction_peak == "Peak":
        vehicle_rec = "🏍️ A motorcycle is recommended to navigate through Malacca's busy heritage areas."
        vehicle_icon = "🏍️"
        consequence_text = "Risk Warning: Cars may face significant delays in Malacca's narrow heritage streets during peak hours."
        consequence_icon = "⚠️"
        risk_class = "risk-warning"
    elif prediction_peak == "Shoulder":
        vehicle_rec = "🚗🏍️ Both vehicles are suitable for exploring Malacca comfortably."
        vehicle_icon = "🚗🏍️"
        consequence_text = "Outlook: Good time to visit Malacca's attractions with moderate traffic."
        consequence_icon = "✅"
        risk_class = "risk-good"
    else:
        vehicle_rec = "🚗 Perfect time for a comfortable car journey through historic Malacca."
        vehicle_icon = "🚗"
        consequence_text = "Outlook: Excellent conditions for sightseeing in Malacca's heritage sites."
        consequence_icon = "✅"
        risk_class = "risk-good"

    # Display recommendations with improved UI
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="recommendation-card">
            <h4 style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 1.8rem; margin-right: 0.8rem;">🚙</span>
                <span>Recommended Vehicle for Malacca</span>
            </h4>
            <div style="display: flex; align-items: center; padding: 1rem; background: rgba(30, 64, 175, 0.1); border-radius: 12px; border-left: 4px solid var(--malacca-blue);">
                <span style="font-size: 3rem; margin-right: 1.5rem; line-height: 1;">{vehicle_icon}</span>
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); line-height: 1.4;">{vehicle_rec}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="recommendation-card">
            <h4 style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 1.8rem; margin-right: 0.8rem;">📋</span>
                <span>Travel Outlook & Consequences</span>
            </h4>
            <div style="display: flex; align-items: center; padding: 1rem; background: rgba(34, 197, 94, 0.1); border-radius: 12px; border-left: 4px solid #22c55e;">
                <span style="font-size: 3rem; margin-right: 1.5rem; line-height: 1;">{consequence_icon}</span>
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); line-height: 1.4;">{consequence_text}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Additional insights
    st.markdown("---")
    st.markdown("## 📈 Weather & Travel Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">🌡️</span>
                <span style="font-size: 0.9rem; color: var(--text-secondary);">Temperature</span>
            </div>
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary);">{temp:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        humidity = safe_get_value(input_data_row, 'relative_humidity_2m', 70.0)
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">💧</span>
                <span style="font-size: 0.9rem; color: var(--text-secondary);">Humidity</span>
            </div>
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary);">{humidity:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        windspeed = safe_get_value(input_data_row, 'windspeed_10m', 5.0)
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">💨</span>
                <span style="font-size: 0.9rem; color: var(--text-secondary);">Wind Speed</span>
            </div>
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary);">{windspeed:.1f} km/h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        is_weekend_text = "Yes" if bool(X_live['is_weekend'].iloc[0]) else "No"
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">📅</span>
                <span style="font-size: 0.9rem; color: var(--text-secondary);">Weekend</span>
            </div>
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary);">{is_weekend_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- FORECAST GRAPH (if forecast_df exists) ---
    if 'forecast_df' in locals() and forecast_df is not None and not forecast_df.empty:
        st.markdown("---")
        st.markdown("### 🌡️ Temperature Trend Today")
        
        # Convert forecast datetime to hours
        forecast_df['hour'] = forecast_df['datetime'].dt.strftime('%H:%M')
        chart_data = forecast_df[['hour', 'temperature_2m']].set_index('hour')
        
        st.line_chart(chart_data)


    # --- RAIN RADAR EMBED ---
    st.markdown("---")
    st.markdown("### 🌧️ Real-Time Rain Radar (Windy.com)")
    components.iframe(
        src="https://embed.windy.com/embed2.html?lat=2.2&lon=102.3&detailLat=2.2&detailLon=102.3&width=650&height=450&zoom=9&level=surface&overlay=rain&menu=&message=true",
        height=RADAR_HEIGHT,
        scrolling=True
    )

    # Refresh button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Malacca Forecast", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Close main content container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()