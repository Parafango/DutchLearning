from math import floor
from math import sqrt
import numpy as np

def get_opposite_index(idx, length):
    mid_idx = floor(length / 2)
    if idx < mid_idx:
        return (mid_idx-idx) + idx + 1
    elif idx > mid_idx:
        return mid_idx - (idx-mid_idx)
    else:
        return mid_idx

def reset_index_to_range(idx, length):
    if idx <= length - 1:
        return idx
    else:
        return idx - length

def get_corner_from_neighbouring_slots(slot1, slot2):
    y1, y2 = slot1[1], slot2[1]
    x1, x2 = slot1[0], slot2[0]
    x_corner = None
    y_corner = None

    if min(x1, x2) == 0:
        x_corner = 0
    elif max(x1, x2) == 2:
        x_corner = 2

    if min(y1, y2) == 0:
        y_corner = 0
    elif max(y1, y2) == 2:
        y_corner = 2

    return (x_corner, y_corner)

def check_coords_in_grid(grid, coords_list, player_value=None):
    matched_coords = []
    if player_value == None:
        for coords in coords_list:
            if grid(coords) == 0:
                matched_coords.append(coords)
    else:
        for coords in coords_list:
            if grid(coords) == player_value:
                matched_coords.append(coords)

    return matched_coords

def get_closest_in_grid(target_slot, possible_slots):
    distances = []
    for possible_slot in possible_slots:
        distance = sqrt((possible_slot[0]-target_slot[0]) **2 + (possible_slot[1]-target_slot[1]) **2)
        distances.append(distance)

    distances = np.array(distances)
    minimum_distance = min(distances)
    coords = possible_slots[distances == minimum_distance]
    return coords