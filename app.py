from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import io
import os
import openai
import csv

app = Flask(__name__)
CORS(app)

# --- OpenAI setup ---
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

# --- Goodland FL Addresses Route ---
@app.route("/data/goodland-addresses", methods=["GET"])
def goodland_addresses():
    try:
        path = "goodland-addresses.geojson"  # Root of repo
        with open(path, "r") as f:
            geojson = json.load(f)

        flat_data = []
        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None])
            flat_data.append({
                "Name": props.get("Name", "N/A"),
                "Address": props.get("Address", "N/A"),
                "Latitude": coords[1] if len(coords) > 1 else None,
                "Longitude": coords[0] if len(coords) > 1 else None
            })

        return jsonify(flat_data)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- CSV Download Route ---
@app.route("/download/goodland-addresses", methods=["GET"])
def download_goodland_addresses():
    try:
        path = "goodland-addresses.geojson"
        with open(path, "r") as f:
            geojson = json.load(f)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["Name", "Address", "Latitude", "Longitude"])
        writer.writeheader()
        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None])
            writer.writerow({
                "Name": props.get("Name", "N/A"),
                "Address": props.get("Address", "N/A"),
                "Latitude": coords[1] if len(coords) > 1 else "",
                "Longitude": coords[0] if len(coords) > 1 else ""
            })

        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                         download_name="goodland_addresses.csv", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Serve Frontend ---
@app.route("/")
def index():
    return send_from_directory(".", "index.html")  # Root folder

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
