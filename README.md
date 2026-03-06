# Project Icarus: The Antigravity Health Monitor

This project is a **Persistent Health Tracking System** built using the **Gemini CLI**.

## Overview

The system is now a unified application:

-   **`dashboard.py`**: The **Unified GUI**. It provides a single interface to:
    -   **Start/Stop** the background monitoring.
    -   **Adjust** the reminder interval (in minutes).
    -   **Manually log** a stretch.
    -   **Visualize** your stretch history with an embedded bar chart.

-   **`script.py`**: (Legacy) Original standalone background worker.

## How to Run

To run the **Project Icarus: The Antigravity Health Monitor**, follow these steps:

### 1. Install Dependencies
Ensure you have `matplotlib` installed:
```bash
pip install matplotlib
```

### 2. Start the Unified App
Run the dashboard to manage your health monitoring:
```bash
python "dashboard.py"
```

### 3. Usage
-   **Enter an interval** (e.g., 30) and click **"Start Monitor"** to begin receiving stretch reminders.
-   Click **"Manual Log"** if you've done a stretch outside of the scheduled reminders.
-   The chart will refresh automatically whenever a stretch is logged.
