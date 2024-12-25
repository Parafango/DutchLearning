import pygame
import numpy as np

class Player():
    def __init__(self, pos, radius, speed):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.crashed = False
        self.velocity = np.asarray([0,0])

    def update_position(self, keys, dt):
        moving_keys = {pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d}
        is_moving = False
        for key in moving_keys:
            if keys[key]:
                is_moving = True
                break

        if not self.crashed:
            if not is_moving:
                self.velocity = np.asarray([0, 0])
            else:
                #TODO: fix original component not getting updated if another key is pressed before
                #the original one is released
                if keys[pygame.K_w]:
                    self.velocity[1] = - self.speed
                if keys[pygame.K_s]:
                    self.velocity[1] = self.speed
                if keys[pygame.K_a]:
                    self.velocity[0] = - self.speed
                if keys[pygame.K_d]:
                    self.velocity[0] = self.speed

        self.pos += self.velocity * dt

class Truck():
    def __init__(self, lefttop, wh, speed):
        self.leftop = lefttop
        self.wh = wh
        self.rect = pygame.Rect(lefttop, wh)
        self.speed = speed
        self.velocity = np.asarray([-speed, 0])

    def reset_if_outofbounds(self, screen):
        if self.rect.right < 0:
            self.rect.move_ip(screen.get_width() + self.rect.w, 0)
        if self.rect.left > screen.get_width():
            self.rect.move_ip(-screen.get_width() - self.rect.w, 0)
        if self.rect.bottom < 0:
            self.rect.move_ip(0, screen.get_height() + self.rect.h)
        if self.rect.top > screen.get_height():
            self.rect.move_ip(0, -screen.get_height() - self.rect.h)

    def simulate_crash(self, player: Player):
        collision_coord = self.detect_collision(player)
        if isinstance(collision_coord, np.ndarray):
            self.get_crash_speed(player, collision_coord)

        return player


    def detect_collision(self, player: Player):
        #calculate coordinates of circumference
        n_points = 24
        circum_coord = np.vstack((np.linspace(0, 2 * np.pi, n_points), np.linspace(0, 2 * np.pi, n_points)))
        circum_coord[0, :] = player.radius * np.cos(circum_coord[0, :])
        circum_coord[1, :] = player.radius * np.sin(circum_coord[1, :])
        circum_coord[0, :] += player.pos[0]
        circum_coord[1, :] += player.pos[1]
        circum_collides = np.zeros(n_points)
        #test if coordinates of player are in rectangle
        for i in range(n_points):
            circum_collides[i] = self.rect.collidepoint(circum_coord[:, i])

        idxs = np.where(circum_collides==1)[0]
        if len(idxs) == 0:
            return None
        else:
            return  circum_coord[:, idxs[0]]

    def get_crash_speed(self, player: Player, collision_coord: np.ndarray):
        center_x = self.rect.left + self.rect.w / 2
        center_y = self.rect.top + self.rect.h / 2
        angle = np.arctan2((collision_coord[1] - center_y), (collision_coord[0] - center_x))
        player.velocity[0] = player.speed * np.cos(angle)
        player.velocity[1] = player.speed * np.sin(angle)
        player.crashed = True
