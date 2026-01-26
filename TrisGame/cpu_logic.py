import random

from tris_classes import TrisCPU, TrisGrid, GameStates
import numpy as np
from utilities import get_corner_from_neighbouring_slots, get_opposite_index, check_coords_in_grid, get_closest_in_grid
from itertools import product

class ImprovedCPU(TrisCPU):
    def __init__(self, grid: TrisGrid, states: GameStates):
        super().__init__(grid, states)

    def traps_logic(self):
        if self.is_second:
            #defense
            coords = self.detect_and_handle_traps()

        if not self.is_second or coords is None:
            #attack
            coords = self.set_up_traps()

        return coords

    def detect_and_handle_traps(self):
        max_dim = np.size(self.grid.grid_values, axis=0) - 1
        corner_positions = [(0, 0), (0, max_dim), (max_dim, 0), (max_dim, max_dim)]
        #two main cases that have to be taken into account:
        #- big L trap-->
            # prevent by getting the center slot
            # handle when two corners are taken by opponent
        #- small L trap-->
            # handle when opponent has one corner and one cross slot
                # either opposite corner if available or corner in between
            # handle when opponent has two close cross slots  --> get corner in between

        #to prevent big L from happening
        if self.grid.grid_values[1,1] == 0:
            coords = (1,1)
            return coords

        pos_adv = np.argwhere(self.grid.grid_values == self.adversary_value)
        pos_adv = [tuple(x) for x in pos_adv.tolist()]
        corners_adv = set(pos_adv).intersection(set(corner_positions))
        n_corners_adv = len(corners_adv)

        #big L handling
        if n_corners_adv == 2:
            #get first non corner value to force adversary to block
            #TODO: this assumes that central slot is taken, is this always fine? And can the trap even be set up if adv doesn't
            # start with corner? probably not so most likely this is fine
            unfilled_slots = np.argwhere(self.grid.grid_values == 0)
            unfilled_slots = set(tuple(x) for x in unfilled_slots.tolist())
            pos_to_iter = unfilled_slots - set(corner_positions)
            return list(pos_to_iter)[0]

        #small L handling
        if n_corners_adv == 1:
            corner_adv = list(corners_adv)[0]
            opposite_corner = (get_opposite_index(corner_adv[0], 3), get_opposite_index(corner_adv[1], 3))
            danger_crosses = [(opposite_corner[0], 1), (1, opposite_corner[1])]
            if self.grid.grid_values[danger_crosses[0]] or self.grid.grid_values[danger_crosses[1]]:
                #TODO: best move would be to get corner in between as that could also lead to a win but for now let's keep it simple
                return opposite_corner

        #check if two close cross slots are taken by adv
        cross_positions = [(0, 1), (1, 2), (2, 1), (1, 0), (0, 1)]
        for i in range(len(cross_positions) - 1):
            cross_pos1 = cross_positions[i]
            cross_pos2 = cross_positions[i + 1]

            if self.grid.grid_values[cross_pos1[0], cross_pos1[1]] == 1 and self.grid.grid_values[
                cross_pos2[0], cross_pos2[1]] == 1:
                corner_from_cross = get_corner_from_neighbouring_slots(cross_pos1, cross_pos2)
                if self.grid.grid_values[corner_from_cross[0], corner_from_cross[1]] == 0:
                    return corner_from_cross
            else:
                continue


        return None

    def set_up_traps(self):
        #for now choice of trap is commiting for the round, no readjustments.
        #If it cannot be applied just go to next logic
        #small L = 0, big L = 1
        if self.trap_style is None:
            trap_style = random.randint(0,1)

        if trap_style == 0:
            coords = self.small_l_trap()
            return coords
        elif trap_style == 1:
            coords = self.big_L_trap()
            return coords

        return None

    def small_l_trap(self):
        cross_positions = [(0, 1), (1, 2), (2, 1), (1, 0)]

        available_crosses = check_coords_in_grid(self.grid.grid_values, cross_positions)
        owned_crosses = check_coords_in_grid(self.grid.grid_values, cross_positions, self.player_value)
        if len(available_crosses) == 4:
            return cross_positions[random.randint(0,3)]
        elif len(owned_crosses) == 1:
            return self.get_free_adjacent_cross(available_crosses, owned_crosses)
        elif len(owned_crosses) == 2:
            # if two adjacent cross and path is free then get corner
            corner_in_between = get_corner_from_neighbouring_slots(owned_crosses[0], owned_crosses[1])
            if self.grid.grid_values[corner_in_between] == 0:
                directions = [(owned_crosses[0][0] - corner_in_between[0], owned_crosses[0][1] - corner_in_between[1]),
                              (owned_crosses[1][0] - corner_in_between[0], owned_crosses[1][1] - corner_in_between[1])]
                slots_to_check = []
                for i, direction in enumerate(directions):
                    slots_to_check.append(
                        (owned_crosses[i][0] + direction[i][0], owned_crosses[i][1] + direction[i][0]))

                available_directions = check_coords_in_grid(self.grid.grid_values, slots_to_check)
                if len(available_directions) == 2:
                    return corner_in_between

        return None

    def get_free_adjacent_cross(self, available_slots, owned_slots):
        # get set of adjacent cross
        # for every cross
        # get corner in between
        # explore direction from corner to cross (with vector applied to cross) and check
        # if free get the cross otherwise continue
        adjacent_crosses = get_closest_in_grid(owned_slots[0], available_slots)
        for cross in adjacent_crosses:
            corner_in_between = get_corner_from_neighbouring_slots(owned_slots[0], cross)
            directions = [(owned_slots[0][0] - corner_in_between[0], owned_slots[0][1] - corner_in_between[1]),
                          (cross[0] - corner_in_between[0], cross[1] - corner_in_between[1])]
            possible_crosses = [owned_slots[0], cross]
            slots_to_check = []
            for i, direction in enumerate(directions):
                slots_to_check.append((possible_crosses[i][0] + direction[i][0], possible_crosses[i][1] + direction[i][0]))

            available_directions = check_coords_in_grid(self.grid.grid_values, slots_to_check)
            if len(available_directions) == 2:
                return cross
        return None

    def big_L_trap(self):
        #on first pass get a random corner
        #on second pass get another corner
            #get adjacent non blocked corner
            #if center is lost then go opposite corner
        #on third pass get third corner
            #if center is not lost or center is lost but adv has one corner then get corner with double chance
            #if center was lost and the adv doesn't have corners then game is most likely tied so return none
        max_dim = np.size(self.grid.grid_values, axis=0) - 1
        corner_positions = list(product([0, max_dim], repeat=2))
        available_corners = check_coords_in_grid(self.grid.grid_values, corner_positions)
        owned_corners = check_coords_in_grid(self.grid.grid_values, corner_positions)
        if len(available_corners) == 4:
            return available_corners[random.randint(0, max_dim)]
        elif len(owned_corners) == 1:
            if self.grid.grid_values[0,0] == self.adversary_value:
                opposite_corner = (get_opposite_index(owned_corners[0][0], 3), get_opposite_index(owned_corners[0][1], 3))
                if opposite_corner in available_corners:
                    return opposite_corner
            else:
                return self.get_free_adjacent_corner(available_corners, owned_corners)
        else:
            lost_corners = check_coords_in_grid(self.grid.grid_values, corner_positions, self.adversary_value)
            win_condition = (self.grid.grid_values[0,0] != self.adversary_value or
                         (self.grid.grid_values[0,0] == self.adversary_value and len(lost_corners) >= 1))
            if win_condition:
                #get corner with double chance
                best_corner = self.get_best_corner(available_corners, owned_corners)
                return best_corner

        return None

    def get_free_adjacent_corner(self, available_slots, owned_corners):
        adjacent_corners = get_closest_in_grid(owned_corners[0], available_slots)
        for corner in adjacent_corners:
            direction = ((owned_corners[0][0] - corner[0])/2, (owned_corners[0][1] - corner[1])/2)
            slot_to_check = (corner[0]+direction[0], corner[1]+direction[1])
            if self.grid.grid_values[slot_to_check] == 0:
                return corner
        return None

    def get_best_corner(self, available_slots, owned_corners):
        if len(owned_corners) < 2:
            return None
        if len(available_slots) == 1:
            return available_slots[0]
        win_scenarios = np.zeros((len(available_slots),1))

        for i, corner in enumerate(available_slots):
            directions = [((owned_corners[0][0] - corner[0])/2, (owned_corners[0][1] - corner[1])/2),
                          ((owned_corners[1][0] - corner[0])/2, (owned_corners[1][1] - corner[1])/2)]
            for direction in directions:
                slot_to_check = (corner[0]+direction[0], corner[1]+direction[1])
                if self.grid.grid_values[slot_to_check] == 0:
                    win_scenarios[i] +=1

        available_slots = np.array(available_slots)
        best_corner = available_slots[np.argmax(win_scenarios)]
        return best_corner