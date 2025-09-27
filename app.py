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
        # Extract ZIP codes and min/max price from query using GPT
        messages = [
            {"role": "system", "content": "Extract ZIP codes and min/max price from user query."},
            {"role": "user", "content": f'Query: "{query}". Return JSON: zip_codes (list), min_price (int or null), max_price (int or null).'}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )
        parsed = json.loads(response.choices[0].message.content.strip())
        zip_codes = parsed.get("zip_codes", [])
        min_price = parsed.get("min_price")
        max_price = parsed.get("max_price")

        if not zip_codes:
            return jsonify({"error": "No ZIP code found in query"}), 400

        final_data = []

        for zip_code in zip_codes:
            # Step 1: Try OpenStreetMap
            osm_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=USA&format=json&addressdetails=1"
            osm_response = requests.get(osm_url, headers={"User-Agent": "PeleeAI/1.0"})
            locations = osm_response.json()

            if not locations:
                # Step 2: GPT fallback
                fallback_prompt = (
                    f"Generate 100 single-family home addresses for ZIP code {zip_code} in the USA. "
                    f"Return JSON array of objects: Address, Estimated_Price (USD), Latitude, Longitude. "
                    f"Do not include apartments, condos, or units."
                )
                gpt_resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": fallback_prompt}],
                    temperature=0
                )
                homes = parse_gpt_json(gpt_resp.choices[0].message.content.strip())

                if not homes:
                    # Last-resort demo homes
                    homes = []
                    for i in range(100):
                        homes.append({
                            "Address": f"{zip_code} Demo Home #{i+1}",
                            "Latitude": random.uniform(28, 30),
                            "Longitude": random.uniform(-82, -80),
                            "Estimated_Price": random.randint(200000, 800000),
                            "Distance_from_Landfall": "N/A"
                        })

                # Ensure Distance_from_Landfall exists
                for home in homes:
                    if "Distance_from_Landfall" not in home:
                        home["Distance_from_Landfall"] = "N/A"

                # Apply min/max price filter
                if min_price or max_price:
                    homes = [h for h in homes if (not min_price or h["Estimated_Price"] >= min_price) and (not max_price or h["Estimated_Price"] <= max_price)]

                final_data.extend(homes)
                continue

            # Process OSM locations (if any)
            for loc in locations:
                address_name = loc.get('display_name')
                if any(x in address_name.lower() for x in ["apt", "apartment", "condo", "unit"]):
                    continue

                # Generate mock estimated prices for OSM homes
                prices = [random.randint(200000, 800000) for _ in range(5)]
                for i, estimated_price in enumerate(prices):
                    if (min_price and estimated_price < min_price) or (max_price and estimated_price > max_price):
                        continue
                    final_data.append({
                        "Address": f"{address_name} #{i+1}",
                        "Latitude": float(loc.get("lat")) + random.uniform(-0.001, 0.001),
                        "Longitude": float(loc.get("lon")) + random.uniform(-0.001, 0.001),
                        "Estimated_Price": estimated_price,
                        "Distance_from_Landfall": "N/A"
                    })

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
