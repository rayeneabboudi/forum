from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8031613048:AAEbku_lTXC5SsA_woS3vQ4sPEPuE7NZ1qw"
TELEGRAM_CHAT_ID = "2084183461"

def send_telegram_alert(applicant_data):
    """Sends a professional summary of the applicant to your Telegram."""
    name = applicant_data.get("doc_meta", {}).get("name", "Unknown")
    # Matching the keys from your gg.html payload
    audit = applicant_data.get("security_audit", {})
    integrity = audit.get("integrity_score", "N/A")
    
    forensics = applicant_data.get("behavioral_forensics", {})
    tab_switches = forensics.get("session", {}).get("tab_switches", 0)
    
    message = (
        f"<b>🚨 New Protocol Entry Received</b>\n\n"
        f"👤 <b>Applicant:</b> {name}\n"
        f"🛡️ <b>Integrity:</b> {integrity}\n"
        f"🔄 <b>Tab Switches:</b> {tab_switches}\n\n"
        f"<i>Check Excel for full forensic report.</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Telegram API Response: {response.status_code}") # Checks if Telegram liked it
    except Exception as e:
        print(f"Telegram alert failed: {e}")

# --- THE MAIN ROUTE ---
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        print(f"✅ Received Dossier for: {data.get('doc_meta', {}).get('name')}")

        # 1. Trigger Telegram Notification
        send_telegram_alert(data)
        
        # 2. Return Success to Frontend
        return jsonify({
            "status": "success", 
            "message": "Protocol Received and Admin Notified"
        }), 200

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    # Placeholder for your admin dashboard
    return jsonify({"status": "active", "info": "Database retrieval requires Firebase link."}), 200

if __name__ == "__main__":
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)