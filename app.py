from flask import Flask, render_template, request, jsonify, send_file
import requests
import io
import json

app = Flask(__name__)

# Mapping of dataset names to Google Drive file IDs
GDRIVE_FILES = {
    "manatee_addresses_simplified": "1y63F4l4XDc9s2ZkQbS3Av9ECoN_E3kGE",
    "manatee_buildings_simplified": "1PpOBVFRWbpKACtahpg6nt6c7L7aJ3qEK",
    "sarasota_addresses_simplified": "1CXzVpetX9lfp-3NDpPUmfsaKGD-QxsmR",
    "sarasota_buildings_simplified": "1RvwlfeQFyAF4xrxSGiFEY5E2Luu3m6b-"
}

def fetch_geojson_from_gdrive(file_id):
    """
    Fetches a Google Drive file as GeoJSON
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url)
    r.raise_for_status()
    
    features = []
    # The file is in JSON Lines format, so parse line by line
    for line in r.text.strip().splitlines():
        if line.strip():
            features.append(json.loads(line))
    return features

@app.route("/")
def index():
    return render_template("index.html", datasets=list(GDRIVE_FILES.keys()))

@app.route("/get_geojson/<dataset>")
def get_geojson(dataset):
    file_id = GDRIVE_FILES.get(dataset)
    if not file_id:
        return jsonify({"error": "Dataset not found"}), 404
    try:
        data = fetch_geojson_from_gdrive(file_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/preview/<dataset>")
def preview(dataset):
    file_id = GDRIVE_FILES.get(dataset)
    if not file_id:
        return jsonify({"error": "Dataset not found"}), 404
    try:
        data = fetch_geojson_from_gdrive(file_id)
        return jsonify(data[:10])  # first 10 features
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<dataset>")
def download(dataset):
    file_id = GDRIVE_FILES.get(dataset)
    if not file_id:
        return jsonify({"error": "Dataset not found"}), 404
    try:
        data = fetch_geojson_from_gdrive(file_id)
        mem_file = io.BytesIO()
        mem_file.write(json.dumps(data).encode("utf-8"))
        mem_file.seek(0)
        return send_file(mem_file, mimetype="application/json", as_attachment=True, download_name=f"{dataset}.json")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
