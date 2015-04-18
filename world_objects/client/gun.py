import random
import math

import pygame

from world_objects import get_vector_to_position
from globals import now
from sprite_sheet import SpriteSheet
from world_objects.server.guns import ServerGun, ServerPistol, ServerRifle, ServerGrapplingGun, ServerBigBertha,\
    ServerGrenadeLauncher, ServerPredator, ServerMachineGun, ServerSuperMachineGun, ServerShotgun, ServerViper,\
    ServerBuster
from utilities import euclid
from animation import Animation
from world_objects.client.projectile import Projectile, PredatorMissile, Grenade, Grapple, Rocket, Grap, Translocator
from background_object import BusterCharge


#gun stuff
IS_EQUIPPED = 999  # gun id
GRAPPLING_HOOK = 998  # gun id
SWORD = 997
NUM_GUNS = 51
WEAPON_SWITCH = .3
NOT_RELOADING = -1
DOUBLE_TAP_MIN = .03


#TODO fix the gun jitter. it is probably caused because we are using doubles for start_position and possibly server_rect

#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************gun**************************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Gun(ServerGun):
    def __init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy, image_list=None,
                 gun_x_position=-10.0, gun_y_position=-10.0, width=80.0, height=25.0, look_left_offset=20.0):
        if image_list is None:
            image_list = [pygame.image.load("resources/images/gunNotShooting.png"),
                          pygame.image.load("resources/images/gunShooting.png")]

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy,
                           gun_x_position, gun_y_position, width, height, look_left_offset)

        self.rect = self.server_rect.get_pygame_rect()
        self.animation = Animation(image_list, self)
        self.image = self.animation.current_image()

#*************************************************************************************************
#*************************************************************************************************
#updates the image
#when gun is charging it will run the animation
    def update_weapon_image(self, player):
        if player.is_shooting:
            self.animation.use_image_at = 1
        else:
            self.animation.use_image_at = 0

        mouse_position = player.mouse_position
        gun_position_vector = get_vector_to_position(mouse_position, self.window_position_center)
        theta = self.roto_theta_conversion_tool_extreme(gun_position_vector) + 90
        if math.fabs(theta) > 90:
            image = pygame.transform.flip(self.animation.current_image(), 1, 0)
            self.image = pygame.transform.rotate(image, theta + 180)
            player.gun_is_pointed_right = False
        else:
            self.image = pygame.transform.rotate(self.animation.current_image(), theta)
            player.gun_is_pointed_right = True

        #set where the player is looking if they aren't dashing
        if not player.is_dashing:
                player.is_looking_right = player.gun_is_pointed_right

        if player.gun_is_pointed_right:
            self.set_center(euclid.Vector2(player.start_position.x + player.get_width() / 2.0 + self.gun_x_position,
                                           player.start_position.y + player.get_height() / 2.0 +
                                           self.gun_y_position))
        else:
            self.set_center(euclid.Vector2(player.start_position.x + player.get_width() / 2.0 + self.gun_x_position +
                                           self.look_left_offset, player.start_position.y + player.get_height() / 2.0 +
                                           self.gun_y_position))

        self.server_rect.reform_rect(self.image.get_width(), self.image.get_height(), self.server_rect.center)
        self.reset_rects()
        self.rect = self.server_rect.get_pygame_rect()

