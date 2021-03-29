"""Constants for easier tuning in one place"""

# Track Generation constants (TG_ prefix)

TG_MAX_ROAD_X = 25          # How far out left/right the road can go from the center
TG_MAX_SKEW_PER_UNIT = 20   # How much the direction can change per one unit forwards
TG_UNITS_PER_CHUNK = 500    # How much units are generated at once for the track
TG_CHUNK_TRIGGER = 201      # How far ahead of the track end a new chunk should be added
TG_MIN_SPAWN_DIST = 100     # Minimum distance between player and new enemy spawn
TG_MAX_SPAWN_DIST = 200     # Maximum distance between player and new enemy spawn
TG_MAX_WIDTH = 28
TG_MIN_WIDTH = 15
TG_WIDTH_CHG_PER_UNIT = 2
