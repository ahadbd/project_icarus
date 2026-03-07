import math
import json
import os
from datetime import datetime

# --- CONFIG & PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "settings.json")
XP_PER_STRETCH = 15

# --- SETTINGS PERSISTENCE ---
DEFAULT_SETTINGS = {
    "interval": 30,
    "quiet_start": "22:00",
    "quiet_end": "08:00",
    "sound_enabled": True,
    "notifications_enabled": True,
    "pomodoro_work": 25,
    "pomodoro_break": 5
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# --- GAMIFICATION LOGIC ---
def calculate_level(total_xp):
    if total_xp == 0: return 1, 0, 100
    level = int(math.sqrt(total_xp / 10)) + 1
    current_level_xp_start = 10 * (level - 1)**2
    next_level_xp_start = 10 * (level)**2
    xp_needed_for_next = next_level_xp_start - current_level_xp_start
    xp_progress = total_xp - current_level_xp_start
    return level, xp_progress, xp_needed_for_next

def get_rank_title(level):
    ranks = {0: "Cadet", 5: "Pilot", 10: "Commander", 20: "Captain", 30: "Orbit Master", 50: "Galactic Legend"}
    for threshold, title in sorted(ranks.items(), reverse=True):
        if level >= threshold: return title
    return "Cadet"

# --- ACHIEVEMENTS ---
ACHIEVEMENTS = [
    {"id": "first_flight", "name": "First Flight", "desc": "Log your very first stretch.", "req": 1, "icon": "🚀"},
    {"id": "early_bird", "name": "Early Bird", "desc": "Log a stretch before 8:00 AM.", "req": "special", "icon": "🌅"},
    {"id": "centurion", "name": "Centurion", "desc": "Reach 100 total stretches.", "req": 100, "icon": "💯"},
    {"id": "streak_7", "name": "Iron Pilot", "desc": "Maintain a 7-day streak.", "req": 7, "icon": "🦾"},
    {"id": "night_owl", "name": "Night Owl", "desc": "Log a stretch after 10:00 PM.", "req": "special", "icon": "🦉"},
    {"id": "balanced", "name": "Balanced Life", "desc": "Log at least 5 stretches in every category.", "req": "special", "icon": "⚖️"}
]

# --- EXERCISE LIBRARY ---
EXERCISES = {
    "Neck Release": {"desc": "Gently tilt your head towards your shoulder. Hold for 10s.", "cat": "Neck"},
    "Seated Spinal Twist": {"desc": "Turn your torso to the side, holding the chair back.", "cat": "Back"},
    "Wrist Flexor": {"desc": "Extend arm, palm up. Gently pull fingers back.", "cat": "Arms"},
    "Shoulder Shrugs": {"desc": "Raise shoulders to ears, hold 3s, release.", "cat": "Shoulders"},
    "Eye Roll": {"desc": "Look in a circle to reduce eye strain.", "cat": "Eyes"},
    "The Reach": {"desc": "Interlace fingers, palms up, stretch high.", "cat": "Full Body"},
    "Leg Extensions": {"desc": "Straighten your legs under your desk, hold 5s.", "cat": "Legs"}
}

MOTIVATIONAL_QUOTES = [
    "Gravity is a habit. Shake it off.",
    "Your future self will thank you for this.",
    "Movement is medicine.",
    "Don't let the chair win!",
    "Status: Anti-gravity systems engaging..."
]
