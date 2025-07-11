# MelakaGo Travel Advisor

A smart, AI-powered travel advisory dashboard for Malacca, Malaysia. Predicts traffic congestion and provides travel recommendations based on weather, time, and historical data.

## 🚗 Project Overview
MelakaGo is a modern Streamlit dashboard that helps travelers and locals plan their journeys in historic Malacca. It uses machine learning models and live weather data to predict traffic jams, peak hours, and gives personalized travel advice.

## ✨ Features
- Real-time digital clock and modern UI (light/dark mode)
- Predicts traffic congestion and peak hours
- Live weather forecast integration
- Smart vehicle recommendations (car/motorcycle)
- Interactive travel time selection
- Beautiful, responsive dashboard

## 🛠️ Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/SyahmiAlwi/MelakaGo_Travel_Advisor.git
   cd MelakaGo_Travel_Advisor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## 📸 Screenshots
_Add your screenshots here!_

## 📂 Project Structure
- `app.py` — Main Streamlit app
- `dashboard_data.csv` — Historical data
- `model_jam_classifier.joblib`, `model_peak_classifier.joblib`, `preprocessor.joblib` — ML models
- `03_FinalModellingPhase.ipynb`, `exploratory_data_analysis.ipynb` — Notebooks

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first.

## 📄 License
MIT 