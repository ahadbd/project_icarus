import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import threading
import time
import random
import winsound
from datetime import datetime, timedelta
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import our new data module
import icarus_data as data

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "stretch_log.csv")

# Color Palette (Nord Theme inspired)
BG_COLOR = "#2E3440"       # Dark Grey/Blue
FG_COLOR = "#ECEFF4"       # Off-White
ACCENT_COLOR = "#88C0D0"   # Frosty Blue
SUCCESS_COLOR = "#A3BE8C"  # Green
WARNING_COLOR = "#BF616A"  # Red
BUTTON_BG = "#4C566A"      # Lighter Grey
BUTTON_ACTIVE = "#5E81AC"  # Blueish
HIGHLIGHT_COLOR = "#EBCB8B" # Yellow/Gold for XP

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Icarus - Health Command Center")
        self.root.geometry("1100x800")
        self.root.configure(bg=BG_COLOR)

        # State
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Variables
        self.interval_minutes = tk.IntVar(value=30)
        self.quiet_start = tk.StringVar(value="22:00")
        self.quiet_end = tk.StringVar(value="08:00")
        self.sound_enabled = tk.BooleanVar(value=True)
        
        # User Stats
        self.total_xp = tk.IntVar(value=0)
        self.current_level = tk.IntVar(value=1)
        self.streak = tk.IntVar(value=0)
        self.rank_title = tk.StringVar(value="Cadet")

        # Style Configuration
        self.setup_styles()
        self.setup_ui()
        self.load_data() # Load initial stats

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        self.style.configure("TButton", 
                             background=BUTTON_BG, 
                             foreground=FG_COLOR, 
                             borderwidth=0, 
                             focuscolor=BUTTON_ACTIVE,
                             font=("Segoe UI", 10, "bold"),
                             padding=6)
        self.style.map("TButton", 
                       background=[('active', BUTTON_ACTIVE)], 
                       foreground=[('active', '#FFFFFF')])
        
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground=ACCENT_COLOR)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 14, "bold"), foreground=HIGHLIGHT_COLOR)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "italic"))
        
        # Notebook (Tabs) Styling
        self.style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BUTTON_BG, foreground=FG_COLOR, padding=[15, 8], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", BG_COLOR)])

        self.style.configure("TLabelframe", background=BG_COLOR, bordercolor=BUTTON_BG)
        self.style.configure("TLabelframe.Label", background=BG_COLOR, foreground=ACCENT_COLOR, font=("Segoe UI", 11, "bold"))

        # Progress Bar
        self.style.configure("Horizontal.TProgressbar", background=SUCCESS_COLOR, troughcolor=BUTTON_BG, bordercolor=BG_COLOR, lightcolor=SUCCESS_COLOR, darkcolor=SUCCESS_COLOR)

    def setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=(25, 25, 25, 10))
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="🚀 PROJECT ICARUS", style="Header.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(header_frame, text="● Systems Offline", style="Status.TLabel", foreground=WARNING_COLOR)
        self.status_label.pack(side=tk.RIGHT)

        # Main Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- TAB 1: DASHBOARD ---
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📊 Mission Control")
        self.setup_dashboard_tab()

        # --- TAB 2: LIBRARY ---
        self.tab_library = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_library, text="📚 Exercise Library")
        self.setup_library_tab()

        # --- TAB 3: SETTINGS ---
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙ Settings")
        self.setup_settings_tab()

    def setup_dashboard_tab(self):
        # Top Section: Pilot Stats
        stats_frame = ttk.LabelFrame(self.tab_dashboard, text="Pilot Profile", padding=20)
        stats_frame.pack(fill=tk.X, pady=(10, 20))

        # Grid layout for stats
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=2) # More space for XP bar
        stats_frame.columnconfigure(2, weight=1)

        # Level & Rank
        f1 = ttk.Frame(stats_frame)
        f1.grid(row=0, column=0, sticky="ew", padx=10)
        ttk.Label(f1, text="RANK", font=("Segoe UI", 8, "bold"), foreground=BUTTON_ACTIVE).pack(anchor="w")
        ttk.Label(f1, textvariable=self.rank_title, style="SubHeader.TLabel").pack(anchor="w")
        ttk.Label(f1, textvariable=self.current_level, font=("Segoe UI", 10)).pack(anchor="w")

        # XP Bar
        f2 = ttk.Frame(stats_frame)
        f2.grid(row=0, column=1, sticky="ew", padx=20)
        ttk.Label(f2, text="EXPERIENCE", font=("Segoe UI", 8, "bold"), foreground=BUTTON_ACTIVE).pack(anchor="w")
        
        self.xp_progress = ttk.Progressbar(f2, style="Horizontal.TProgressbar", mode="determinate", length=300)
        self.xp_progress.pack(fill=tk.X, pady=(5, 5))
        
        self.xp_label = ttk.Label(f2, text="0 / 100 XP", font=("Segoe UI", 9))
        self.xp_label.pack(anchor="e")
        
        # Streak
        f3 = ttk.Frame(stats_frame)
        f3.grid(row=0, column=2, sticky="ew", padx=10)
        ttk.Label(f3, text="CURRENT STREAK", font=("Segoe UI", 8, "bold"), foreground=BUTTON_ACTIVE).pack(anchor="e")
        
        streak_container = ttk.Frame(f3)
        streak_container.pack(anchor="e")
        ttk.Label(streak_container, text="🔥 ", font=("Segoe UI", 14)).pack(side=tk.LEFT)
        ttk.Label(streak_container, textvariable=self.streak, style="SubHeader.TLabel").pack(side=tk.LEFT)
        
        ttk.Label(f3, text="Days", font=("Segoe UI", 10)).pack(anchor="e")

        # Controls
        control_frame = ttk.Frame(self.tab_dashboard)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶ Engage Monitor", command=self.toggle_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="⚡ Quick Stretch", command=self.trigger_reminder).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="✍ Log Manual", command=self.manual_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Refresh", command=self.load_data).pack(side=tk.RIGHT, padx=5)

        # Chart Area
        self.chart_frame = ttk.Frame(self.tab_dashboard)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def setup_library_tab(self):
        container = ttk.Frame(self.tab_library, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate Exercises
        for name, details in data.EXERCISES.items():
            card = ttk.LabelFrame(scrollable_frame, text=f"{name} ({details['category']})", padding=15)
            card.pack(fill=tk.X, pady=10, padx=5)
            
            # Description
            ttk.Label(card, text=details['desc'], wraplength=700, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 20))
            
            # Action Button
            btn = ttk.Button(card, text="▶ Start", command=lambda n=name: self.launch_specific_exercise(n))
            btn.pack(side=tk.RIGHT)

    def launch_specific_exercise(self, name):
        """Triggers the popup for a specific exercise."""
        self.trigger_reminder(force_exercise=name)

    def setup_settings_tab(self):
        container = ttk.Frame(self.tab_settings, padding=30)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Center the settings
        center_frame = ttk.Frame(container)
        center_frame.pack(fill=tk.X)

        # Timer Settings
        g1 = ttk.LabelFrame(center_frame, text="⏱ Timer Configuration", padding=20)
        g1.pack(fill=tk.X, pady=10)
        
        ttk.Label(g1, text="Interval (minutes):").grid(row=0, column=0, padx=10, sticky="w")
        ttk.Entry(g1, textvariable=self.interval_minutes, width=5).grid(row=0, column=1, sticky="w")

        # Quiet Hours
        g2 = ttk.LabelFrame(center_frame, text="🌙 Quiet Hours (24h format HH:MM)", padding=20)
        g2.pack(fill=tk.X, pady=10)

        ttk.Label(g2, text="Start Quiet Time:").grid(row=0, column=0, padx=10, sticky="w")
        ttk.Entry(g2, textvariable=self.quiet_start, width=8).grid(row=0, column=1, sticky="w")
        
        ttk.Label(g2, text="End Quiet Time:").grid(row=1, column=0, padx=10, sticky="w", pady=5)
        ttk.Entry(g2, textvariable=self.quiet_end, width=8).grid(row=1, column=1, sticky="w", pady=5)

        # Audio
        g3 = ttk.LabelFrame(center_frame, text="🔊 Audio Feedback", padding=20)
        g3.pack(fill=tk.X, pady=10)
        ttk.Checkbutton(g3, text="Enable Notification Sounds", variable=self.sound_enabled).pack(anchor="w")

    # --- LOGIC ---

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
            
            # Refresh data after logging
            self.root.after(0, self.load_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write to log: {e}")

    def manual_log(self):
        self.log_stretch(method="Manual")
        messagebox.showinfo("Success", "Mission logged manually, Commander!")

    def load_data(self):
        """Reads CSV, calculates stats, updates chart."""
        if not os.path.exists(LOG_FILE):
            self.update_chart({})
            return

        dates = []
        timestamps = []
        try:
            with open(LOG_FILE, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts_str = row.get("Timestamp")
                    if ts_str:
                        try:
                            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                            dates.append(dt.date())
                            timestamps.append(dt)
                        except ValueError:
                            continue
        except Exception:
            return 
        
        # 1. Update Charts
        date_counts = Counter(dates)
        self.update_chart(date_counts)

        # 2. Update Gamification Stats
        total_stretches = len(timestamps)
        current_xp = total_stretches * data.XP_PER_STRETCH
        self.total_xp.set(current_xp)

        level, progress, needed = data.calculate_level(current_xp)
        self.current_level.set(level)
        self.xp_label.config(text=f"{progress} / {needed} XP")
        
        # Update Progress Bar
        if hasattr(self, 'xp_progress'):
             self.xp_progress['maximum'] = needed
             self.xp_progress['value'] = progress
        
        self.rank_title.set(data.get_rank_title(level))

        # 3. Calculate Streak
        sorted_dates = sorted(list(set(dates)))
        streak = 0
        if sorted_dates:
            today = datetime.now().date()
            if sorted_dates[-1] == today:
                streak = 1
                current_check = today - timedelta(days=1)
                # Check backwards
                for i in range(len(sorted_dates)-2, -1, -1):
                    if sorted_dates[i] == current_check:
                        streak += 1
                        current_check -= timedelta(days=1)
                    else:
                        break
            elif sorted_dates[-1] == today - timedelta(days=1):
                # Streak is still active if we stretched yesterday, just haven't done today yet
                 streak = 1 
                 # Logic for yesterday matches above if needed
                 pass

        self.streak.set(streak)


    def update_chart(self, data_counter):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not data_counter:
            ttk.Label(self.chart_frame, text="No mission data found.\nStart monitoring to begin your journey.", anchor="center").pack(fill=tk.BOTH, expand=True)
            return

        sorted_dates = sorted(data_counter.keys())
        counts = [data_counter[date] for date in sorted_dates]
        labels = [d.strftime("%b %d") for d in sorted_dates]

        # Use last 7 days only for clarity if list is long
        if len(labels) > 7:
            labels = labels[-7:]
            counts = counts[-7:]

        # Matplotlib
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        bars = ax.bar(labels, counts, color=ACCENT_COLOR, alpha=0.8, width=0.5)
        
        # Labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}', ha='center', va='bottom', color=FG_COLOR, fontsize=8)

        ax.set_title("Recent Activity", color=FG_COLOR, fontsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(BUTTON_BG)
        ax.tick_params(axis='x', colors=FG_COLOR)
        ax.tick_params(axis='y', colors=BG_COLOR) # Hide Y axis ticks
        ax.set_yticks([]) # Hide Y axis values

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # --- MONITORING ---

    def toggle_monitor(self):
        if not self.is_monitoring:
            try:
                if self.interval_minutes.get() <= 0: raise ValueError
                self.is_monitoring = True
                self.start_btn.config(text="⏹ Disengage Monitor")
                self.status_label.config(text="● Systems Active", foreground=SUCCESS_COLOR)
                
                self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
                self.monitor_thread.start()
            except ValueError:
                messagebox.showerror("Error", "Invalid interval settings.")
        else:
            self.is_monitoring = False
            self.start_btn.config(text="▶ Engage Monitor")
            self.status_label.config(text="● Systems Offline", foreground=WARNING_COLOR)

    def is_quiet_time(self):
        try:
            now = datetime.now().time()
            start = datetime.strptime(self.quiet_start.get(), "%H:%M").time()
            end = datetime.strptime(self.quiet_end.get(), "%H:%M").time()
            
            if start < end:
                return start <= now <= end
            else: # Crosses midnight
                return now >= start or now <= end
        except ValueError:
            return False # Invalid time format, ignore quiet time

    def monitor_loop(self):
        while self.is_monitoring:
            time.sleep(self.interval_minutes.get() * 60)
            
            if self.is_monitoring and not self.is_quiet_time():
                self.root.after(0, self.trigger_reminder)

    def trigger_reminder(self, force_exercise=None):
        # Sound
        if self.sound_enabled.get():
            try:
                winsound.Beep(1000, 200) # Frequency 1000Hz, Duration 200ms
            except:
                pass 

        if force_exercise:
             ex_name = force_exercise
             ex_data = data.EXERCISES[force_exercise]
        else:
            # Pick random exercise
            ex_name, ex_data = random.choice(list(data.EXERCISES.items()))
        
        quote = random.choice(data.MOTIVATIONAL_QUOTES)

        # Custom Popup Window
        popup = tk.Toplevel(self.root)
        popup.title("Incoming Transmission")
        popup.geometry("450x300")
        popup.configure(bg=BG_COLOR)
        popup.attributes("-topmost", True)
        
        # Center popup
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 150
        popup.geometry(f"+{x}+{y}")

        ttk.Label(popup, text="⚠ GRAVITY ALERT ⚠", font=("Segoe UI", 14, "bold"), foreground=WARNING_COLOR, background=BG_COLOR).pack(pady=(20, 10))
        
        ttk.Label(popup, text=f"Recommended Action: {ex_name}", font=("Segoe UI", 12, "bold"), foreground=ACCENT_COLOR, background=BG_COLOR).pack(pady=5)
        ttk.Label(popup, text=ex_data['desc'], wraplength=380, justify="center", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10)).pack(pady=10)
        
        ttk.Label(popup, text=f'"{quote}"', font=("Segoe UI", 9, "italic"), foreground=BUTTON_ACTIVE, background=BG_COLOR).pack(pady=15)

        def confirm():
            self.log_stretch()
            popup.destroy()

        btn = ttk.Button(popup, text="✅ Mission Complete (Log It)", command=confirm)
        btn.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitorApp(root)
    root.mainloop()
