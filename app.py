import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import pandas as pd

app = Flask(__name__)
CORS(app)

# Pull secrets from Render environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

@app.route("/")
def home():
    return "Hello! HurricaneMarty is running safely."

# Example route using Google API key
@app.route("/example")
def example():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Google API key not set"}), 500

    # Example: placeholder for your Google API call logic
    return jsonify({"message": "Google API key loaded successfully!"})

# Example route to test OpenAI usage
@app.route("/chat", methods=["POST"])
def chat():
    if not OPENAI_API_KEY:
        return jsonify({"error": "OpenAI API key not set"}), 500

    data = request.json
    user_prompt = data.get("prompt", "")

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_prompt}]
        )
        answer = response.choices[0].message["content"]
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
