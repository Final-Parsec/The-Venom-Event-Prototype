from world_objects import WorldObject, ServerRect, sign, get_displacement
from utilities import euclid
from globals import now
from world_objects.server.projectiles import ServerGrapple
from world_objects.server.guns import IS_EQUIPPED, GRAPPLING_HOOK, NUM_GUNS
from key_store import LEFT, DASH_LEFT, DASH_RIGHT, RIGHT, SHOOT, UP, GRAPPLE, PREVIOUS_WEAPON, NEXT_WEAPON, LOAD_GUN, \
    MOUSE_X, MOUSE_Y
from world_objects.server.plaftorms import ServerStep, ServerStairs
import math


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************SpritePlayer*****************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
class ServerSpritePlayer(WorldObject):

    def __init__(self, start_position, height, length, weapons, world_object_list_dictionary,
                 velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0), health=100.0):

        WorldObject.__init__(self, start_position, length, height, velocity)
        self.rect = self.server_rect.get_pygame_rect()

        self.start_position = start_position
        self.weapons = weapons  # this is a dictionary of guns
        self.world_object_list_dictionary = world_object_list_dictionary
        self.gravity = gravity
        self.hitbox = ServerRect(self.rect.left, self.rect.top, self.rect.width / 2.1, self.rect.height - 10)
        self.hitbox.center = self.rect.center
        self.window_position_center = (0, 0)

        #health and stuff
        self.health = health
        self.max_health = 100.0

        self.acceleration = euclid.Vector2(-50.0, -200.0)
        self.in_air_acceleration = self.acceleration.x / 5.0
        self.max_speed = euclid.Vector2(-400.0, -1000.0)  # is now a vector containing max x speed and jumpspeed.
        self.drag = euclid.Vector2(3.0, 3.0)

        #directions
        self.is_looking_right = True  # change the direction the image is facing
        self.is_moving_right = True  # used for turning around logic
        self.gun_is_pointed_right = True  # change the direction the player is looking. used in gun

        #last_time is the last time that this event happened
        self.last_left_time = 1.0
        self.last_right_time = 1.0
        self.last_dash_time = 0.0

        #misc. boolean values
        self.switch_weapon_held = False
        self.can_jump = False  # indicates if player is in the air or not
        self.is_jumping = False

        #dashing
        self.dash_acceleration = euclid.Vector2(self.acceleration.x * 10.0, 0.0)
        self.is_dashing = False
        self.dash_delay = .005  # time you have to wait until you can dash again

        #locaiton of player in the camera
        self.window_position = euclid.Vector2(0.0, 0.0)

        #gun stuff
        #equip first gun
        self.weapons[IS_EQUIPPED] = weapons[weapons.keys()[0]]
        self.is_reloading = False
        self.is_shooting = False
        self.last_reload_time = 0
        self.last_fire_time = 0.0

        self.mouse_position = euclid.Vector2(0, 0)

        #HUD stuff
        self.ammo_string = ""
        self.weapon_string = ""

        self.update_weapon_heads_up_display()

    def can_dash(self):
        return now() - self.last_dash_time > self.dash_delay

    def not_walking(self, delta_time):
        return now() - self.last_left_time > delta_time and now() - self.last_right_time > delta_time

    def left_logic(self, user_input):
        if user_input[LEFT]:
            if user_input[DASH_LEFT] and self.can_dash() and not self.is_dashing:
                self.dash(self.dash_acceleration.x)
            elif self.can_jump:
                self.walk(self.acceleration.x)
            else:
                self.walk(self.in_air_acceleration)

            if self.is_moving_right:  # player just turned around
                self.turn_around()

            self.last_left_time = now()

    def right_logic(self, user_input):
        if user_input[RIGHT]:
            if user_input[DASH_RIGHT] and self.can_dash() and not self.is_dashing:
                self.dash(-self.dash_acceleration.x)
            elif self.can_jump:  # on the ground
                self.walk(-self.acceleration.x)
            else:  # in the air
                self.walk(-self.in_air_acceleration)

            if not self.is_moving_right:  # player just turned around
                self.turn_around()

            self.last_right_time = now()

    def up_logic(self, user_input):
        if user_input[UP]:
            if self.is_jumping or self.can_jump:  # normal jumping
                #activate is_jumping
                if self.can_jump:
                    self.is_jumping = True
                self.jump(self.acceleration.y)
        else:
            self.is_jumping = False

    def shoot_logic(self, user_input):
        self.is_shooting = False
        shot = []
        if user_input[SHOOT]:
            shot = self.weapons[IS_EQUIPPED].use_weapon(self)
        elif not user_input[SHOOT] and self.weapons[IS_EQUIPPED].is_charging:
            shot = self.weapons[IS_EQUIPPED].shoot_unpressed(self)

        if shot is not None:
            self.add_list_to_world(shot, "projectiles")
            self.update_ammo_hud()

    def special_equipment_logic(self, user_input):
        pass

    def weapon_rotation_logic(self, user_input):
        if user_input[NEXT_WEAPON]:
            self.equip_next_gun()
        if user_input[PREVIOUS_WEAPON]:
            self.equip_previous_gun()

    def reload_logic(self, user_input):
        if user_input[LOAD_GUN]:
            self.reload()

