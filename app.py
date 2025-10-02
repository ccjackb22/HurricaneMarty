from flask import Flask, render_template, send_from_directory, jsonify
import os, json

app = Flask(__name__)
DATA_FOLDER = "data"

# Load all GeoJSON files from 'data'
def load_all_geojson():
    geojson_files = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".geojson"):
            with open(os.path.join(DATA_FOLDER, filename)) as f:
                geojson_files[filename] = json.load(f)
    return geojson_files

geojson_data = load_all_geojson()

@app.route("/")
def index():
    # Send the first GeoJSON file for preview/map
    first_file = list(geojson_data.keys())[0]
    features = geojson_data[first_file]["features"][:10]  # first 10 rows
    preview_data = [
        {
            "Number": f["properties"]["number"],
            "Street": f["properties"]["street"],
            "City": f["properties"]["city"],
            "District": f["properties"]["district"],
            "Region": f["properties"]["region"],
            "Postcode": f["properties"]["postcode"]
        }
        for f in features
    ]
    return render_template("index.html", geojson_file=first_file, preview_data=preview_data)

@app.route("/data/<filename>")
def download(filename):
    return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