#*************************************************************************************************
#*************************************************************************************************
#returns a projectile that the Player shot
    def use_weapon(self, player):  # self is da gun

        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)
        time_since_fire = current_time - player.last_fire_time

        shot = []
        if time_since_fire >= self.delay and self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            player.is_shooting = True
            player.last_fire_time = current_time
            self.ammo -= 1
            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(Projectile(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                   (bullet_position_vector.y +
                                    random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))

            return shot
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Pistol (IS A gun)************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Pistol(ServerPistol, Gun):

    def __init__(self, bullet_image_list):

        sprite_sheet_1 = SpriteSheet("resources/images/Sprite Sheet1.png")
        image_list = [sprite_sheet_1.imageAt(pygame.Rect(732, 316, 58, 30)),
                      sprite_sheet_1.imageAt(pygame.Rect(811, 315, 84, 40))]

        reload_time = 2
        accuracy = .1
        damage = 10
        ammo = 30
        max_ammo = 30
        delay = .8
        bullet_velocity = 1000
        width = 58
        height = 30
        look_left_offset = 16
        gun_x_position = -9.0
        gun_y_position = -13.0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy, image_list,
                     gun_x_position, gun_y_position, width, height, look_left_offset)

        ServerPistol.__init__(self)
        self.bullet_image_list = bullet_image_list


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Rifle (IS A gun)*************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Rifle(ServerRifle, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 800
        delay = .1
        damage = 10
        ammo = 25
        max_ammo = 120
        reload_time = 0.8
        accuracy = 0.0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        ServerRifle.__init__(self)

        self.bullet_image_list = bullet_image_list


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************MachineGun (IS A gun)********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class MachineGun(ServerMachineGun, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 850
        delay = .01
        accuracy = .14
        damage = 8
        ammo = 150
        max_ammo = 400
        reload_time = 0.8

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)
        ServerMachineGun.__init__(self)

        self.bullet_image_list = bullet_image_list


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************SuperMachineGun (IS A gun)***************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class SuperMachineGun(ServerSuperMachineGun, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 1000.0
        reload_time = 0.8
        delay = .01
        damage = 8
        ammo = 15000
        max_ammo = 40000
        accuracy = 0.1

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)
        ServerSuperMachineGun.__init__(self)

        self.bullet_image_list = bullet_image_list


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Shotgun (IS A gun)***********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Shotgun(ServerShotgun, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 800
        sprite_sheet_1 = SpriteSheet("resources/images/Sprite Sheet1.png")
        image_list = [sprite_sheet_1.imageAt(pygame.Rect(966, 332, 35, 21)),
                      sprite_sheet_1.imageAt(pygame.Rect(471, 93, 102, 40))]
        gun_x_position = 7.0
        gun_y_position = 0.0
        delay = 1
        damage = 5
        ammo = 30
        max_ammo = 30
        reload_time = 2.0
        accuracy = .07
        width = 35
        height = 21
        look_left_offset = -16

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy, image_list,
                     gun_x_position, gun_y_position, width, height, look_left_offset)

        ServerShotgun.__init__(self)

        self.bullet_image_list = bullet_image_list


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Viper (IS A gun)*************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Viper(ServerViper, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 1000
        delay = 2.6
        damage = 6
        max_ammo = 6
        ammo = 6
        reload_time = 1.0
        accuracy = 0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        ServerViper.__init__(self)

        self.bullet_image_list = bullet_image_list

    def use_weapon(self, player):

        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)
        time_since_fire = current_time - player.last_fire_time

        shot = []
        if time_since_fire >= self.delay and self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            player.is_shooting = True
            player.last_fire_time = current_time
            self.ammo -= 1
            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(Projectile(
                            self.end_of_barrel, self, player,
                            euclid.Vector2((bullet_position_vector.x +
                                           random.uniform(-self.accuracy, self.accuracy)) *
                                           self.bullet_velocity * a,

                                           (bullet_position_vector.y +
                                           random.uniform(-self.accuracy, self.accuracy)) *
                                           self.bullet_velocity * a)))
        return shot


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************BigBertha (IS A gun)*********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class BigBertha(ServerBigBertha, Gun):

    def __init__(self, bullet_image_list):
        #load image for bigbertha
        image_list = []  # override gun's image list
        sprite_sheet_1 = SpriteSheet("resources/images/Sprite Sheet1.png")
        image_list.append(sprite_sheet_1.imageAt(pygame.Rect(726, 131, 146, 34)))
        image_list.append(sprite_sheet_1.imageAt(pygame.Rect(726, 187, 146, 34)))
        bullet_velocity = 700
        delay = .4
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy, image_list)

        ServerBigBertha.__init__(self)

        self.bullet_image_list = bullet_image_list

#*************************************************************************************************
#*************************************************************************************************
#returns a projectile that the Player shot
    def use_weapon(self, player):  # self is da gun
        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)
        time_since_fire = current_time - player.last_fire_time

        shot = []
        if time_since_fire >= self.delay and self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            player.is_shooting = True
            player.last_fire_time = current_time
            self.ammo -= 1
            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(Rocket(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))

            return shot
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************grenadeLauncher (IS A gun)***************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class GrenadeLauncher(ServerGrenadeLauncher, Gun):

    def __init__(self, bullet_image_list):
        #load image for bigbertha
        image_list = []  # override gun's image list
        sprite_sheet_1 = SpriteSheet("resources/images/Sprite Sheet1.png")
        image_list.append(sprite_sheet_1.imageAt(pygame.Rect(726, 131, 146, 34)))
        image_list.append(sprite_sheet_1.imageAt(pygame.Rect(726, 187, 146, 34)))
        bullet_velocity = 1100
        delay = .8
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0.2

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy, image_list)

        ServerGrenadeLauncher.__init__(self)

        self.bullet_image_list = bullet_image_list