#*************************************************************************************************
#*************************************************************************************************
#takes all of the user input and says what to do about it
    def react(self, user_input):
        self.mouse_position = euclid.Vector2(user_input[MOUSE_X], user_input[MOUSE_Y])
        if not self.is_dashing:
            #MOVEMENT
            #left
            #can't walk while dashing
            self.left_logic(user_input)

            #right
            #can't walk while dashing
            self.right_logic(user_input)

            #up
            #can't jump while dashing
            self.up_logic(user_input)

        #pause
        #TODO add back player hud logic

        #shoot
        #assume player isn't shooting
        self.shoot_logic(user_input)

        #grappling hook
        self.special_equipment_logic(user_input)

        # next weapon and previous weapon
        self.weapon_rotation_logic(user_input)

        #reload (updates ammo = max_ammo at the end of reload_time, not the beginning
        self.reload_logic(user_input)

#*************************************************************************************************
#*************************************************************************************************
#updates the on screen HUD displaying the current weapon
    def update_weapon_heads_up_display(self):
        self.weapon_string = self.weapons[IS_EQUIPPED].name

    def update_ammo_hud(self):
        current_weapon = self.weapons[IS_EQUIPPED]
        if not self.is_reloading:
            self.ammo_string = str(current_weapon.ammo) + '/' + str(current_weapon.remaining_ammo)
        else:
            self.ammo_string = ('-/' + str(self.weapons[IS_EQUIPPED].remaining_ammo))

#*************************************************************************************************
#*************************************************************************************************
#equips the next gun that the player owns in guns[]
    def equip_next_gun(self):
        self.is_reloading = False  # nextWeapon cancels reloading
        self.update_ammo_hud()
        if len(self.weapons) <= 2:
            return self.weapons[IS_EQUIPPED]
        next_gun = self.weapons[IS_EQUIPPED].gun_id + 1
        for i in range(0, NUM_GUNS):
            if next_gun == NUM_GUNS + 1:
                next_gun = 0
            elif next_gun in self.weapons:
                self.weapons[IS_EQUIPPED] = self.weapons[next_gun]
            else:
                next_gun += 1
        self.update_weapon_heads_up_display()
        self.update_ammo_hud()
        return self.weapons[IS_EQUIPPED]

#*************************************************************************************************
#*************************************************************************************************
#equips the previous gun that the player owns in guns[]
    def equip_previous_gun(self):
        self.is_reloading = False  # nextWeapon cancels reloading
        self.update_ammo_hud()
        if len(self.weapons) <= 2:  # 2 for the grappling hook.
            return self.weapons[IS_EQUIPPED]
        next_gun = self.weapons[IS_EQUIPPED].gun_id - 1
        for i in range(0, NUM_GUNS):
            if next_gun == -1:
                next_gun = NUM_GUNS
            elif next_gun in self.weapons:
                self.weapons[IS_EQUIPPED] = self.weapons[next_gun]
            else:
                next_gun -= 1
        self.update_weapon_heads_up_display()
        self.update_ammo_hud()
        return self.weapons[IS_EQUIPPED]

#*************************************************************************************************
#*************************************************************************************************
#reloads the players weapon.  Things that cancel reloading: shoot, dash, switch weapon
    def reload(self):
        current_gun = self.weapons[IS_EQUIPPED]
        #check if player can reload
        if self.time_since_reload() > current_gun.reload_time and current_gun.remaining_ammo != 0 and\
           current_gun.ammo != current_gun.magazine_size:
                #now player is reloading and player can't shoot
                self.last_reload_time = now()
                current_gun.is_charging = False
                self.is_reloading = True
                self.update_ammo_hud()
        #actual reloading is done in update() when time_since_reload() > current_gun.reload_time

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image
    def time_since_reload(self):
        return now() - self.last_reload_time

