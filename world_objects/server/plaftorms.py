import math

from utilities import euclid
from world_objects import WorldObject, get_displacement
from world_objects.server.projectiles import ServerProjectile


class ServerPlatform(WorldObject):
    """boring old platform"""
    def __init__(self, start_position, width, height, velocity=euclid.Vector2(0.0, 0.0)):
        WorldObject.__init__(self, start_position=start_position, width=width, height=height, velocity=velocity)

    def detect_collision(self, rects):
        """no collision detection for default platforms"""
        pass

    def move(self, delta_time):
        """default platforms don't move"""
        pass


class ServerMovingPlatform(ServerPlatform):
    """moves in both the x and y directions"""

    def __init__(self, start_position, width, height, velocity=euclid.Vector2(0.0, 10.0),
                 max_displacement=euclid.Vector2(0, 5)):
        ServerPlatform.__init__(self, start_position, width, height, velocity)
        self.max_displacement = max_displacement  # in pixels
        self.initial_position = start_position.copy()

    def move(self, delta_time):
        """move the platform and see if it has moved too far"""
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)
        self.start_position += self.velocity * delta_time
        self.correct_position()
        self.reset_rects()

    def correct_position(self):
        """tests if the platform has moved too far and corrects it"""

        displacement_vector = get_displacement(self.initial_position, self.start_position)
        if self.start_position.x != self.initial_position.x and displacement_vector.x > self.max_displacement.x:
            #either -1 or 1
            #(-)...(+)
            direction_x = (self.start_position.x - self.initial_position.x) / math.fabs(self.start_position.x -
                                                                                        self.initial_position.x)
            #correct position
            self.start_position.x = self.initial_position.x + (self.max_displacement.x * direction_x)
            #change polarity
            self.velocity.x *= -1.0

        if self.start_position.y != self.initial_position.y and displacement_vector.y > self.max_displacement.y:
            #(-)
            #.
            #(+)
            direction_y = (self.start_position.y - self.initial_position.y) / math.fabs(self.start_position.y -
                                                                                        self.initial_position.y)
            self.start_position.y = self.initial_position.y + (self.max_displacement.y * direction_y)
            self.velocity.y *= -1.0

    def on_collision(self, actor, direction):
        if direction == 'above':
            actor.velocity += self.velocity


class ServerDestructiblePlatform(ServerPlatform):

    def __init__(self, start_position, width, height, health=100):
        ServerPlatform.__init__(self, start_position, width, height)
        self.health = health
        self.max_health = self.health

    def on_collision(self, actor, direction):
        """listens for bullets hitting it"""
        if type(actor) is ServerProjectile:
            if actor.can_break_rocks:
                self.health -= actor.shot_from.damage
            if self.health <= 0.0:
                self.is_alive = False
                return


class ServerSpringPlatform(ServerPlatform):

    def __init__(self, start_position, width, height, launch_velocity=euclid.Vector2(0.0, 1000.0)):
        ServerPlatform.__init__(self, start_position, width, height)
        self.launch_velocity = launch_velocity

#*************************************************************************************************
#*************************************************************************************************
#updates position and velocity
    def on_collision(self, actor, direction):
        if direction == 'above':
            actor.velocity.y -= self.launch_velocity.y  # up if velocity is positive
            actor.velocity.x -= self.launch_velocity.x  # left if velocity is positive


class ServerStairs(ServerPlatform):
    """Makes a block of stairs the players can run up"""

    def __init__(self, start_position, height, length, number_of_steps, direction):
        ServerPlatform.__init__(self, start_position, height, length)
        self.steps = self.make_hitboxes(number_of_steps, direction)

    def make_hitboxes(self, number_of_steps, direction):
        """initializes the hitboxes that make up
            the steps"""
        hitboxes = []
        step_height = self.server_rect.height / number_of_steps
        delta_width = self.server_rect.width / number_of_steps
        left_start_position = self.server_rect.right - delta_width
        polarity = -1
        if direction == "left":
            left_start_position = self.server_rect.left
            polarity = 1

        for step in range(1, number_of_steps + 1):
            step_left = left_start_position + polarity * (step - 1.0) * delta_width
            step_top = self.server_rect.bottom - step * step_height
            step_width = self.server_rect.width - (step - 1.0) * delta_width

            hitboxes.append(ServerStep(step_left, step_top, step_width, step_height))

        return hitboxes


class ServerStep(WorldObject):
    """used to detect collisions for players"""

    def __init__(self, step_left, step_top, step_width, step_height):
        WorldObject.__init__(self, euclid.Vector2(step_left, step_top), step_width, step_height)