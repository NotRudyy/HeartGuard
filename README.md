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
  - Optional, consent-based SMS updates after each assessment: high/moderate estimates send an alert and low estimates send a normal update when Twilio is configured.
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
├── index.py                # Vercel Flask function entry point
├── requirements.txt        # Root dependency entry for Vercel
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

### Optional automatic SMS setup

Demo mode is on by default. It stores a preview contact in the browser and displays the normal-message or risk-alert text after an assessment; it does not call the SMS endpoints or send any message. To use real SMS, explicitly turn demo mode off, verify the phone number, and confirm the recipient's consent. Real sending remains unavailable until the server has Twilio credentials. Keep these values in your local environment or the hosting provider's server-side environment settings; never add credentials to frontend code or commit them to Git.

Set these environment variables on the server:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER` (your SMS-enabled Twilio number)
- `TWILIO_VERIFY_SERVICE_SID` (a Twilio Verify service)
- `TWILIO_VERIFY_PHONE_RATE_LIMIT` (the Verify rate limit's unique name)
- `CONTACT_TOKEN_SECRET` (a separate long random secret used to sign verified-contact tokens)

Create a Verify rate limit named `contact_phone` and a bucket such as 3 verification messages per phone number per hour, then set `TWILIO_VERIFY_PHONE_RATE_LIMIT=contact_phone`. Enable Twilio's verification fraud protections and restrict supported destination countries in the Twilio Console. These controls matter because this is a public demo. The recipient must enter the OTP and the site user must confirm they have permission to send assessment updates. Verified numbers can be from any country supported by your Twilio account, in international `+` format; a 10-digit Indian mobile is also accepted and converted to `+91`.

The message includes the estimated risk category; it is an educational estimate, not a diagnosis. Low estimates send a normal update, while moderate and high estimates send an alert. SMS charges and delivery depend on the provider and carrier. A website cannot control the recipient's phone sound settings or override Silent / Do Not Disturb. The SOS call and location steps remain a simulation.

### Vercel deployment notes

The root `index.py` exposes the Flask app to Vercel. User login/check-in data uses a temporary `/tmp` file on Vercel Functions and may be lost when an instance restarts; use a managed database for persistent production data. For the interview demo, keep SMS demo mode enabled. Add Twilio credentials only as Vercel server-side environment variables if real SMS is intentionally configured.

For local PowerShell development, set the variables in the current shell before starting Flask, for example:

```powershell
$env:TWILIO_ACCOUNT_SID = "your-account-sid"
$env:TWILIO_AUTH_TOKEN = "your-auth-token"
$env:TWILIO_FROM_NUMBER = "+1XXXXXXXXXX"
$env:TWILIO_VERIFY_SERVICE_SID = "VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_VERIFY_PHONE_RATE_LIMIT = "contact_phone"
$env:CONTACT_TOKEN_SECRET = "use-a-separate-long-random-secret"
python backend/app.py
```

Do not use real health data or recipient numbers in an interview demo. Use a provider test account and a verified test recipient where available.

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
