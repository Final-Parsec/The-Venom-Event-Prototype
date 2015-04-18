import pygame
from menu_elements.menu_object import MenuObject
from key_store import *


class TextField(MenuObject):
    def __init__(self, start_position, width, height, text, image_list, font_size=10, frame_parent=None,
                 text_pos=(5, 1)):
        MenuObject.__init__(self, start_position, frame_parent, width, height, image_list)
        self.is_active = False
        self.font = pygame.font.Font("resources/fonts/Zebulon.ttf", font_size)
        self.text = text
        self.text_pos = text_pos
        self.text_bar = "|"
        self.last_blink_time = 0.0

        #config
        self.put_name_on_images()

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #will blink the text bar
    def blink_bar(self):
        current_time = now()
        if current_time - self.last_blink_time > .5:
            self.last_blink_time = current_time
            if self.text_bar == "":
                self.text_bar = "|"
            else:
                self.text_bar = ""

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #update the label
    def update(self, menu_input):
        self.blink_bar()
        self.rect.center = self.get_center_frame_pov()
        if menu_input[LEFT_CLICK]:
            if self.was_clicked((menu_input[MOUSE_X], menu_input[MOUSE_Y])):
                self.is_active = True
                menu_input[INPUT_STRING] = self.text
            else:
                self.is_active = False

        if menu_input[RETURN] and self.is_active:
            self.is_active = False

        if self.is_active:
            self.text = menu_input[INPUT_STRING]
            self.use_image_at = 0
        else:
            self.use_image_at = 1

        self.put_name_on_images()

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #puts text on the button images. Label only uses 1 image
    def put_name_on_images(self):
        text_img = self.font.render(self.text, True, [255, 255, 255])
        bar_img = self.font.render(self.text_bar, True, [255, 255, 255])
        self.image = self.image_list[self.use_image_at].copy()

        if text_img.get_width() >= self.image.get_width() - self.text_pos[0]:
            self.image.blit(text_img, (-(text_img.get_width() - self.image.get_width() + self.text_pos[0]),
                                       self.text_pos[1]))
            if self.is_active:
                self.image.blit(bar_img, (self.image.get_width() - self.text_pos[0], self.text_pos[1]))
        else:
            self.image.blit(text_img, self.text_pos)
            if self.is_active:
                self.image.blit(bar_img, (text_img.get_width() + self.text_pos[0], self.text_pos[1]))

