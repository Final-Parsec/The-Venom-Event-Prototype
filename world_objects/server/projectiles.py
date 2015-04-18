import math

from utilities import euclid
from world_objects import WorldObject, get_vector_to_position, get_displacement


class ServerProjectile(WorldObject):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):
        #start_position will be updated later in the constructor so send 0,0 for now;
        WorldObject.__init__(self, euclid.Vector2(0.0, 0.0), shot_from.bullet_size_x, shot_from.bullet_size_y, velocity)

        #configure
        self.set_center(center)

        self.shot_from = shot_from
        self.player = player
        self.gravity = gravity
        self.time = shot_from.bullet_range
        self.number_of_hits = 0
        self.can_break_rocks = True
        self.has_collided = False

        self.rotation_theta = 0.0

    def move(self, delta_time):
        """moves the projectile"""
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)

        self.time -= delta_time
        self.range_logic()

        self.start_position += self.velocity * delta_time
        self.velocity += self.gravity * delta_time

        self.reset_rects()

    def collision(self, direction, thing_hit):
        """sets objects position and velocity"""
        if thing_hit.is_solid:
            if direction == 'under':
                self.collision_under(thing_hit)

            elif direction == 'above':
                self.collision_above(thing_hit)

            elif direction == 'on the left':
                self.collision_on_left(thing_hit)

            elif direction == 'on the right':
                self.collision_on_right(thing_hit)

            elif direction == 'inside':
                pass

            else:
                raise Exception('Collision: no valid direction')

        thing_hit.on_collision(self, direction)

    def collision_above(self, thing_hit):
        """self is above the object"""
        self.has_collided = True
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))
        self.start_position.y = thing_hit.start_position.y - self.get_height()

        self.can_bounce()

    def collision_under(self, thing_hit):
        """self is under the object"""
        self.has_collided = True
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))
        self.start_position.y = thing_hit.start_position.y + thing_hit.get_height()

        self.can_bounce()

    def collision_on_left(self, thing_hit):
        """self is to the left of the object"""
        self.has_collided = True
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))
        self.start_position.x = thing_hit.start_position.x - self.get_width()

        self.can_bounce()

    def collision_on_right(self, thing_hit):
        """self is to the right of the object"""
        self.has_collided = True
        self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))
        self.start_position.x = thing_hit.start_position.x + thing_hit.get_width()

        self.can_bounce()

    def can_bounce(self):
        """kill object if it can't bounce"""
        if self.number_of_hits >= self.shot_from.number_ricochets:
            self.time = 0  # kills bullet on next frame
            self.is_alive = False
            return False
        self.number_of_hits += 1
        return True

    def range_logic(self):
        """kill if it runs out of time"""
        if self.time < 0.0:
            self.is_alive = False


