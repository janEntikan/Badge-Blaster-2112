"""Constants for easier tuning in one place"""

from panda3d.core import Vec2, Vec3

# Shader constants (SH_ prefix)

SH_Z_SHADE_COLOR = Vec3(0.002, 0.001, 0.0005)
SH_Z_SHADE_EXP = 1.1


# Music/SFX (SND_ prefix)

SND_BGM = [f'assets/music/{i}.ogg' for i in range(1, 8)]


# Difficulty (DF_ prefix)

DF_SPLINE_PTS = [
    Vec2(0, -0.8),
    Vec2(1, 0.0),
    Vec2(2, 0.3),
    Vec2(3, 0.25),
    Vec2(4, 0.47),
    Vec2(5, 0.69),
    Vec2(6, 0.54),
    Vec2(7, 0.78),
    Vec2(8, 0.65),
    Vec2(9, 0.84),
    Vec2(10, 0.92),
    Vec2(11, 0.8),
    Vec2(12, 0.75),
    Vec2(13, 1.1)
]                           # Spline points representing difficulty
DF_INC_PER_SEC = 0.002


# Follow Cam constants (FC_ prefix)

FC_MAX_SPEED = 1.0
FC_EXP = 0.25


# Track Generation constants (TG_ prefix)

TG_MAX_ROAD_X = 80          # How far out left/right the road can go from the center
TG_MAX_CURVE_X = 11         # How much average X offset a curve of multiple parts can traverse
TG_MAX_SKEW_PER_UNIT = 10   # How much the direction can change per one unit forwards
TG_UNITS_PER_CHUNK = 500    # How much units are generated at once for the track
TG_CHUNK_TRIGGER = 499      # How far ahead of the track end a new chunk should be added
TG_MIN_SPAWN_DIST = 100     # Minimum distance between player and new enemy spawn
TG_MAX_SPAWN_DIST = 100     # Maximum distance between player and new enemy spawn
TG_WIDTHS = 12, 15, 20, 25  # Road widths
TG_CURVE_RNG = -0.5, 1.6    # Range to sample to compare against diffculty. sample < difficulty == curve
TG_VISIBLE = 250            # How far ahead of the car visible road parts have to be spawned
TG_UNIT = 20                # Track length
TG_DESPAWN = TG_UNIT * 15   # Distance behind player car to despawn parts
TG_PART_CHG_RNG = 15, 30    # randint range for choosing a different part
TG_LEVEL_CHG_RNG = 4, 4     # randint range for choosing when to transition to a new level (number of part changes)
TG_TRANS_RNG = 12, 12       # randint range for choosing how many transition parts to place
TG_MIN_AABB = 50            # The minimum number of AABB instances to keep for prop placement logic

# Used internally
TG_LOCAL_CURVE_DIV = TG_MAX_ROAD_X / TG_MAX_CURVE_X
TG_UNIT_MULT = 1 / TG_UNIT  # Inverse track length for fast division (i.e. mult)


# Props constants (PR_ prefix)

PR_SCALE = 1.8              # Scale applied to props
PR_OFFSET = 12              # Offset distance multiplier (2_somethin = 1 * PR_OFFSET)
PR_ATTEMPTS = 1, 4          # Number of props to try to place (depends on RNG vs density as well)
PR_DEFAULT_DENSITY = 0.4    # Default density if none was specified
PR_PLACE_ATTEMPTS = 10      # Number of attempts to find a free spot to place
