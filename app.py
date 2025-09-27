from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import requests
import openai

app = Flask(__name__)

# --- Environment variables ---
OSM_API_KEY = os.environ.get("OSM_API")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# --- In-memory storage for CSV export ---
export_data_store = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    subscription = data.get("subscription", "free")

    if not OSM_API_KEY:
        return jsonify({"error": "OSM API key not configured"}), 500

    try:
        # Extract zip code or location from query (simple parsing for now)
        # Example: "homes in ZIP 33101"
        zip_code = None
        parts = query.split()
        for i, p in enumerate(parts):
            if p.lower() == "zip":
                zip_code = parts[i+1]
                break

        if not zip_code:
            return jsonify({"error": "No ZIP code found in query"}), 400

        # Call LocationIQ / OSM API to get addresses in the ZIP code
        url = "https://us1.locationiq.com/v1/search.php"
        params = {
            "key": OSM_API_KEY,
            "postalcode": zip_code,
            "format": "json",
            "countrycodes": "us",
            "addressdetails": 1,
            "limit": 50
        }
        response = requests.get(url, params=params)
        results = response.json()

        # Prepare final data
        final_data = []
        for place in results:
            address = place.get("display_name")
            lat = place.get("lat")
            lon = place.get("lon")

            final_data.append({
                "Address": address,
                "Latitude": lat,
                "Longitude": lon
            })

        # Use OpenAI to optionally filter / classify homes based on value or hurricane impact
        if "over $400k" in query.lower() or "hurricane" in query.lower():
            addresses_text = "\n".join([d["Address"] for d in final_data])
            prompt = f"From this list of addresses, identify which homes are likely over $400k or could be impacted by a hurricane:\n{addresses_text}"
            
            openai.api_key = OPENAI_API_KEY
            ai_response = openai.Completion.create(
                model="gpt-4",
                prompt=prompt,
                max_tokens=500
            )
            filtered_text = ai_response.choices[0].text.strip()
            # For simplicity, we'll just return the text from OpenAI
            # You could also parse it and match addresses to create structured CSV
            final_data.append({"AI_Filtered": filtered_text})

        # Save for CSV export
        export_data_store["current_search"] = final_data

        # Limit preview
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

@app.route("/download", methods=["GET"])
def download_csv():
    subscription = request.args.get("subscription", "free")
    data = export_data_store.get("current_search", [])

    # Determine max exportable rows
    max_rows = 5 if subscription == "free" else 20
    export_data = data[:max_rows]

    # Create CSV
    output = io.StringIO()
    fieldnames = export_data[0].keys() if export_data else ["Address", "Latitude", "Longitude", "AI_Filtered"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in export_data:
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                     download_name="homes_export.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
