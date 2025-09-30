import csv
import os

def save_csv():
    data = [
        {"address": "123 Main St", "city": "Goodland", "state": "FL", "zip": "34140"},
        {"address": "456 Oak Ave", "city": "Goodland", "state": "FL", "zip": "34140"},
        # Add more addresses here
    ]
    
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "goodland_addresses.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return csv_path
