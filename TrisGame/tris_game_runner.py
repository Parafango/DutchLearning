import sys

import pygame
import numpy as np
from tris_classes import TrisGrid, GameStates


class TrisGameRunner():
    def __init__(self, config):
        self.config = config

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        running = True
        dt = 0
        grid = self.paint_grid(screen)
        states = GameStates()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(grid.grid_values)
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.update_grid(event, grid, states, screen)

            self.check_game_status(grid, states, screen)
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

        coords = self.check_click_grid(pos, grid, states)
        if coords is not None:
            self.draw_symbol(coords, states, grid, screen)
            states.turn_count += 1


    def draw_symbol(self, coords, states:GameStates, grid:TrisGrid, screen: pygame.Surface):
        x_center = coords[0] * grid.unit_size + grid.unit_size/2 + grid.left
        y_center = coords[1] * grid.unit_size + grid.unit_size / 2 + grid.top
        if states.determine_turn() == 'x':
            x_left = x_center - grid.unit_size * 2 / 6
            x_right = x_center + grid.unit_size * 2 / 6
            y_top = y_center + grid.unit_size * 2 / 6
            y_bottom = y_center +-grid.unit_size * 2 / 6
            pygame.draw.line(screen, 'white',(x_left, y_top), (x_right, y_bottom), width=4)
            pygame.draw.line(screen, 'white', (x_right, y_top), (x_left, y_bottom), width=4)
        elif states.determine_turn() == 'o':
            radius = grid.unit_size * 2/6
            pygame.draw.circle(screen, 'white',(x_center,y_center), radius)
        else:
            sys.exit('Something went wrong')
        pygame.display.flip()

    def check_click_grid(self, pos, grid: TrisGrid, states: GameStates):
        x_click = pos[0]
        y_click = pos[1]
        x_within = grid.right > x_click > grid.left
        y_within = grid.bottom > y_click > grid.top
        if x_within and y_within:
            for i in range(3):
                x_square = grid.left + grid.unit_size * i
                if x_square + grid.unit_size > x_click > x_square:
                    break

            for j in range(3):
                y_square = grid.top + grid.unit_size * j
                if y_square + grid.unit_size > y_click > y_square:
                    break

            turn_symbol = states.determine_turn()
            value = grid.map_symbol_to_value(turn_symbol)
            if grid.grid_values[i,j] == 0:
                grid.grid_values[i,j] = value
            else:
                return None
            coords = (i,j)
            return coords
        else:
            return None

    def check_game_status(self, grid:TrisGrid, states: GameStates, screen):
        winner = self.check_win_conditions(grid, states)
        if winner is not None:
            self.display_win_screen(screen, winner)


    def check_win_conditions(self, grid:TrisGrid, states: GameStates):
        oblique_sum1 = grid.grid_values[0,0] + grid.grid_values[1,1] + grid.grid_values[2,2]
        oblique_sum2 = grid.grid_values[0,2] + grid.grid_values[1,1] + grid.grid_values[2,0]

        h_sum = np.sum(grid.grid_values, axis=1)
        v_sum = np.sum(grid.grid_values, axis=0)

        p1_win_value = 3
        p2_win_value = -3
        if (any(h_sum==p1_win_value) or any(v_sum==p1_win_value) or
                (oblique_sum1==p1_win_value) or (oblique_sum2==p1_win_value)):
            states.score[0] += 1
            return 1
        elif (any(h_sum == p2_win_value) or any(v_sum == p2_win_value) or
              (oblique_sum1 == p2_win_value) or (oblique_sum2 == p2_win_value)):
            states.score[1] += 1
            return 2
        else:
            return None

    def display_win_screen(self, screen: pygame.Surface, winner):
        width = int(screen.get_width())/3
        height = int(screen.get_height())/3
        win_rect = pygame.Rect(width, height, width, height)
        pygame.draw.rect(screen, color='black', rect=win_rect)
        pygame.draw.rect(screen, color='white', rect=win_rect, width=4)
        font = pygame.font.Font(None, 64)
        win_text = f'Player {winner} wins!'
        win_surf = font.render(win_text, True, 'white')
        win_surf_rect = win_surf.get_rect(center=(width * 3 / 2, height * 3 / 2))
        screen.blit(win_surf, win_surf_rect)
        pygame.display.flip()