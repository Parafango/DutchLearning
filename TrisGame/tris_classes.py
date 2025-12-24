import pygame.font
from pygame import Rect
import numpy as np
import sys

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


class GameStates():
    def __init__(self):
        self.turn_count = 0
        self.score = np.zeros((2,1))
        self.replay_selector = ReplaySelector()
        self.restart_game = False
        self.quit_game = False

    def determine_turn(self):
        if self.turn_count % 2 == 0:
            return 'x'
        else:
            return 'o'

    def reset_states(self):
        self.turn_count = 0
        self.restart_game = False
        self.replay_selector = ReplaySelector()


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
