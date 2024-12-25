import pygame
from custom_classes import Player, Truck

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

#initialize truck and player instances
player_radius = 30
player_speed = 300
player_pos = [screen.get_width() / 2, screen.get_height()]
player = Player(player_pos, player_radius, player_speed)
truck_size = [80, 40]
truck_speed = 150
truck_lefttop = [screen.get_width() - truck_size[0], screen.get_height()/2]
truck = Truck(truck_lefttop, truck_size, truck_speed)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    pygame.draw.circle(screen, "red", player.pos, player.radius)
    pygame.draw.rect(screen, "white", truck.rect)

    keys = pygame.key.get_pressed()
    player.update_position(keys, dt)

    truck.rect = truck.rect.move(truck.velocity * dt)
    truck.reset_if_outofbounds(screen)
    player = truck.simulate_crash(player)
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()




