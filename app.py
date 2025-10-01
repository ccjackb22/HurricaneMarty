import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Load Goodland data (just once, at startup)
GOODLAND_DATA = []
try:
    with open("data/goodland.json", "r") as f:
        GOODLAND_DATA = json.load(f)
except Exception as e:
    print("⚠️ Could not load Goodland data:", e)


@app.route("/")
def home():
    return "HurricaneMarty API is running!"


@app.route("/ask", methods=["POST"])
def ask():
    """Main chat endpoint."""
    data = request.json
    user_message = data.get("message", "").lower()

    # If user asks for addresses in Goodland
    if "address" in user_message and "goodland" in user_message:
        if not GOODLAND_DATA:
            return jsonify({"reply": "Sorry, no data available for Goodland right now."})
        addresses = [f"{row['address']}, {row['city']}, {row['state']} {row['zip']}"
                     for row in GOODLAND_DATA]
        reply = "Here are the residential addresses I have for Goodland, FL:\n" + "\n".join(addresses)
        return jsonify({"reply": reply})

    # If they ask about addresses somewhere else
    if "address" in user_message:
        return jsonify({"reply": "Right now I only have residential address data for Goodland, Florida."})

    # Otherwise, fall back to OpenAI chat
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Hurricane Marty, a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )
        reply = completion.choices[0].message["content"].strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {e}"}), 500


@app.route("/data/goodland")
def get_goodland_data():
    """Return Goodland JSON directly."""
    return jsonify(GOODLAND_DATA)


@app.route("/download/goodland")
def download_goodland_csv():
    """Generate CSV download of Goodland addresses (no pandas)."""
    from io import StringIO
    import csv
    from flask import Response

    if not GOODLAND_DATA:
        return "No Goodland data available", 404

    # Create CSV in-memory
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["address", "city", "state", "zip"])
    writer.writeheader()
    writer.writerows(GOODLAND_DATA)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=goodland_addresses.csv"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
