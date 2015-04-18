import math

import pygame

from utilities import euclid
from world_objects import get_vector_to_position
from world_objects.server.projectiles import ServerChain, ServerGrapple, ServerPredatorMissile, ServerProjectile, ServerRocket, \
    ServerGrenade
from animation import Animation


chainImage = pygame.image.load("resources/images/Grapple Rope.png")


class Projectile(ServerProjectile):
    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerProjectile.__init__(self, center, shot_from, player, velocity, gravity)

        bullet_position_vector = euclid.Vector2(self.velocity.x / shot_from.bullet_velocity,
                                                self.velocity.y / shot_from.bullet_velocity)
        self.rect = self.server_rect.get_pygame_rect()
        self.animation = Animation([self.shot_from.bullet_image_list[0]], self)  # image for in flight projectile
        self.image = pygame.transform.rotate(self.animation.current_image(),
                                             self.roto_theta_conversion_tool_extreme(bullet_position_vector))

    def update(self):
        super(Projectile, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class Grapple(ServerGrapple, Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):
        """can you handle the inheritance"""
        ServerGrapple.__init__(self, center, shot_from, player, velocity, gravity)
        Projectile.__init__(self, center, shot_from, player, velocity, gravity)

    def update(self):
        self.image = pygame.transform.rotate(self.animation.current_image(), self.rotation_theta)

        for link in self.chain:
            link.image = pygame.transform.rotate(link.animation.current_image(), link.rotation_theta)

        #call ServerGrapple update()
        super(Grapple, self).update()
        self.rect = self.server_rect.get_pygame_rect()

    def make_chain(self):
        """override to make Chains not ServerChains"""
        #creates and updates the link positions
        new_chain = []
        my_center = self.get_center()
        player_center = self.player.get_center()
        distance_line = math.sqrt(math.pow(player_center.x - my_center.x, 2) +
                                  math.pow(player_center.y - my_center.y, 2))
        link_distance = math.sqrt(math.pow(self.link_size.x - 3.0, 2) + math.pow(self.link_size.y - 3.0, 2))
        number_of_links_int = int(math.ceil(distance_line / link_distance))
        exact_number_of_links = distance_line / link_distance

        if exact_number_of_links != 0:
            x_increment = (player_center.x - my_center.x) / exact_number_of_links
            y_increment = (player_center.y - my_center.y) / exact_number_of_links
        else:
            return new_chain

        for x in range(0, number_of_links_int):
            link_position = euclid.Vector2(player_center.x - (x * x_increment), player_center.y - (y_increment * x))
            if x < len(self.chain):
                self.chain[x].set_center(link_position)
            else:
                self.chain.append(Chain(link_position, self.link_size.x, self.link_size.y, [chainImage], self))
                new_chain.append(self.chain[-1])

        #kills a link when the player moves forward
        #all the links are killed when the grapple is killed, but that is done in the chain update method
        if number_of_links_int < len(self.chain):
            for x in range(number_of_links_int, len(self.chain)):
                self.chain[-1].is_alive = False
                self.chain.pop()

        #makes the grapple always face the player
        self.rotation_theta = self.roto_theta_conversion_tool_extreme(get_vector_to_position(my_center, player_center))

        #makes the links point to the center of the player
        for x in range(0, len(self.chain)):
            theta = self.roto_theta_conversion_tool_extreme(get_vector_to_position(self.get_center(), player_center))
            self.chain[x].rotation_theta = theta

        return new_chain


class Grap(Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        Projectile.__init__(self, center, shot_from, player, velocity, gravity)

        self.shot_from = shot_from  # the gun that shot the projectile
        self.velocity = velocity
        self.gravity = gravity

        self.height = shot_from.bullet_size_y
        self.length = shot_from.bullet_size_x
        self.time = shot_from.bullet_range

        self.numHits = 0
        self.canBreakRocks = False

        self.player = player

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image
    def update(self):
        #self.screen.blit(self.image, self.rect)
        self.rect.center = euclid.Vector2(self.start_position.x + self.length / 2, self.start_position.y + self.height / 2)

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def hitBottom(self, collidingObject):
        self.canBounce()
        self.player.grappleHit = True
        self.player.velocity = self.velocity
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))

#*************************************************************************************************
#*************************************************************************************************
#hit bottom of object
    def hitTop(self, collidingObject):
        self.canBounce()
        self.player.grappleHit = True
        self.player.velocity = self.velocity
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))

