from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import random

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

export_data_store = {}

# Common street names for demo purposes
STREET_NAMES = [
    "Maple St", "Oak Ave", "Pine Ln", "Cedar Ct", "Elm St",
    "Washington Blvd", "Lincoln Rd", "Jefferson Ave", "Madison St",
    "Adams St", "1st St", "2nd Ave", "3rd St", "4th Ave", "Sunset Blvd"
]

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
        # --- Extract city and min price using GPT ---
        messages = [
            {"role": "system", "content": "Extract city name and min price from user query."},
            {"role": "user", "content": f'Query: "{query}". Return JSON with "city" and "min_price" (int or null).'}
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
        city = parsed.get("city", "Unknown City")
        min_price = parsed.get("min_price", 0)

        # --- Generate 100+ realistic homes ---
        final_data = []
        for i in range(100):
            house_number = random.randint(100, 9999)
            street = random.choice(STREET_NAMES)
            address = f"{house_number} {street}, {city}, USA"
            estimated_price = random.randint(200000, 2000000)
            if min_price and estimated_price < min_price:
                estimated_price += min_price
            final_data.append({
                "Address": address,
                "Latitude": round(random.uniform(28.0, 30.0), 6),
                "Longitude": round(random.uniform(-82.0, -80.0), 6),
                "Estimated_Price": estimated_price,
                "Distance_from_Landfall": "N/A"
            })

        # Store for CSV export
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
