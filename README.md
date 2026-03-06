# Project Icarus: The Antigravity Health Monitor

This project is a **Persistent Health Tracking System** built using the **Gemini CLI**.

## Overview

The system consists of two main components:

-   **`script.py`**: The background worker (The "Producer"). It triggers a `tkinter` popup reminder every 30 minutes to encourage stretching and logs your activity.
-   **`dashboard.py`**: The data visualizer (The "Wow" factor). It uses `matplotlib` to read the activity logs and display a bar chart of your daily progress.

## How to Use

1.  **Start the Reminder**: Run `python script.py`. A popup will appear every 30 minutes. Click 'OK' to log your stretch.
2.  **View Your Stats**: Run `python dashboard.py` to see a bar chart of your stretches per day.

*Note: You may need to install the required libraries:*
`pip install matplotlib`
