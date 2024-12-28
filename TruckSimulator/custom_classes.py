import pygame
import numpy as np
from sympy.physics.units import velocity
from sympy.solvers import solve, nsolve
from sympy import var, Eq, real_root
import sympy
import inspect


class Player():
    def __init__(self, pos, radius, speed, mass):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.crashed = False
        self.velocity = np.asarray([0,0])
        self.mass = mass

    def update_position(self, keys, dt):
        moving_keys = {pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT,
                       pygame.K_LEFT}
        is_moving = False
        for key in moving_keys:
            if keys[key]:
                is_moving = True
                break

        if not self.crashed:
            if not is_moving:
                self.velocity = np.asarray([0, 0])
            else:
                #set velocity to zero to erase previous frame values
                self.velocity = np.asarray([0, 0])
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.velocity[1] = self.velocity[1] - self.speed
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.velocity[1] = self.velocity[1] + self.speed
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.velocity[0] = self.velocity[0] - self.speed
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.velocity[0] = self.velocity[0] + self.speed

        self.pos += np.asarray(list(map(int, self.velocity * dt)))

    def reset_if_outofbounds(self, screen: pygame.Surface):
        if self.pos[0] - self.radius > screen.get_width():
            self.pos[0] = -self.radius
        if self.pos[0] + self.radius < 0:
            self.pos[0] = screen.get_width() + self.radius
        if self.pos[1] - self.radius > screen.get_height():
            self.pos[1] = - self.radius
        if self.pos[1] + self.radius < 0:
            self.pos[1] = screen.get_height() + self.radius

    def movement(self, keys, dt, screen: pygame.Surface):
        self.update_position(keys, dt)
        self.reset_if_outofbounds(screen)



class Truck():
    def __init__(self, lefttop, wh, speed, mass):
        self.leftop = lefttop
        self.wh = wh
        self.rect = pygame.Rect(lefttop, wh)
        self.speed = speed
        self.velocity = np.asarray([-speed, 0])
        self.mass = mass

    def update_position(self, dt):
        self.rect.move_ip(self.velocity * dt)

    def reset_if_outofbounds(self, screen: pygame.Surface):
        if self.rect.right < 0:
            self.rect.move_ip(screen.get_width() + self.rect.w, 0)
        if self.rect.left > screen.get_width():
            self.rect.move_ip(-screen.get_width() - self.rect.w, 0)
        if self.rect.bottom < 0:
            self.rect.move_ip(0, screen.get_height() + self.rect.h)
        if self.rect.top > screen.get_height():
            self.rect.move_ip(0, -screen.get_height() - self.rect.h)

    def movement(self, dt, screen: pygame.Surface):
        self.update_position(dt)
        self.reset_if_outofbounds(screen)

    def simulate_crash(self, player: Player):
        collision_coord = self.detect_collision(player)
        if isinstance(collision_coord, np.ndarray) and not player.crashed:
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
        inelastic = True

        truck_gx = self.rect.left + self.rect.w / 2
        truck_gy = self.rect.top + self.rect.h / 2
        alfa = np.arctan2((collision_coord[1] - truck_gy), (collision_coord[0] - truck_gx))
        beta = np.arctan2((collision_coord[1] - player.pos[1]), (collision_coord[0] - player.pos[0]))


        v1i = np.sqrt(np.sum(np.square(self.velocity)))
        v2i = np.sqrt(np.sum(np.square(player.velocity)))
        theta1i = np.arctan2(self.velocity[1], self.velocity[0])
        theta2i = np.arctan2(player.velocity[1], player.velocity[0])
        angle_scaler1 = player.mass * v2i / (self.mass * v1i)
        angle_scaler2 = (self.mass * v1i - player.mass * v2i) / (self.mass * v1i)

        angles = [alfa, beta, theta1i, theta2i]
        updated_angles = [angles_to_02pi(angle) for angle in angles]
        alfa, beta, theta1i, theta2i = updated_angles

        theta1f = theta1i + angle_scaler1 * (beta - theta1i)
        theta2f = theta2i + angle_scaler2 * (alfa - theta2i)

        if inelastic:
            sol = linear_momentum_conservation_2d_perf_inelastic(m1=self.mass, m2=player.mass, v1i=v1i, v2i=v2i,
                                                                 theta1i=theta1i,
                                                                 theta2i=theta2i, v12=None, theta12=None)
            sol = list(sol[0].values())
            v12 = float(sol[0])
            theta12 = float(sol[1])

            self.velocity[0] = v12 * np.cos(theta12)
            self.velocity[1] = v12 * np.sin(theta12)

            player.velocity[0] = self.velocity[0]
            player.velocity[1] = self.velocity[1]
        else:
            sol = linear_momentum_conservation_2d(m1=self.mass, m2=player.mass, v1i=v1i, v2i=v2i, theta1i=theta1i,
                                                  theta2i=theta2i, theta1f=None, theta2f=theta2f, v1f=None, v2f=None)
            sol = list(sol[0].values())

            theta1f = sol[0]

            self.velocity[0] = sol[1] * np.cos(theta1f)
            self.velocity[1] = sol[1] * np.sin(theta1f)

            player.velocity[0] = sol[2] * np.cos(theta2f)
            player.velocity[1] = sol[2] * np.sin(theta2f)

        player.crashed = True


