import os
import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

def load_all_geojson():
    """Load all geojson files from the data folder."""
    all_data = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".geojson"):
            path = os.path.join(DATA_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    all_data[filename] = json.load(f)
            except Exception as e:
                print(f"Skipping {filename}: {e}")
    return all_data

# Load data once at startup
geojson_data = load_all_geojson()

@app.route("/")
def index():
    return render_template("index.html", files=list(geojson_data.keys()))

@app.route("/data/<filename>")
def get_data(filename):
    if filename in geojson_data:
        return jsonify(geojson_data[filename])
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
