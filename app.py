from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import requests
import json

app = Flask(__name__)

# --- OpenAI API ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- In-memory storage for CSV export ---
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
        # --- Use OpenAI to parse query ---
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts ZIP codes, min/max prices, and hurricane-related info from user queries."},
            {"role": "user", "content": f'Extract structured info from this query: "{query}". Return JSON with fields: zip_codes (list), min_price (int or null), max_price (int or null), hurricane_related (true/false).'}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )

        structured_text = response.choices[0].message.content.strip()
        structured_data = json.loads(structured_text)

        zip_codes = structured_data.get("zip_codes", [])
        min_price = structured_data.get("min_price")
        max_price = structured_data.get("max_price")
        hurricane_related = structured_data.get("hurricane_related", False)

        if not zip_codes:
            return jsonify({"error": "No ZIP code found in query"}), 400

        # --- Query OSM / Nominatim for each ZIP ---
        final_data = []
        for zip_code in zip_codes:
            osm_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=USA&format=json&addressdetails=1"
            osm_response = requests.get(osm_url, headers={"User-Agent": "PeleeAI/1.0"})
            locations = osm_response.json()

            for loc in locations:
                # OSM only provides building/address data; AI_Filtered tags can include price/hurricane info
                final_data.append({
                    "Address": loc.get("display_name"),
                    "Latitude": loc.get("lat"),
                    "Longitude": loc.get("lon"),
                    "AI_Filtered": f"Hurricane related: {hurricane_related}, Min price: {min_price}, Max price: {max_price}"
                })

        # Save for CSV export
        export_data_store["current_search"] = final_data

        # Front-end preview: show only 5 rows for usability
        preview_data = final_data[:5]

        return jsonify({
            "preview": preview_data,
            "preview_count": len(preview_data),
            "total_count": len(final_data),
            "subscription": "free"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_csv():
    data = export_data_store.get("current_search", [])

    # No limit on export anymore
    export_data = data

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Address", "Latitude", "Longitude", "AI_Filtered"])
    writer.writeheader()
    for row in export_data:
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     download_name="homes_export.csv",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
