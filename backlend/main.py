from flask import Flask, request, jsonify
from flask_cors import CORS  # MUST HAVE THIS

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