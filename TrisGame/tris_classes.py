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

    def determine_turn(self):
        if self.turn_count % 2 == 0:
            return 'x'
        else:
            return 'o'