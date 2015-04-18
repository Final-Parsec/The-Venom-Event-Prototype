import pygame
from menu_object import MenuObject
from key_store import*
import inspect
import globals


class Button(MenuObject):
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #makes button
    def __init__(self, start_position, width, height, image_list, frame_parent=None, function=None):
        MenuObject.__init__(self, start_position, frame_parent, width, height, image_list)
        self.function = function
        self.sound = globals.button_1_sound

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #update button status
    def update(self, user_input):
        self.rect.center = self.get_center_frame_pov()
        if user_input[LEFT_CLICK]:
            if self.was_clicked((user_input[MOUSE_X], user_input[MOUSE_Y])):
                self.is_pressed = not self.is_pressed
                self.use_image_at += 1
                if self.sound:
                    self.sound.play()
                if self.function:
                    if len(inspect.getargspec(self.function).args) == 2:
                        self.function(self)
                    else:
                        self.function()
            if self.use_image_at == len(self.image_list):
                self.use_image_at = 0

        self.image = self.image_list[self.use_image_at]


class TextButton(Button):
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    def __init__(self, start_position, width, height, image_list, text, frame_parent=None, function=None,
                 text_pos=(0, 0)):
        Button.__init__(self, start_position, width, height, image_list, frame_parent, function)
        self.font = pygame.font.Font("resources/fonts/Zebulon.ttf", 10)
        self.text = text
        self.text_pos = text_pos
        self.put_name_on_images()

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #update button status
    def put_name_on_images(self):
        if self.text:
            for x in range(0, len(self.image_list)):
                temp_surface = self.font.render(self.text, True, [255, 255, 255])
                self.image_list[x].blit(temp_surface, self.text_pos)
        self.image = self.image_list[self.use_image_at]


class ScalingTextButton(TextButton):
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    def __init__(self, start_position, image_list, text, frame_parent=None, function=None, text_pos=(0, 0)):
        self.font = pygame.font.Font("resources/fonts/Zebulon.ttf", 10)
        image_temp = self.font.render(text, False, [0, 0, 0])
        width, height = image_temp.get_size()
        width += 40  # horizontal padding
        height += 10  # vertical padding
        TextButton.__init__(self, start_position, width, height, image_list, text, frame_parent, function, text_pos)


class MomentaryButton(Button):
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    def __init__(self, start_position, width, height, image_list, frame_parent=None, function=None):
        Button.__init__(self, start_position, width, height, image_list, frame_parent, function)

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #update button status
    def update(self, user_input):
        self.rect.center = self.get_center_frame_pov()
        if user_input[LEFT_CLICK]:
            if self.was_clicked((user_input[MOUSE_X], user_input[MOUSE_Y])):
                self.use_image_at = 1
                self.is_pressed = not self.is_pressed
                if self.sound:
                    self.sound.play()
                if self.function:
                    if len(inspect.getargspec(self.function).args) == 2:
                        self.function(self)
                    else:
                        self.function()

        if user_input[LEFT_CLICK_UP]:
            self.use_image_at = 0

        if self.use_image_at == len(self.image_list):
                self.use_image_at = 0

        self.image = self.image_list[self.use_image_at]
