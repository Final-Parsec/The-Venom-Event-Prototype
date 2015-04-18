import math

from utilities import euclid


class WorldObject(object):
    """better than ever base object.
        no pygame in sight."""
    def __init__(self, start_position=euclid.Vector2(0, 0), width=0, height=0, velocity=euclid.Vector2(0.0, 0.0),
                 image_code=None):
        self.start_position = start_position
        self.server_rect = ServerRect(int(self.start_position.x), int(self.start_position.y), width, height)
        self.velocity = velocity
        self.image_code = image_code

        self.is_alive = True  # removes object from map
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)
        self.is_solid = True

    def collision(self, direction, thing_hit):
        """sets objects position and velocity"""
        if thing_hit.is_solid:
            if direction == 'under':
                self.velocity = euclid.Vector2(self.velocity.x, 0.0)
                self.start_position.x = thing_hit.rect.bottom

            elif direction == 'above':
                self.velocity = euclid.Vector2(self.velocity.x, 0.0)
                self.start_position.x = thing_hit.rect.top + self.get_height()

            elif direction == 'on the left':
                self.velocity = euclid.Vector2(0.0, self.velocity.y)
                self.start_position.y = thing_hit.rect.left + self.get_width()

            elif direction == 'on the right':
                self.velocity = euclid.Vector2(0.0, self.velocity.y)
                self.start_position.y = thing_hit.rect.right

            elif direction == 'inside':
                pass

            else:
                raise Exception('Collision: no valid direction')

        thing_hit.on_collision(self, direction)

#*************************************************************************************************
#*************************************************************************************************
#returns the direction in radians that the object is moving in. 0 is to the right, pi & -pi are the left,
#down is negative
    def get_direction(self):
        return math.atan2(self.velocity.y, self.velocity.x)

#*************************************************************************************************
#*************************************************************************************************
#returns the last position of the object / same as projectile
# put into world object when made
    def get_last_position(self):
        return ServerRect(self.last_pos.x, self.last_pos.y, self.get_width(), self.get_height())

    def update(self):
        """reset the rects and do the other things,
            not because they are easy... but because
            they are hard"""
        self.reset_rects()

    def reset_rects(self):
        """does the same job as update but with out
            anything extra that needs to be in update"""
        self.server_rect.set_center(start_position=self.start_position)

#*************************************************************************************************
#*************************************************************************************************
#moves the sprite
    def move(self, delta_time):
        self.last_pos = euclid.Vector2(self.start_position.x, self.start_position.y)
        self.start_position += self.velocity * delta_time
        self.reset_rects()

#*************************************************************************************************
#*************************************************************************************************
#returns the height of the object in pixels
    def get_height(self):
        return self.server_rect.height

#*************************************************************************************************
#*************************************************************************************************
#returns the width of the object in pixels
    def get_width(self):
        return self.server_rect.width

#*************************************************************************************************
#*************************************************************************************************
#used to update the center of the rect and correct the start_position of the object
    def set_center(self, new_center):
        self.server_rect.set_center(center=new_center)
        self.start_position = euclid.Vector2(self.server_rect.left, self.server_rect.top)

#*************************************************************************************************
#*************************************************************************************************
#get the quadrant that the object is moving in.
    @staticmethod
    def get_quadrant(direction):  # must call using projectile.get_direction()
        if -math.pi / 2 < direction <= 0:
            return 1
        elif -math.pi <= direction <= -math.pi / 2:
            return 2
        elif math.pi / 2 < direction <= math.pi:
            return 3
        elif 0 < direction <= math.pi / 2:
            return 4

        return -1

#*************************************************************************************************
#*************************************************************************************************
#generates a larger rectangle to test for collisions with. B is a location vector of the last position
# of the object
    @staticmethod
    def get_test_rectangle(a, b):
        if a.left < b.left:
            left = a.left
            width = b.right - a.left
        else:
            left = b.left
            width = a.right - b.left

        if a.top < b.top:
            top = a.top
            height = b.bottom - a.top
        else:
            top = b.top
            height = a.bottom - b.top

        return ServerRect(left, top, width, height)

