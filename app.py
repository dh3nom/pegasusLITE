import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔹 Ambil token & chat ID dari environment variables
TELEGRAM_TOKEN = os.getenv("7723449593:AAH-UdXxSvkRqfNa14cMn1Km2LX-HHkaqYo")
CHAT_ID = os.getenv("6458597760")

# 🔹 Setup Firebase dari environment variables
firebase_credentials = os.getenv("{"type": "service_account","project_id": "pegasuslite-5211e","private_key_id": "b799128780506e9660936f6a4ce7f15a72d370e1","private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJqEc686P9EcUd\n5ka4/UpjyvB0rD7k5qrgJjC5ajAMZeHwSQvT3m4tZcWQqbhwGduc6IlURBUxGWGJ\n1qDjnZK5+rY3EhoBQqYKjLEJytSx4GGOKxhPzdsTNmVWydqgY7bC99Sfy84uonOu\nmgipS7nv/hP133ZEzUmaD4Hl33Gfegli36wqnj4pHr/n32ZFM5D4n34Uk3HC/7ve\nRWpwCpJmdUyRomkbMjOpwUjhZvMWzV6Nn8ynfUzfuhdNLKkv7YmGAwqZUCaWanNN\nxrRyGJblJ30b+8xUadgL8NXbC9fmyv2MOPMRbmvvM6Sz5zz1yUBirzjdhELUVzvQ\ntX7f5uOxAgMBAAECggEAWzYlOdH4C8Cc4yBEPuo6WpbxWiSKsihvg8FiaotQPlta\n7b9sfSFvvlL5IKzTwsi/X+KCMz40Q6gSSTFuRmYAduSixJgIcSd/SOhIL4Cx4d72\n4UI21enrvG3vOmlE3SUdBmTopHqfwNIz9vavEjwxVw8aYiz4JrigIPIAtEPz9ciD\nplsMxx2CUWlPBVK8bcoBbC8NXv1c1CQiI2tEVKAE6huxL5Y5y4afTmJGbMOyKnPm\nMg9jCV7t2J2sRkNU6aYygvu+3l6TZjCiBqoqJGSpxwLF5FFuw84w3vbyu62TOuBv\nZMwZ5K/mDlslmZnWWoSUtdAAQO8Cdi4mUq72t4q6/QKBgQD66zBx3elOJz1CFkgi\nxVbzooOVGa0F22u7B+xnqX72WYWRGNH0pO9CXQxubAK+T3eXGmN3uGo8yZbmsHPW\neHRfWwc72NzXPlOHIjUVxR18mTUU52wWXG5OydjX3syNpNqlZNiXCivuOzw6EesD\nmIEKHShruWj7jh9GT1+TpKKH4wKBgQDNvbVmwcIPh6Gh5RfiH3QFW0ldoKe1K0A/\neF26cvq5xCnVXoOHpRdrBoQNaUYgkaKeF5oBuiTiyRB8K4X443BR6OFzlotR/1YG\nUVdsPG2f5mYbE1OsAlrbCm1NWrcDXliLlG3IXIjO8wId9q8y9kM35oGKl3/40oG9\n1Gdgq2TyWwKBgFfGmoXayVjLpURPIyD2w7oq6bjo6HwaDA+7b9m7k2x+WJkvg5L/\nd6tRfZ3LLxKAHie/1Xf2DUQCiUVeCMfID32kDF3FOUwaw4GMV+GruOrzdXxAkLEp\n2HS7a53olMogF1SweIwtxLxsAF+YEQyK9ukg1hkJHU6SoyIndhniB/FdAoGAFY+P\n9xjPEXmRQroTaqsJKZaLdbhkWuQRc5VVnTh3dghMqgOhnRF8BsdEB3PE2Zzpgc/P\nX+b1/p47kAevnomXN75EAi0ApLMxfLABjWI3ys4GXUgFOL12cAYDtluPWlcEyHvh\nlWG9JJLq4eD8M0cDfFQ3tyJxUs4cspwTyVms1okCgYEAz4fyDSkfEKQOg5FSE85x\nHtnrtObt/WwGMr3lrQ1+/ULuDCmDbWKjOj8s1xyWDoazKVJezeqrDz7Rcx4IsGnc\nRNZ3BMlqPf6xG5RpCStaO9Zw8ToSiYJ5p3D4KEBTdzYytCj6UBHieNrFaOY+qC6/\nR6v0lFXKK3A7D4wd40Ybi4g=\n-----END PRIVATE KEY-----\n","client_email": "firebase-adminsdk-fbsvc@pegasuslite-5211e.iam.gserviceaccount.com","client_id": "111023341435534423278","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40pegasuslite-5211e.iam.gserviceaccount.com","universe_domain": "googleapis.com"}")
firebase_url = os.getenv("https://pegasuslite-5211e-default-rtdb.firebaseio.com/")

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
