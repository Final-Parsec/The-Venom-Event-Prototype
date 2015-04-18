from animation import Animation
from world_objects import WorldObject
from utilities import euclid


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************AnimatedObject*******************************************
#*************************************************************************************************************
#*************************************************************************************************************
class AnimatedObject(WorldObject):

    def __init__(self, start_position, width, height, image_list, run_time):
        WorldObject.__init__(self, start_position, width, height)
        self.rect = self.server_rect.get_pygame_rect()
        self.default_animation = Animation(image_list, self, run_time)
        self.image = self.default_animation.current_image()

#*************************************************************************************************
#*************************************************************************************************
#used to update object rect
    def update(self):
        self.default_animation.animate_movement()
        self.rect.center = euclid.Vector2(self.start_position.x + self.get_width() / 2,
                                          self.start_position.y + self.get_height() / 2)


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************spawn****************************************************
#*************************************************************************************************************
#*************************************************************************************************************
class Spawnimation(AnimatedObject):

    def __init__(self, start_position, width, height, image_list, player, run_time=.05):
        AnimatedObject.__init__(self, start_position, width, height, image_list, run_time)
        self.player = player

#*************************************************************************************************
#*************************************************************************************************
#used to update object rect
    def update(self):
        self.is_alive = not self.default_animation.animate_movement()
        if not self.is_alive:
            self.image = self.default_animation.last_image()

        self.rect.center = self.player.rect.center
        self.rect.bottom = self.player.rect.bottom
        self.start_position = euclid.Vector2(self.rect.left, self.rect.top)


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************GrandfatherClock*****************************************
#*************************************************************************************************************
#*************************************************************************************************************
class GrandfatherClock(AnimatedObject):

    def __init__(self, start_position, width, height, image_list):
        run_time = .5
        AnimatedObject.__init__(self, start_position, width, height, image_list, run_time)


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************DustCloud************************************************
#*************************************************************************************************************
#*************************************************************************************************************
class DustCloud(AnimatedObject):

    def __init__(self, start_position, width, height, image_list):
        run_time = .1
        AnimatedObject.__init__(self, start_position, width, height, image_list, run_time)

#*************************************************************************************************
#*************************************************************************************************
#used to update object rect
    def update(self):
        self.is_alive = not self.default_animation.animate_movement()
        if not self.is_alive:
            self.image = self.default_animation.last_image()
        self.rect.center = euclid.Vector2(self.start_position.x + self.get_width() / 2,
                                          self.start_position.y + self.get_height() / 2)


#*************************************************************************************************************
#*************************************************************************************************************
#****************************************************BusterCharge************************************************
#*************************************************************************************************************
#*************************************************************************************************************
class BusterCharge(AnimatedObject):

    def __init__(self, start_position, width, height, image_list, buster):
        run_time = .15
        AnimatedObject.__init__(self, start_position, width, height, image_list, run_time)
        self.buster = buster
        self.is_alive = False

#*************************************************************************************************
#*************************************************************************************************
#used to update object animation
    def update(self):
        if not self.buster.is_charging:
            self.is_alive = False

        self.default_animation.animate_movement()

#*************************************************************************************************
#*************************************************************************************************
#needed to stop image lag
    def manual_update(self):
        self.rect.center = self.buster.end_of_barrel