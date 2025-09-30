from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
import openai
import pandas as pd

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Load your Goodland dataset
DATA_FILE = os.path.join(os.path.dirname(__file__), "goodland_addresses.csv")
data_df = pd.read_csv(DATA_FILE)

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
        # Use OpenAI to parse query
        messages = [
            {"role": "system", "content": "Extract city name and minimum price from user query."},
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

        city = parsed.get("city", "").lower()
        min_price = parsed.get("min_price", 0)

        # Filter dataset
        filtered = data_df.copy()
        if city:
            filtered = filtered[filtered['city'].str.lower() == city]
        if min_price:
            filtered = filtered[filtered['Estimated_Price'] >= min_price]

        # Convert to list of dicts
        final_data = filtered.to_dict(orient="records")
        export_data_store["current_search"] = final_data

        # Send first 5 results as preview
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
    if not data:
        return jsonify({"error": "No data to export"}), 400

    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     download_name="goodland_homes.csv",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
