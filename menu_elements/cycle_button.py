from button import MomentaryButton
import globals
from utilities import euclid
from UI_frame import UIFrame


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************Cycle button*****************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#Where a player finds a game
class CycleButton(UIFrame):

    def __init__(self, start_position, width, height, labels=[], frame_parent=None):
        UIFrame.__init__(self, start_position, width, height, frame_parent)

        #elements
        self.back_button = MomentaryButton(euclid.Vector2(0, 0), 18, 15,
                                         list(globals.small_back_button_img_list), self,
                                         self.back_pressed)
        self.forward_button = MomentaryButton(euclid.Vector2(width - 20, 0), 18, 15,
                                            list(globals.small_forward_button_img_list), self,
                                            self.forward_pressed)
        self.labels = labels  # contains labels

        if self.labels:
            self.current_label = 0
        else:
            self.current_label = None

        #config
        self.center_elements()

    #*************************************************************************************************
    #*************************************************************************************************
    #gets the selected element
    def get_selection(self):
        if self.current_label is not None:
            return self.labels[self.current_label].text
        else:
            return "error"

    #*************************************************************************************************
    #*************************************************************************************************
    #putes a label in the elements list
    def add_element(self, label):
        label.rect.center = self.get_center()
        self.labels.append(label)

    #*************************************************************************************************
    #*************************************************************************************************
    #centers the labels in the cycle_button
    def center_elements(self):
        for label in self.labels:
            label.rect.center = self.get_center()

    #*************************************************************************************************
    #*************************************************************************************************
    #returns a list of all the buttons in the frame
    def get_displayed_objects(self):
        if self.current_label is not None:
            value = [self.labels[self.current_label], self.back_button, self.forward_button]
        else:
            value = [self.back_button, self.forward_button]
        return value

    #*************************************************************************************************
    #*************************************************************************************************
    #if forward is pressed
    def forward_pressed(self):
        if self.current_label is not None and self.current_label < len(self.labels):
            self.current_label += 1
        elif self.current_label is None:
            self.current_label = 0

        if self.current_label > len(self.labels) - 1:
            self.current_label = 0

        self.forward_button.is_pressed = False

    #*************************************************************************************************
    #*************************************************************************************************
    #if back is pressed
    def back_pressed(self):

        if self.current_label is not None and self.current_label >= 0:
            self.current_label -= 1
        elif self.current_label is None:
            self.current_label = len(self.labels) - 1

        if self.current_label < 0:
            self.current_label = len(self.labels) - 1

        self.back_button.is_pressed = False

    #*************************************************************************************************
    #*************************************************************************************************
    #blits buttons to the frame
    def update(self, user_input):
        self.rect.center = self.get_center_frame_pov()
        self.back_button.update(user_input)
        self.forward_button.update(user_input)

        self.image.fill([50, 50, 50])
        for element in self.get_displayed_objects():
            self.image.blit(element.image, element.rect)

    #*************************************************************************************************
    #*************************************************************************************************
    #blits buttons to the frame
    def get_center(self):
        return  euclid.Vector2(self.image.get_width() / 2.0, self.image.get_height() / 2.0)