#*************************************************************************************************
#*************************************************************************************************
#returns a projectile that the Player shot
    def use_weapon(self, player):  # self is da gun
        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)
        time_since_fire = current_time - player.last_fire_time

        shot = []
        if time_since_fire >= self.delay and self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            player.is_shooting = True
            player.last_fire_time = current_time
            self.ammo -= 1
            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(Grenade(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))

            return shot
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Predator (IS A gun)**********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class Predator(ServerPredator, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 1.0
        delay = .1
        damage = 420
        ammo = 100
        max_ammo = 100
        reload_time = 1.5
        accuracy = 0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        ServerPredator.__init__(self)

        self.bullet_image_list = bullet_image_list

#*************************************************************************************************
#*************************************************************************************************
#returns a projectile that the Player shot
    def use_weapon(self, player):  # self is da gun
        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)
        time_since_fire = current_time - player.last_fire_time

        shot = []
        if time_since_fire >= self.delay and self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            player.is_shooting = True
            player.last_fire_time = current_time
            self.ammo -= 1
            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(PredatorMissile(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))

            return shot
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Buster (IS A gun)************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
#Buster acts as a weak and slow rifle until you hold down the fire key, where it starts to charge up a super shot!
class Buster(ServerBuster, Gun):

    def __init__(self, bullet_image_list, animation_images):
        bullet_velocity = 700
        delay = .5
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        ServerBuster.__init__(self)

        self.charge_animation_object = BusterCharge(self.end_of_barrel, 20, 20, animation_images, self)
        self.bullet_image_list = bullet_image_list

