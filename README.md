# Project Icarus: The Antigravity Health Monitor

![Version](https://img.shields.io/badge/version-2.1-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> "Gravity is a habit that is hard to shake. Shake it anyway."

**Project Icarus** is a Python-based health monitor designed for developers and desk workers. It reminds you to stretch, tracks your progress, and gamifies your health to keep you flying high.

## 🚀 Features (v2.1)

### 🎮 Gamified Health
*   **XP Progress Bar:** Visualize your journey to the next rank with a dynamic progress bar.
*   **XP & Leveling System:** Earn XP for every stretch. Rank up from "Cadet" to "Galactic Legend".
*   **Streak Tracking:** Keep your momentum going with the daily 🔥 streak counter.
*   **Pilot Profile:** A central hub showing your current rank, level, and experience.

### 🧘 Smart & Interactive Reminders
*   **⚡ Quick Stretch:** Feeling stiff? Trigger a random stretch instantly with one click.
*   **Interactive Library:** Launch specific exercises directly from the library whenever you need them.
*   **Variety:** Popups suggest specific exercises (e.g., "Neck Release", "Wrist Flexor") with motivational quotes.
*   **Quiet Hours:** Set "Do Not Disturb" times (e.g., 22:00 to 08:00) to keep your nights peaceful.
*   **Audio Feedback:** Gentle chimes when a reminder is triggered (optional).

### 📊 Mission Control (Dashboard)
*   **Modern UI/UX:** A sleek, Nord-theme inspired interface with intuitive icons and refined spacing.
*   **Activity Charts:** High-contrast bar charts visualize your daily stretching habits.
*   **Exercise Library:** A comprehensive reference guide for all recommended desk exercises.
*   **Manual Logging:** Easily log stretches you did away from your desk.

## 🛠 Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/project-icarus.git
    cd project-icarus
    ```

2.  **Install Dependencies:**
    Project Icarus requires `matplotlib` for charts and `tkinter` (usually built-in) for the GUI.
    ```bash
    pip install matplotlib
    ```

## 🕹 Usage

1.  **Launch the Command Center:**
    ```bash
    python dashboard.py
    ```
2.  **Engage Systems:**
    *   Click **"▶ Engage Monitor"** to start the background timer.
    *   The app runs in the background. When the timer hits, a popup appears.
    *   Click **"✅ Mission Complete"** to log your progress and gain XP!
3.  **Customize:**
    *   Go to the **"⚙ Settings"** tab to adjust intervals, quiet hours, or toggle sounds.

## 📂 File Structure

*   `dashboard.py`: The main "Mission Control" application (GUI & Monitor).
*   `icarus_data.py`: Core logic for XP, levels, exercises, and motivational quotes.
*   `stretch_log.csv`: Your personal mission log (History).
*   `script.py`: (Legacy) Minimalist headless script for background monitoring.

## 🤝 Contributing

Feel free to fork this project and submit PRs for new exercises, themes, or features!

## 📜 License

MIT License. Fly safe!
