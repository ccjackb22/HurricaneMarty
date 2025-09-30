from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Existing chat route
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"answer": "Please provide a prompt."})
    
    # Here you would call your AI summarization function
    # For now, we just echo the prompt
    response_text = f"Received: {prompt}"
    return jsonify({"answer": response_text})

# New export CSV route
@app.route("/export_goodland", methods=["GET"])
def export_goodland():
    try:
        # Run the script
        subprocess.run(["python", "save_goodland_data.py"], check=True)

        # CSV path (adjust if your script saves it elsewhere)
        csv_path = "goodland_addresses.csv"
        if os.path.exists(csv_path):
            return send_file(csv_path, as_attachment=True)
        else:
            return jsonify({"error": "CSV not found after running the script."}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to run script: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
