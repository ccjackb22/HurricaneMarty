from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os
import openai
import io
import csv

app = Flask(__name__)
CORS(app)

# OpenAI API Key is read from Render environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- AI chat ---
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

# --- Goodland data as JSON ---
@app.route("/data/goodland", methods=["GET"])
def goodland_data():
    try:
        with open("data/goodland.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Goodland data as CSV download ---
@app.route("/download/goodland", methods=["GET"])
def download_goodland():
    try:
        # Load the JSON data
        with open("data/goodland.json", "r") as f:
            data = json.load(f)

        # Ensure data is a list of dicts
        if not isinstance(data, list):
            return jsonify({"error": "Data format invalid"}), 500

        # Write CSV in-memory
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            download_name="goodland_export.csv",
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Home route ---
@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