class ServerGrapple(ServerProjectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):
        ServerProjectile.__init__(self, center, shot_from, player, velocity, gravity)

        self.pull_speed = 1000
        self.can_break_rocks = False
        self.go_to_coordinates = euclid.Vector2(0.0, 0.0)
        self.colliding_object = None
        #chain
        self.chain = []
        self.link_size = euclid.Vector2(8.0, 16.0)

    def move(self, delta_time):
        """moves the projectile"""
        if not self.has_collided:
            self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)

            self.time -= delta_time
            self.range_logic()

            self.start_position += self.velocity * delta_time
            self.velocity += self.gravity * delta_time

        self.reset_rects()

    def update(self):
        """check for object changes
            update server rect"""
        if self.has_collided:
            self.transfer_velocity()

        # if the colliding_object dies then the grapple will too
        if self.colliding_object and not self.colliding_object.is_alive:
            self.is_alive = False
            self.player.velocity = euclid.Vector2(0.0, 0.0)

        self.reset_rects()

    def collision(self, direction, thing_hit):
        """sets objects position and velocity"""
        if thing_hit.is_solid:
            if direction == 'under':
                self.collision_under(thing_hit)

            elif direction == 'above':
                self.collision_above(thing_hit)

            elif direction == 'on the left':
                self.collision_on_left(thing_hit)

            elif direction == 'on the right':
                self.collision_on_right(thing_hit)

            elif direction == 'inside':
                if not self.has_collided:
                    self.colliding_object = thing_hit
                    self.has_collided = True
                    self.go_to_coordinates.x = self.start_position.x
                    self.go_to_coordinates.y = self.start_position.y

            else:
                raise Exception('Collision: no valid direction')

        thing_hit.on_collision(self, direction)

    def collision_above(self, thing_hit):
        if not self.has_collided:
            self.colliding_object = thing_hit
            self.has_collided = True
            self.go_to_coordinates.x = self.start_position.x
            self.go_to_coordinates.y = thing_hit.start_position.y + thing_hit.get_height()
            self.start_position.y = thing_hit.start_position.y

            if self.start_position.x + self.get_width() > thing_hit.start_position.x + thing_hit.get_width():
                self.start_position.x = thing_hit.start_position.x + thing_hit.get_width() - self.get_width()
            if self.start_position.x < thing_hit.start_position.x:
                self.start_position.x = thing_hit.start_position.x

    def collision_under(self, thing_hit):
        if not self.has_collided:
            self.colliding_object = thing_hit
            self.has_collided = True
            self.go_to_coordinates.x = self.start_position.x
            self.go_to_coordinates.y = thing_hit.start_position.y
            self.start_position.y = thing_hit.start_position.y + thing_hit.get_height() - self.get_height()

            if self.start_position.x + self.get_width() > thing_hit.start_position.x + thing_hit.get_width():
                self.start_position.x = thing_hit.start_position.x + thing_hit.get_width() - self.get_width()
            if self.start_position.x < thing_hit.start_position.x:
                self.start_position.x = thing_hit.start_position.x

    def collision_on_left(self, thing_hit):
        if not self.has_collided:
            self.colliding_object = thing_hit
            self.has_collided = True
            self.go_to_coordinates.x = thing_hit.start_position.x
            self.start_position.x = thing_hit.start_position.x
            self.go_to_coordinates.y = self.start_position.y

    def collision_on_right(self, thing_hit):
        if not self.has_collided:
            self.colliding_object = thing_hit
            self.has_collided = True
            self.go_to_coordinates.x = thing_hit.start_position.x + thing_hit.get_width()
            self.start_position.x = thing_hit.start_position.x + thing_hit.get_width() - self.get_width()
            self.go_to_coordinates.y = self.start_position.y

    def transfer_velocity(self):
        grapple_center = self.get_center()
        if not(-5.0 < self.go_to_coordinates.x - grapple_center.x < 5.0 and
           -5.0 < self.go_to_coordinates.y - grapple_center.y < 5.0):

            self.time = .1  # keep showing grapple after it hits a wall
            if self.has_collided and not self.is_alive:
                self.has_collided = False  # there are fringe cases where it will collide but
                return                    # still be killed when it is at it's max range. So stop the collision.

            vel = get_vector_to_position(self.get_center(), self.player.get_center())
            vel.x *= self.pull_speed
            vel.y *= self.pull_speed

            self.velocity = euclid.Vector2(0.0, 0.0)
            self.player.velocity = vel

    def make_chain(self):
        """makes the chain"""
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
                self.chain[x].start_position = link_position
            else:
                self.chain.append(ServerChain(link_position, self.link_size.x, self.link_size.y, self))
                new_chain.append(self.chain[-1])
            self.chain[x].set_center(self.chain[x].start_position)

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


class ServerChain(WorldObject):
    def __init__(self, center, width, height, grapple_projectile, velocity=euclid.Vector2(0.0, 0.0),
                 gravity=euclid.Vector2(0.0, 0.0)):
        WorldObject.__init__(self, width=width, height=height, velocity=velocity)
        self.is_solid = False

        self.set_center(center)  # sets self.start_position

        self.velocity = velocity
        self.gravity = gravity
        self.grapple = grapple_projectile

        self.rotation_theta = 0.0

    def update(self):
        """used to update the rect.
            If the grapple is killed then the link will be killed"""
        self.set_center(self.get_center())
        if not self.grapple.is_alive:
            self.is_alive = False

        self.reset_rects()


