import json
import pandas as pd
import os

# Load your Goodland GeoJSON
geojson_path = os.path.join("data", "goodland.geojson")
with open(geojson_path, "r") as f:
    data = json.load(f)

# Extract addresses
addresses = []
for feature in data.get("features", []):
    props = feature.get("properties", {})
    addr = props.get("address")  # adjust if needed
    if addr:
        addresses.append(addr)

# Save to CSV
csv_path = "goodland_addresses.csv"
df = pd.DataFrame(addresses, columns=["Address"])
df.to_csv(csv_path, index=False)

# Print a simple summary
print(f"Exported {len(addresses)} addresses to {csv_path}")
