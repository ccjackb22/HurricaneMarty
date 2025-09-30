from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # <- renders your HTML

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
