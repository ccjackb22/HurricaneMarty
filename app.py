from flask import Flask, render_template, request, jsonify, send_file
import googlemaps
import os
import csv
import io

app = Flask(__name__)

# --- Google Maps API ---
gmaps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=gmaps_api_key) if gmaps_api_key else None

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

    if not gmaps:
        return jsonify({"error": "Google Maps API not configured"}), 500

    try:
        # Initial place search
        results = gmaps.places(query)
        final_data = []

        for place in results.get('results', []):
            place_id = place.get('place_id')

            # ✅ Explicitly request details fields
            details = gmaps.place(
                place_id=place_id,
                fields=[
                    "name",
                    "formatted_address",
                    "formatted_phone_number",
                    "website",
                    "opening_hours"
                ]
            ).get('result', {})

            final_data.append({
                'Name': details.get('name', place.get('name', 'N/A')),
                'Address': details.get('formatted_address', place.get('formatted_address', 'N/A')),
                'Phone': details.get('formatted_phone_number', 'N/A'),
                'Website': details.get('website', 'N/A'),
                'Hours': "\n".join(details.get('opening_hours', {}).get('weekday_text', [])) if details.get('opening_hours') else 'N/A'
            })

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
    writer = csv.DictWriter(output, fieldnames=["Name", "Address", "Phone", "Website", "Hours"])
    writer.writeheader()
    for row in export_data:
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                     download_name="places_export.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
