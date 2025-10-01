from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

DATA_FOLDER = "data"

def load_all_geojson():
    geojson_data = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".geojson"):
            path = os.path.join(DATA_FOLDER, filename)
            with open(path, "r", encoding="utf-8") as f:
                geojson_data[filename] = json.load(f)
    return geojson_data

geojson_data = load_all_geojson()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_geojson/<filename>")
def get_geojson(filename):
    data = geojson_data.get(filename)
    if data:
        return jsonify(data)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
