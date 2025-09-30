from flask import Flask, render_template, request, jsonify, send_file
import geopandas as gpd
import io
import csv
import openai

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# File paths (repo root)
ADDRESSES_FILE = "goodland-addresses.geojson"
BUILDINGS_FILE = "goodland-buildings.geojson"

# Load GeoJSON data
addresses = gpd.read_file(ADDRESSES_FILE)
buildings = gpd.read_file(BUILDINGS_FILE)

# Prepare export storage
export_data_store = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # --- Use OpenAI to extract city from user query ---
        messages = [
            {"role": "system", "content": "Extract city name from the user query."},
            {"role": "user", "content": f'Query: "{query}". Return JSON with "city" only.'}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )
        try:
            parsed = eval(response.choices[0].message.content.strip())
        except:
            parsed = {}
        city = parsed.get("city", "").lower()

        # --- Filter addresses for that city ---
        filtered_addresses = addresses[addresses['city'].str.lower() == city]

        # Bounding box for filtered addresses
        if not filtered_addresses.empty:
            minx, miny, maxx, maxy = filtered_addresses.total_bounds
            filtered_buildings = buildings.cx[minx:maxx, miny:maxy]
        else:
            filtered_buildings = gpd.GeoDataFrame(columns=buildings.columns)

        # Prepare data for CSV
        csv_data = []
        for idx, row in filtered_addresses.iterrows():
            csv_data.append({
                "Address": f"{row['number']} {row['street']}, {row['city']}, USA",
                "Latitude": row.geometry.y,
                "Longitude": row.geometry.x
            })

        # Store for download
        export_data_store["current_search"] = csv_data

        # Preview first 5 addresses
        preview_data = csv_data[:5]

        return jsonify({
            "preview": preview_data,
            "preview_count": len(preview_data),
            "total_count": len(csv_data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_csv():
    data = export_data_store.get("current_search", [])
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Address", "Latitude", "Longitude"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     download_name="goodland_addresses.csv",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
