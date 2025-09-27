from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import requests
import json
import random

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

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
        # Step 1: Parse user query for ZIP code and price
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

        # Step 2: Pull addresses from OpenStreetMap
        for zip_code in zip_codes:
            osm_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=USA&format=json&addressdetails=1"
            osm_response = requests.get(osm_url, headers={"User-Agent": "PeleeAI/1.0"})
            locations = osm_response.json()

            for loc in locations:
                # Step 3: Ask GPT for 100 rough estimated prices in one batch
                estimate_prompt = (
                    f"Provide 100 rough estimated prices in USD for typical residential homes "
                    f"in the area of {loc.get('display_name')}. Return as a JSON array of numbers only."
                )
                try:
                    price_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": estimate_prompt}],
                        temperature=0
                    )
                    prices = json.loads(price_response.choices[0].message.content.strip())
                    if not isinstance(prices, list):
                        raise ValueError("GPT did not return a list")
                except:
                    # fallback to random prices
                    prices = [random.randint(200000, 800000) for _ in range(100)]

                # Step 4: Create 100 demo homes per OSM location
                for i, estimated_price in enumerate(prices):
                    if (min_price and estimated_price < min_price) or (max_price and estimated_price > max_price):
                        continue

                    final_data.append({
                        "Address": f"{loc.get('display_name')} Apt {i+1}",
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