#*************************************************************************************************
#*************************************************************************************************
#The actual reloading of the gun occurs at the end of the reloading delay.
#  This happens here when time_since_reload() > gun.reload_time
    def reload_update(self):
        current_gun = self.weapons[IS_EQUIPPED]
        if self.is_reloading and self.time_since_reload() > current_gun.reload_time:
            current_gun.remaining_ammo = current_gun.ammo + current_gun.remaining_ammo - current_gun.magazine_size
            if current_gun.remaining_ammo > 0:
                current_gun.ammo = current_gun.magazine_size
            else:
                current_gun.ammo = current_gun.magazine_size + current_gun.remaining_ammo
                current_gun.remaining_ammo = 0
            self.is_reloading = False
            self.update_ammo_hud()

#*************************************************************************************************
#*************************************************************************************************
    def reset_rects(self):
        """updates the rects"""
        self.server_rect.set_center(start_position=self.start_position)
        self.hitbox.set_center(self.server_rect.center)
        self.rect.center = self.get_center()

#*************************************************************************************************
#*************************************************************************************************
#moves the object
    def move(self, delta_time):
        self.last_pos = euclid.Vector2(self.hitbox.left, self.hitbox.top)

        if math.fabs(self.velocity.y) > 50.0:  # if the player is moving in the y direction.
            self.can_jump = False

        #apply gravity
        if not self.is_jumping:  # ignore gravity while the user accelerates the jump
                self.velocity += self.gravity * delta_time

        self.start_position += self.velocity * delta_time + 0.5 * (self.gravity * (delta_time ** 2))

        #slow down player if they are moving too fast in the X
        if math.fabs(self.velocity.x) > math.fabs(self.max_speed.x) and not self.is_dashing:
            self.velocity.x -= self.velocity.x * self.drag.x * delta_time
            #taking x velocity and multiplying it by drag and time and then adding it to add drag
        #stop the player in the x direction if they are on the ground and stopped giving input
        elif self.can_jump and self.not_walking(delta_time) and not self.is_dashing:
                self.velocity = euclid.Vector2(0.0, self.velocity.y)

        #slow down player if they are moving too fast in the Y
        if math.fabs(self.velocity.y) > math.fabs(self.max_speed.y):
            self.velocity.y -= self.velocity.y * self.drag.y * delta_time
            if math.fabs(self.velocity.y) < math.fabs(self.max_speed.y):
                self.velocity.y = self.max_speed.y

        #reset rects
        self.reset_rects()

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image
    def update(self):

        self.reload_update()
        self.change_animation()

        self.weapons[IS_EQUIPPED].update_weapon_image(self)

        #reset rects
        self.reset_rects()

#*************************************************************************************************
#*************************************************************************************************
#gets new image of our running man
    def change_animation(self):
        pass

#*************************************************************************************************
#*************************************************************************************************
#returns true if the player is moving right
    def movement_direction(self):
        movement = False
        if self.velocity.x > 5.0:
            movement = True

        return movement == self.is_looking_right

#*************************************************************************************************
#*************************************************************************************************
#returns true if the player is running on the ground
    def is_running(self):
        running = True
        if -.1 < self.velocity.x < .1:
            #consider player not moving
            self.velocity.x = 0
            running = False
        return not self.is_dashing and self.can_jump and running

#*************************************************************************************************
#*************************************************************************************************
#returns true if the player is falling and not dashing
    def is_falling(self):
        in_the_air = False
        if math.fabs(self.velocity.y) > 5.0:
            in_the_air = True
        return not self.is_dashing and in_the_air

#*************************************************************************************************
#*************************************************************************************************
#adds the Player's velocity
    def walk(self, velocity):
        if math.fabs((self.velocity.x + velocity)) < math.fabs(self.max_speed.x):
            self.velocity.x += velocity

#*************************************************************************************************
#*************************************************************************************************
#adds the Player's velocity in the y direction
    def jump(self, velocity):
        if math.fabs((self.velocity.y + velocity)) < math.fabs(self.max_speed.y) and self.velocity.y <= 0:
            self.velocity.y += velocity
        else:
            self.velocity.y = self.max_speed.y
            self.is_jumping = False

#*************************************************************************************************
#*************************************************************************************************
#double tap initiates dash which increases x velocity for a short time.  dash cancels reload, grapple
    def dash(self, velocity):
        self.velocity.x += velocity
        # let the players velocity go past their max speed
        self.last_dash_time = now()
        self.is_dashing = True
        self.is_reloading = False  # dashing cancels reloading

