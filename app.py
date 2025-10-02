from flask import Flask, render_template, send_from_directory, jsonify
import os
import json

app = Flask(__name__)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
GEOJSON_FILENAME = 'test_region.geojson'  # small file that worked yesterday

def load_geojson():
    path = os.path.join(DATA_FOLDER, GEOJSON_FILENAME)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

geojson_data = load_geojson()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(geojson_data)

@app.route('/download')
def download():
    return send_from_directory(DATA_FOLDER, GEOJSON_FILENAME, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
