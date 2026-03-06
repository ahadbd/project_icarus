import math
from datetime import datetime

# --- GAMIFICATION CONFIG ---
XP_PER_STRETCH = 15
LEVEL_CONSTANT = 100  # XP needed for level 1 -> 2 approx.

def calculate_level(total_xp):
    """Calculates level based on total XP. 
    Formula: Level = 1 + sqrt(XP) * 0.1 (approx) or linear/exponential tiers.
    Let's use a simple quadratic curve: XP = Level^2 * Constant
    So Level = Sqrt(XP / Constant)
    """
    if total_xp == 0:
        return 1, 0, LEVEL_CONSTANT
    
    level = int(math.sqrt(total_xp / 10)) + 1
    
    # Calculate progress to next level
    current_level_xp_start = 10 * (level - 1)**2
    next_level_xp_start = 10 * (level)**2
    
    xp_needed_for_next = next_level_xp_start - current_level_xp_start
    xp_progress = total_xp - current_level_xp_start
    
    return level, xp_progress, xp_needed_for_next

def get_rank_title(level):
    if level < 5: return "Cadet"
    if level < 10: return "Pilot"
    if level < 20: return "Commander"
    if level < 30: return "Captain"
    if level < 50: return "Orbit Master"
    return "Galactic Legend"

# --- EXERCISE LIBRARY ---
EXERCISES = {
    "Neck Release": {
        "desc": "Gently tilt your head towards your shoulder. Hold for 10s on each side.",
        "category": "Upper Body"
    },
    "Seated Spinal Twist": {
        "desc": "In your chair, turn your torso to the side, holding the back of the chair.",
        "category": "Back"
    },
    "Wrist Flexor": {
        "desc": "Extend arm, palm up. Gently pull fingers back with other hand.",
        "category": "Arms/Hands"
    },
    "Shoulder Shrugs": {
        "desc": "Raise shoulders to ears, hold for 3s, release. Repeat 10 times.",
        "category": "Upper Body"
    },
    "Eye Roll": {
        "desc": "Look up, right, down, left in a circle. Reverse. Reduces eye strain.",
        "category": "Eyes"
    },
    "The Reach": {
        "desc": "Interlace fingers, palms up, and stretch arms high above head.",
        "category": "Full Body"
    }
}

# --- QUOTES ---
MOTIVATIONAL_QUOTES = [
    "Gravity is a habit that is hard to shake. Shake it anyway.",
    "Your future self will thank you for this stretch.",
    "Movement is medicine.",
    "Don't let the chair defeat you!",
    "Status: Anti-gravity systems engaging..."
]
