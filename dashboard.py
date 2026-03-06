import csv
import os
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Configuration
LOG_FILE = "stretch_log.csv"

def get_stretch_counts():
    """Reads the log file and returns a count of stretches per day."""
    if not os.path.exists(LOG_FILE):
        print(f"Log file '{LOG_FILE}' not found. Please log some stretches first!")
        return {}

    dates = []
    try:
        with open(LOG_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp_str = row.get("Timestamp")
                if timestamp_str:
                    # Convert full timestamp string into just a date string (YYYY-MM-DD)
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    dates.append(dt.strftime("%Y-%m-%d"))
    except (csv.Error, ValueError) as e:
        print(f"Error reading log file: {e}")
        return {}

    # Returns a dictionary: {date: count}
    return Counter(dates)

def display_dashboard():
    """Generates and shows a bar chart of stretches per day."""
    stretch_counts = get_stretch_counts()
    
    if not stretch_counts:
        return

    # Sort dates to ensure the chart is in chronological order
    sorted_dates = sorted(stretch_counts.keys())
    counts = [stretch_counts[date] for date in sorted_dates]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_dates, counts, color='skyblue', edgecolor='black')
    
    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Stretches')
    plt.title('Daily Stretches (Project Icarus - Antigravity Health Monitor)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Automatically adjust layout to avoid overlapping text
    plt.tight_layout()
    
    print("Displaying dashboard...")
    plt.show()

if __name__ == "__main__":
    display_dashboard()
