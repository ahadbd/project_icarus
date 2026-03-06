import tkinter as tk
from tkinter import messagebox
import csv
import os
from datetime import datetime
import time

# Configuration
LOG_FILE = "stretch_log.csv"
REMINDER_INTERVAL_SECONDS = 30 * 60  # 30 minutes

def log_stretch():
    """Appends the current timestamp to the CSV log file."""
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        # Write header if file is new
        if not file_exists:
            writer.writerow(["Timestamp"])
        
        # Log current time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([now])
        print(f"Logged stretch at: {now}")

def show_reminder():
    """Displays a tkinter popup reminder."""
    # Initialize a hidden root window for the messagebox
    root = tk.Tk()
    root.withdraw() 
    root.attributes("-topmost", True)
    
    # Show the popup
    messagebox.showinfo("Health Reminder", "Time to stretch! Click OK to log your progress.")
    
    # Log the stretch after user acknowledges
    log_stretch()
    
    # Clean up the hidden window
    root.destroy()

def main():
    """Main loop to trigger reminders every 30 minutes."""
    print(f"Icarus Health Monitor started. Reminders every {REMINDER_INTERVAL_SECONDS // 60} minutes.")
    
    try:
        while True:
            # Wait for the interval
            time.sleep(REMINDER_INTERVAL_SECONDS)
            show_reminder()
    except KeyboardInterrupt:
        print("\nMonitor stopped. Stay healthy!")

if __name__ == "__main__":
    main()
