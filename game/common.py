"""Constants for easier tuning in one place"""

# Follow Cam constants (FC_ prefix)

FC_MAX_SPEED = 1.0
FC_EXP = 0.25


# Track Generation constants (TG_ prefix)

TG_MAX_ROAD_X = 80          # How far out left/right the road can go from the center
TG_MAX_CURVE_X = 8          # How much X offset a curve of multiple parts can traverse
TG_MAX_SKEW_PER_UNIT = 10   # How much the direction can change per one unit forwards
TG_UNITS_PER_CHUNK = 500    # How much units are generated at once for the track
TG_CHUNK_TRIGGER = 499      # How far ahead of the track end a new chunk should be added
TG_MIN_SPAWN_DIST = 100     # Minimum distance between player and new enemy spawn
TG_MAX_SPAWN_DIST = 200     # Maximum distance between player and new enemy spawn
TG_WIDTHS = 12, 15, 20, 25  # Road widths
TG_CURVE_RNG = -0.1, 1.6    # Range to sample to compare against diffculty. sample < difficulty == curve
TG_VISIBLE = 150            # How far ahead of the car visible road parts have to be spawned
TG_UNIT = 20                # Track length
TG_DESPAWN = TG_UNIT * 10   # Distance behind player car to despawn parts
TG_PART_CHG_RNG = 250, 500  # randint range for choosing a different part
TG_LEVEL_CHG_RNG = 3, 7     # randint range for choosing when to transition to a new level (number of part changes)
TG_TRANS_RNG = 50, 120      # randint range for choosing how many transition parts to place

# Used internally
TG_LOCAL_CURVE_DIV = TG_MAX_ROAD_X / TG_MAX_CURVE_X
TG_UNIT_MULT = 1 / TG_UNIT  # Inverse track length for fast division (i.e. mult)


# Props constants (PR_ prefix)

PR_SCALE = 1.8              # Scale applied to props
PR_OFFSET = 12              # Offset distance multiplier (2_somethin = 1 * PR_OFFSET)
PR_ATTEMPTS = 1, 4          # Number of props to try to place (depends on RNG vs density as well)
PR_DEFAULT_DENSITY = 0.4    # Default density if none was specified
PR_PLACE_ATTEMPTS = 10      # Number of attempts to find a free spot to place
