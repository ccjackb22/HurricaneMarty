from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import openai

app = Flask(__name__)
CORS(app)

# Pull API key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "HurricaneMarty API is running"})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data", methods=["GET"])
def data():
    try:
        file_path = os.path.join(os.getcwd(), "data.json")  # replace with your file
        if not os.path.exists(file_path):
            return jsonify({"error": "Data file not found"}), 404

        # Load JSON manually instead of pandas
        with open(file_path, "r") as f:
            records = json.load(f)
        return jsonify(records[:10])  # return first 10 records
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
