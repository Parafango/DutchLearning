from typing import Tuple

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