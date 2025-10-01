from flask import Flask, render_template, jsonify, send_file
import requests
import io
import json

app = Flask(__name__)

# Map dataset names to Google Drive download links
DATASETS = {
    "Manatee Addresses": "https://drive.google.com/uc?export=download&id=1y63F4l4XDc9s2ZkQbS3Av9ECoN_E3kGE",
    "Manatee Buildings": "https://drive.google.com/uc?export=download&id=1PpOBVFRWbpKACtahpg6nt6c7L7aJ3qEK",
    "Sarasota Addresses 1": "https://drive.google.com/uc?export=download&id=1CXzVpetX9lfp-3NDpPUmfsaKGD-QxsmR",
    "Sarasota Addresses 2": "https://drive.google.com/uc?export=download&id=1RvwlfeQFyAF4xrxSGiFEY5E2Luu3m6b-"
}

def fetch_data(name):
    url = DATASETS.get(name)
    if not url:
        return []
    res = requests.get(url)
    features = []
    for line in res.text.strip().splitlines():
        try:
            features.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return features

@app.route("/")
def index():
    return render_template("index.html", datasets=list(DATASETS.keys()))

@app.route("/preview/<dataset>")
def preview(dataset):
    data = fetch_data(dataset)
    return jsonify(data[:10])  # first 10 rows

@app.route("/download/<dataset>")
def download(dataset):
    data = fetch_data(dataset)
    json_bytes = io.BytesIO("\n".join(json.dumps(f) for f in data).encode("utf-8"))
    return send_file(json_bytes, mimetype="application/json", as_attachment=True, download_name=f"{dataset}.json")

if __name__ == "__main__":
    app.run(debug=True)
