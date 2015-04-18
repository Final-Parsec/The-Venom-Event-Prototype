from menu_elements.menu_object import MenuObject
from sprite_sheet import SpriteSheet

import pygame


class ReadyStatusIndicator(MenuObject):

    def __init__(self, start_position, ready=False):
        MenuObject.__init__(self, start_position)

        self.ready = False if not ready else True

        # Import ready status indicator images.
        ready_status_indicator_sheet = SpriteSheet('resources/images/ready_status_indicators.png')
        ready_status_image_list = [ready_status_indicator_sheet.imageAt(pygame.Rect(0, 0, 15, 15)),
                                   ready_status_indicator_sheet.imageAt(pygame.Rect(15, 0, 15, 15))]
        self.image_list = ready_status_image_list

    def update(self, user_input=None):
        if self.ready:
            self.image = self.image_list[1]
        else:
            self.image = self.image_list[0]