from world_objects.server.pick_ups import ServerPickUp, ServerAmmo, ServerHealthPack, ServerLandMine
from utilities import euclid
from animation import Animation


class PickUp(ServerPickUp):
    def __init__(self, start_position, width, height, image_list, velocity=euclid.Vector2(0.0, 10.0),
                 max_displacement=euclid.Vector2(0, 5)):
        ServerPickUp.__init__(self, start_position, width, height, velocity, max_displacement)

        self.rect = self.server_rect.get_pygame_rect()
        self.animation = Animation(image_list, self)
        self.image = self.animation.current_image()


class Ammo(ServerAmmo, PickUp):
    def __init__(self, start_position, width, height, image_list):
        PickUp.__init__(self, start_position, width, height, image_list)
        ServerAmmo.__init__(self, start_position, width, height)

    def update(self):
        super(Ammo, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class HealthPack(ServerHealthPack, PickUp):
    def __init__(self, start_position, width, height, image_list, restores=float('inf')):
        PickUp.__init__(self, start_position, width, height, image_list)
        ServerHealthPack.__init__(self, start_position, width, height, restores)

    def update(self):
        super(HealthPack, self).update()
        self.rect = self.server_rect.get_pygame_rect()


class LandMine(ServerLandMine, PickUp):
    def __init__(self, start_position, width, height, image_list, damage=50):
        PickUp.__init__(self, start_position, width, height, image_list)
        ServerLandMine.__init__(self, start_position, width, height, damage)

    def update(self):
        super(LandMine, self).update()
        self.rect = self.server_rect.get_pygame_rect()


#***********************************************************************************************************************
#***********************************************************************************************************************
#****************************************************BeachBall** (IS A Pickup)******************************************
#***********************************************************************************************************************
#********test to make pickups bounce around*****************************************************************************
class BeachBall(PickUp):
    def __init__(self, start_position, canMove, height, length, time, image, velocity=euclid.Vector2(0.0, 0.0), gravity=euclid.Vector2(0.0, 100.0), damage=50):
        PickUp.__init__(self, start_position, canMove, height, length, time, image, velocity, gravity)
        #overrides
        self.is_solid = True

        self.floatTime = 15  # number of frames the object will float up.  This is half of the entire float process of up and down.
        self.displacement = 0  # number of frames moved since last time at original position.  this will equal floatTime at the top of the objects float cycle.
        self.floatRate = 12
        self.framesSinceLastFloat = 0
        self.damage = damage
        self.canMove = True
        self.bounce = 3
        self.disappear_on_use = False
        self.gravity = gravity

#*************************************************************************************************
#*************************************************************************************************
#damages for self.damage
    def on_collision(self, thing_hit):
        self.velocity = thing_hit.velocity + self.velocity

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image.
    def update(self):
        self.rect.center = euclid.Vector2(self.start_position.x + self.length / 2, self.start_position.y + self.height / 2)

#****PickUps can get pushed around when exploded and whatnot**************************************
#*************************************************************************************************
#hit top of object
    def collision_under(self, thing_hit):
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))
        self.start_position.y = thing_hit.start_position.y + thing_hit.get_height()

#*************************************************************************************************
#*************************************************************************************************
#hit bottom of object
    def collision_above(self, thing_hit):
        self.velocity = self.velocity.reflect(euclid.Vector2(0, 1))
        if math.fabs(self.velocity.y) < 150.0:
            self.velocity.y = 0.0
        self.start_position.y = thing_hit.start_position.y - self.get_height()

#*************************************************************************************************
#*************************************************************************************************
#hit right of object
    def collision_on_left(self, thing_hit):
        if type(player) is SpritePlayer:
            self.on_collision(thing_hit)
        else:
            self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))
            self.start_position.x = thing_hit.start_position.x - self.get_width()

#*************************************************************************************************
#*************************************************************************************************
#hit top of object
    def collision_on_right(self, thing_hit):
        if type(player) is SpritePlayer:
            self.on_collision(thing_hit)
        else:
            self.velocity = self.velocity.reflect(euclid.Vector2(1, 0))
            self.start_position.x = thing_hit.start_position.x + thing_hit.get_width()