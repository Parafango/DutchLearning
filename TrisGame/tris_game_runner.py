import pygame
import numpy as np

class TrisGameRunner():
    def __init__(self, config):
        self.config = config

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        running = True
        dt = 0
        self.paint_grid(screen)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
        return




