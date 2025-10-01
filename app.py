from flask import Flask, jsonify, send_file, send_from_directory
import json
import io
import os

app = Flask(__name__)

# --- Load addresses ---
ADDRESS_FILE = "goodland-addresses.geojson"
BUILDING_FILE = "goodland-buildings.geojson"

@app.route("/api/addresses", methods=["GET"])
def get_addresses():
    try:
        with open(ADDRESS_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download/addresses", methods=["GET"])
def download_addresses():
    try:
        with open(ADDRESS_FILE, "r") as f:
            data = json.load(f)
        # Convert GeoJSON to CSV string
        output = io.StringIO()
        fieldnames = ["number", "street", "unit", "city", "district", "region", "postcode", "id", "longitude", "latitude"]
        output.write(",".join(fieldnames) + "\n")
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None])
            row = [
                str(props.get("number", "")),
                str(props.get("street", "")),
                str(props.get("unit", "")),
                str(props.get("city", "")),
                str(props.get("district", "")),
                str(props.get("region", "")),
                str(props.get("postcode", "")),
                str(props.get("id", "")),
                str(coords[0]),
                str(coords[1])
            ]
            output.write(",".join(row) + "\n")
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                         download_name="addresses.csv", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
