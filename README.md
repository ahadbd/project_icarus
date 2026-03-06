# Project Icarus: The Antigravity Health Monitor

This project is a **Persistent Health Tracking System** built using the **Gemini CLI**.

## Overview

The system consists of two main components:

-   **`script.py`**: The background worker (The "Producer"). It triggers a `tkinter` popup reminder every 30 minutes to encourage stretching and logs your activity.
-   **`dashboard.py`**: The data visualizer (The "Wow" factor). It uses `matplotlib` to read the activity logs and display a bar chart of your daily progress.

## How to Run

To run the **Project Icarus: The Antigravity Health Monitor**, follow these steps:

### 1. Install Dependencies
Ensure you have `matplotlib` installed for the dashboard:
```bash
pip install matplotlib
```

### 2. Start the Health Reminder
Run the background worker to receive stretch reminders every 30 minutes:
```bash
python "script.py"
```
*   A popup will appear every 30 minutes. 
*   Click **'OK'** to log your stretch into `stretch_log.csv`.

### 3. View the Dashboard
To see your progress visualized in a bar chart, run the visualizer:
```bash
python "dashboard.py"
```
*Note: The dashboard will only display data after you have clicked 'OK' on at least one reminder.*
