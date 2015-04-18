import random
import math

from world_objects import WorldObject, get_vector_to_position
from world_objects.server.projectiles import ServerProjectile, ServerRocket, ServerGrenade, ServerPredatorMissile, ServerGrapple
from globals import now
from utilities import euclid


#gun stuff
IS_EQUIPPED = 999  # gun id
GRAPPLING_HOOK = 998  # gun id
SWORD = 997
NUM_GUNS = 51
WEAPON_SWITCH = .3
NOT_RELOADING = -1
DOUBLE_TAP_MIN = .03


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************gun**************************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerGun(WorldObject):
    def __init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy,
                 gun_x_position=-10.0, gun_y_position=-10.0, width=80.0, height=25.0, look_left_offset=20.0):

        WorldObject.__init__(self, width=width, height=height)

        self.bullet_velocity = bullet_velocity
        self.delay = delay
        self.damage = damage
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.reload_time = reload_time
        self.accuracy = accuracy

        self.remaining_ammo = self.max_ammo
        self.magazine_size = self.ammo
        self.shoots_this_many_at_a_time = 1
        self.gun_x_position = gun_x_position  # how far from the middle of the player the gun is displayed
        self.gun_y_position = gun_y_position  # how far from the middle of the player the gun is displayed
        self.end_of_barrel = euclid.Vector2(0, 0)  # calculated in update_weapon_image()
        self.window_position_center = euclid.Vector2(0, 0)  # for bullet origin
        self.look_left_offset = look_left_offset  # pixels to move the gun over when the player turns around

        self.rotation_theta = 0.0

        #TODO remove this variable, it is only needed for one class, but spriteplayer depends on knowing it
        self.is_charging = False

    def calculate_end_of_barrel(self, player):
        """calculates the bullet's spawn location"""
        mouse_position = player.mouse_position
        gun_position_vector = get_vector_to_position(mouse_position, self.window_position_center)
        theta = self.roto_theta_conversion_tool_extreme(gun_position_vector) + 90
        x_offset = self.server_rect.width / 4.0
        y_offset = self.server_rect.height / 4.0
        gun_center = self.get_center()
        y = (mouse_position.y - self.window_position_center.y)
        x = (mouse_position.x - self.window_position_center.x)
        if x != 0:
            slope = float(y) / float(x)
            if slope != 0:
                x_val = y_offset / slope
            else:
                x_val = 0
        else:
            slope = 0
            x_val = 0

        if 0 < theta <= 45:
            self.end_of_barrel = euclid.Vector2(gun_center.x + x_offset, gun_center.y + (slope * x_offset))

        elif 45 < theta <= 135:
            self.end_of_barrel = euclid.Vector2(gun_center.x - x_val, gun_center.y - y_offset)

        elif 135 < theta <= 180:
            self.end_of_barrel = euclid.Vector2(gun_center.x - x_offset, gun_center.y - (slope * x_offset))

        elif -180 < theta <= -135:
            self.end_of_barrel = euclid.Vector2(gun_center.x - x_offset, gun_center.y - (slope * x_offset))

        elif -135 < theta <= -45:
            self.end_of_barrel = euclid.Vector2(gun_center.x + x_val, gun_center.y + y_offset)

        if -45 < theta <= 0:
            self.end_of_barrel = euclid.Vector2(gun_center.x + x_offset, gun_center.y + (slope * x_offset))

    def detect_collision(self, rects):  # self is moving
        """guns don't need to detect collisions"""
        pass

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
                shot.append(ServerProjectile(
                            self.end_of_barrel, self, player,
                            euclid.Vector2((bullet_position_vector.x +
                                           random.uniform(-self.accuracy, self.accuracy)) *
                                           self.bullet_velocity,

                                           (bullet_position_vector.y +
                                           random.uniform(-self.accuracy, self.accuracy)) *
                                           self.bullet_velocity)))
        return shot

    def shoot_unpressed(self, player):
        """shot is unpressed"""
        pass

    def update_weapon_image(self, player):
        mouse_position = player.mouse_position
        gun_position_vector = get_vector_to_position(mouse_position, self.window_position_center)
        self.rotation_theta = self.roto_theta_conversion_tool_extreme(gun_position_vector) + 90
        if math.fabs(self.rotation_theta) > 90:
            self.rotation_theta += 180
            player.gun_is_pointed_right = False
        else:
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

        #TODO notice that the server gun wil not always have the correct size rect. But it will have the correct center
        #self.server_rect.reform_rect(self.image.get_width(), self.image.get_height(), self.server_rect.center)
        self.reset_rects()


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Pistol (IS A gun)************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerPistol(ServerGun):

    def __init__(self):

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

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy,
                           gun_x_position, gun_y_position, width, height, look_left_offset)

        self.bullet_size_y = 5
        self.bullet_size_x = 5
        self.bullet_range = 1.7
        self.number_ricochets = 0
        self.gun_id = 0
        self.name = "Pistol"


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Rifle (IS A gun)*************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerRifle(ServerGun):

    def __init__(self):
        bullet_velocity = 800
        delay = .1
        damage = 10
        ammo = 25
        max_ammo = 120
        reload_time = 0.8
        accuracy = 0.0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.bullet_size_y = 9
        self.bullet_size_x = 9
        self.bullet_range = 3
        self.number_ricochets = 1
        self.gun_id = 10
        self.name = "Rifle"


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************MachineGun (IS A gun)********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerMachineGun(ServerGun):

    def __init__(self):
        bullet_velocity = 850
        delay = .01
        accuracy = .14
        damage = 8
        ammo = 150
        max_ammo = 400
        reload_time = 0.8

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.bullet_size_y = 7
        self.bullet_size_x = 7
        self.bullet_range = 3
        self.number_ricochets = 0
        self.gun_id = 11
        self.name = "Machine Gun"


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************SuperMachineGun (IS A gun)***************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerSuperMachineGun(ServerGun):

    def __init__(self):
        bullet_velocity = 1000.0
        reload_time = 0.8
        delay = .01
        damage = 8
        ammo = 15000
        max_ammo = 40000
        accuracy = 0.1

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.bullet_size_y = 5
        self.bullet_size_x = 7
        self.bullet_range = 9
        self.number_ricochets = 10
        self.gun_id = 12
        self.shoots_this_many_at_a_time = 20
        self.name = "SUPER MACHINE GUN"


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Shotgun (IS A gun)***********************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerShotgun(ServerGun):

    def __init__(self):
        bullet_velocity = 800
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

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy,
                           gun_x_position, gun_y_position, width, height, look_left_offset)

        self.bullet_size_y = 4
        self.bullet_size_x = 4
        self.bullet_range = 1
        self.number_ricochets = 0
        self.gun_id = 20
        self.shoots_this_many_at_a_time = 12
        self.name = "Shotgun"


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Viper (IS A gun)*************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerViper(ServerGun):

    def __init__(self):
        bullet_velocity = 1000
        delay = 2.6
        damage = 6
        max_ammo = 6
        ammo = 6
        reload_time = 1.0
        accuracy = 0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.bullet_size_y = 15
        self.bullet_size_x = 7
        self.bullet_range = 1
        self.number_ricochets = 2
        self.gun_id = 30
        self.shoots_this_many_at_a_time = 8
        self.name = "Viper"

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
                shot.append(ServerProjectile(
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
class ServerBigBertha(ServerGun):

    def __init__(self):
        bullet_velocity = 700
        delay = .4
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.max_bullet_velocity = 900
        self.bullet_size_y = 30
        self.bullet_size_x = 30
        self.bullet_range = 4
        self.number_ricochets = 0
        self.gun_id = 40
        self.name = "Big Bertha"

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
                shot.append(ServerRocket(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))
        return shot


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************grenadeLauncher (IS A gun)***************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerGrenadeLauncher(ServerGun):

    def __init__(self):
        bullet_velocity = 1100
        delay = .8
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0.2

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.max_bullet_velocity = 900
        self.bullet_size_y = 30
        self.bullet_size_x = 30
        self.bullet_range = 6
        self.number_ricochets = 5
        self.gun_id = 42
        self.name = "Grenade Launcher"

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
                shot.append(ServerGrenade(
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
class ServerPredator(ServerGun):

    def __init__(self):
        bullet_velocity = 1.0
        delay = .1
        damage = 420
        ammo = 100
        max_ammo = 100
        reload_time = 1.5
        accuracy = 0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.max_bullet_velocity = 1000.0

        self.bullet_size_y = 20
        self.bullet_size_x = 20
        self.bullet_range = 400
        self.number_ricochets = 0
        self.gun_id = 41
        self.name = "Predator"

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
                shot.append(ServerPredatorMissile(
                    self.end_of_barrel, self, player,
                    euclid.Vector2((bullet_position_vector.x +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity,

                                  (bullet_position_vector.y +
                                   random.uniform(-self.accuracy, self.accuracy)) *
                                   self.bullet_velocity)))
        return shot


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Buster (IS A gun)************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
#Buster acts as a weak and slow rifle until you hold down the fire key, where it starts to charge up a super shot!
class ServerBuster(ServerGun):

    def __init__(self):
        bullet_velocity = 700
        delay = .5
        damage = 420
        ammo = 10
        max_ammo = 10
        reload_time = 1.5
        accuracy = 0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        #TODO after making server animations revisit this
        #self.charge_animation =

        self.max_bullet_velocity = 900

        self.bullet_size_x = 10
        self.bullet_size_y = 10
        self.original_bullet_size_x = self.bullet_size_x
        self.original_bullet_size_y = self.bullet_size_y
        self.bullet_range = 4
        self.original_bullet_range = self.bullet_range
        self.original_damage = damage
        self.is_charging = False  # if this is True the player is charging a super shot
        self.last_charge_time = 0.0
        self.number_ricochets = 0
        self.gun_id = 13
        self.use_image_at = 0
        self.name = "Buster"

    def use_weapon(self, player):
        """starts the charge"""
        current_time = now()
        time_since_fire = current_time - player.last_fire_time

        # check if the player is starting a charge or not
        if self.ammo > 0 and time_since_fire >= DOUBLE_TAP_MIN and not self.is_charging:
            self.is_charging = True
            self.last_charge_time = current_time
            player.last_fire_time = current_time

        return None

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
                shot.append(ServerProjectile(
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
#******************************************************GrapplingGun (IS A gun)******************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#Grappling gun shoots a grapple that pulls the player to it when it collides with a wall.
#IDs of a gun has to start at 0 and go up from there for every gun in the game.
# at guns[IS_EQUIPPED] is the equipped player
class ServerGrapplingGun(ServerGun):

    def __init__(self):
        bullet_velocity = 750
        delay = .8
        damage = 0
        ammo = 200
        max_ammo = 200
        reload_time = 2
        accuracy = 0

        ServerGun.__init__(self, bullet_velocity, delay, damage, ammo, max_ammo, reload_time, accuracy)

        self.bullet_size_y = 15
        self.bullet_size_x = 15
        self.bullet_range = .2
        self.number_ricochets = 0
        self.gun_id = GRAPPLING_HOOK

    def use_weapon(self, player):
        current_time = now()
        bullet_position_vector = get_vector_to_position(player.mouse_position, player.window_position_center)
        time_since_fire = current_time - player.last_grapple_time

        if time_since_fire >= self.delay and self.ammo > 0:
            #player shot
            player.last_grapple_time = current_time
            self.ammo -= 1
            player.grapple_projectile.is_alive = False  # get rid of last grapple
            grapple_projectile = ServerGrapple(player.get_center(), self, player,
                                               euclid.Vector2((bullet_position_vector.x * self.bullet_velocity),
                                                              (bullet_position_vector.y * self.bullet_velocity)))
            player.grapple_projectile = grapple_projectile  # new grapple

            return [grapple_projectile]
        return None
