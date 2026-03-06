# Project Icarus: The Antigravity Health Monitor

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> "Gravity is a habit that is hard to shake. Shake it anyway."

**Project Icarus** is a Python-based health monitor designed for developers and desk workers. It reminds you to stretch, tracks your progress, and gamifies your health to keep you flying high.

## 🚀 Features (v2.0)

### 🎮 Gamified Health
*   **XP & Leveling System:** Earn XP for every stretch. Rank up from "Cadet" to "Galactic Legend".
*   **Streak Tracking:** Keep your momentum going by stretching daily.
*   **Pilot Profile:** Visual dashboard of your current rank and progress.

### 🧘 Smart Reminders
*   **Variety:** Instead of a generic alert, Icarus suggests specific exercises (e.g., "Neck Release", "Wrist Flexor").
*   **Quiet Hours:** Configure start and end times to prevent interruptions during sleep.
*   **Audio Feedback:** Optional sound notifications when a reminder is triggered.

### 📊 Mission Control (Dashboard)
*   **Dark Mode UI:** A sleek, Nord-theme inspired interface easy on the eyes.
*   **Activity Charts:** Visual bar charts of your daily stretching habits.
*   **Exercise Library:** Built-in reference guide for all recommended exercises.
*   **Manual Logging:** Forgot to click the popup? Log stretches manually.

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
    *   Click **"Engage Monitor"** to start the background timer (default: 30 mins).
    *   The app will run in the background.
    *   When the timer hits, a popup will appear with a recommended exercise.
3.  **Customize:**
    *   Go to the **"Settings"** tab to adjust the interval, quiet hours, or toggle sound.

## 📂 File Structure

*   `dashboard.py`: The main application entry point (GUI, Logic, Monitor).
*   `icarus_data.py`: Data file containing exercise definitions, quotes, and XP logic.
*   `stretch_log.csv`: Automatically generated log file storing your history.
*   `script.py`: (Legacy) Minimalist headless script for background monitoring.

## 🤝 Contributing

Feel free to fork this project and submit PRs for new exercises, themes, or features!

## 📜 License

MIT License. Fly safe!