#*************************************************************************************************
#*************************************************************************************************
#detects collisions
    def detect_collision(self, objects):  # self is moving
        things_hit = []

        last_rect_location = self.get_last_position()

        test_rect = self.get_test_rectangle(self.server_rect, last_rect_location)

        for thing in objects:
            if ServerRect.colliderect(test_rect, thing.server_rect):
                things_hit.append(thing)

        for thing_hit in things_hit:
            from world_objects.client.platform import Stairs
            if type(thing_hit) is Stairs:
                for step in thing_hit.steps:
                    if ServerRect.colliderect(test_rect, step.server_rect):
                        things_hit.append(step)
                things_hit.remove(thing_hit)

        for x in range(0, len(things_hit)):
            thing_hit_last_rect = things_hit[x].get_last_position()

            if things_hit[x].is_solid:
                if last_rect_location.bottom <= thing_hit_last_rect.top:
                    self.collision('above', things_hit[x])

                elif last_rect_location.right <= thing_hit_last_rect.left:
                    self.collision('on the left', things_hit[x])

                elif last_rect_location.left >= thing_hit_last_rect.right:
                    self.collision('on the right', things_hit[x])

                elif last_rect_location.top >= thing_hit_last_rect.bottom:
                    self.collision('under', things_hit[x])

                else:
                    self.collision('inside', things_hit[x])

#*************************************************************************************************
#*************************************************************************************************
#at one point this method would convert a given vector to a theta that is usable by the pygame.rotate method
#returns a theta
    @staticmethod
    def roto_theta_conversion_tool_extreme(vec):
        return -(math.degrees(math.atan2(vec.y, vec.x)) + 90)

#*************************************************************************************************
#*************************************************************************************************
#returns the center of the object using it's start position
    def get_center(self):
        return euclid.Vector2(self.start_position.x + self.get_width() / 2.0,
                              self.start_position.y + self.get_height() / 2.0)

#*************************************************************************************************
#*************************************************************************************************
#things can act on the actor when they get hit
    def on_collision(self, actor, direction):
        pass


class ServerRect(object):
    """for the people, by the people"""
    def __init__(self, left=1, top=1, width=2, height=2):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.center = self.get_center()
        self.bottom = self.top + self.height
        self.right = self.left + self.width

    def get_center(self):
        return euclid.Vector2(self.left + self.width / 2,
                              self.top + self.height / 2)

    def set_center(self, center=None, start_position=None):
        """correct entire object"""
        if center:
            self.left = center.x - self.width / 2
            self.top = center.y - self.height / 2
        elif start_position:
            self.left = start_position.x
            self.top = start_position.y

        self.center = self.get_center()
        self.bottom = self.top + self.height
        self.right = self.left + self.width

    @staticmethod
    def colliderect(rect_1, rect_2):
        """note that objects cannot be 'touching'"""
        overlap = True
        if rect_1.left >= rect_2.right or rect_1.right <= rect_2.left or rect_1.top >= rect_2.bottom or\
           rect_1.bottom <= rect_2.top:
            overlap = False

        return overlap

    def get_pygame_rect(self):
        from pygame import Rect
        return Rect(self.left, self.top, self.width, self.height)

    def reform_rect(self, width, height, center):
        self.width = width
        self.height = height
        self.set_center(center=center)

    def to_string(self):
        return str(self.left)+","+str(self.top)+"   "+str(self.width)+","+str(self.height)

    def set_bottom(self, new_bottom):
        self.bottom = new_bottom
        self.reform_with_bottom()

    def reform_with_bottom(self):
        self.top = self.bottom - self.height
        self.center = self.get_center()


#*************************************************************************************************
#*************************************************************************************************
#gets the vector from the mouse to an object
def get_vector_to_position(mouse_position, object_position):
    theta = math.atan2((mouse_position.y - object_position.y), (mouse_position.x - object_position.x))
    x_component = math.cos(theta)
    y_component = math.sin(theta)
    return euclid.Vector2(x_component, y_component)


#*************************************************************************************************
#*************************************************************************************************
#gets the distance as a vector from one object to another
def get_displacement(obj1pos, obj2pos):
    x_distance = math.fabs(obj1pos.x - obj2pos.x)
    y_distance = math.fabs(obj1pos.y - obj2pos.y)
    return euclid.Vector2(x_distance, y_distance)


def sign(value):
    """returns the sign of a given value"""
    return value / math.fabs(value)  # returns 1 or -1
