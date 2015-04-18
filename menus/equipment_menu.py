import globals
from utilities import euclid
from menu_elements.UI_frame import UIFrame
from menu_elements.button import TextButton
from menu_elements.label import Label
from menu_elements.text_field import TextField
from networking.configuration import user_name


#****************************************************************************************************
#****************************************************************************************************
#******************************************************EquipmentFrame********************************
#****************************************************************************************************
#****************************************************************************************************
#Where a player finds a game
class EquipmentFrame(UIFrame):

    def __init__(self, start_position, width, height, frame_parent):
        #images
        UIFrame.__init__(self, start_position, width, height, frame_parent)
        self.is_active = False
        self.player_data_frame = PlayerDataFrame(euclid.Vector2(170, 150), 300, 100, self)

        self.all_elements = [self.player_data_frame]


#****************************************************************************************************
#****************************************************************************************************
#******************************************************PlayerDataFrame*******************************
#****************************************************************************************************
#****************************************************************************************************
#Where a player finds a game
class PlayerDataFrame(UIFrame):

    def __init__(self, start_position, width, height, parent_frame=None):
        #images
        UIFrame.__init__(self, start_position, width, height, parent_frame)
        self.display_name_label = Label(euclid.Vector2(0, 0), "Displayed Name:", self)
        self.display_name_textfield = TextField(euclid.Vector2(width - 150,
                                                               self.display_name_label.rect.top),
                                                150, 15, user_name, list(globals.text_field_img_list), 10, self)

        self.save_button = TextButton(euclid.Vector2(width / 2 - 25, height - 20), 50, 20,
                                      list(globals.ready_button_img_list), "Save", self, self.save_pressed)

        self.all_elements = [self.display_name_label, self.display_name_textfield, self.save_button]

    #*************************************************************************************************
    #*************************************************************************************************
    #runs when the save button is pressed
    def save_pressed(self):
        if self.display_name_textfield.text:
            fuckn_whatever = self.display_name_textfield.text