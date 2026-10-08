"""
collisions: frog-vs-vehicle collision detection.
"""

CELL_SIZE = 50


def check_collision(frog, vehicles):
    """
    Returns True if the frog is currently hit by any vehicle.
    """
    for v in vehicles:
        vehicle_col = int(v.x // CELL_SIZE)
        if vehicle_col == frog.col and v.row == frog.row:
            return True
    return False
