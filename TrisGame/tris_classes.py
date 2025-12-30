from math import floor
from typing import Tuple

import pygame
from pygame import Rect
import numpy as np
import sys
from random import randint

class TrisGrid(Rect):
    def __init__(self, left, bottom, width, height):
        super().__init__(left, bottom, width, height)
        self.unit_size = self.h/3
        self.grid_values = np.zeros((3,3))

    def map_symbol_to_value(self, symbol):
        if symbol == 'x':
            return 1
        elif symbol == 'o':
            return -1
        else:
            sys.exit("Something went wrong")

    def check_click_grid(self, pos, states: 'GameStates'):
        x_click = pos[0]
        y_click = pos[1]
        x_within = self.right > x_click > self.left
        y_within = self.bottom > y_click > self.top
        if x_within and y_within:
            for i in range(3):
                x_square = self.left + self.unit_size * i
                if x_square + self.unit_size > x_click > x_square:
                    break

            for j in range(3):
                y_square = self.top + self.unit_size * j
                if y_square + self.unit_size > y_click > y_square:
                    break

            turn_symbol = states.determine_turn()
            value = self.map_symbol_to_value(turn_symbol)
            if self.grid_values[i,j] == 0:
                self.grid_values[i,j] = value
            else:
                return None
            coords = (i,j)
            return coords
        else:
            return None

    def draw_symbol(self, coords, states:'GameStates', screen: pygame.Surface):
        x_center = coords[0] * self.unit_size + self.unit_size/2 + self.left
        y_center = coords[1] * self.unit_size + self.unit_size / 2 + self.top
        if states.determine_turn() == 'x':
            x_left = x_center - self.unit_size * 2 / 6
            x_right = x_center + self.unit_size * 2 / 6
            y_top = y_center + self.unit_size * 2 / 6
            y_bottom = y_center +-self.unit_size * 2 / 6
            pygame.draw.line(screen, 'white',(x_left, y_top), (x_right, y_bottom), width=4)
            pygame.draw.line(screen, 'white', (x_right, y_top), (x_left, y_bottom), width=4)
        elif states.determine_turn() == 'o':
            radius = self.unit_size * 2/6
            pygame.draw.circle(screen, 'white',(x_center,y_center), radius)
        else:
            sys.exit('Something went wrong')
        pygame.display.flip()

    def reset_values(self):
        self.grid_values = np.zeros((3,3))

class GameOptions():
    def __init__(self):
        self.gamemode = 0 #0 is 1v1, 1 is vs CPU
        self.fontsize = 40


class GameStates():
    def __init__(self):
        self.turn_count = 0
        self.score = np.zeros((2,1))
        self.replay_selector = ReplaySelector()
        self.restart_game = False
        self.quit_game = False
        self.last_winner = None
        self.game_options = GameOptions()

    def determine_turn(self):
        if self.turn_count % 2 == 0:
            return 'x'
        else:
            return 'o'

    def reset_states(self):
        self.turn_count = 0
        self.restart_game = False
        self.replay_selector = ReplaySelector()
        self.last_winner = None


class ReplaySelector():
    def __init__(self):
        self.replay_pos = None
        self.selected_value = 'y'

    def get_x_replay_pos(self, font: pygame.font.Font, x_start):
        if self.selected_value == 'y':
            x_start = x_start
            x_end = x_start + font.size('Yes')[0]
        elif self.selected_value == 'n':
            x_start = x_start + font.size('Yes    ')[0]
            x_end = x_start + font.size('No')[0]
        else:
            print('Something went wrong')
            return

        self.replay_pos = (x_start, x_end)
        return self.replay_pos

    def switch_selection(self):
        if self.selected_value == 'y':
            self.selected_value = 'n'
        elif self.selected_value == 'n':
            self.selected_value = 'y'

