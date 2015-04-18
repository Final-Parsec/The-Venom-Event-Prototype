from utilities import euclid
from animation import Animation
from world_objects.server.plaftorms import ServerStep, ServerSpringPlatform, ServerPlatform, ServerMovingPlatform,\
    ServerDestructiblePlatform, ServerStairs


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************Platform*************************************************
#*************************************************************************************************************
#*************************************************************************************************************
class Platform(ServerPlatform):

    def __init__(self, start_position, width, height, image_list, velocity=euclid.Vector2(0.0, 0.0)):
        ServerPlatform.__init__(self, start_position, width, height, velocity)
        self.rect = self.server_rect.get_pygame_rect()
        self.animation = Animation(image_list, self)
        self.image = self.animation.current_image()

    def update(self):
        super(Platform, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class MovingPlatform(ServerMovingPlatform, Platform):

    def __init__(self, start_position, width, height, image, velocity=euclid.Vector2(0.0, 50.0),
                 max_displacement=euclid.Vector2(0, 250)):
        Platform.__init__(self, start_position, width, height, image, velocity)
        ServerMovingPlatform.__init__(self, start_position, width, height, velocity, max_displacement)


class DestructiblePlatform(ServerDestructiblePlatform, Platform):

    def __init__(self, start_position, width, height, image, health=100):
        Platform.__init__(self, start_position, width, height, image)
        ServerDestructiblePlatform.__init__(self, start_position, width, height, health)

#*************************************************************************************************
#*************************************************************************************************
#listens for bullets hitting it
    def on_collision(self, actor, direction):
        #call super
        super(DestructiblePlatform, self).on_collision(actor, direction)

        self.image = self.animation.image_list[0].copy()  # image at position 0 is full health
        interval = self.max_health / (len(self.animation.image_list) - 1)
        self.image.blit(self.animation.image_list[(len(self.animation.image_list) - 1) - (self.health / interval)],
                        (0, 0))

    def update(self):
        super(DestructiblePlatform, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class SpringPlatform(ServerSpringPlatform, Platform):

    def __init__(self, start_position, width, height, image, launch_velocity=euclid.Vector2(0.0, 1000.0)):
        Platform.__init__(self, start_position, width, height, image)
        ServerSpringPlatform.__init__(self, start_position, width, height, launch_velocity)

    def update(self):
        super(SpringPlatform, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class Stairs(ServerStairs, Platform):
    """Makes a block of stairs the players can run up"""

    def __init__(self, start_position, width, height, image, number_of_steps, direction):
        Platform.__init__(self, start_position, width, height, image)
        ServerStairs.__init__(self, start_position, width, height, number_of_steps, direction)

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

            hitboxes.append(Step(step_left, step_top, step_width, step_height))

        return hitboxes

    def update(self):
        super(Stairs, self).update()
        for step in self.steps:
            step.update()
        self.rect = self.server_rect.get_pygame_rect()


class Step(ServerStep):
    """used to detect collisions for players"""

    def __init__(self, step_left, step_top, step_width, step_height):
        ServerStep.__init__(self, step_left, step_top, step_width, step_height)
        self.rect = self.server_rect.get_pygame_rect()

    def update(self):
        super(Step, self).update()
        self.rect = self.server_rect.get_pygame_rect()