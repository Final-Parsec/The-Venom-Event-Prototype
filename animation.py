from globals import now, scale_image_list


#**********************************************************************************************************************
#**********************************************************************************************************************
#******************************************************Animation*******************************************************
#**********************************************************************************************************************
#**********************************************************************************************************************
#This class manages animated graphics for Snakes in space.
#The only thing an animation requires to exist is an image_list. However, you need to set it's other vars to show it on
#  the screen.  run_time is in seconds. Each image will be distributed evenly throughout the run_time.
#image_list_offset is a list of tuples indicating how far off each image is of it's intended location in an animation.
class Animation(object):
    def __init__(self, image_list, owner=None, run_time=0.0, function_on_reset=None, image_list_offset=None,
                 display_offset=None):

        self.image_list = image_list
        self.use_image_at = 0
        self.owner = owner  # owner is a world object
        self.run_time = run_time  # now is the time each frame is on the screen
        self.function_on_reset = function_on_reset
        self.image_list_offset = image_list_offset  # list of tuples
        self.display_offset = display_offset

        if owner:
            scale_image_list(self.owner.rect.width, self.owner.rect.height, self.image_list)

        self.last_image_change_time = 0
        self.start_time = -1  # when an animation starts this gets set to now(). when the animation ends it sets to -`1
        self.is_animating = False
        self.loop = False
        self.scale_flag = False
        self.reruns = 0
        self.start_image = 0  # the image to start the animation at.  all images before this in image_list are ignored.
        self.scale_width = 0
        self.scale_height = 0
        self.rect_list = []

#*************************************************************************************************
#*************************************************************************************************
#Start the animation.
#assumes you're running animation every frame.
    def start_animation(self, loop=False, reruns=0):
        self.use_image_at = 0
        self.start_time = now()
        self.is_animating = True
        self.loop = loop
        self.reruns = reruns
        self.scale_flag = False

#*************************************************************************************************
#*************************************************************************************************
#Start the animation with scaling each image to a constant size.
#assumes you're running animation every frame.
    def start_animation_constant_size(self, scale_width, scale_height, loop=False, reruns=0):
        self.start_time = now()
        self.is_animating = True
        self.loop = loop
        self.reruns = reruns
        self.scale_width = scale_width
        self.scale_height = scale_height
        self.scale_flag = True

#*************************************************************************************************
#*************************************************************************************************
#ends the animation.
    def end_animation(self):
        self.is_animating = False
        self.use_image_at = len(self.image_list) - 1

#*************************************************************************************************
#*************************************************************************************************
#returns current animation image the animation is on.
    def current_image(self):
        return self.image_list[self.use_image_at]

#*************************************************************************************************
#*************************************************************************************************
#Start the animation.
#assumes you're running animation every frame.
    def last_image(self):
        return self.image_list[-1]

#*************************************************************************************************
#*************************************************************************************************
#returns a copy of the animation with the correct owner
    def copy_animation(self, new_owner):
        return Animation(list(self.image_list), new_owner, self.run_time, self.function_on_reset)

#*************************************************************************************************
#*************************************************************************************************
#for things like displaying player running/dashing
    def animate_movement(self, left_to_right=True):
        current_time = now()
        time_to_switch = (current_time - self.last_image_change_time) > self.run_time
        reset = False

        if time_to_switch:
            #left_to_right will either display the images
            #going forward or backwards
            if left_to_right:
                self.use_image_at += 1
                if self.use_image_at >= len(self.image_list):
                    self.use_image_at = 0
                    reset = True
                    if self.function_on_reset:
                        self.function_on_reset()
            else:  # running backwards
                self.use_image_at -= 1
                if self.use_image_at <= -1:
                    self.use_image_at = len(self.image_list) - 1
                    reset = True
                    if self.function_on_reset:
                        self.function_on_reset()

            self.last_image_change_time = current_time

        self.owner.image = self.image_list[self.use_image_at]

        return reset