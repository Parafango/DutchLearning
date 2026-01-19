from math import floor


def get_opposite_index(idx, len):
    mid_idx = floor(len / 2)
    if idx < mid_idx:
        return (mid_idx-idx) + idx + 1
    elif idx > mid_idx:
        return mid_idx - (idx-mid_idx)
    else:
        return mid_idx

def reset_index_to_range(idx, len):
    if idx <= len - 1:
        return idx
    else:
        return idx - len

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