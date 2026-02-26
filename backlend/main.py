from flask import Flask, request, jsonify
from flask_cors import CORS  # MUST HAVE THIS
import os
token = os.getenv("TELEGRAM_TOKEN")
app = Flask(__name__)
CORS(app) # This tells the browser "It's okay to send data from my website"

# This is the "Route" that matches your JavaScript URL
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.json
        print("Received Protocol Data:", data)
        
        # LOGIC: Save to your Excel or Database here
        
        return jsonify({"status": "success", "message": "Protocol Received"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # Add this route to your main.py
@app.route('/get_data', methods=['GET'])
def get_data():
    # If you are using a global list for testing:
    # return jsonify(all_applications) 
    
    # If you are using Firebase, fetch the docs and return them:
    # applicants = db.collection("applicants").stream()
    # return jsonify([doc.to_dict() for doc in applicants])
    return jsonify({"status": "error", "message": "No database linked yet"}), 500
import requests

# Replace with your actual details
TELEGRAM_TOKEN = "8031613048:AAEbku_lTXC5SsA_woS3vQ4sPEPuE7NZ1qw"
TELEGRAM_CHAT_ID = "2084183461"

def send_telegram_alert(applicant_data):
    """Sends a professional summary of the applicant to your Telegram."""
    
    name = applicant_data.get("doc_meta", {}).get("name", "Unknown")
    integrity = applicant_data.get("security_audit", {}).get("integrity_score", "N/A")
    tab_switches = applicant_data.get("behavioral_forensics", {}).get("session", {}).get("tab_switches", 0)
    
    # Format the message (Supports HTML or Markdown)
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
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

# --- Call this inside your /submit route ---
@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    # ... existing Firebase save logic ...
    
    send_telegram_alert(data) # This sends the live ping
    return {"status": "success"}, 200