class BasicDisplayer():
    def __init__(self, screen: pygame.Surface, states: GameStates, subscreen_rect: pygame.Rect):
        self.screen = screen
        self.states = states
        self.fontsize = states.game_options.fontsize
        self.subscreen_rect = subscreen_rect
        self.font = None
        self.selected_option = None
        self.selectable_positions = None
        self.selector_thickness = None
        self.options_dimensions = None

    def display_choice_screen(self, message):
        #draw subscreen
        pygame.draw.rect(self.screen, color='black', rect=self.subscreen_rect)
        pygame.draw.rect(self.screen, color='white', rect=self.subscreen_rect, width=4)

        self.font = pygame.font.Font(None, self.fontsize)
        font_height = self.font.size('Y')[1]

        label = []
        for line in message:
            label.append(self.font.render(line, True, 'white'))

        y = self.subscreen_rect.top + font_height
        for i in range(len(label)):
            center_rect = label[i].get_rect(center=(self.subscreen_rect.center[0], y))
            self.screen.blit(label[i], center_rect)
            y = y + 3 * font_height

        y_end = y - 5/2 * font_height

        self.selector_thickness = 2
        selected_position = (self.subscreen_rect.center[0] - self.font.size(message[-1])[0] / 2, y_end)
        text_handler = TextHandler(self.font, message[-1], selected_position)
        self.selectable_positions, self.options_dimensions = text_handler.get_start_positions()

        self.selected_option = 0
        first_option = (message[-1]).split(' ')[0]
        x_start = selected_position[0]
        x_end = x_start + self.font.size(first_option)[0]

        pygame.draw.line(self.screen, 'white', (x_start, y_end), (x_end, y_end), width=self.selector_thickness)

        pygame.display.flip()



    def update_choice_screen(self, choice_line, key_action):
        pos_change = 0
        if key_action == pygame.K_LEFT:
            pos_change = -1
        elif key_action == pygame.K_RIGHT:
            pos_change = 1

        self.selected_option = (self.selected_option + pos_change) % len(self.selectable_positions)
        selected_position = self.selectable_positions[self.selected_option]

        line_dim = self.font.size(choice_line)[0]
        selected_rect = Rect(self.selectable_positions[0][0], self.selectable_positions[0][1],
                             line_dim, self.selector_thickness)
        self.screen.fill('black', selected_rect)
        x_start = selected_position[0]
        x_end = x_start + self.options_dimensions[self.selected_option][0]
        y = selected_position[1]
        pygame.draw.line(self.screen, 'white', (x_start, y), (x_end, y))
        pygame.display.flip()



class WinDisplayer(BasicDisplayer):
    def __init__(self, screen: pygame.Surface, states: GameStates, subscreen_rect):
        super().__init__(screen, states, subscreen_rect)
        self.line_selector_coords = None
        self.line_selector_x_start = None

    def display_win_screen(self):
        width = int(self.screen.get_width()) / 3
        height = int(self.screen.get_height()) / 3
        win_rect = pygame.Rect(width, height, width, height)
        pygame.draw.rect(self.screen, color='black', rect=win_rect)
        pygame.draw.rect(self.screen, color='white', rect=win_rect, width=4)
        self.font = pygame.font.Font(None, self.fontsize)
        if self.states.last_winner == 'Tie':
            first_win_line = 'It''s a tie!'
        else:
            first_win_line = f'Player {self.states.last_winner} wins!'
            self.states.score[self.states.last_winner-1] += 1

        win_text = [first_win_line,
                    'Play again?',
                    'Yes    No']
        label = []
        for line in win_text:
            label.append(self.font.render(line, True, 'white'))
        y_start = height + 15 * 3
        for line in range(len(label)):
            center_rect = label[line].get_rect(center=(width * 3 / 2, y_start + line * self.fontsize + 15 * line))
            self.screen.blit(label[line], center_rect)

        y_end = y_start + line * self.fontsize + 15 * line + self.fontsize / 2

        self.line_selector_x_start = width * 3 / 2 - self.font.size(win_text[-1])[0] / 2
        x_pos = self.states.replay_selector.get_x_replay_pos(self.font, self.line_selector_x_start)

        pygame.draw.line(self.screen, 'white', (x_pos[0], y_end), (x_pos[1], y_end), width=2)
        pygame.display.flip()

        self.line_selector_coords = [x_pos, y_end]


    def paint_selector_line(self):
        #to erase previous selected line
        self.display_win_screen()

        x_pos = self.line_selector_coords[0]
        y_end = self.line_selector_coords[1]
        #draw selector line
        pygame.draw.line(self.screen, 'white', (x_pos[0], y_end), (x_pos[1], y_end), width=2)
        pygame.display.flip()

    def switch_selector_line(self):
        self.states.replay_selector.switch_selection()
        self.line_selector_coords[0] = self.states.replay_selector.get_x_replay_pos(self.font, self.line_selector_x_start)

