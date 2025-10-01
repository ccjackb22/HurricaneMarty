from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)

# --- OpenAI API ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Helper to get file path robustly ---
def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

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

# --- Goodland data route ---
@app.route("/data/goodland-addresses", methods=["GET"])
def goodland_addresses():
    try:
        path = get_file_path("goodland-addresses.geojson")
        with open(path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Download Goodland data ---
@app.route("/download/goodland-addresses", methods=["GET"])
def download_goodland():
    try:
        path = get_file_path("goodland-addresses.geojson")
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Home page ---
@app.route("/")
def index():
    path = get_file_path("templates/index.html")
    return send_file(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