#*************************************************************************************************
#*************************************************************************************************
#Turn 'dat ass around
    def turn_around(self):
        self.is_moving_right = not self.is_moving_right

    def collision(self, direction, thing_hit):
        """sets objects position and velocity"""
        if thing_hit.is_solid:
            if direction == 'under':
                self.collision_under(thing_hit)

            elif direction == 'above':
                self.collision_above(thing_hit)

            elif direction == 'on the left':
                self.collision_on_the_left(thing_hit)

            elif direction == 'on the right':
                self.collision_on_the_right(thing_hit)

            elif direction == 'inside':
                pass

            else:
                raise Exception('Collision: no valid direction')

        thing_hit.on_collision(self, direction)

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def collision_above(self, thing_hit):
        if not self.can_jump and math.fabs(self.velocity.y) >= math.fabs(self.max_speed.y) - 100.0:
            #dust_cloud = DustCloud(euclid.Vector2(self.start_position.x + self.hitbox.width / 2.0 - 150 / 2.0,
            #                                      self.start_position.y + self.hitbox.height - 41),
            #                       150, 41, self.dust_image_list)
            #self.add_to_world(dust_cloud, "foreground")
            #TODO re implement dust cloud
            pass
        self.velocity = euclid.Vector2(self.velocity.x, 0.0)
        self.can_jump = True
        #calculates offset to y position
        self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()

#*************************************************************************************************
#*************************************************************************************************
#hit bottom of object
    def collision_under(self, thing_hit):
        self.is_jumping = False
        self.velocity = euclid.Vector2(self.velocity.x, 0.0)
        self.start_position.y = thing_hit.start_position.y + thing_hit.get_height()

    def collision_on_the_left(self, thing_hit):
        if isinstance(thing_hit, ServerStep):
            self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()
            return
        else:
            self.velocity = euclid.Vector2(0.0, self.velocity.y)
        self.start_position.x = thing_hit.start_position.x - self.server_rect.width + self.side_padding()

    def collision_on_the_right(self, thing_hit):
        if isinstance(thing_hit, ServerStep):
            self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()
            return
        else:
            self.velocity = euclid.Vector2(0.0, self.velocity.y)
        self.start_position.x = thing_hit.start_position.x + thing_hit.get_width() - self.side_padding()

#*************************************************************************************************
#*************************************************************************************************
#returns the center of the object
    def get_window_position_center(self):
        return euclid.Vector2(self.window_position.x + self.get_width() / 2.0,
                              self.window_position.y + self.get_height() / 2.0)

#*************************************************************************************************
#*************************************************************************************************
#returns the last position of the hitbox
    def get_last_position(self):
        last_rect_location = ServerRect(int(self.last_pos.x), int(self.last_pos.y), self.hitbox.width,
                                        self.hitbox.height)
        return last_rect_location

#*************************************************************************************************
#*************************************************************************************************
#detects collisions
    def detect_collision(self, objects, test_rect=None):  # self is moving
        things_hit = []
        last_rect_location = self.get_last_position()

        test_rect = self.get_test_rectangle(self.hitbox, last_rect_location)

        for thing in objects:
            if ServerRect.colliderect(test_rect, thing.server_rect):
                things_hit.append(thing)

        for thing_hit in things_hit:
            if isinstance(thing_hit, ServerStairs):
                for step in thing_hit.steps:
                    if ServerRect.colliderect(test_rect, step.server_rect):
                        things_hit.append(step)
                things_hit.remove(thing_hit)

        hit_list_above = []
        hit_list_under = []
        hit_list_on_the_right = []
        hit_list_on_the_left = []

        for x in range(0, len(things_hit)):
            thing_hit_last_rect = things_hit[x].get_last_position()

            if last_rect_location.bottom <= thing_hit_last_rect.top:
                hit_list_above.append(things_hit[x])

            elif last_rect_location.right <= thing_hit_last_rect.left:
                hit_list_on_the_left.append(things_hit[x])

            elif last_rect_location.left >= thing_hit_last_rect.right:
                hit_list_on_the_right.append(things_hit[x])

            elif last_rect_location.top >= thing_hit_last_rect.bottom:
                hit_list_under.append(things_hit[x])

            else:
                self.collision('inside', things_hit[x])

        hit_object = self.get_closest_y(hit_list_above)
        if hit_object:
            self.collision('above', hit_object)

        hit_object = self.get_closest_y(hit_list_under)
        if hit_object:
            self.collision('under', hit_object)

        hit_object = self.get_closest_y(hit_list_on_the_right)
        if hit_object:
            self.collision('on the right', hit_object)

        hit_object = self.get_closest_y(hit_list_on_the_left)
        if hit_object:
            self.collision('on the left', hit_object)

    def get_closest_y(self, object_list):
        closest_object = None
        closest_distance = float("inf")
        for hit_object in object_list:
            displacement = get_displacement(self.get_last_position().center, hit_object.get_last_position().center)
            if displacement.y < closest_distance:
                closest_object = hit_object
                closest_distance = displacement.y

        return closest_object

    def get_closest_x(self, object_list):
        closest_object = None
        closest_distance = float("inf")
        for hit_object in object_list:
            displacement = get_displacement(self.get_last_position().center, hit_object.get_last_position().center)
            if displacement.x < closest_distance:
                closest_object = hit_object
                closest_distance = displacement.x
        return closest_object


