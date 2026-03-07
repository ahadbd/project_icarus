import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import threading
import time
import random
import winsound
import json
from datetime import datetime, timedelta
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Core Data & Logic
import icarus_data as data

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "stretch_log.csv")

# Nord Theme Colors
BG_COLOR = "#2E3440"
FG_COLOR = "#ECEFF4"
ACCENT_COLOR = "#88C0D0"
SUCCESS_COLOR = "#A3BE8C"
WARNING_COLOR = "#BF616A"
BUTTON_BG = "#4C566A"
BUTTON_ACTIVE = "#5E81AC"
HIGHLIGHT_COLOR = "#EBCB8B"

class IcarusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Icarus v3.0 - Pro Command Center")
        self.root.geometry("1150x850")
        self.root.configure(bg=BG_COLOR)

        # 1. State & Settings
        self.is_monitoring = False
        self.monitor_thread = None
        self.settings = data.load_settings()
        
        # Pomodoro State
        self.pomodoro_running = False
        self.pomodoro_mode = "Work" # Work or Break
        self.pomo_time_left = self.settings["pomodoro_work"] * 60
        self.pomo_thread = None

        # 2. UI Variables
        self.setup_variables()
        self.setup_styles()
        self.setup_ui()
        
        # 3. Initialization
        self.load_data()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_variables(self):
        # Monitor settings
        self.interval_var = tk.IntVar(value=self.settings["interval"])
        self.q_start_var = tk.StringVar(value=self.settings["quiet_start"])
        self.q_end_var = tk.StringVar(value=self.settings["quiet_end"])
        self.sound_var = tk.BooleanVar(value=self.settings["sound_enabled"])
        self.toast_var = tk.BooleanVar(value=self.settings["notifications_enabled"])
        
        # Pomodoro vars
        self.pomo_work_var = tk.IntVar(value=self.settings["pomodoro_work"])
        self.pomo_break_var = tk.IntVar(value=self.settings["pomodoro_break"])
        self.pomo_timer_display = tk.StringVar(value="25:00")
        self.pomo_status_text = tk.StringVar(value="Ready to Focus")

        # Stats vars
        self.rank_title = tk.StringVar(value="Cadet")
        self.current_level = tk.IntVar(value=1)
        self.streak = tk.IntVar(value=0)
        self.total_stretches = 0

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 22, "bold"), foreground=ACCENT_COLOR)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 15, "bold"), foreground=HIGHLIGHT_COLOR)
        
        style.configure("TButton", background=BUTTON_BG, foreground=FG_COLOR, borderwidth=0, padding=8, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[('active', BUTTON_ACTIVE)])
        
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=BUTTON_BG, foreground=FG_COLOR, padding=[20, 10], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", BG_COLOR)])

        style.configure("Horizontal.TProgressbar", background=SUCCESS_COLOR, troughcolor=BUTTON_BG)

    def setup_ui(self):
        # Global Header
        header = ttk.Frame(self.root, padding=(30, 20, 30, 0))
        header.pack(fill=tk.X)
        ttk.Label(header, text="🚀 PROJECT ICARUS PRO", style="Header.TLabel").pack(side=tk.LEFT)
        self.status_lbl = ttk.Label(header, text="● Systems Ready", font=("Segoe UI", 10, "italic"), foreground=SUCCESS_COLOR)
        self.status_lbl.pack(side=tk.RIGHT)

        # Tabs
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.setup_dashboard_tab()
        self.setup_pomodoro_tab()
        self.setup_achievements_tab()
        self.setup_library_tab()
        self.setup_settings_tab()

    def setup_dashboard_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="📊 Mission Control")

        # Profile Card
        profile = ttk.LabelFrame(tab, text="Pilot Profile", padding=20)
        profile.pack(fill=tk.X, pady=10)
        profile.columnconfigure((0,1,2), weight=1)

        # Rank
        f1 = ttk.Frame(profile)
        f1.grid(row=0, column=0, sticky="ew")
        ttk.Label(f1, text="CURRENT RANK", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        ttk.Label(f1, textvariable=self.rank_title, style="SubHeader.TLabel").pack(anchor="w")
        ttk.Label(f1, text="Level ").pack(side=tk.LEFT)
        ttk.Label(f1, textvariable=self.current_level).pack(side=tk.LEFT)

        # XP
        f2 = ttk.Frame(profile)
        f2.grid(row=0, column=1, sticky="ew", padx=20)
        ttk.Label(f2, text="EXPERIENCE PROGRESS", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.xp_bar = ttk.Progressbar(f2, style="Horizontal.TProgressbar", length=200)
        self.xp_bar.pack(fill=tk.X, pady=5)
        self.xp_lbl = ttk.Label(f2, text="0 / 100 XP", font=("Segoe UI", 9))
        self.xp_lbl.pack(anchor="e")

        # Streak
        f3 = ttk.Frame(profile)
        f3.grid(row=0, column=2, sticky="ew")
        ttk.Label(f3, text="DAILY STREAK", font=("Segoe UI", 8, "bold")).pack(anchor="e")
        s_cont = ttk.Frame(f3)
        s_cont.pack(anchor="e")
        ttk.Label(s_cont, text="🔥", font=("Segoe UI", 18)).pack(side=tk.LEFT)
        ttk.Label(s_cont, textvariable=self.streak, style="SubHeader.TLabel").pack(side=tk.LEFT)

        # Controls
        ctrls = ttk.Frame(tab, padding=10)
        ctrls.pack(fill=tk.X)
        self.mon_btn = ttk.Button(ctrls, text="▶ Engage Monitor", command=self.toggle_monitor)
        self.mon_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrls, text="⚡ Quick Stretch", command=self.trigger_reminder).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrls, text="✍ Manual Log", command=self.manual_log).pack(side=tk.LEFT, padx=5)

        # Analytics Area (Two columns: Bar chart and Pie chart)
        stats_area = ttk.Frame(tab)
        stats_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.bar_frame = ttk.Frame(stats_area)
        self.bar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.pie_frame = ttk.Frame(stats_area)
        self.pie_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_pomodoro_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="🍅 Pomodoro Focus")

        container = ttk.Frame(tab, padding=50)
        container.pack(expand=True)

        ttk.Label(container, textvariable=self.pomo_status_text, font=("Segoe UI", 14, "italic"), foreground=ACCENT_COLOR).pack()
        ttk.Label(container, textvariable=self.pomo_timer_display, font=("Segoe UI", 72, "bold")).pack(pady=20)

        btn_f = ttk.Frame(container)
        btn_f.pack(pady=20)
        self.pomo_btn = ttk.Button(btn_f, text="START FOCUS", command=self.toggle_pomodoro)
        self.pomo_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_f, text="RESET", command=self.reset_pomodoro).pack(side=tk.LEFT, padx=10)

        settings_f = ttk.LabelFrame(container, text="Timer Settings", padding=20)
        settings_f.pack(fill=tk.X, pady=20)
        
        ttk.Label(settings_f, text="Work (min):").grid(row=0, column=0, padx=5)
        ttk.Entry(settings_f, textvariable=self.pomo_work_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(settings_f, text="Break (min):").grid(row=0, column=2, padx=5)
        ttk.Entry(settings_f, textvariable=self.pomo_break_var, width=5).grid(row=0, column=3, padx=5)

    def setup_achievements_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="🏆 Achievements")
        
        canvas = tk.Canvas(tab, bg=BG_COLOR, highlightthickness=0)
        scroll = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        self.ach_container = ttk.Frame(canvas)

        self.ach_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.ach_container, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scroll.pack(side="right", fill="y")

    def setup_library_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="📚 Exercises")
        # Same scrollable logic as library v2
        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for name, d in data.EXERCISES.items():
            card = ttk.LabelFrame(scrollable_frame, text=f"{name} [{d['cat']}]", padding=15)
            card.pack(fill=tk.X, pady=5, padx=5)
            ttk.Label(card, text=d['desc'], wraplength=700).pack(side=tk.LEFT)
            ttk.Button(card, text="▶ Start", command=lambda n=name: self.trigger_reminder(n)).pack(side=tk.RIGHT)

    def setup_settings_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="⚙ Settings")
        
        c = ttk.Frame(tab, padding=30)
        c.pack(fill=tk.BOTH)

        # Monitor Settings
        m_f = ttk.LabelFrame(c, text="Mission Parameters", padding=20)
        m_f.pack(fill=tk.X, pady=10)
        
        ttk.Label(m_f, text="Interval (minutes):").grid(row=0, column=0, sticky="w")
        ttk.Entry(m_f, textvariable=self.interval_var, width=5).grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(m_f, text="Quiet Time (Start):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(m_f, textvariable=self.q_start_var, width=8).grid(row=1, column=1, sticky="w", padx=10)
        
        ttk.Label(m_f, text="Quiet Time (End):").grid(row=2, column=0, sticky="w")
        ttk.Entry(m_f, textvariable=self.q_end_var, width=8).grid(row=2, column=1, sticky="w", padx=10)

        # Features
        f_f = ttk.LabelFrame(c, text="System Feedback", padding=20)
        f_f.pack(fill=tk.X, pady=10)
        ttk.Checkbutton(f_f, text="Enable Audio Alerts", variable=self.sound_var).pack(anchor="w")
        ttk.Checkbutton(f_f, text="Enable Desktop Notifications", variable=self.toast_var).pack(anchor="w")

        ttk.Button(c, text="💾 SAVE CONFIGURATION", command=self.save_app_settings).pack(pady=20)

    # --- CORE LOGIC ---

    def save_app_settings(self):
        new_s = {
            "interval": self.interval_var.get(),
            "quiet_start": self.q_start_var.get(),
            "quiet_end": self.q_end_var.get(),
            "sound_enabled": self.sound_var.get(),
            "notifications_enabled": self.toast_var.get(),
            "pomodoro_work": self.pomo_work_var.get(),
            "pomodoro_break": self.pomo_break_var.get()
        }
        data.save_settings(new_s)
        self.settings = new_s
        messagebox.showinfo("Systems", "Configuration saved and encrypted.")

    def log_stretch(self, category="General", method="Automatic"):
        exists = os.path.isfile(LOG_FILE)
        now = datetime.now()
        try:
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                if not exists:
                    writer.writerow(["Timestamp", "Category", "Method"])
                writer.writerow([now.strftime("%Y-%m-%d %H:%M:%S"), category, method])
            self.load_data()
        except Exception as e:
            print(f"Log Error: {e}")

    def load_data(self):
        if not os.path.exists(LOG_FILE):
            self.update_analytics({}, {})
            return

        dates = []
        cats = []
        timestamps = []
        
        try:
            with open(LOG_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts = row.get("Timestamp")
                    cat = row.get("Category", "General")
                    if ts:
                        try:
                            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            dates.append(dt.date())
                            cats.append(cat)
                            timestamps.append(dt)
                        except: continue
        except: return

        # Update Analytics
        self.total_stretches = len(timestamps)
        self.update_analytics(Counter(dates), Counter(cats))
        
        # Update Stats
        xp = self.total_stretches * data.XP_PER_STRETCH
        lvl, prog, need = data.calculate_level(xp)
        self.current_level.set(lvl)
        self.rank_title.set(data.get_rank_title(lvl))
        self.xp_bar['maximum'] = need
        self.xp_bar['value'] = prog
        self.xp_lbl.config(text=f"{prog} / {need} XP")

        # Streak
        sd = sorted(list(set(dates)))
        streak = 0
        if sd:
            today = datetime.now().date()
            if sd[-1] == today:
                streak = 1
                curr = today - timedelta(days=1)
                for i in range(len(sd)-2, -1, -1):
                    if sd[i] == curr:
                        streak += 1
                        curr -= timedelta(days=1)
                    else: break
            elif sd[-1] == today - timedelta(days=1):
                streak = 1 # Simplified check
        self.streak.set(streak)
        
        self.update_achievements(timestamps, cats, streak)

    def update_analytics(self, date_counts, cat_counts):
        # 1. Bar Chart
        for w in self.bar_frame.winfo_children(): w.destroy()
        if date_counts:
            sorted_d = sorted(date_counts.keys())[-7:]
            labels = [d.strftime("%b %d") for d in sorted_d]
            counts = [date_counts[d] for d in sorted_d]
            
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(5, 3.5))
            fig.patch.set_facecolor(BG_COLOR)
            ax.set_facecolor(BG_COLOR)
            ax.bar(labels, counts, color=ACCENT_COLOR, alpha=0.8)
            ax.set_title("Activity (7 Days)", fontsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            
            canv = FigureCanvasTkAgg(fig, master=self.bar_frame)
            canv.draw()
            canv.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 2. Pie Chart
        for w in self.pie_frame.winfo_children(): w.destroy()
        if cat_counts:
            labels = list(cat_counts.keys())
            values = list(cat_counts.values())
            
            fig, ax = plt.subplots(figsize=(4.5, 3.5))
            fig.patch.set_facecolor(BG_COLOR)
            ax.set_facecolor(BG_COLOR)
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=[ACCENT_COLOR, SUCCESS_COLOR, HIGHLIGHT_COLOR, BUTTON_ACTIVE, WARNING_COLOR])
            ax.set_title("Health Balance", fontsize=10)
            fig.tight_layout()
            
            canv = FigureCanvasTkAgg(fig, master=self.pie_frame)
            canv.draw()
            canv.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_achievements(self, timestamps, cats, streak):
        for w in self.ach_container.winfo_children(): w.destroy()
        
        total = len(timestamps)
        cat_set = set(cats)
        
        for ach in data.ACHIEVEMENTS:
            is_unlocked = False
            if ach['id'] == "first_flight": is_unlocked = total >= 1
            elif ach['id'] == "centurion": is_unlocked = total >= 100
            elif ach['id'] == "streak_7": is_unlocked = streak >= 7
            elif ach['id'] == "early_bird": is_unlocked = any(t.hour < 8 for t in timestamps)
            elif ach['id'] == "night_owl": is_unlocked = any(t.hour >= 22 for t in timestamps)
            elif ach['id'] == "balanced": is_unlocked = len(cat_set) >= 5
            
            color = SUCCESS_COLOR if is_unlocked else BUTTON_BG
            opacity = 1.0 if is_unlocked else 0.4
            
            card = ttk.Frame(self.ach_container, padding=10)
            card.pack(fill=tk.X, pady=5)
            
            l1 = ttk.Label(card, text=ach['icon'], font=("Segoe UI", 24))
            l1.pack(side=tk.LEFT, padx=10)
            
            info = ttk.Frame(card)
            info.pack(side=tk.LEFT, fill=tk.X)
            ttk.Label(info, text=ach['name'], font=("Segoe UI", 12, "bold"), foreground=color).pack(anchor="w")
            ttk.Label(info, text=ach['desc'], font=("Segoe UI", 9, "italic")).pack(anchor="w")
            
            if is_unlocked:
                ttk.Label(card, text="UNLOCKED", foreground=SUCCESS_COLOR, font=("Segoe UI", 8, "bold")).pack(side=tk.RIGHT)

    # --- FEATURES ---

    def toggle_monitor(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.mon_btn.config(text="⏹ Disengage Monitor")
            self.status_lbl.config(text="● Systems Active", foreground=SUCCESS_COLOR)
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.is_monitoring = False
            self.mon_btn.config(text="▶ Engage Monitor")
            self.status_lbl.config(text="● Systems Offline", foreground=WARNING_COLOR)

    def monitor_loop(self):
        while self.is_monitoring:
            time.sleep(self.settings["interval"] * 60)
            if self.is_monitoring and not self.is_quiet_time():
                self.root.after(0, self.trigger_reminder)

    def is_quiet_time(self):
        try:
            now = datetime.now().time()
            start = datetime.strptime(self.settings["quiet_start"], "%H:%M").time()
            end = datetime.strptime(self.settings["quiet_end"], "%H:%M").time()
            if start < end: return start <= now <= end
            return now >= start or now <= end
        except: return False

    def trigger_reminder(self, force_ex=None):
        if self.settings["sound_enabled"]: winsound.Beep(1000, 250)
        
        # Windows Toast Fallback (using a hidden root if needed, but standard messagebox for now)
        if self.settings["notifications_enabled"]:
             # In a real app we'd use win10toast, but for compatibility we'll use a styled TopLevel
             pass

        name = force_ex or random.choice(list(data.EXERCISES.keys()))
        ex = data.EXERCISES[name]
        quote = random.choice(data.MOTIVATIONAL_QUOTES)

        popup = tk.Toplevel(self.root)
        popup.title("Gravity Alert")
        popup.geometry("450x300")
        popup.configure(bg=BG_COLOR)
        popup.attributes("-topmost", True)
        
        ttk.Label(popup, text="⚠ MISSION ALERT ⚠", font=("Segoe UI", 14, "bold"), foreground=WARNING_COLOR).pack(pady=20)
        ttk.Label(popup, text=f"Target Action: {name}", font=("Segoe UI", 12, "bold"), foreground=ACCENT_COLOR).pack()
        ttk.Label(popup, text=ex['desc'], wraplength=400, justify="center").pack(pady=10)
        ttk.Label(popup, text=f'"{quote}"', font=("Segoe UI", 9, "italic"), foreground=BUTTON_ACTIVE).pack(pady=15)

        def complete():
            self.log_stretch(category=ex['cat'])
            popup.destroy()
        
        ttk.Button(popup, text="✅ MISSION COMPLETE", command=complete).pack(pady=10)

    # --- POMODORO ---

    def toggle_pomodoro(self):
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.pomo_btn.config(text="STOP FOCUS")
            self.start_pomo_thread()
        else:
            self.pomodoro_running = False
            self.pomo_btn.config(text="START FOCUS")

    def start_pomo_thread(self):
        def loop():
            while self.pomodoro_running and self.pomo_time_left > 0:
                time.sleep(1)
                self.pomo_time_left -= 1
                mins, secs = divmod(self.pomo_time_left, 60)
                self.pomo_timer_display.set(f"{mins:02d}:{secs:02d}")
            
            if self.pomodoro_running and self.pomo_time_left <= 0:
                self.root.after(0, self.pomo_finished)
        
        threading.Thread(target=loop, daemon=True).start()

    def pomo_finished(self):
        winsound.Beep(1500, 500)
        if self.pomodoro_mode == "Work":
            self.pomodoro_mode = "Break"
            self.pomo_time_left = self.settings["pomodoro_break"] * 60
            self.pomo_status_text.set("Mission Success! Take a Break.")
            messagebox.showinfo("Pomodoro", "Work session finished! Time for a stretch.")
            self.trigger_reminder()
        else:
            self.pomodoro_mode = "Work"
            self.pomo_time_left = self.settings["pomodoro_work"] * 60
            self.pomo_status_text.set("Break Over. Focus Initiated.")
            messagebox.showinfo("Pomodoro", "Break over. Back to work, Pilot!")
        
        self.start_pomo_thread()

    def reset_pomodoro(self):
        self.pomodoro_running = False
        self.pomodoro_mode = "Work"
        self.pomo_time_left = self.settings["pomodoro_work"] * 60
        self.pomo_timer_display.set(f"{self.settings['pomodoro_work']:02d}:00")
        self.pomo_status_text.set("Ready to Focus")
        self.pomo_btn.config(text="START FOCUS")

    def manual_log(self):
        # Pick category
        cat_win = tk.Toplevel(self.root)
        cat_win.title("Log Mission")
        cat_win.geometry("300x400")
        cat_win.configure(bg=BG_COLOR)
        
        ttk.Label(cat_win, text="Select Category:", font=("Segoe UI", 12, "bold")).pack(pady=20)
        for cat in set(ex['cat'] for ex in data.EXERCISES.values()):
            ttk.Button(cat_win, text=cat, command=lambda c=cat: [self.log_stretch(c, "Manual"), cat_win.destroy()]).pack(fill=tk.X, padx=20, pady=5)

    def on_closing(self):
        self.save_app_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IcarusApp(root)
    root.mainloop()