class ScoreDisplayer(BasicDisplayer):
    def __init__(self, screen:pygame.Surface, states:GameStates, subscreen_rect):
        super().__init__(screen, states, subscreen_rect)
        self.score = states.score

    def update_score(self, states: GameStates):
        self.score = states.score

    def paint_score(self):
        width = int(self.screen.get_width())
        self.font = pygame.font.Font(None, self.fontsize)
        score1 = int((self.score[0][0]))
        score2 = int((self.score[1][0]))

        size1 = self.font.size(str(score1))
        size2 = self.font.size(str(score2))

        rect_sx = Rect((0,0), size1)
        rect_dx = Rect((width - size2[0],0), size2)

        score1 = self.font.render(f'{score1}', True, 'white')
        score2 = self.font.render(f'{score2}', True, 'white')

        self.screen.fill('black', rect_sx)
        self.screen.blit(score1, (0, 0))
        self.screen.fill('black', rect_dx)
        self.screen.blit(score2, (width-size2[0], 0))

        pygame.display.flip()


class TextHandler():
    def __init__(self, font, fulltext, start_coords):
        self.font = font
        self.fulltext = fulltext
        self.start_coords = start_coords

    def get_start_positions(self):
        start_positions = [self.start_coords]
        first_option = self.fulltext.split(' ')[0]
        options_dimensions = [self.font.size(first_option)]
        options_counter = 1
        for i in range(len(self.fulltext)):
            if self.fulltext[i] == ' ' and self.fulltext[i+1] != ' ':
                option = (self.fulltext[i+1:]).split(' ')[0]
                options_counter += 1
                x_start = self.start_coords[0] + self.font.size(self.fulltext[0:i+1])[0]
                y_start = self.start_coords[1]
                start_positions.append((x_start, y_start))
                options_dimensions.append(self.font.size(option))
        return start_positions, options_dimensions

