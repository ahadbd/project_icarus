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
import matplotlib.dates as mdates

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "stretch_log.csv")

# Color Palette (Dark Theme)
BG_COLOR = "#2E3440"       # Dark Grey/Blue
FG_COLOR = "#ECEFF4"       # Off-White
ACCENT_COLOR = "#88C0D0"   # Frosty Blue
SUCCESS_COLOR = "#A3BE8C"  # Green
WARNING_COLOR = "#BF616A"  # Red
BUTTON_BG = "#4C566A"      # Lighter Grey
BUTTON_ACTIVE = "#5E81AC"  # Blueish

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Icarus - Health Dashboard")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG_COLOR)

        self.is_monitoring = False
        self.monitor_thread = None
        self.interval_minutes = tk.IntVar(value=30)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam' allows more customization than 'vista'
        
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        self.style.configure("TButton", 
                             background=BUTTON_BG, 
                             foreground=FG_COLOR, 
                             borderwidth=0, 
                             focuscolor=BUTTON_ACTIVE,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", 
                       background=[('active', BUTTON_ACTIVE)], 
                       foreground=[('active', '#FFFFFF')])
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_COLOR)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "italic"))
        self.style.configure("TLabelframe", background=BG_COLOR, bordercolor=BUTTON_BG)
        self.style.configure("TLabelframe.Label", background=BG_COLOR, foreground=ACCENT_COLOR, font=("Segoe UI", 11, "bold"))

        self.setup_ui()
        self.update_chart()

    def setup_ui(self):
        # Main Container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="PROJECT ICARUS", style="Header.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(header_frame, text="● Monitor Stopped", style="Status.TLabel", foreground=WARNING_COLOR)
        self.status_label.pack(side=tk.RIGHT)

        # Control Panel
        control_frame = ttk.LabelFrame(main_container, text="Controls", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 20))

        # Interval Setting
        interval_frame = ttk.Frame(control_frame)
        interval_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(interval_frame, text="Interval (min):").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(interval_frame, textvariable=self.interval_minutes, width=5, font=("Segoe UI", 10))
        entry.pack(side=tk.LEFT)

        # Action Buttons
        self.start_btn = ttk.Button(control_frame, text="Start Monitor", command=self.toggle_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Log Manual Stretch", command=self.manual_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh Data", command=self.update_chart).pack(side=tk.RIGHT, padx=5)

        # Chart Area
        self.chart_frame = ttk.Frame(main_container)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

    def log_stretch(self, method="Automatic"):
        """Logs a stretch to the CSV file."""
        file_exists = os.path.isfile(LOG_FILE)
        now = datetime.now()
        
        try:
            with open(LOG_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Method"])
                writer.writerow([now.strftime("%Y-%m-%d %H:%M:%S"), method])
            
            # Refresh chart after logging
            self.root.after(0, self.update_chart)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write to log: {e}")

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
                self.status_label.config(text="● Monitoring Active", foreground=SUCCESS_COLOR)
                
                self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
                self.monitor_thread.start()
            except (ValueError, tk.TclError):
                messagebox.showerror("Error", "Please enter a valid number of minutes.")
        else:
            self.is_monitoring = False
            self.start_btn.config(text="Start Monitor")
            self.status_label.config(text="● Monitor Stopped", foreground=WARNING_COLOR)

    def monitor_loop(self):
        """Background loop for reminders."""
        while self.is_monitoring:
            # Wait for the interval (converting minutes to seconds)
            time.sleep(self.interval_minutes.get() * 60)
            
            if self.is_monitoring:
                # Use after() to safely trigger messagebox from main thread
                self.root.after(0, self.show_reminder)

    def show_reminder(self):
        # We need a custom dialog to match the theme ideally, but standard messagebox is safer for blocking
        if messagebox.showinfo("Time to Stretch!", "Take a break and stretch! Click OK to log it."):
            self.log_stretch(method="Automatic")

    def get_stretch_data(self):
        if not os.path.exists(LOG_FILE):
            return {}

        dates = []
        try:
            with open(LOG_FILE, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts = row.get("Timestamp")
                    if ts:
                        try:
                            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            dates.append(dt.date())
                        except ValueError:
                            continue # Skip malformed dates
        except Exception:
            return {}
        
        return Counter(dates)

    def update_chart(self):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        data = self.get_stretch_data()
        
        if not data:
            no_data_label = ttk.Label(self.chart_frame, text="No stretch data recorded yet.\nStart the monitor or log manually!", anchor="center", justify="center")
            no_data_label.pack(fill=tk.BOTH, expand=True)
            return

        sorted_dates = sorted(data.keys())
        counts = [data[date] for date in sorted_dates]
        
        # Prepare date labels for display
        date_labels = [d.strftime("%b %d") for d in sorted_dates]

        # Create Matplotlib Figure with Dark Theme
        plt.style.use('dark_background')
        
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        # Create bars
        bars = ax.bar(date_labels, counts, color=ACCENT_COLOR, edgecolor=BG_COLOR, linewidth=0.5, alpha=0.9, width=0.6)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}',
                    ha='center', va='bottom', color=FG_COLOR, fontsize=9, fontweight='bold')

        # Styling
        ax.set_title("Daily Activity", color=FG_COLOR, fontsize=14, pad=20, fontname="Segoe UI")
        ax.set_ylabel("Stretches", color=FG_COLOR, fontsize=10)
        
        # Customizing Grid and Spines
        ax.grid(axis='y', color=BUTTON_BG, linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_axisbelow(True)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['bottom'].set_color(BUTTON_BG)

        # Tick styling
        ax.tick_params(axis='x', colors=FG_COLOR, rotation=0)
        ax.tick_params(axis='y', colors=FG_COLOR)
        
        # Adjust layout
        fig.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg=BG_COLOR)
        canvas_widget.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    # Attempt to set icon if available, otherwise skip
    # try: root.iconbitmap("icon.ico")
    # except: pass
    
    app = HealthMonitorApp(root)
    root.mainloop()
