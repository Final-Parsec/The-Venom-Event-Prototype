from utilities import euclid
import pygame


class MenuObject(pygame.sprite.Sprite):

    def __init__(self, start_position, frame_parent=None, width=0, height=0, image_list=[]):
        pygame.sprite.Sprite.__init__(self)

        self.start_position = start_position
        self.use_image_at = 0
        self.image_list = image_list
        self.frame_parent = frame_parent
        self.is_pressed = False
        self.is_active = True
        self.sound = None

        if image_list:
            scale_image_list(width, height, self.image_list)
            self.image = self.image_list[self.use_image_at]
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
            self.image_list = [self.image]

        self.rect = self.image.get_rect()
        self.rect.center = euclid.Vector2(start_position.x + width / 2.0, start_position.y + height / 2.0)

    #*****************************************************************************************
    #*****************************************************************************************
    #returns true if object was clicked
    def was_clicked(self, mouse_position):
        frame_pos = self.total_offset()

        value1 = self.rect.top + frame_pos[1] < mouse_position[1] and\
                 self.rect.bottom + frame_pos[1] > mouse_position[1]
        value2 = self.rect.left + frame_pos[0] < mouse_position[0] and\
                 self.rect.right + frame_pos[0] > mouse_position[0]

        return value1 and value2

    #*************************************************************************************************
    #*************************************************************************************************
    #finds the main frame
    def main_frame_parent(self):
        itr = self.frame_parent
        while hasattr(itr, 'frame_parent'):
            itr = itr.frame_parent

        return itr

    #*************************************************************************************************
    #*************************************************************************************************
    #finds the posiiton offset needed for the was_clicked method
    def total_offset(self):
        x_offset = 0.0
        y_offset = 0.0
        itr = self.frame_parent
        while itr and hasattr(itr, 'rect'):  # while not None
            x_offset = itr.rect.left + x_offset
            y_offset = itr.rect.top + y_offset
            itr = itr.frame_parent

        return x_offset, y_offset

    #*************************************************************************************************
    #*************************************************************************************************
    #returns the height of the object in pixels
    def get_height(self):
        return self.rect.bottom - self.rect.top

    #*************************************************************************************************
    #*************************************************************************************************
    #returns the width of the object in pixels
    def get_width(self):
        return self.rect.right - self.rect.left

    #*************************************************************************************************
    #*************************************************************************************************
    #gets center of object
    def get_center_frame_pov(self):
        return euclid.Vector2(self.start_position.x + self.get_width() / 2.0, self.start_position.y + self.get_height() / 2.0)


#*************************************************************************************************
#*************************************************************************************************
#scales all the images for the object
def scale_image_list(width, height, image_list, range_top=None, range_bottom=None):
    if range_top is None or range_bottom is None:
        range_top = len(image_list)
        range_bottom = 0
    for a in range(range_bottom, range_top):
        #print self.image_list[a], a
        image_list[a] = pygame.transform.scale(image_list[a], [int(width), int(height)])
