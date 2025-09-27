from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import requests
import json
import random
import re

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

export_data_store = {}

def parse_gpt_json(raw_text):
    """Extract JSON array from GPT output robustly."""
    try:
        match = re.search(r"(\[.*\])", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass
    return []

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
        # Extract city and min/max price using GPT
        messages = [
            {"role": "system", "content": "Extract city name and min/max price from user query."},
            {"role": "user", "content": f'Query: "{query}". Return JSON: city (str), min_price (int or null), max_price (int or null).'}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )
        try:
            parsed = json.loads(response.choices[0].message.content.strip())
        except:
            parsed = {}
        city = parsed.get("city")
        min_price = parsed.get("min_price")
        max_price = parsed.get("max_price")

        if not city:
            return jsonify({"error": "No city found in query"}), 400

        final_data = []

        # Step 1: Get city polygon from OSM
        osm_url = f"https://nominatim.openstreetmap.org/search?city={city}&country=USA&format=json&polygon_geojson=1"
        osm_response = requests.get(osm_url, headers={"User-Agent": "HurricaneMarty/1.0"})
        city_results = osm_response.json() if osm_response.status_code == 200 else []

        # Step 2: Generate homes
        if not city_results:
            # fallback GPT if OSM city not found
            city_name = city
        else:
            city_name = city_results[0].get("display_name", city)

        fallback_prompt = (
            f"Generate 100 single-family home addresses in {city_name}, USA. "
            f"Return JSON array of objects: Address, Estimated_Price (USD), Latitude, Longitude. "
            f"Do not include apartments, condos, or units."
        )
        try:
            gpt_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": fallback_prompt}],
                temperature=0
            )
            homes = parse_gpt_json(gpt_resp.choices[0].message.content.strip())
        except:
            homes = []

        if not homes:
            # fallback demo homes
            homes = []
            for i in range(100):
                homes.append({
                    "Address": f"{city_name} Demo Home #{i+1}",
                    "Latitude": random.uniform(28, 30),
                    "Longitude": random.uniform(-82, -80),
                    "Estimated_Price": random.randint(200000, 800000),
                    "Distance_from_Landfall": "N/A"
                })

        # Apply min/max price filter
        if min_price or max_price:
            homes = [h for h in homes if (not min_price or h["Estimated_Price"] >= min_price) and (not max_price or h["Estimated_Price"] <= max_price)]

        final_data.extend(homes)
        export_data_store["current_search"] = final_data
        preview_data = final_data[:5]

        return jsonify({
            "preview": preview_data,
            "preview_count": len(preview_data),
            "total_count": len(final_data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_csv():
    data = export_data_store.get("current_search", [])
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Address", "Latitude", "Longitude", "Estimated_Price", "Distance_from_Landfall"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     download_name="homes_export.csv",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
