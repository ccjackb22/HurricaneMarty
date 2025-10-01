from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)

# --- OpenAI API Key ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- AI Chat Route ---
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"answer": "Please provide some text to summarize."})
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].text.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

# --- Goodland Addresses Data Route ---
@app.route("/data/goodland-addresses", methods=["GET"])
def goodland_addresses():
    try:
        with open("goodland-addresses.geojson", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Goodland Addresses Download Route ---
@app.route("/download/goodland-addresses", methods=["GET"])
def download_goodland_addresses():
    try:
        return send_from_directory(".", "goodland-addresses.geojson", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Goodland Buildings Data Route (optional) ---
@app.route("/data/goodland-buildings", methods=["GET"])
def goodland_buildings():
    try:
        with open("goodland-buildings.geojson", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Goodland Buildings Download Route (optional) ---
@app.route("/download/goodland-buildings", methods=["GET"])
def download_goodland_buildings():
    try:
        return send_from_directory(".", "goodland-buildings.geojson", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Home Route ---
@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
