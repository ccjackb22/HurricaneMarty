from flask import Flask, send_file
import save_goodland_data  # your script

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    from flask import request, jsonify
    data = request.json
    prompt = data.get("prompt", "")
    # For now, just echo the prompt
    return jsonify({"answer": f"Received: {prompt}"})

@app.route("/export_goodland", methods=["GET"])
def export_goodland():
    # Generate CSV
    csv_path = save_goodland_data.save_csv()  # Make sure your function returns the file path
    return send_file(csv_path, as_attachment=True, download_name="goodland_addresses.csv")

if __name__ == "__main__":
    app.run()
