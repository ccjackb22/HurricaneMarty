import pandas as pd
import os

# Make sure you have a "data" folder
os.makedirs("data", exist_ok=True)

def save_goodland_csv():
    """
    Reads your Goodland data and saves it as a CSV.
    Returns the path to the saved CSV.
    """

    # Example: If you have a JSON or CSV of addresses
    # Here, we'll create a simple dummy dataset for demonstration
    data = [
        {"Address": "123 Main St", "City": "Goodland", "State": "FL", "ZIP": "34140"},
        {"Address": "456 Oak Ave", "City": "Goodland", "State": "FL", "ZIP": "34140"},
        {"Address": "789 Pine Rd", "City": "Goodland", "State": "FL", "ZIP": "34140"}
    ]

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Save CSV
    csv_path = os.path.join("data", "goodland_addresses.csv")
    df.to_csv(csv_path, index=False)

    return csv_path

# Optional: run directly to test
if __name__ == "__main__":
    path = save_goodland_csv()
    print(f"CSV saved at: {path}")
