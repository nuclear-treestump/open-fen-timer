# constants.py

SRC_SELECTION = ["Twitch"]
APP_VERSION = "1.0.0"
ASCII_DATA = """  ____                   ______      _______ _                     
 / __ \                 |  ____|    |__   __(_)                    
| |  | |_ __   ___ _ __ | |__ ___ _ __ | |   _ _ __ ___   ___ _ __ 
| |  | | '_ \ / _ \ '_ \|  __/ _ \ '_ \| |  | | '_ ` _ \ / _ \ '__|
| |__| | |_) |  __/ | | | | |  __/ | | | |  | | | | | | |  __/ |   
 \____/| .__/ \___|_| |_|_|  \___|_| |_|_|  |_|_| |_| |_|\___|_|   
       | |                                                         
       |_|"""
optional_modules_enabled = ["patreon"]
FONT_NAME = "VCR OSD Mono"
BG_COLOR = "#00FF00"
PAUSE_COLOR = "#33FFFF"
FONT_SIZE = 100
max_visible_donations = 10
donations_display_time = 30

# How many minutes per dollar
minute_multiplier = 2

# Enable Sub Bomb support (+x minutes on top of subs)
subbomb = 10

# Sub Bomb minimum (default: 5)
subbomb_limit = 5

# Sub Bomb type (type 1: Applied once, type 2: Applied x times ( number of subs / subbomb_limit ))
subbomb_type = 2

# Sub Cost Setting
# Reminder: Twitch takes 50%. Default 50% value of sub cost. Set to 1 to ignore Twitch cut. 
# Example: 5 Tier 1 subs * 0.5 = 12.5, 5 Tier 1 subs * 2 = 50
subcost = 2

# PATREON SETTINGS
# PATREON MAP
# Key = dollar value of tier
# Value = time to be added
# Example below

PATREON_PRICE_CHART = {
    3: 10 * 60,    # 10 minutes in seconds
    5: 15 * 60,    # 15 minutes in seconds
    7.5: 20 * 60,  # 20 minutes in seconds
    10: 25 * 60,   # 25 minutes in seconds
    15: 30 * 60,   # 30 minutes in seconds
    25: 1 * 60 * 60, # 1 hour in seconds
    50: 2 * 60 * 60, # 2 hours in seconds
    75: 4 * 60 * 60, # 4 hours in seconds
    100: 6 * 60 * 60 # 6 hours in seconds
}

START_HOURS = 4
START_MINUTES = 0
START_SECONDS = 0