def linear_momentum_conservation_2d(**kwargs):

    unknowns = []

    for key, value in kwargs.items():
        if value is None:
            kwargs[key] = sympy.symbols(key, real=True)
            unknowns.append(key)


    if len(unknowns) > 3:
        raise (f'Too many unknowns, number of equations is 3 while number of unknowns is {len(unknowns)}')



    eqx = Eq(kwargs['m1'] * kwargs['v1i'] * sympy.cos(kwargs['theta1i']) + kwargs['m2'] * kwargs['v2i'] * sympy.cos(
        kwargs['theta2i']) -
             kwargs['m1'] * kwargs['v1f'] * sympy.cos(kwargs['theta1f']) - kwargs['m2'] * kwargs['v2f'] * sympy.cos(
        kwargs['theta2f']), 0)
    eqy = Eq(kwargs['m1'] * kwargs['v1i'] * sympy.sin(kwargs['theta1i']) + kwargs['m2'] * kwargs['v2i'] * sympy.sin(
        kwargs['theta2i']) -
             kwargs['m1'] * kwargs['v1f'] * sympy.sin(kwargs['theta1f']) - kwargs['m2'] * kwargs['v2f'] * sympy.sin(
        kwargs['theta2f']), 0)
    eqe = Eq((0.5 * kwargs['m1'] * kwargs['v1i'] **2 + 0.5 * kwargs['m2'] * kwargs['v2i'] **2) -
             0.5 * kwargs['m1'] * kwargs['v1f'] **2 - 0.5 * kwargs['m2'] * kwargs['v2f'] **2, 0)

    sol = solve([eqx, eqy, eqe], unknowns[0], unknowns[1], unknowns[2], dict=True)
    Ki = 0.5 * kwargs['m1'] * kwargs['v1i'] **2 + 0.5 * kwargs['m2'] * kwargs['v2i'] **2
    Kf = 0.5 * kwargs['m1'] * sol[0][kwargs['v1f']] **2 + 0.5 * kwargs['m2'] * sol[0][kwargs['v2f']] **2
    if Kf > Ki:
        print(f'Kinetic energy is not conserved. Kf-Ki={Kf-Ki}')
    return sol

def linear_momentum_conservation_2d_perf_inelastic(**kwargs):

    unknowns = []

    for key, value in kwargs.items():
        if value is None:
            kwargs[key] = sympy.symbols(key, real=True)
            unknowns.append(key)


    if len(unknowns) > 2:
        raise (f'Too many unknowns, number of equations is 2 while number of unknowns is {len(unknowns)}')



    eqx = Eq(kwargs['m1'] * kwargs['v1i'] * sympy.cos(kwargs['theta1i']) + kwargs['m2'] * kwargs['v2i'] * sympy.cos(
        kwargs['theta2i']) - (kwargs['m1'] + kwargs['m2']) * kwargs['v12'] * sympy.cos(kwargs['theta12']), 0)
    eqy = Eq(kwargs['m1'] * kwargs['v1i'] * sympy.sin(kwargs['theta1i']) + kwargs['m2'] * kwargs['v2i'] * sympy.sin(
        kwargs['theta2i']) - (kwargs['m1'] + kwargs['m2']) * kwargs['v12'] * sympy.sin(kwargs['theta12']), 0)

    sol = nsolve([eqx, eqy], [kwargs['v12'], kwargs['theta12']], [kwargs['v1i'], kwargs['theta1i']], dict=True)
    Ki = 0.5 * kwargs['m1'] * kwargs['v1i'] **2 + 0.5 * kwargs['m2'] * kwargs['v2i'] **2
    Kf = 0.5 * (kwargs['m1'] + kwargs['m2']) * sol[0][kwargs['v12']] **2
    if Kf > Ki:
        print(f'Kinetic energy is not conserved. Kf-Ki={Kf-Ki}')
    return sol

def angles_to_02pi(angle):
    if angle < 0:
        angle = angle + 2 * np.pi
    return angle