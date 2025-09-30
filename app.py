from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import io
import os

app = Flask(__name__)

# --- Load Goodland addresses dataset on startup ---
DATA_FILE = os.path.join(os.path.dirname(__file__), "goodland_addresses.csv")
if os.path.exists(DATA_FILE):
    goodland_df = pd.read_csv(DATA_FILE)
else:
    goodland_df = pd.DataFrame(columns=["Address", "Latitude", "Longitude", "Estimated_Price", "Distance_from_Landfall"])

# Store the current search results for CSV export
export_data_store = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    """
    Search endpoint: filters Goodland dataset based on user query.
    Currently supports simple city filter and min_price filter.
    """
    data = request.get_json()
    query = data.get("query", "").strip().lower()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # --- Simple parsing from query ---
        # Example query: "Give me a list of homes in Goodland with min price 500000"
        city_filter = "goodland"
        min_price = 0
        if "min price" in query:
            parts = query.split("min price")
            try:
                min_price = int(''.join(filter(str.isdigit, parts[1])))
            except:
                min_price = 0

        # --- Filter dataset ---
        filtered = goodland_df.copy()
        # If your CSV has city info, you could filter by it; here we assume all rows are Goodland
        filtered = filtered[filtered["Estimated_Price"] >= min_price]

        # --- Preview for UI ---
        preview_data = filtered.head(5).to_dict(orient="records")

        # Store for CSV export
        export_data_store["current_search"] = filtered.to_dict(orient="records")

        return jsonify({
            "preview": preview_data,
            "preview_count": len(preview_data),
            "total_count": len(filtered)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_csv():
    """
    Downloads the current search results as CSV
    """
    data = export_data_store.get("current_search", [])
    output = io.StringIO()
    if data:
        writer = pd.DataFrame(data).to_csv(output, index=False)
    else:
        output.write("Address,Latitude,Longitude,Estimated_Price,Distance_from_Landfall\n")
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        download_name="goodland_addresses.csv",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