#*************************************************************************************************
#ends the dash animation. it is called at the end of the dash animation cycle.
    def end_dash_animation(self):
        self.is_dashing = False

    def add_to_world(self, thing_to_add, list_name):
        """adds thing_to_add to the list specified by list_name"""
        self.world_object_list_dictionary[list_name].append(thing_to_add)

    def add_list_to_world(self, list_to_add, list_name):
        """concatenates list_to_add to the list specified by list_name"""
        self.world_object_list_dictionary[list_name] += list_to_add

    def top_padding(self):
        return (self.server_rect.height - self.hitbox.height) / 2.0

    def side_padding(self):
        return (self.server_rect.width - self.hitbox.width) / 2.0


class LunarPioneer(ServerSpritePlayer):

    def __init__(self, start_position, height, length, weapons, world_object_list_dictionary,
                 velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0), health=100.0):

        ServerSpritePlayer.__init__(self, start_position, height, length, weapons, world_object_list_dictionary,
                                    velocity, gravity, health)

        #grapple attributes
        self.last_grapple_time = 0.0
        self.grapple_projectile = ServerGrapple(start_position, self.weapons[0], self)
        self.grapple_projectile.is_alive = False  # kill default grapple
        self.is_grapple_jumping = False
        self.max_grapple_speed = euclid.Vector2(self.max_speed.x / 1.5, self.max_speed.y / 1.5)

#*************************************************************************************************
#*************************************************************************************************
#tells if the player is grappled to a wall or not
    def is_grappled(self):
        return self.grapple_projectile.is_alive and self.grapple_projectile.has_collided

#*************************************************************************************************
#*************************************************************************************************
#makes it so the player will only jump if they are next to their grapple
    def grapple_jump_logic(self):
        if self.is_grappled():
            player_center = self.get_center()
            grapple_center = self.grapple_projectile.get_center()
            if math.fabs(player_center.x - grapple_center.x) <= self.rect.w / 1.2 and\
               math.fabs(player_center.y - grapple_center.y) <= self.get_height() / 1.2:
                    return True
        return False

#*************************************************************************************************
#*************************************************************************************************
#adds the Player's velocity in the y direction, but less
    def grapple_jump(self, velocity):
        self.grapple_projectile.is_alive = False  # get rid of last grapple
        if math.fabs((self.velocity.y + velocity)) < math.fabs(self.max_grapple_speed.y):
            self.velocity.y += velocity
        else:
            self.is_grapple_jumping = False

    def up_logic(self, user_input):
        if user_input[UP]:
            if (self.is_jumping or self.can_jump) and not self.is_grappled():  # normal jumping
                #activate is_jumping
                if self.can_jump:
                    self.is_jumping = True
                self.jump(self.acceleration.y)
            elif self.is_grapple_jumping or self.grapple_jump_logic():  # jumping while grappled
                if self.grapple_jump_logic():
                    self.is_grapple_jumping = True
                self.grapple_jump(self.acceleration.y)

            if self.grapple_projectile.has_collided:
                self.grapple_projectile.is_alive = False  # get rid of last grapple
        else:
            self.is_grapple_jumping = False
            self.is_jumping = False

    def special_equipment_logic(self, user_input):
        if user_input[GRAPPLE]:
            grapple = self.weapons[GRAPPLING_HOOK].use_weapon(self)
            if grapple is not None:
                self.last_grapple_time = now()
                self.add_list_to_world(grapple, "projectiles")

        # make chain projectiles
        if self.grapple_projectile.is_alive:
            links = self.grapple_projectile.make_chain()
            self.add_list_to_world(links, "projectiles")

