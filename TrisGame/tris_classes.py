import pygame
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


class GameStates():
    def __init__(self):
        self.turn_count = 0
        self.score = np.zeros((2,1))
        self.replay_selector = ReplaySelector()
        self.restart_game = False
        self.quit_game = False
        self.last_winner = None

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

class BasicDisplayer():
    def __init__(self, screen: pygame.Surface, states: GameStates, fontsize):
        self.screen = screen
        self.states = states
        self.fontsize = fontsize
        self.font = None

class WinDisplayer(BasicDisplayer):
    def __init__(self, screen: pygame.Surface, states: GameStates, fontsize):
        super().__init__(screen, states, fontsize)
        self.line_selector_coords = None
        self.line_selector_x_start = None

    def display_win_screen(self):
        width = int(self.screen.get_width()) / 3
        height = int(self.screen.get_height()) / 3
        win_rect = pygame.Rect(width, height, width, height)
        pygame.draw.rect(self.screen, color='black', rect=win_rect)
        pygame.draw.rect(self.screen, color='white', rect=win_rect, width=4)
        self.font = pygame.font.Font(None, self.fontsize)
        win_text = [f'Player {self.states.last_winner} wins!',
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
