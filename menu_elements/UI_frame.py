from menu_elements.button import Button, ScalingTextButton
from menu_elements.menu_object import MenuObject
from utilities import euclid


import globals


#****************************************************************************************************
#****************************************************************************************************
#******************************************************UIFrame***************************************
#****************************************************************************************************
#****************************************************************************************************
#Where a player finds a game
class UIFrame(MenuObject):

    def __init__(self, start_position, width, height, frame_parent=None):
        MenuObject.__init__(self, start_position, frame_parent, width, height)
        self.all_elements = []

    #*************************************************************************************************
    #*************************************************************************************************
    #updates the frame image and all of its components
    def update(self, user_input):
        self.image.fill(0)
        for element in self.all_elements:
            element.update(user_input)
            self.image.blit(element.image, element.rect)


#****************************************************************************************************
#****************************************************************************************************
#*****************************************************PopFrame***************************************
#****************************************************************************************************
#****************************************************************************************************
#Where a player finds a game
class PopFrame(UIFrame):

    def __init__(self, start_position, width, height, frame_parent):
        UIFrame.__init__(self, start_position, width, height, frame_parent)
        self.close_button = Button(euclid.Vector2(0, 0), 25, 25,
                                   list(globals.forward_button_img_list), self, self.close)
        self.is_active = False

    #*************************************************************************************************
    #*************************************************************************************************
    #updates the frame image and all of its components
    def close(self, user_input):
        self.is_active = False


#****************************************************************************************************
#****************************************************************************************************
#******************************************************TabView**************************************
#****************************************************************************************************
#****************************************************************************************************
#Where a player finds a game
class TabFrame(UIFrame):

    def __init__(self, start_position, width, height, names_frame_map, frame_parent):
        #images
        UIFrame.__init__(self, start_position, width, height, frame_parent)
        self.all_elements = []
        self.names_frame_map = names_frame_map
        for name in names_frame_map:
            if self.all_elements:
                self.all_elements.append(ScalingTextButton(euclid.Vector2(self.all_elements[-1].rect.right + 10,
                                                                          0),
                                                           list(globals.button_img_list), name, self,
                                                           self.activate_frame, text_pos=(21, 6)))
            else:
                self.all_elements.append(ScalingTextButton(euclid.Vector2(10, 0),
                                                           list(globals.button_img_list), name,
                                                           self, self.activate_frame, text_pos=(20, 6)))

    #*************************************************************************************************
    #*************************************************************************************************
    #updates the frame image and all of its components
    def activate_frame(self, button):
        for frame in self.names_frame_map.values():
            if frame != self.names_frame_map[button.text]:
                frame.is_active = False
            else:
                frame.is_active = True
