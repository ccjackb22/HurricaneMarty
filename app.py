from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Google Drive file IDs for each dataset
COUNTY_FILES = {
    "manatee_addresses": "1m5l1EJ_K6TVEvgdazqZMbpFfdmI-Y62e",
    "manatee_buildings": "1Pis_NhDoow0ZaFeky62Hb7Guq-UtegBY",
    "sarasota_addresses": "1tezaBGS36_0IZeQqgN6hpr6Zd98mARlz",
    "sarasota_buildings": "1ZkB3e7Uqa1rGOXKvzujnYZmG60mYMNuA"
}

def fetch_geojson(file_id):
    """Fetch a GeoJSON file from Google Drive by file_id."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": f"Failed to fetch file {file_id}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_geojson/<dataset>")
def get_geojson(dataset):
    """API endpoint to get GeoJSON data by dataset key (e.g., manatee_addresses)."""
    file_id = COUNTY_FILES.get(dataset)
    if not file_id:
        return jsonify({"error": "Dataset not found"}), 404

    data = fetch_geojson(file_id)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
