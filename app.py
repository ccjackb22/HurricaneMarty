from flask import Flask, render_template, request, send_file
import csv
import datetime
import googlemaps
import os

app = Flask(__name__)
# Hardcoded Google API key
gmaps = googlemaps.Client(key='AIzaSyDD4r0XTtELhEw2kStXTEVTXS2eUR1xr8A')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('query')
        results = gmaps.places(query=query, location='Cleveland, OH', radius=5000)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'search_{query.replace(" ", "_")}_{timestamp}.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Address'])
            for place in results['results']:
                writer.writerow([place['name'], place['formatted_address']])
        return render_template('index.html', message=f'CSV saved. <a href="/download/{csv_file}">Download</a>')
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))  # Use Heroku's PORT or 8080 locally
    app.run(host='0.0.0.0', port=port)