from flask import Flask, request, jsonify
from flask_cors import CORS # 1. Import CORS

app = Flask(__name__)
CORS(app) # 2. Enable CORS for all routes

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    print("Received Dossier:", data)
    # Your logic to save to Firebase or Excel goes here
    return jsonify({"status": "success", "message": "Dossier Received"}), 200

if __name__ == "__main__":
    app.run()