#*************************************************************************************************
#*************************************************************************************************
#moves the object
    def move(self, delta_time):
        self.last_pos = euclid.Vector2(self.hitbox.left, self.hitbox.top)

        if math.fabs(self.velocity.y) > 50.0:  # if the player is moving in the y direction.
            self.can_jump = False

        #apply gravity
        if not self.is_jumping:  # ignore gravity while the user accelerates the jump
                self.velocity += self.gravity * delta_time

        self.start_position += self.velocity * delta_time + 0.5 * (self.gravity * (delta_time ** 2))

        #slow down player if they are moving too fast in the X
        if math.fabs(self.velocity.x) > math.fabs(self.max_speed.x) and not self.grapple_projectile.is_alive and\
           not self.is_dashing:
            self.velocity.x -= self.velocity.x * self.drag.x * delta_time
            #taking x velocity and multiplying it by drag and time and then adding it to add drag
        #stop the player in the x direction if they are on the ground and stopped giving input
        elif self.can_jump and self.not_walking(delta_time) and not self.is_dashing:
            self.velocity = euclid.Vector2(0.0, self.velocity.y)

        #slow down player if they are moving too fast in the Y
        if math.fabs(self.velocity.y) > math.fabs(self.max_speed.y) and not self.grapple_projectile.is_alive:
            self.velocity.y -= self.velocity.y * self.drag.y * delta_time
            if math.fabs(self.velocity.y) < math.fabs(self.max_speed.y):
                self.velocity.y = self.max_speed.y * -sign(self.velocity.y)  # take the inverse of the sign

        #reset rects
        self.reset_rects()

#*************************************************************************************************
#*************************************************************************************************
#gets new image of our running man
    def change_animation(self):
        pass

#*************************************************************************************************
#*************************************************************************************************
#double tap initiates dash which increases x velocity for a short time.  dash cancels reload, grapple
    def dash(self, velocity):
        if self.is_grappled():
            self.velocity.x = velocity  # make it so you move when you dash from a grapple
        else:
            self.velocity.x += velocity
          # let the players velocity go past their max speed
        self.last_dash_time = now()
        self.is_dashing = True
        self.is_reloading = False  # dashing cancels reloading
        self.grapple_projectile.is_alive = False  # get rid of last grapple

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def collision_above(self, thing_hit):
        if self.is_grappled():
            self.velocity = euclid.Vector2(0.0, 0.0)
        else:
            if not self.can_jump and math.fabs(self.velocity.y) >= math.fabs(self.max_speed.y) - 100.0:
                #dust_cloud = DustCloud(euclid.Vector2(self.start_position.x + self.hitbox.width / 2.0 - 150 / 2.0,
                #                                      self.start_position.y + self.hitbox.height - 41),
                #                       150, 41, self.dust_image_list)
                #self.add_to_world(dust_cloud, "foreground")
                #TODO re implement dust cloud
                pass
            self.velocity = euclid.Vector2(self.velocity.x, 0.0)
            self.can_jump = True
        #calculates offset to y position
        self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()

#*************************************************************************************************
#*************************************************************************************************
#hit bottom of object
    def collision_under(self, thing_hit):
        if self.is_grappled():
            self.velocity = euclid.Vector2(0.0, 0.0)
        else:
            self.is_jumping = False
            self.is_grapple_jumping = False
            self.velocity = euclid.Vector2(self.velocity.x, 0.0)
        self.start_position.y = thing_hit.start_position.y + thing_hit.get_height() - self.top_padding()

    def collision_on_the_left(self, thing_hit):
        if self.is_grappled():
            self.velocity = euclid.Vector2(0.0, 0.0)
        else:
            if isinstance(thing_hit, ServerStep):
                self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()
                return
            else:
                self.velocity = euclid.Vector2(0.0, self.velocity.y)
        self.start_position.x = thing_hit.start_position.x - self.server_rect.width + self.side_padding()

    def collision_on_the_right(self, thing_hit):
        if self.is_grappled():
            self.velocity = euclid.Vector2(0.0, 0.0)
        else:
            if isinstance(thing_hit, ServerStep):
                self.start_position.y = thing_hit.start_position.y - self.hitbox.height - self.top_padding()
                return
            else:
                self.velocity = euclid.Vector2(0.0, self.velocity.y)
        self.start_position.x = thing_hit.start_position.x + thing_hit.get_width() - self.side_padding()