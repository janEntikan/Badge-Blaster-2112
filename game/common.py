"""Constants for easier tuning in one place"""

# Track Generation constants (TG_ prefix)

TG_MAX_ROAD_X = 25          # How far out left/right the road can go from the center
TG_MAX_SKEW_PER_UNIT = 10   # How much the direction can change per one unit forwards
TG_UNITS_PER_CHUNK = 500    # How much units are generated at once for the track
TG_CHUNK_TRIGGER = 499      # How far ahead of the track end a new chunk should be added
TG_MIN_SPAWN_DIST = 100     # Minimum distance between player and new enemy spawn
TG_MAX_SPAWN_DIST = 200     # Maximum distance between player and new enemy spawn
TG_WIDTHS = 12, 15, 20, 25  # Road widths
TG_CURVE_RNG = -0.1, 1.6    # Range to sample to compare against diffculty. sample < difficulty == curve
TG_VISIBLE = 150            # How far ahead of the car visible road parts have to be spawned
TG_UNIT = 20                # Track length
TG_UNIT_MULT = 1 / TG_UNIT  # Inverse track length for fast division (i.e. mult)
TG_DESPAWN = TG_UNIT * 10   # Distance behind player car to despawn parts


# Props constants (PR_ prefix)

PR_SCALE = 1.8              # Scale applied to props
PR_OFFSET = 12              # Offset distance multiplier (2_somethin = 1 * PR_OFFSET)
PR_ATTEMPTS = 1, 4          # Number of props to try to place (depends on RNG vs density as well)
PR_DEFAULT_DENSITY = 0.4    # Default density if none was specified
PR_PLACE_ATTEMPTS = 10      # Number of attempts to find a free spot to place
