from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import requests

app = Flask(__name__)

# --- OpenAI API ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- In-memory storage for CSV export ---
export_data_store = {}

# --- Home page ---
@app.route("/")
def index():
    return render_template("index.html")

# --- Search endpoint ---
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    subscription = data.get("subscription", "free")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # --- Step 1: Use OpenAI to parse the query ---
        prompt = f"""
        Extract structured information from this user query for real estate search:
        Query: "{query}"
        Return JSON with fields:
        - zip_codes: list of 5-digit ZIP codes
        - min_price: minimum home price in dollars (optional)
        - max_price: maximum home price in dollars (optional)
        - hurricane_related: true/false
        """

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=150
        )

        structured_text = response.choices[0].text.strip()
        import json
        structured_data = json.loads(structured_text)

        zip_codes = structured_data.get("zip_codes", [])
        min_price = structured_data.get("min_price")
        max_price = structured_data.get("max_price")
        hurricane_related = structured_data.get("hurricane_related", False)

        if not zip_codes:
            return jsonify({"error": "No ZIP code found in query"}), 400

        # --- Step 2: Query OpenStreetMap / Nominatim for each ZIP ---
        final_data = []
        for zip_code in zip_codes:
            osm_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=USA&format=json&addressdetails=1"
            osm_response = requests.get(osm_url, headers={"User-Agent": "PeleeAI/1.0"})
            locations = osm_response.json()

            for loc in locations:
                # Optional: filter by type (residential)
                if loc.get("type") in ["house", "residential", "building"]:
                    final_data.append({
                        "Address": loc.get("display_name"),
                        "Latitude": loc.get("lat"),
                        "Longitude": loc.get("lon"),
                        "AI_Filtered": f"Hurricane related: {hurricane_related}, Min price: {min_price}, Max price: {max_price}"
                    })

        # Save for CSV export
        export_data_store["current_search"] = final_data

        # Limit preview for display
        preview_rows = 5
        preview_data = final_data[:preview_rows]

        return jsonify({
            "preview": preview_data,
            "preview_count": len(preview_data),
            "total_count": len(final_data),
            "max_export": 20,
            "subscription": subscription
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CSV download endpoint ---
@app.route("/download", methods=["GET"])
def download_csv():
    subscription = request.args.get("subscription", "free")
    data = export_data_store.get("current_search", [])

    # Determine max exportable rows
    max_rows = 5 if subscription == "free" else 20
    export_data = data[:max_rows]

    # Create CSV
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

# --- Run Flask app ---
if __name__ == "__main__":
    app.run(debug=True)
