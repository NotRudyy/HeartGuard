# HeartGuard – Heart Attack Risk Checker & Health Assistant ❤️

A web application designed to estimate heart attack risk based on physiological indicators (age, blood pressure, cholesterol, heart rate, and more), offering personalized precautions, emergency contacts, daily health check-in tracking, and a directory of cardiac hospitals across Indian states and cities.

> **Medical Disclaimer:** HeartGuard is created for educational and informational purposes only. It does not replace professional clinical diagnosis, consultation, or medical advice.

---

## 🌟 Key Features

- **Heart Attack Risk Assessment:**
  - Evaluates cardiovascular indicators including Age, Resting Blood Pressure, Cholesterol, Maximum Heart Rate, Exercise-Induced Angina, and ST Slope.
  - Classifies risk into **Low**, **Moderate**, or **High** with score breakdowns and personalized health recommendations.
- **State & City Hospital Directory:**
  - Browse verified cardiac hospitals across multiple Indian states and cities.
- **Emergency Assistance:**
  - One-click emergency contact guides (112, 102, 108) and essential first-aid steps during a suspected cardiac event.
- **Daily Health Tracker / Dashboard:**
  - Log daily vitals including Blood Pressure, Resting Heart Rate, Daily Steps, and Mood.
- **Clean Architecture & Fast Performance:**
  - Lightweight Python (Flask) backend with responsive, dependency-free HTML5/CSS3/Vanilla JS frontend.

---

## 📁 Project Structure

```text
heartguard/
├── backend/
│   ├── app.py              # Flask server and REST API endpoints
│   ├── hospitals.py        # Indian states and cities hospital registry
│   ├── risk_model.py       # Risk scoring algorithm & lifestyle tips
│   ├── requirements.txt    # Python dependencies
│   └── data/               # Local database storage (.gitkeep)
├── frontend/
│   ├── index.html          # Main application page
│   ├── style.css           # Styling and responsive layout
│   └── script.js           # Client-side interactions & API calls
├── .gitignore              # Files and folders excluded from Git tracking
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system.
- Optional: Git (for version control and pushing to GitHub).

---

### Installation & Setup

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/<your-username>/heartguard.git
   cd heartguard
   ```

2. **Create and Activate a Virtual Environment:**
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

---

## ▶️ Running the Application

1. Make sure your virtual environment is active.
2. Run the Flask backend:
   ```bash
   python backend/app.py
   ```
3. Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the frontend web app |
| `GET` | `/api/locations` | Returns list of available states and cities |
| `GET` | `/api/hospitals?state=<state>&city=<city>` | Returns cardiac hospitals for a specific city |
| `POST` | `/api/assess` | Calculates heart attack risk score and returns advice |
| `POST` | `/api/login` | Simple user authentication/profile initialization |
| `POST` | `/api/checkin` | Saves a daily vitals log |
| `GET` | `/api/checkins?user_id=<user_id>` | Retrieves user's check-in history |

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE) (or choose an open source license of your choice).
