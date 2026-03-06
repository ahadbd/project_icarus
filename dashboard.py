import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import threading
import time
from datetime import datetime
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuration
LOG_FILE = "stretch_log.csv"

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Icarus - Unified Health Monitor")
        self.root.geometry("900x700")

        self.is_monitoring = False
        self.monitor_thread = None
        self.interval_minutes = tk.IntVar(value=30)

        self.setup_ui()
        self.update_chart()

    def setup_ui(self):
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Interval Setting
        ttk.Label(control_frame, text="Reminder Interval (min):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, textvariable=self.interval_minutes, width=5).pack(side=tk.LEFT, padx=5)

        # Buttons
        self.start_btn = ttk.Button(control_frame, text="Start Monitor", command=self.toggle_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Manual Log", command=self.manual_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh Chart", command=self.update_chart).pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", foreground="red")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Chart Area
        self.chart_frame = tk.Frame(self.root)
        self.chart_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log_stretch(self, method="Automatic"):
        """Logs a stretch to the CSV file."""
        file_exists = os.path.isfile(LOG_FILE)
        now = datetime.now()
        
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Method"])
            writer.writerow([now.strftime("%Y-%m-%d %H:%M:%S"), method])
        
        # Refresh chart after logging
        self.root.after(0, self.update_chart)

    def manual_log(self):
        self.log_stretch(method="Manual")
        messagebox.showinfo("Success", "Stretch logged manually!")

    def toggle_monitor(self):
        if not self.is_monitoring:
            try:
                # Validate interval
                if self.interval_minutes.get() <= 0:
                    raise ValueError
                
                self.is_monitoring = True
                self.start_btn.config(text="Stop Monitor")
                self.status_label.config(text="Status: Monitoring", foreground="green")
                
                self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
                self.monitor_thread.start()
            except (ValueError, tk.TclError):
                messagebox.showerror("Error", "Please enter a valid number of minutes.")
        else:
            self.is_monitoring = False
            self.start_btn.config(text="Start Monitor")
            self.status_label.config(text="Status: Stopped", foreground="red")

    def monitor_loop(self):
        """Background loop for reminders."""
        while self.is_monitoring:
            # Wait for the interval (converting minutes to seconds)
            time.sleep(self.interval_minutes.get() * 60)
            
            if self.is_monitoring:
                # Use after() to safely trigger messagebox from main thread
                self.root.after(0, self.show_reminder)

    def show_reminder(self):
        if messagebox.showinfo("Health Reminder", "Time to stretch! Click OK to log your progress."):
            self.log_stretch(method="Automatic")

    def get_stretch_data(self):
        if not os.path.exists(LOG_FILE):
            return {}, {}

        dates = []
        try:
            with open(LOG_FILE, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts = row.get("Timestamp")
                    if ts:
                        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        dates.append(dt.strftime("%Y-%m-%d"))
        except Exception:
            return {}, {}
        
        return Counter(dates)

    def update_chart(self):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        data = self.get_stretch_data()
        if not data:
            ttk.Label(self.chart_frame, text="No data to display yet. Log a stretch!").pack(pady=50)
            return

        sorted_dates = sorted(data.keys())
        counts = [data[date] for date in sorted_dates]

        # Create Matplotlib Figure
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(sorted_dates, counts, color='skyblue', edgecolor='black')
        ax.set_title("Stretches per Day")
        ax.set_ylabel("Count")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        fig.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitorApp(root)
    root.mainloop()
