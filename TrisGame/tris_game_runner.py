import sys

import pygame
import numpy as np

from TrisGame.tris_classes import BasicDisplayer, WinDisplayer, ScoreDisplayer, TrisCPU
from tris_classes import TrisGrid, GameStates
import time

class TrisGameRunner():
    def __init__(self, config):
        self.config = config

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        running = True
        dt = 0
        grid, states = self.start_game(screen)
        score_displayer = ScoreDisplayer(screen, states, None)
        CPU_player = TrisCPU(grid, states)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.update_grid(event, grid, states, screen)

            if states.game_options.gamemode == 1 and states.determine_turn() == 'o':
                winner = self.check_win_conditions(grid, states)
                if winner is None:
                    coords = CPU_player.play()
                    grid.draw_symbol(coords, states, screen)
                    states.turn_count += 1

            self.check_game_status(grid, states, screen, score_displayer)
            if states.restart_game:
                grid = self.restart_game(screen)
                states.reset_states()
                states.increment_round()
                CPU_player.change_turn_order()
                CPU_player.grid = grid
                CPU_player.states = states

            if states.quit_game:
                self.quit_screen(screen, states)
                running = False
            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = clock.tick(60) / 1000

        pygame.quit()

    def paint_grid(self, screen: pygame.Surface):
        screen.fill('black')
        width = int(screen.get_width())
        height = int(screen.get_height())

        square_size = height / 4
        buffer_w = (width - square_size * 3) / 2

        #horizontal
        pygame.draw.line(screen, 'white', (0 + buffer_w, height*3/8),
                         (width - buffer_w, height*3/8), width=3)
        pygame.draw.line(screen, 'white', (0 + buffer_w, height*5/8),
                         (width - buffer_w, height*5/8), width=3)

        #vertical
        pygame.draw.line(screen, 'white', ((width-square_size)/2, height/8),
                         ((width-square_size)/2, height*7/8), width=3)
        pygame.draw.line(screen, 'white', ((width+square_size)/2, height/8),
                         ((width+square_size)/2, height*7/8), width=3)

        pygame.display.flip()
        grid = TrisGrid(0+buffer_w, height/8, width-2*buffer_w, height*3/4)
        return grid

    def update_grid(self, click_event: pygame.event.Event, grid: TrisGrid, states: GameStates, screen: pygame.Surface):
        pos = click_event.pos

        coords = grid.check_click_grid(pos, states)
        if coords is not None:
            grid.draw_symbol(coords, states, screen)
            states.turn_count += 1

    def check_game_status(self, grid:TrisGrid, states: GameStates, screen, score_displayer: ScoreDisplayer):
        winner = self.check_win_conditions(grid, states)
        score_displayer.update_score(states)
        score_displayer.paint_score()
        if winner is not None:
            states.last_winner = winner
            grid.reset_values()
            win_displayer = WinDisplayer(screen, states, None)
            win_displayer.display_win_screen()
            new_game_unselected = True
            while new_game_unselected:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            win_displayer.switch_selector_line()
                            win_displayer.paint_selector_line()
                        if event.key == pygame.K_RETURN:
                            if states.replay_selector.selected_value == 'y':
                                states.restart_game = True
                            elif states.replay_selector.selected_value == 'n':
                                states.quit_game = True
                            new_game_unselected = False
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()

    def check_win_conditions(self, grid:TrisGrid, states: GameStates):
        oblique_sum1 = grid.grid_values[0,0] + grid.grid_values[1,1] + grid.grid_values[2,2]
        oblique_sum2 = grid.grid_values[0,2] + grid.grid_values[1,1] + grid.grid_values[2,0]

        h_sum = np.sum(grid.grid_values, axis=1)
        v_sum = np.sum(grid.grid_values, axis=0)

        p1_win_value = 3
        p2_win_value = -3
        if (any(h_sum==p1_win_value) or any(v_sum==p1_win_value) or
                (oblique_sum1==p1_win_value) or (oblique_sum2==p1_win_value)):
            return 1
        elif (any(h_sum == p2_win_value) or any(v_sum == p2_win_value) or
              (oblique_sum1 == p2_win_value) or (oblique_sum2 == p2_win_value)):
            return 2
        elif self.is_game_over(grid):
            return 'Tie'
        else:
            return None

    def display_win_screen(self, screen: pygame.Surface, winner, states: GameStates):
        fontsize = states.game_options.fontsize
        width = int(screen.get_width())/3
        height = int(screen.get_height())/3
        win_rect = pygame.Rect(width, height, width, height)
        pygame.draw.rect(screen, color='black', rect=win_rect)
        pygame.draw.rect(screen, color='white', rect=win_rect, width=4)
        font = pygame.font.Font(None, fontsize)
        win_text = [f'Player {winner} wins!',
                    'Play again?',
                    'Yes    No']
        label = []
        for line in win_text:
            label.append(font.render(line, True, 'white'))
        y_start = height + 15 * 3
        for line in range(len(label)):
            center_rect = label[line].get_rect(center=(width * 3 / 2, y_start + line * fontsize + 15 * line))
            screen.blit(label[line], center_rect)

        y_end = y_start + line * fontsize + 15 * line + fontsize / 2

        x_start = width * 3 / 2 - font.size(win_text[-1])[0] / 2
        x_pos = states.replay_selector.get_x_replay_pos(font, x_start)

        pygame.draw.line(screen, 'white', (x_pos[0], y_end), (x_pos[1], y_end), width=2)
        pygame.display.flip()

        coords = [x_pos, y_end]
        return coords, font

    def paint_selector_line(self, screen: pygame.Surface, coords):
        x_pos = coords[0]
        y_end = coords[1]
        #draw selector line
        pygame.draw.line(screen, 'white', (x_pos[0], y_end), (x_pos[1], y_end), width=2)
        pygame.display.flip()
        return

    def restart_game(self, screen: pygame.Surface):
        grid = self.paint_grid(screen)
        grid.reset_values()
        return grid

    def quit_screen(self, screen: pygame.Surface, states: GameStates):
        screen.fill('black')
        fontsize = states.game_options.fontsize
        width = int(screen.get_width())/3
        height = int(screen.get_height())/3
        win_rect = pygame.Rect(width, height, width, height)
        pygame.draw.rect(screen, color='black', rect=win_rect)
        pygame.draw.rect(screen, color='white', rect=win_rect, width=4)
        font = pygame.font.Font(None, fontsize)
        win_text = 'Thanks for playing!'
        label = font.render(win_text, True, 'white')

        center_rect = label.get_rect(center=(width * 3 / 2, height * 3 / 2))
        screen.blit(label, center_rect)

        pygame.display.flip()

        time.sleep(4)

    def start_game(self, screen):
        states = GameStates()
        mode_selection_message = ['Welcome to Tris!',
                                  'Which mode do you want to play?',
                                  '1vs1    1vsCPU']
        #greet
        screen.fill('black')
        pygame.display.flip()

        #pick rect size
        w = int(screen.get_width())/2
        h = int(screen.get_height())/2
        displayer_rect = pygame.Rect(w/2,h/2,w,h)
        gamemode_displayer = BasicDisplayer(screen, states, displayer_rect)
        gamemode_displayer.display_choice_screen(mode_selection_message)
        gamemode_unselected = True
        while gamemode_unselected:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        gamemode_displayer.update_choice_screen(mode_selection_message[-1], event.key)
                    if event.key == pygame.K_RETURN:
                        if gamemode_displayer.selected_option == 0:
                            states.game_options.gamemode = 0
                        elif gamemode_displayer.selected_option == 1:
                            states.game_options.gamemode = 1
                        gamemode_unselected = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        grid = self.paint_grid(screen)

        return grid, states

    def is_game_over(self, grid):
        is_game_over = np.all(grid.grid_values != 0)
        return is_game_over