#*************************************************************************************************
#*************************************************************************************************
#updates the image
#when gun is charging it will run the animation
    def update_weapon_image(self, player):
        if player.is_shooting:
            self.animation.use_image_at = 1
        else:
            self.animation.use_image_at = 0

        mouse_position = player.mouse_position
        gun_position_vector = get_vector_to_position(mouse_position, self.window_position_center)
        theta = self.roto_theta_conversion_tool_extreme(gun_position_vector) + 90
        if math.fabs(theta) > 90:
            image = pygame.transform.flip(self.animation.current_image(), 1, 0)
            self.image = pygame.transform.rotate(image, theta + 180)
            player.gun_is_pointed_right = False
        else:
            self.image = pygame.transform.rotate(self.animation.current_image(), theta)
            player.gun_is_pointed_right = True

        #set where the player is looking if they aren't dashing
        if not player.is_dashing:
                player.is_looking_right = player.gun_is_pointed_right

        self.rect = self.image.get_rect()
        if player.gun_is_pointed_right:
            self.set_center(euclid.Vector2(player.start_position.x + player.get_width() / 2.0 + self.gun_x_position,
                                           player.start_position.y + player.get_height() / 2.0 +
                                           self.gun_y_position))
        else:
            self.set_center(euclid.Vector2(player.start_position.x + player.get_width() / 2.0 + self.gun_x_position +
                                           self.look_left_offset, player.start_position.y + player.get_height() / 2.0 +
                                           self.gun_y_position))

        #stuff to display charge animation. Must be done at end of update weapon image
        if self.is_charging:
            if not self.charge_animation_object.is_alive:
                self.charge_animation_object.is_alive = True
                player.add_to_world(self.charge_animation_object, "foreground")
            self.calculate_end_of_barrel(player)
            self.charge_animation_object.manual_update()

        self.server_rect.reform_rect(self.image.get_width(), self.image.get_height(), self.server_rect.center)
        self.reset_rects()
        self.rect = self.server_rect.get_pygame_rect()

    def shoot_unpressed(self, player):
        bullet_position_vector = get_vector_to_position(player.mouse_position, self.window_position_center)

        shot = []
        if self.ammo > 0 and not player.is_reloading:
            #player shot
            self.calculate_end_of_barrel(player)
            self.is_charging = False
            player.is_shooting = True
            player.last_fire_time = now()
            self.ammo -= 1

            # set attributes to charged mode
            if not (now() - self.last_charge_time) * 15 < 10:
                    self.bullet_size_x = ((now() - self.last_charge_time) * 15)
                    self.bullet_size_y = ((now() - self.last_charge_time) * 15)
                    self.damage = ((now() - self.last_charge_time) * 15)
                    self.bullet_range = ((now() - self.last_charge_time) * 15)

            for a in range(1, self.shoots_this_many_at_a_time + 1):
                shot.append(Projectile(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))

            # set attributes back to normal
            self.bullet_size_x = self.original_bullet_size_x
            self.bullet_size_y = self.original_bullet_size_y
            self.bullet_range = self.original_bullet_range
            self.damage = self.original_damage

        return shot


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************DatGrap (IS A gun)***********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#DatGrap shoots a Grap, and upon collision a Grap adds it's velocity to the player's velocity.
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class DatGrap(Gun):

    def __init__(self, bullet_image_list):

        self.bullet_size_y = 15
        self.bullet_size_x = 15
        self.bullet_velocity = 750
        self.bullet_range = .9
        self.bullet_image_list = bullet_image_list
        self.delay = .3
        self.number_ricochets = 0
        self.damage = 0
        self.ammo = 200
        self.max_ammo = 200
        self.gun_id = GRAPPLING_HOOK
        self.reload_time = 2
        self.accuracy = 0
        Gun.__init__(self, self.bullet_velocity, self.delay, self.damage, self.ammo, self.max_ammo, self.reload_time,
                     self.accuracy)

    def use(self, start_position, bullet_position_vector, time_since_grapple, timeSinceReload, player):
        if time_since_grapple > self.delay:
            return [Grap(euclid.Vector2(start_position.x + 1, start_position.y + 1), self, player,
                         euclid.Vector2(bullet_position_vector.x * self.bullet_velocity * 3,
                                        bullet_position_vector.y * self.bullet_velocity * 3))]
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************TeleGrap (IS A gun)**********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#Grappling gun shoots a grapple that pulls the player to it when it collides with a wall.
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class TeleGrap(Gun):

    def __init__(self, bullet_image_list):

        self.bullet_size_y = 15
        self.bullet_size_x = 15
        self.bullet_velocity = 1200
        self.bullet_range = 2
        self.bullet_image_list = bullet_image_list
        self.delay = .3
        self.number_ricochets = 0
        self.damage = 0
        self.ammo = 200
        self.max_ammo = 200
        self.gun_id = GRAPPLING_HOOK
        self.reload_time = 0
        self.accuracy = 0
        Gun.__init__(self, self.bullet_velocity, self.delay, self.damage, self.ammo, self.max_ammo, self.reload_time,
                     self.accuracy)

    def use(self, start_position, bullet_position_vector, time_since_grapple, timeSinceReload, player):

        if time_since_grapple > self.delay:
            return [Translocator(euclid.Vector2(start_position.x, start_position.y), self, player,
                                 euclid.Vector2(bullet_position_vector.x * self.bullet_velocity,
                                                bullet_position_vector.y * self.bullet_velocity))]
        return None


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************GrapplingGun (IS A gun)******************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#Grappling gun shoots a grapple that pulls the player to it when it collides with a wall.
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class GrapplingGun(ServerGrapplingGun, Gun):

    def __init__(self, bullet_image_list):
        bullet_velocity = 750
        delay = .8
        damage = 0
        ammo = 200
        max_ammo = 200
        reload_time = 2
        accuracy = 0

        Gun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)
        ServerGrapplingGun.__init__(self)

        self.bullet_image_list = bullet_image_list

    def use_weapon(self, player):
        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, player.window_position_center)
        time_since_fire = current_time - player.last_grapple_time

        if time_since_fire >= self.delay and self.ammo > 0:
            #player shot
            player.last_grapple_time = current_time
            self.ammo -= 1
            player.grapple_projectile.is_alive = False  # get rid of last grapple
            grapple_projectile = Grapple(player.get_center(), self, player,
                                         euclid.Vector2((bullet_position_vector.x * self.bullet_velocity),
                                                        (bullet_position_vector.y * self.bullet_velocity)))
            player.grapple_projectile = grapple_projectile  # new grapple

            return [grapple_projectile]
        return None