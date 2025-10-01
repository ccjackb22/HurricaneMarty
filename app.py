from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Map friendly names to Google Drive download URLs
GEOJSON_FILES = {
    "manatee_addresses": "https://drive.google.com/uc?export=download&id=1y63F4l4XDc9s2ZkQbS3Av9ECoN_E3kGE",
    "manatee_buildings": "https://drive.google.com/uc?export=download&id=1PpOBVFRWbpKACtahpg6nt6c7L7aJ3qEK",
    "sarasota_addresses": "https://drive.google.com/uc?export=download&id=1CXzVpetX9lfp-3NDpPUmfsaKGD-QxsmR",
    "sarasota_buildings": "https://drive.google.com/uc?export=download&id=1RvwlfeQFyAF4xrxSGiFEY5E2Luu3m6b-",
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_geojson/<filename>")
def get_geojson(filename):
    url = GEOJSON_FILES.get(filename)
    if not url:
        return jsonify({"error": "File not found"}), 404
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch file {filename}", "details": str(e)}), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
