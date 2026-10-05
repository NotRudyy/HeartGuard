import base64
import hashlib
import hmac
import json
import os
import re
import tempfile
import time
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, send_from_directory

from hospitals import HOSPITALS
from risk_model import TIPS, assess

BASE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.join(BASE, "..", "frontend")
DATA_DIR = os.path.join(BASE, "data")
if os.environ.get("VERCEL"):
    # Vercel Functions have a read-only deployment bundle; /tmp is writable but ephemeral.
    DATA_DIR = os.path.join(tempfile.gettempdir(), "heartguard")
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


def normalize_phone(raw):
    phone = re.sub(r"[\s()-]", "", str(raw or ""))
    if re.fullmatch(r"[6-9]\d{9}", phone):
        return "+91" + phone
    if re.fullmatch(r"\+91[6-9]\d{9}", phone):
        return phone
    if re.fullmatch(r"\+[1-9]\d{7,14}", phone):
        return phone
    return None


def sms_configuration():
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    sender = os.environ.get("TWILIO_FROM_NUMBER", "").strip()
    signing_secret = os.environ.get("CONTACT_TOKEN_SECRET", "").strip()
    if not all((sid, token, sender, signing_secret)):
        return None
    return sid, token, sender, signing_secret


def verify_configuration():
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    service = os.environ.get("TWILIO_VERIFY_SERVICE_SID", "").strip()
    phone_rate_limit = os.environ.get("TWILIO_VERIFY_PHONE_RATE_LIMIT", "").strip()
    if not all((sid, token, service, phone_rate_limit)):
        return None
    return sid, token, service, phone_rate_limit


def twilio_post(url, sid, token, params):
    credentials = base64.b64encode(f"{sid}:{token}".encode("utf-8")).decode("ascii")
    req = Request(
        url,
        data=urlencode(params).encode("utf-8"),
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode("utf-8")), response.status


def contact_proof(phone, expires_at, secret):
    signature = hmac.new(secret.encode("utf-8"), f"{phone}:{expires_at}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{expires_at}.{signature}"


def valid_contact_proof(phone, proof, secret):
    try:
        expires_text, signature = str(proof or "").split(".", 1)
        expires_at = int(expires_text)
    except (ValueError, TypeError):
        return False
    if expires_at <= int(time.time()) or expires_at > int(time.time()) + 31 * 24 * 60 * 60:
        return False
    expected = contact_proof(phone, expires_at, secret).split(".", 1)[1]
    return hmac.compare_digest(signature, expected)


def send_assessment_sms(phone, level):
    config = sms_configuration()
    if not config:
        return False, "Automatic SMS is not configured yet. Your assessment is still available."
    sid, token, sender, _signing_secret = config

    if level == "Low":
        message = (
            "HeartGuard update: a new assessment estimated low risk. "
            "This educational estimate is not a diagnosis."
        )
    elif level == "Moderate":
        message = (
            "HeartGuard update: a new assessment estimated moderate risk. "
            "Please check in with the person using HeartGuard. This is not a diagnosis."
        )
    else:
        message = (
            "HeartGuard alert: a new assessment estimated high risk. "
            "Please contact the person using HeartGuard. If there are emergency symptoms, call 112. "
            "This is not a diagnosis."
        )

    try:
        _result, status = twilio_post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            sid, token, {"From": sender, "To": phone, "Body": message},
        )
        if status not in (200, 201):
            return False, "The SMS provider did not accept the message."
    except (HTTPError, URLError, TimeoutError, OSError):
        app.logger.exception("SMS provider request failed")
        return False, "The SMS could not be sent. Please check the provider configuration."
    return True, "SMS accepted by the provider. Delivery and alert sound depend on the recipient's carrier and phone settings."


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


@app.post("/api/notify")
def notify():
    d = request.get_json(silent=True) or {}
    if d.get("consent") is not True:
        return bad("Consent is required before sending assessment updates.", 400)
    phone = normalize_phone(d.get("phone"))
    if not phone:
        return bad("Enter a valid mobile number with its country code.", 400)
    config = sms_configuration()
    if not config:
        return jsonify({"sent": False, "message": "Automatic SMS is not configured yet. Your assessment is still available."}), 503
    if not valid_contact_proof(phone, d.get("verification_token"), config[3]):
        return bad("Verify this contact number before sending assessment updates.", 403)
    level = d.get("level")
    if level not in ("Low", "Moderate", "High"):
        return bad("Invalid assessment level.", 400)
    sent, message = send_assessment_sms(phone, level)
    if not sent:
        return jsonify({"sent": False, "message": message}), 503
    return jsonify({"sent": True, "message": message})


@app.post("/api/contact/send-code")
def send_contact_code():
    d = request.get_json(silent=True) or {}
    phone = normalize_phone(d.get("phone"))
    if not phone:
        return bad("Enter a valid mobile number with its country code.", 400)
    config = verify_configuration()
    if not config or not sms_configuration():
        return jsonify({"message": "Phone verification is not configured yet."}), 503
    sid, token, service, phone_rate_limit = config
    try:
        result, _status = twilio_post(
            f"https://verify.twilio.com/v2/Services/{service}/Verifications",
            sid, token, {"To": phone, "Channel": "sms", f"RateLimits[{phone_rate_limit}]": phone},
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        app.logger.exception("Contact verification request failed")
        return jsonify({"message": "Could not send a verification code. Check the provider settings and try again."}), 502
    if result.get("status") not in ("pending", "approved"):
        return jsonify({"message": "The SMS provider did not start phone verification."}), 502
    return jsonify({"sent": True, "phone": phone, "message": "Verification code sent. It expires in 10 minutes."})


@app.post("/api/contact/verify")
def verify_contact():
    d = request.get_json(silent=True) or {}
    phone = normalize_phone(d.get("phone"))
    code = re.sub(r"\s", "", str(d.get("code", "")))
    if not phone or not re.fullmatch(r"\d{4,10}", code):
        return bad("Enter the valid phone number and the code you received.", 400)
    config = verify_configuration()
    sms_config = sms_configuration()
    if not config or not sms_config:
        return jsonify({"message": "Phone verification is not configured yet."}), 503
    sid, token, service, _phone_rate_limit = config
    try:
        result, _status = twilio_post(
            f"https://verify.twilio.com/v2/Services/{service}/VerificationCheck",
            sid, token, {"To": phone, "Code": code},
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        app.logger.exception("Contact verification check failed")
        return jsonify({"message": "The code could not be verified. Request a new code and try again."}), 502
    if result.get("status") != "approved":
        return jsonify({"message": "That code was not accepted. Check it and try again."}), 400
    expires_at = int(time.time()) + 30 * 24 * 60 * 60
    proof = contact_proof(phone, expires_at, sms_config[3])
    return jsonify({"verified": True, "phone": phone, "verification_token": proof, "expires_at": expires_at})


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
