import pygame
from menu_object import MenuObject


class Label(MenuObject):
    def __init__(self, start_position, text, frame_parent=None, font_size=10):
        MenuObject.__init__(self, start_position, frame_parent)

        self.font = pygame.font.Font("resources/fonts/Zebulon.ttf", font_size)
        self.text = text
        self.image = self.font.render(self.text, False, [255, 255, 255])
        self.rect = self.image.get_rect()

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #update the label
    def update(self, user_input=None):
        self.rect.center = self.get_center_frame_pov()

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #puts text on the button images. Label only uses 1 image
    def put_name_on_images(self):
        self.image = self.font.render(self.text, False, [255, 255, 255])



