from flask import Flask, render_template, request, jsonify, send_file
import requests
import io
import json

app = Flask(__name__)

# Map dataset names to Google Drive "download" URLs
DATASETS = {
    "Manatee Addresses": "https://drive.google.com/uc?export=download&id=1y63F4l4XDc9s2ZkQbS3Av9ECoN_E3kGE",
    "Manatee Buildings": "https://drive.google.com/uc?export=download&id=1PpOBVFRWbpKACtahpg6nt6c7L7aJ3qEK",
    "Sarasota Addresses 1": "https://drive.google.com/uc?export=download&id=1CXzVpetX9lfp-3NDpPUmfsaKGD-QxsmR",
    "Sarasota Addresses 2": "https://drive.google.com/uc?export=download&id=1RvwlfeQFyAF4xrxSGiFEY5E2Luu3m6b-"
}

@app.route("/")
def index():
    return render_template("index.html", datasets=list(DATASETS.keys()))

def fetch_dataset(name):
    url = DATASETS.get(name)
    if not url:
        return None
    r = requests.get(url)
    r.raise_for_status()
    # Each line is a separate JSON object
    features = [json.loads(line) for line in r.text.splitlines() if line.strip()]
    return features

@app.route("/preview/<dataset_name>")
def preview(dataset_name):
    try:
        features = fetch_dataset(dataset_name)
        return jsonify(features[:10])  # first 10 lines
    except Exception as e:
        return jsonify({"error": str(e), "details": "Failed to fetch file"}), 400

@app.route("/get_geojson/<dataset_name>")
def get_geojson(dataset_name):
    try:
        features = fetch_dataset(dataset_name)
        return jsonify(features)
    except Exception as e:
        return jsonify({"error": str(e), "details": "Failed to fetch file"}), 400

@app.route("/download/<dataset_name>")
def download(dataset_name):
    url = DATASETS.get(dataset_name)
    if not url:
        return "Dataset not found", 404
    r = requests.get(url)
    return send_file(io.BytesIO(r.content),
                     download_name=f"{dataset_name}.json",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
