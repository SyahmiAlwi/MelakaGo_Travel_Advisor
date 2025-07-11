# Fix 1: Make the clock tick continuously using `st_autorefresh`
# Fix 2: Improve theme switching to apply consistent styles

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime, date
from streamlit_autorefresh import st_autorefresh

# PAGE CONFIG
st.set_page_config(
    page_title="MelakaGo - Smart Travel Advisory",
    page_icon="\ud83d\ude97",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEME TOGGLE INITIALIZATION
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- FIX 1: Auto-refresh for live clock ---
# Refresh every 1000ms (1 second) for live clock updates
st_autorefresh(interval=1000, key="clock_refresh")

# --- FIX 2: Consistent Theme CSS ---
def apply_theme():
    mode = "dark" if st.session_state.dark_mode else "light"
    st.markdown(f"""
        <style>
        html, body, .stApp {{
            background-color: {'#1a1a1a' if mode == 'dark' else '#ffffff'} !important;
            color: {'#ffffff' if mode == 'dark' else '#1a1a1a'} !important;
        }}
        
        .css-1d391kg, .css-1cypcdb, .css-17eq0hr, .stSidebar {{
            background-color: {'#2d2d2d' if mode == 'dark' else '#f8fafc'} !important;
            color: {'#ffffff' if mode == 'dark' else '#1a1a1a'} !important;
        }}
        
        .stButton > button {{
            background-color: {'#1e40af' if mode == 'light' else '#fbbf24'};
            color: white;
        }}
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p {{
            color: {'#ffffff' if mode == 'dark' else '#1a1a1a'} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# Theme Toggle
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    theme_icon = "\ud83c\udf19" if not st.session_state.dark_mode else "\u2600\ufe0f"
    theme_text = "Dark" if not st.session_state.dark_mode else "Light"
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# --- CLOCK DISPLAY ---
def display_live_clock():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%A, %B %d")
    st.markdown(f"""
    <div style='padding:1rem; background-color:#1e40af; color:white; border-radius:10px; text-align:center;'>
        <div style='font-size:1.5rem;'>{current_time}</div>
        <div style='font-size:0.9rem;'>{current_date}</div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    display_live_clock()

# Continue with app logic below...
# This is just the theme and clock fix implementation
# Your original `load_models_and_data()` and `main()` logic goes here