class ServerRocket(ServerProjectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerProjectile.__init__(self, center, shot_from, player, velocity, gravity)
        self.start_direction = self.get_direction()

    def update(self):
        if not self.has_collided:
            self.accelerate()
        self.reset_rects()

    def accelerate(self):
        """speed up rocket"""
        self.velocity.x += math.cos(self.start_direction) * 130
        self.velocity.y += math.sin(self.start_direction) * 130

    def collision_above(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_under(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_on_left(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_on_right(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)


class ServerGrenade(ServerProjectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerProjectile.__init__(self, center, shot_from, player, velocity, gravity)

        self.start_direction = self.get_direction()
        self.is_exploding = False

    def range_logic(self):
        """modified for is_exploding"""
        if self.time < 0.0:
            self.is_exploding = True
            self.velocity = euclid.Vector2(0.0, 0.0)

    def can_bounce(self):
        """modified for is_exploding"""
        if self.number_of_hits >= self.shot_from.number_ricochets:
            self.time = 0  # kills bullet on next frame
            self.is_exploding = True
            return False
        self.number_of_hits += 1
        return True

    def move(self, delta_time):
        """modified for is_exploding"""
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)
        if not self.is_exploding:
            self.time -= delta_time
            self.range_logic()

            self.start_position += self.velocity * delta_time
            self.velocity += self.gravity * delta_time

        self.reset_rects()

    def collision(self, direction, thing_hit):
        """modified for on_hit()"""
        if thing_hit.is_solid:
            self.on_hit(thing_hit)
            if direction == 'under':
                self.collision_under(thing_hit)

            elif direction == 'above':
                self.collision_above(thing_hit)

            elif direction == 'on the left':
                self.collision_on_left(thing_hit)

            elif direction == 'on the right':
                self.collision_on_right(thing_hit)

            elif direction == 'inside':
                pass

            else:
                raise Exception('Collision: no valid direction')

        thing_hit.on_collision(self, direction)

    def on_hit(self, thing_hit):
        """checks if what was hit can be killed"""
        if hasattr(thing_hit, 'health'):
            self.is_exploding = True


class ServerPredatorMissile(ServerProjectile):

    def __init__(self, center, shot_from, player, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 0.0)):

        ServerProjectile.__init__(self, center, shot_from, player, velocity, gravity)

        self.delay_time = 2.0  # time that the seeker will not move before it goes to target
        self.distance = get_displacement(self.shot_from.window_position_center, player.mouse_position)
        self.starting_location = euclid.Vector2(self.start_position.x, self.start_position.y)
        self.acceleration = 1.1

    def hit_target(self):
        """returns true if it has reached the target"""
        current_distance = get_displacement(self.starting_location, self.start_position)
        if math.fabs(current_distance.x - self.distance.x) < 10.0 and\
           math.fabs(current_distance.y - self.distance.y) < 10.0:
            self.has_collided = True
            self.velocity = euclid.Vector2(0.0, 0.0)
            return True
        return False

    def move(self, delta_time):
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)
        self.delay_time -= delta_time
        self.time -= delta_time
        self.range_logic()

        if self.delay_time <= 2.0:
            self.start_position += self.velocity * delta_time
            velocity = math.sqrt(math.pow(self.velocity.x, 2) + math.pow(self.velocity.y, 2))
            if velocity < self.shot_from.max_bullet_velocity:
                self.velocity += self.gravity * delta_time
                self.velocity *= self.acceleration

        self.reset_rects()

    def collision_above(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_under(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_on_left(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)

    def collision_on_right(self, thing_hit):
        if not self.has_collided:
            self.has_collided = True
        self.velocity = euclid.Vector2(0.0, 0.0)
