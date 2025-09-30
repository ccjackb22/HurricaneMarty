from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import openai
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Pull keys from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
openai.api_key = OPENAI_API_KEY

# Example route for health check
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "HurricaneMarty API is running"})

# Example route using OpenAI API
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )

        answer = response.choices[0].text.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example route to read a CSV or GeoJSON using pandas
@app.route("/data", methods=["GET"])
def data():
    try:
        # Example: Load a CSV/GeoJSON from a local file
        file_path = os.path.join(os.getcwd(), "data.csv")  # replace with your file
        if not os.path.exists(file_path):
            return jsonify({"error": "Data file not found"}), 404

        df = pd.read_csv(file_path)  # works with default pandas
        return jsonify(df.head(10).to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
