from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)

# OpenAI API Key from Render environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")

# AI chat route
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

# Serve Goodland addresses
@app.route("/data/goodland-addresses", methods=["GET"])
def goodland_addresses():
    try:
        with open("goodland-addresses.geojson", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# Download route
@app.route("/download/goodland-addresses", methods=["GET"])
def download_goodland_addresses():
    try:
        return send_from_directory(".", "goodland-addresses.geojson", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# Optional: serve buildings data
@app.route("/data/goodland-buildings", methods=["GET"])
def goodland_buildings():
    try:
        with open("goodland-buildings.geojson", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
