import json
import os
import re
from datetime import date

from flask import Flask, jsonify, request, send_from_directory

from hospitals import HOSPITALS
from risk_model import TIPS, assess

BASE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.join(BASE, "..", "frontend")
DATA_DIR = os.path.join(BASE, "data")
DB_FILE = os.path.join(DATA_DIR, "db.json")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONT, static_url_path="")


def load_db():
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"users": {}, "checkins": {}}


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f)


def clean_id(raw):
    uid = re.sub(r"[^a-z0-9._@-]", "", str(raw or "").strip().lower())
    return uid if 3 <= len(uid) <= 40 else None


def bad(msg, code=400):
    return jsonify({"error": msg}), code


@app.get("/")
def home():
    return send_from_directory(FRONT, "index.html")


@app.get("/api/locations")
def locations():
    return jsonify({s: list(c.keys()) for s, c in HOSPITALS.items()})


@app.get("/api/hospitals")
def hospitals():
    s, c = request.args.get("state"), request.args.get("city")
    return jsonify(HOSPITALS.get(s, {}).get(c, []))


@app.get("/api/tips")
def tips():
    return jsonify(TIPS)


@app.post("/api/risk")
def risk():
    try:
        return jsonify(assess(request.get_json(silent=True) or {}))
    except ValueError as e:
        return bad(str(e))


@app.post("/api/login")
def login():
    """Demo login: a Login ID + name, no password. Not secure authentication."""
    d = request.get_json(silent=True) or {}
    uid, name = clean_id(d.get("id")), str(d.get("name", "")).strip()[:40]
    if not uid or not name:
        return bad("Enter your name and a Login ID (3-40 letters, numbers, . _ @ -).")
    db = load_db()
    db["users"].setdefault(uid, {"name": name})
    save_db(db)
    return jsonify({"id": uid, "name": db["users"][uid]["name"]})


@app.post("/api/checkin")
def checkin():
    d = request.get_json(silent=True) or {}
    uid = clean_id(d.get("id"))
    db = load_db()
    if uid not in db["users"]:
        return bad("Please log in first.", 401)
    try:
        hr, sys_, dia, steps = (int(d[k]) for k in ("hr", "sys", "dia", "steps"))
    except (KeyError, TypeError, ValueError):
        return bad("Fill in heart rate, BP and steps as numbers.")
    if not (30 <= hr <= 220 and 70 <= sys_ <= 260 and 40 <= dia <= 160 and 0 <= steps <= 100000):
        return bad("One of the values is out of range.")
    row = {"date": date.today().isoformat(), "hr": hr, "sys": sys_, "dia": dia,
           "steps": steps, "mood": str(d.get("mood", "Good"))[:12]}
    rows = [r for r in db["checkins"].get(uid, []) if r["date"] != row["date"]] + [row]
    db["checkins"][uid] = rows[-60:]
    save_db(db)
    return jsonify(row)


@app.get("/api/checkins/<uid>")
def checkins(uid):
    return jsonify(load_db()["checkins"].get(clean_id(uid) or "", [])[-7:])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
