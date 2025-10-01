from flask import Flask, render_template, jsonify, send_file
import os
import json

app = Flask(__name__)

DATA_FOLDER = "data"

def load_all_geojson():
    geojson_data = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".geojson"):
            path = os.path.join(DATA_FOLDER, filename)
            features = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            features.append(json.loads(line))
                        except json.JSONDecodeError:
                            print(f"Skipping line due to JSON error: {line[:50]}...")
            # Use filename without extension for endpoint
            key = filename.replace("_simplified.geojson","").replace(".geojson","")
            geojson_data[key] = {"type":"FeatureCollection","features":features}
    return geojson_data

geojson_data = load_all_geojson()

@app.route("/")
def index():
    # Send a list of available datasets to index.html
    datasets = list(geojson_data.keys())
    return render_template("index.html", datasets=datasets)

@app.route("/get_geojson/<dataset>")
def get_geojson(dataset):
    data = geojson_data.get(dataset)
    if data:
        return jsonify(data)
    return jsonify({"error": "Dataset not found"}), 404

@app.route("/download/<dataset>")
def download(dataset):
    # Send the raw file from DATA_FOLDER
    for filename in os.listdir(DATA_FOLDER):
        key = filename.replace("_simplified.geojson","").replace(".geojson","")
        if key == dataset:
            return send_file(os.path.join(DATA_FOLDER, filename), as_attachment=True)
    return jsonify({"error": "Dataset not found"}), 404

@app.route("/preview/<dataset>")
def preview(dataset):
    data = geojson_data.get(dataset)
    if data:
        preview_features = data["features"][:10]
        return jsonify(preview_features)
    return jsonify({"error": "Dataset not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
