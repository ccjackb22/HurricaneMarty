from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import save_goodland_data  # Your script that handles CSV export
import openai
import os

app = Flask(__name__)
CORS(app)

# Make sure your OpenAI API key is set in Render environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "HurricaneMarty API is running!"

# AI Chat endpoint
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt.strip():
        return jsonify({"answer": "Please provide text to summarize."})

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300
        )
        answer = response.choices[0].text.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)})

# Export Goodland CSV endpoint
@app.route("/export_goodland", methods=["GET"])
def export_goodland():
    try:
        csv_path = save_goodland_data.save_goodland_csv()
        return send_file(csv_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
