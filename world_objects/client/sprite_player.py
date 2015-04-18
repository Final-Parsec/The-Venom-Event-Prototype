import pygame
import math
from utilities import euclid
from world_objects.server.server_sprite_player import LunarPioneer
from animation import Animation
from background_object import Spawnimation, DustCloud
from world_objects.client.projectile import Grapple


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************SpritePlayer*****************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
class SpritePlayer(LunarPioneer):

    def __init__(self, start_position, height, length, image_list, weapons, world_object_list_dictionary,
                 spawn_animation, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0), health=100.0):

        LunarPioneer.__init__(self, start_position, height, length, weapons, world_object_list_dictionary,
                              velocity, gravity, health)

        #images
        self.spawn_animation = Spawnimation(self.start_position, 90, 651, spawn_animation, self)
        self.dashing_animation = Animation(image_list[9:14], self, .1, self.end_dash_animation)
        self.dust_image_list = image_list[15:21]
        self.running_animation = Animation(image_list[0:9], self, .08)
        self.image = self.running_animation.current_image()

        self.rect = self.server_rect.get_pygame_rect()

        #override
        self.grapple_projectile = Grapple(start_position, self.weapons[0], self)
        self.grapple_projectile.is_alive = False  # kill default grapple

        self.add_to_world(self.spawn_animation, "foreground")

#*************************************************************************************************
#*************************************************************************************************
#gets new image of our running man
    def change_animation(self):

        if self.is_running():
            self.running_animation.animate_movement(self.movement_direction())
            self.image = pygame.transform.flip(self.running_animation.current_image(), not self.is_looking_right, 0)

        elif self.is_dashing:
            self.dashing_animation.animate_movement()
            self.image = pygame.transform.flip(self.dashing_animation.current_image(), not self.is_moving_right, 0)

        #elif self.grapple_projectile.is_alive:
            #self.image = pygame.transform.flip(self.running_animation.image_list[0], not self.is_looking_right, 0)

        #elif self.is_falling():
            #self.image = pygame.transform.flip(self.running_animation.image_list[0], not self.is_looking_right, 0)

        else:  # player is standing still
            self.image = pygame.transform.flip(self.running_animation.image_list[0], not self.is_looking_right, 0)

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def collision_above(self, thing_hit):
        if self.is_grappled():
            self.velocity = euclid.Vector2(0.0, 0.0)
        else:
            if not self.can_jump and math.fabs(self.velocity.y) >= math.fabs(self.max_speed.y) - 100.0:
                dust_cloud = DustCloud(euclid.Vector2(self.start_position.x + self.hitbox.width / 2.0 - 150 / 2.0,
                                                      self.start_position.y + self.hitbox.height - 41),
                                       150, 41, self.dust_image_list)
                self.add_to_world(dust_cloud, "foreground")
            self.velocity = euclid.Vector2(self.velocity.x, 0.0)
            self.can_jump = True
        #calculates offset to y position
        self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()
