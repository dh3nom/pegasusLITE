import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔹 Ambil token & chat ID dari environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔹 Setup Firebase dari environment variables
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
firebase_url = os.getenv("FIREBASE_URL")

if not firebase_credentials or not firebase_url:
    raise ValueError("Firebase credentials atau URL belum dikonfigurasi!")

cred = credentials.Certificate(json.loads(firebase_credentials))
firebase_admin.initialize_app(cred, {"databaseURL": firebase_url})

# 🔹 Fungsi kirim pesan ke Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# 🔹 API menerima data lokasi
@app.route("/track_location", methods=["POST"])
def track_location():
    data = request.json  
    if not data or "latitude" not in data or "longitude" not in data or "device_id" not in data:
        return {"status": "error", "message": "Invalid data"}, 400

    ref = db.reference(f"users/{data['device_id']}/locations")
    ref.push({
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "timestamp": datetime.utcnow().isoformat()
    })

    message = f"📍 *Lokasi Baru dari {data['device_id']}*\n🌍 Latitude: {data['latitude']}\n🌍 Longitude: {data['longitude']}\n🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    send_telegram_message(message)

    return {"status": "success", "message": "Location saved"}, 200

# 🔹 API laporan mingguan
@app.route("/weekly_report", methods=["GET"])
def weekly_report():
    users_ref = db.reference("users")
    users = users_ref.get()

    if not users:
        return {"status": "error", "message": "No location data found"}, 200

    report = "📍 **Rekap Lokasi Mingguan** 📍\n"
    for device_id, data in users.items():
        report += f"\n🔹 **{device_id}**\n"
        for key, location in data.get("locations", {}).items():
            timestamp = datetime.fromisoformat(location['timestamp'])
            if timestamp >= datetime.utcnow() - timedelta(days=7):  
                report += f"📍 {location['latitude']}, {location['longitude']} 🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

    send_telegram_message(report)
    return {"status": "success", "message": "Weekly report sent"}, 200

# 🔹 Webhook Railway
@app.route("/", methods=["GET"])
def home():
    return "🚀 API Tracking Lokasi Berjalan!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
