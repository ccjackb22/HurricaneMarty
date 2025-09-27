import os
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- OpenAI API ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Use OpenAI to parse the query
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

        # Parse the JSON output
        import json
        structured_data = json.loads(structured_text)

        return jsonify({
            "parsed_query": structured_data,
            "original_query": query
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