class TrisCPU():
    def __init__(self, grid: TrisGrid, states: GameStates):
        self.grid = grid
        self.states = states

    def play(self):
        coords = self.check_winning_condition(factor=-1) #to win
        if coords is not None:
            self.grid.grid_values[coords] = -1
            return coords

        coords = self.check_winning_condition(factor=1) #to block lose con
        if coords is not None:
            self.grid.grid_values[coords] = -1
            return coords


        filled_slots = self.check_any_filled_slot(factor=1)
        if filled_slots is not None:
            coords = self.find_optimal_slot(filled_slots)
        else:
            coords = self.free_action()
        #check if any row has 1 o
        #if yes then check if there is a free slot in any direction from it
        #if yes then add first free slot in the direction
        #if not then add random/first free slot
        #if not random/first free slot
        #otherwise attack
        #first empty box
        # self.states.turn_count += 1
        self.grid.grid_values[tuple(coords)] = -1
        return coords

    def check_winning_condition(self, factor):
        win_cond_value = 2 * factor
        oblique_sum1 = self.grid.grid_values[0, 0] + self.grid.grid_values[1, 1] + self.grid.grid_values[2, 2]
        oblique_sum2 = self.grid.grid_values[0, 2] + self.grid.grid_values[1, 1] + self.grid.grid_values[2, 0]

        h_sum = np.sum(self.grid.grid_values, axis=1)
        v_sum = np.sum(self.grid.grid_values, axis=0)

        if oblique_sum1 == win_cond_value:
            for i in range(3):
                if self.grid.grid_values[i,i] == 0:
                    coords = (i,i)
                    return coords

        if oblique_sum2 == win_cond_value:
            for i in range(3):
                if self.grid.grid_values[i,2-i] == 0:
                    coords = (i,2-i)
                    return coords

        h_sum_cond = (h_sum == win_cond_value)
        if any(h_sum_cond):
            free_idx = np.arange(3)[h_sum_cond][0]
            for i in range(3):
                if self.grid.grid_values[free_idx, i] == 0:
                    coords = (free_idx, i)
                    return coords

        v_sum_cond = (v_sum == win_cond_value)
        if any(v_sum_cond):
            free_idx = np.arange(3)[v_sum_cond][0]
            for i in range(3):
                if self.grid.grid_values[i, free_idx] == 0:
                    coords = (i, free_idx)
                    return coords

        return None

    def check_any_filled_slot(self, factor):
        value_to_check = -1 * factor
        filled_slots = (self.grid.grid_values == value_to_check)
        if filled_slots.any():
            return filled_slots
        else:
            return None

    def free_action(self, random=False):
        free_slots = np.argwhere(self.grid.grid_values==0)
        if random:
            #this gets passed if match is over anyway and choice doesn't matter
            coords = free_slots[randint(0,len(free_slots)-1)]
        else:
            #in this case we can do something smart possibly
            if self.grid.grid_values[1,1] == 0:
                coords = (1,1)
            else:
                coords = free_slots[0]
        return coords

    def find_optimal_slot(self, filled_slots):
        best_coords = self.lay_trap()
        if best_coords is not None:
            return best_coords
        else:
            candidate_matrix = self.find_optimal_direction(filled_slots)
            if candidate_matrix is None:
                coords = self.free_action(random=True)
                return coords

            best_coords = self.pick_among_candidates(candidate_matrix)
            #find optimal direction: return matrix with highest value in most optimal slot
                #check only in directions with 1 o and 0 x
                #if there is no free direction then return and do free action
            #get most optimal slot from matrix

        return best_coords

    def find_optimal_direction(self, filled_slots):
        #get coords of os
        coords = np.argwhere(filled_slots)
        candidate_matrix = np.zeros((3,3))

        #check for each slot if any direction is free
        for coord in coords:
            #horizontal check
            h_check = True
            for i in range(3):
                if self.grid.grid_values[coord[0], i] == 1:
                    h_check = False

            if h_check:
                candidate_matrix[coord[0], :] += 1

            #vertical check
            v_check = True
            for i in range(3):
                if self.grid.grid_values[i, coord[1]] == 1:
                    v_check = False

            if v_check:
                candidate_matrix[:, coord[1]] += 1

            #oblique1 check
            oblique_1 = [(x,x) for x in range(3)]
            if tuple(coord) in oblique_1:
                if np.trace(self.grid.grid_values) == -1:
                    candidate_matrix = candidate_matrix + np.eye(3)

            #oblique2 check
            oblique_2 = [(x,2-x) for x in range(3)]
            if tuple(coord) in oblique_2:
                if np.trace(np.flip(self.grid.grid_values)) == -1:
                    candidate_matrix = candidate_matrix + np.flip(np.eye(3))

        #assign 0 to candidate matrix wherever filled slots is not 0
        candidate_matrix[self.grid.grid_values != 0] = 0

        #if candidate matrix is 0 everywhere (as there is not a winning stategy) then return None
        if np.sum(candidate_matrix) == 0:
            return None

        return candidate_matrix

    def pick_among_candidates(self, candidate_matrix):
        #for now first choice
        best_coords = np.unravel_index(np.argmax(candidate_matrix), np.shape(candidate_matrix))
        return best_coords

    def lay_trap(self):
        #if central is o
        #place o in corner:
        #if x is in one corner -->priority to opposite corner
        #else take first available corner
        #else
        #take one of the corners:
        #if a corner is already o then pick closest corner
        #else first available corner
        central_value = self.grid.grid_values[1,1]
        max_dim = np.size(self.grid.grid_values, axis=0) - 1
        corner_positions = [(0,0), (0, max_dim), (max_dim, 0), (max_dim, max_dim)]
        if central_value == -1:
            x_pos = np.argwhere(self.grid.grid_values == 1)
            x_pos = [tuple(x) for x in x_pos.tolist()]
            x_in_corner = set(x_pos).intersection(set(corner_positions))
            if len(x_in_corner) == 1:
                x_in_corner = list(x_in_corner)[0]
                opposite_corner = (get_opposite_index(x_in_corner[0], 3), get_opposite_index(x_in_corner[1], 3))
                if self.grid.grid_values[opposite_corner[0], opposite_corner[1]] == 0:
                    return opposite_corner
                else:
                    for corner in corner_positions:
                        if self.grid.grid_values[corner[0], corner[1]] == 0:
                            return corner
            else:
                for corner in corner_positions:
                    if self.grid.grid_values[corner[0], corner[1]] == 0:
                        return corner
        else:
            corner_copy = corner_positions.copy()
            for corner in corner_positions:
                if self.grid.grid_values[corner[0], corner[1]] == -1:
                    opposite_corner = (get_opposite_index(corner[0], 3), get_opposite_index(corner[1], 3))
                    corner_copy.remove(corner)
                    corner_copy.remove(opposite_corner)

            if corner_copy != corner_positions:
                for corner in corner_copy:
                    if self.grid.grid_values[corner[0], corner[1]] == 0:
                        return corner
            else:
                for corner in corner_positions:
                    if self.grid.grid_values[corner[0], corner[1]] == 0:
                        return corner
        return None


def get_opposite_index(idx, len):
    mid_idx = floor(len / 2)
    if idx < mid_idx:
        return (mid_idx-idx) + idx + 1
    elif idx > mid_idx:
        return mid_idx - (idx-mid_idx)
    else:
        return mid_idx
