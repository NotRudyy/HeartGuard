"""Rule-based heart attack risk scoring for HeartGuard (educational, not a diagnosis)."""

RANGES = {"age": (18, 100), "sys": (70, 260), "dia": (40, 160), "chol": (80, 500), "hr": (30, 220)}


def assess(d):
    v = {}
    for k, (lo, hi) in RANGES.items():
        try:
            v[k] = float(d.get(k))
        except (TypeError, ValueError):
            raise ValueError(f"Enter a valid number for {k}.")
        if not lo <= v[k] <= hi:
            raise ValueError(f"{k} must be between {lo} and {hi}.")
    if v["dia"] >= v["sys"]:
        raise ValueError("Diastolic BP must be lower than systolic BP.")
    male = d.get("gender") == "M"
    f = []  # (label, points)

    if v["age"] >= 65: f.append(("Age 65 or above", 3))
    elif v["age"] >= 55: f.append(("Age 55-64", 2))
    elif v["age"] >= 45: f.append(("Age 45-54", 1))
    if male and v["age"] >= 45: f.append(("Male aged 45+", 1))
    if v["sys"] >= 180 or v["dia"] >= 120: f.append(("Blood pressure in crisis range", 4))
    elif v["sys"] >= 140 or v["dia"] >= 90: f.append(("High blood pressure", 3))
    elif v["sys"] >= 130 or v["dia"] >= 80: f.append(("Blood pressure above ideal", 1))
    if v["chol"] >= 240: f.append(("High cholesterol", 3))
    elif v["chol"] >= 200: f.append(("Borderline cholesterol", 1))
    if v["hr"] >= 100: f.append(("High resting heart rate", 2))
    elif v["hr"] < 50: f.append(("Unusually low heart rate", 1))
    if d.get("smoking"): f.append(("Smoking / tobacco", 3))
    if d.get("diabetes"): f.append(("Diabetes", 3))
    if d.get("family"): f.append(("Family history of heart disease", 2))
    if d.get("chest"): f.append(("Chest pain or breathlessness", 4))

    pts = sum(p for _, p in f)
    level = "High" if pts >= 9 or (d.get("chest") and pts >= 6) else "Moderate" if pts >= 4 else "Low"
    return {"score": min(10, round(pts / 1.6)), "level": level, "factors": [l for l, _ in f]}


TIPS = {
    "precautions": [
        ["Monitor your blood pressure regularly", "Keep it below 120/80 mmHg if possible."],
        ["Manage cholesterol levels", "Follow a heart-healthy diet and take medicines if prescribed."],
        ["Quit smoking and tobacco", "Tobacco significantly increases heart attack risk."],
        ["Manage diabetes", "Keep your blood sugar under control with regular tests."],
        ["Maintain a healthy weight", "Focus on balanced diet and regular activity."],
        ["Know the warning signs", "Chest pressure, pain in arm or jaw, cold sweat, sudden breathlessness."],
    ],
    "exercise": [
        ["Walking", "30-45 min", "5 days/week", "\U0001F6B6"],
        ["Cycling", "20-30 min", "3-5 days/week", "\U0001F6B4"],
        ["Yoga", "20-30 min", "daily", "\U0001F9D8"],
        ["Light strength training", "20 min", "2-3 days/week", "\U0001F3CB"],
    ],
    "exercise_rules": [
        "Start slowly and increase intensity gradually.",
        "Stay hydrated and avoid extreme weather.",
        "If you feel chest pain, breathlessness or excessive fatigue, stop and rest.",
        "Always consult your doctor before starting a new exercise program.",
    ],
    "diet": [
        ["Cut salt", "Limit pickles, papad, chips and packaged snacks."],
        ["Use less ghee and oil", "Avoid frequent deep-fried and street food."],
        ["Eat more fibre", "Vegetables, fruit, dal, oats, nuts and fish."],
        ["Limit alcohol, sleep well", "Aim for 7-8 hours of sleep and manage stress."],
    ],
}