#*************************************************************************************************
#*************************************************************************************************
#hit right of object
    def hitRight(self, collidingObject):
        self.canBounce()
        self.player.grappleHit = True
        self.player.velocity = self.velocity
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def hitLeft(self, collidingObject):
        self.canBounce()
        self.player.grappleHit = True
        self.player.velocity = self.velocity
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))

#*************************************************************************************************
#*************************************************************************************************
#hit corner of object
    def hitCorner(self, collidingObject):
        self.canBounce()
        self.player.grappleHit = True
        self.player.velocity = self.velocity
        self.velocity = euclid.Vector2(-self.velocity.x, -self.velocity.y)


class Translocator(Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        Projectile.__init__(self, center, shot_from, player, velocity, gravity)

        self.shot_from = shot_from  # the gun that shot the projectile
        self.velocity = velocity
        self.gravity = euclid.Vector2(0.0, 2000.0)

        self.height = shot_from.bullet_size_y
        self.length = shot_from.bullet_size_x
        self.time = shot_from.bullet_range

        self.numHits = 0
        self.canBreakRocks = False

        self.player = player

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image
    def update(self):
        #self.screen.blit(self.image, self.rect)
        self.rect.center = euclid.Vector2(self.start_position.x + self.length / 2, self.start_position.y + self.height / 2)

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def hitBottom(self, collidingObject):
        self.canBounce()
        self.player.start_position = self.start_position
        self.player.start_position.y -= 60  # Without this you appear on the bottom of small self.platforms.
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))

#*************************************************************************************************
#*************************************************************************************************
#hit bottom of object
    def hitTop(self, collidingObject):
        self.canBounce()
        self.player.start_position = self.start_position
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))

#*************************************************************************************************
#*************************************************************************************************
#hit right of object
    def hitRight(self, collidingObject):
        self.canBounce()
        self.player.start_position = self.start_position
        self.player.start_position.x -= 60
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def hitLeft(self, collidingObject):
        self.canBounce()
        self.player.start_position = self.start_position
        self.player.start_position.x += 60
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))

#*************************************************************************************************
#*************************************************************************************************
#hit corner of object
    def hitCorner(self, collidingObject):
        self.canBounce()
        self.player.start_position = self.start_position
        self.velocity = euclid.Vector2(-self.velocity.x, -self.velocity.y)


class Rocket(ServerRocket, Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerRocket.__init__(self, center, shot_from, player, velocity, gravity)
        Projectile.__init__(self, center, shot_from, player, velocity, gravity)
        self.explosion_animation = Animation(self.shot_from.bullet_image_list[1:6],
                                             self, .15)

    def update(self):
        if self.has_collided:
            #kill after animation finishes
            if self.explosion_animation.animate_movement():
                self.is_alive = False
                self.image = self.explosion_animation.last_image()

        super(Rocket, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class Grenade(ServerGrenade, Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerGrenade.__init__(self, center, shot_from, player, velocity, gravity)
        Projectile.__init__(self, center, shot_from, player, velocity, gravity)
        self.explosion_animation = Animation(self.shot_from.bullet_image_list[1:6],
                                             self, .15)

    def update(self):
        if self.is_exploding:
            #kill after animation finishes
            if self.explosion_animation.animate_movement():
                self.is_alive = False
                self.image = self.explosion_animation.last_image()

        super(Grenade, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class PredatorMissile(ServerPredatorMissile, Projectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerPredatorMissile.__init__(self, center, shot_from, player, velocity, gravity)
        Projectile.__init__(self, center, shot_from, player, velocity, gravity)
        self.explosion_animation = Animation(self.shot_from.bullet_image_list[1:6],
                                             self, .15)

    def update(self):
        if self.has_collided or self.hit_target():
            #kill after animation finishes
            if self.explosion_animation.animate_movement():
                self.is_alive = False
                self.image = self.explosion_animation.last_image()

        super(PredatorMissile, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class Chain(ServerChain):

    def __init__(self, center, width, height, image_list, grapple_projectile, velocity=euclid.Vector2(0.0, 0.0),
                 gravity=euclid.Vector2(0.0, 0.0)):

        ServerChain.__init__(self, center, width, height, grapple_projectile, velocity, gravity)

        self.can_break_rocks = False
        self.rect = self.server_rect.get_pygame_rect()
        self.animation = Animation(image_list, self)
        self.image = self.animation.current_image()

    def update(self):
        super(Chain, self).update()
        self.rect = self.server_rect.get_pygame_rect()
