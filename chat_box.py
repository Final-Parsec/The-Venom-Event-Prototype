from colors import WHITE
from datetime import datetime, timedelta
from menu_elements.text_field import *
from networking.configuration import user_name
from sprite_sheet import SpriteSheet
from string import *
from menu_elements.UI_frame import UIFrame
from utilities.threading_helper import RepeatTask

import globals
import pygame


class ChatBox(UIFrame):
    """
    Used for chatting. Handles user input and displays a log of messages.
    """

    LINE_HEIGHT = 18.5  # number of pixels a 12 font arial is in height about.

    def __init__(self, always_visible=False, x_offset=0, y_offset=0, box_width=None, box_height=None, max_chars=65,
                 player_heads_up_display=None, screen=None):
        self.screen = screen
        self.always_visible = always_visible
        self.max_chars = max_chars
        self.view_offset = 0  # The part of the text log you're viewing.  0 is the most recent on the bottom.

        # These values move the ChatBox from it's default position at the bottom left hand corner of the screen.
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.hidden = not self.always_visible  # while this is true the ChatBox shouldn't be displayed.
        self.alpha = 255
        self.delaying_to_fade = False
        self.is_fading = False  # while this is true, the ChatBox text is fading to transparency.
        self.fade_delay = 3  # seconds after the ChatBox is deselected until the text starts to fade.
        self.fade_time = 2  # seconds that it fades for after the fadeDelay
        self.last_deselect_time = 0  # time that the fade process started.
        self.last_fade_start_time = 0
        self.selected = False
        self.fade_proportion = 0  # This will hold the proportion to convert the time to terms of opacity (0-255)
        self.font = pygame.font.SysFont('arial', 12)

        self.cursor_blink_time = 1.5  # the cursor will change every half of this number
        self.last_cursor_blink = 0
        self.cursor_is_blinking = False
        self.cursor_surface = self.font.render("|", True, [255, 255, 255])

        self.text_content = []  # list of strings. lower index = older
        self.input = None  # a string of input to send to the textBox.
        self.surface_content = []  # a list of surface slices. lower index = older
        self.border_offset = 14  # offset text by ten pixels to account for the border of the chatBox
        self.blit_dict = {}
        self.alpha_blit_dict = {}

        temp_sprite_sheet = SpriteSheet("resources/images/Sprite Sheet1.png")
        self.box_image = temp_sprite_sheet.imageAt(pygame.Rect(5, 15, 370, 135))
        # this image is cursed to never change color.
        self.unfocused_image = temp_sprite_sheet.imageAt(pygame.Rect(6, 158, 368, 130))
        if box_width is not None and box_height is not None:
            self.box_image = pygame.transform.scale(self.box_image, (box_width, box_height))
            self.unfocused_image = pygame.transform.scale(self.box_image, (box_width, box_height))
        self.image = self.box_image  # everything will be blit onto here.

        self.shift_is_pressed = False

        if hasattr(globals, 'online_game'):
            self.last_message_received = 0
            self.get_new_messages_thread = RepeatTask(1, self.get_new_messages)
            self.get_new_messages_thread.start()

        self.player_heads_up_display = player_heads_up_display
        self.last_paused = datetime.now()

    #*************************************************************************************************
    #*************************************************************************************************
    #Updates the TextBox image if it's not hidden.
    #blits stuff on its own
    def update(self, userInput):
        returnString = ""

        #empty blitting dictionaries
        self.blit_dict.clear()
        self.alpha_blit_dict.clear()

        if (not self.hidden) or self.always_visible:
            if self.selected:
                #self.screen.blit(self.box_image, (0, self.screen.get_height() - self.box_image.get_height()))
                self.blit_dict.update({self.box_image: (0, self.screen.get_height() - self.box_image.get_height())})
                self.cursorBlink()
            elif self.delaying_to_fade and not self.always_visible:
                self.delay()  # waiting to fade text
            elif self.is_fading and not self.always_visible:
                #changes the self.alpha for the surface slices of text. The method disengage() sets isFading to true
                #  or not and sets lastFadeTime to now()
                self.fade()
            if self.always_visible and not self.selected:  # display a faded edge around the chatbox
                #TODO: unfocused_image is broken and cursed. nothing will change it's color. change it's color.
                ypos = self.screen.get_height() - self.unfocused_image.get_height()
                #self.screen.blit(self.unfocused_image, (0, ypos))
                self.blit_dict.update({self.unfocused_image: (0, ypos)})
            self.buildChatBoxImage(userInput)  # blits stuff

        # ChatBox handling for user input. Engages and disengages ChatBox.
        # These controls are disabled if the user is in the pause menu
        # (and 1 second after pausing due to conflict with Enter button).
        # if self.player_heads_up_display and self.player_heads_up_display.pause_menu.is_paused:
        #     self.last_paused = datetime.now()

        # if not self.player_heads_up_display or \
        #    (not self.player_heads_up_display.pause_menu.is_paused and
        #         (self.last_paused and datetime.now() - self.last_paused > timedelta(seconds=1))):
        # if not self.player_heads_up_display or \
        #         (self.last_paused and datetime.now() - self.last_paused > timedelta(seconds=1)):
        if self.last_paused and datetime.now() - self.last_paused > timedelta(seconds=1):
            if userInput[RETURN] and self.selected:  # if enter is pressed
                if userInput[INPUT_STRING]:
                    # Take out addText if you want to not artificially increase local user chat update speed.
                    # Other part is in get_new_messages.
                    returnString = userInput[INPUT_STRING]
                    self.addText(user_name + ': ' + userInput[INPUT_STRING])
                    userInput[INPUT_STRING] = ""
                    self.view_offset = 0
                self.disengage()
            elif userInput[RETURN]:
                userInput[INPUT_STRING] = ""
                self.engage()
            #elif (userInput[MOUSE_SCROLL_UP_PRESSED] and current_time - userInput[MOUSE_SCROLL_UP_UNPRESSED] == 0) or (userInput[ARROW_UP] and current_time - userInput[ARROW_UP_PRESSED] == 0):
            #scroll up and down
            elif userInput[MOUSE_SCROLL_UP] and self.view_offset < len(self.surface_content) - math.floor(self.box_image.get_height() / self.LINE_HEIGHT) + 1 and self.selected:  # round down.:
                self.view_offset += 1
            elif userInput[MOUSE_SCROLL_DOWN] and self.view_offset != 0 and self.selected:
                self.view_offset -= 1

        if returnString:
            return returnString

    #*************************************************************************************************
    #*************************************************************************************************
    #Builds the image of the chatbox using slices of text.
    #create the chat from the bottom up. lower index = older.
    def buildChatBoxImage(self, userInput):
        i = 0
        #chatboxCapacity includes the spot in the bottom for text input.
        chatBoxCapacity = math.floor(self.box_image.get_height() / self.LINE_HEIGHT)  # round down.

        #calculate x component of position
        curr_xpos = self.border_offset + self.x_offset

        #get first part of y component of position
        ypos_independent_offset = self.screen.get_height() - self.box_image.get_height()  # independent from i
        input_ypos_independent_offset = self.screen.get_height() - self.box_image.get_height()
        input_surface_xpos = self.border_offset + 5 + self.x_offset
        cursor_independent_ypos = self.screen.get_height() - self.box_image.get_height()

        while i < chatBoxCapacity - 1 and i < len(self.surface_content):
            #find the slice to blit; top to bottom here
            curr_slice = self.surface_content[len(self.surface_content) - (i + self.view_offset) - 1]

            #get the ypos components and add them together to get the y component of position
            slice_height = self.surface_content[len(self.surface_content) - i - 1].get_height()
            ypos_dependent_offset = (chatBoxCapacity - i - 1) * slice_height  # dependant on i
            curr_ypos = ypos_independent_offset + ypos_dependent_offset

            #globals.blit_alpha(curr_slice, (curr_xpos, curr_ypos), self.screen, self.alpha, self.box_image.get_rect())
            self.alpha_blit_dict.update({curr_slice: (curr_xpos, curr_ypos)})
            i += 1
        #draw the text that the user is typing in
        if userInput[INPUT_STRING] is not None and self.selected:
            #scroll the text left and right if it's too big for the input box
            if len(userInput[INPUT_STRING]) > self.max_chars:
                snipIndex = len(userInput[INPUT_STRING]) - self.max_chars
            else:
                snipIndex = 0
            inputSurface = self.font.render(userInput[INPUT_STRING][snipIndex:len(userInput[INPUT_STRING])], True, WHITE)

            #blit input surface
            input_dependent_ypos = (chatBoxCapacity) * inputSurface.get_height()
            input_ypos = input_ypos_independent_offset + input_dependent_ypos
            #self.screen.blit(inputSurface, (input_surface_xpos, input_ypos))
            self.blit_dict.update({inputSurface: (input_surface_xpos, input_ypos)})

            #blit cursor
            cursor_xpos = self.border_offset + 5 + self.x_offset + inputSurface.get_width()
            cursor_ypos = cursor_independent_ypos + (chatBoxCapacity) * inputSurface.get_height()
            #self.screen.blit(self.cursor_surface, (cursor_xpos, cursor_ypos))
            self.blit_dict.update({self.cursor_surface: (cursor_xpos, cursor_ypos)})

    #*************************************************************************************************
    #*************************************************************************************************
    #Add a new line of text to the chatbox
    #important: in order to set the alpha of text, you have to first blit it to a surface.  if you just blit the text, it won't ever be able to be transparent.
    def addText(self, text, color=[255, 255, 255]):
        chatLine = ChatLine(text, self.max_chars)  # returns a list of surfaces if the text needs to be wordwrapped.
        self.text_content.append(text)  # store text into textContent before it's truncated
        if len(text) > self.max_chars:
            text = text[0:self.max_chars]  # substring from 0 to maxChars.  The full string is still stored in textContent.
        for x in chatLine.lines:  # rest of chat box
            self.surface_content.append(self.font.render(x, True, color))
        #self.surfaceContent.append(self.font.render(text, True, color))

    #*************************************************************************************************
    #*************************************************************************************************
    #get ready to accept input
    def engage(self):
        self.hidden = False
        self.alpha = 255  # set each surfacecontent surface's alpha to 250
        self.selected = True  # when the chatbox is selected it is accepting input from the player.

    #*************************************************************************************************
    #*************************************************************************************************
    #stop accepting input
    def disengage(self):
        self.selected = False
        self.delaying_to_fade = True
        self.last_deselect_time = now()

    #*************************************************************************************************
    #*************************************************************************************************
    #makes the cursor blink.
    def cursorBlink(self):
        if now() - self.last_cursor_blink > self.cursor_blink_time / 2 and now() - self.last_cursor_blink < self.cursor_blink_time:
            self.cursor_surface = self.font.render(" ", True, [255, 255, 255])
            self.cursor_is_blinking = True
        elif now() - self.last_cursor_blink > self.cursor_blink_time:
            self.cursor_surface = self.font.render("|", True, [255, 255, 255])
            self.cursor_is_blinking = False
            self.last_cursor_blink = now()

    #*************************************************************************************************
    #*************************************************************************************************
    #show text on screen until delay timer expires
    def delay(self):
        if now() - self.last_deselect_time > self.fade_delay:  # now() returns seconds.  It's time to fade the text if this is True
            self.is_fading = True
            self.fade_proportion = now() / 255
            self.last_fade_start_time = now()
            self.delaying_to_fade = False

    #*************************************************************************************************
    #*************************************************************************************************
    #fade the text to nothing after a delay.  assume self.isfading == True and self.lastDeselectTime has been set.
    def fade(self):
        for index in range(0, len(self.surface_content)):
            #self.surfaceContent[index].set_alpha(255 - ((now() - self.lastFadeStartTime) * (255 / self.fadeTime)))
            self.alpha = 255 - ((now() - self.last_fade_start_time) * (255 / self.fade_time))
            #print self.surfaceContent[index].get_alpha()
        if now() - self.last_fade_start_time > self.fade_time:  # done fading
            self.is_fading = False
            self.hidden = True

    def get_new_messages(self):
        """
        Polls the server for new messages on a timer.
        """

        if hasattr(globals, 'online_game') and globals.online_game is not None:
            response = globals.online_game.get_new_messages(self.last_message_received)

            if response['last_received'] > self.last_message_received:
                self.last_message_received = response['last_received']

            for new_message in response['messages']:
                self.engage()
                self.disengage()
                if find(new_message, user_name[:len(user_name)]) == -1:  # string.find find the lowest index.-1 no match
                    self.addText(new_message)
        else:
            self.get_new_messages_thread.stop()

    #*************************************************************************************************
    #*************************************************************************************************
    #gets blit_dict
    def get_blit_info(self):
        return self.blit_dict

    #*************************************************************************************************
    #*************************************************************************************************
    #gets alpha_blit_dict
    def get_alpha_blit_info(self):
        return self.alpha_blit_dict

    #*************************************************************************************************
    #*************************************************************************************************
    #gets alpha_blit_dict
    def get_alpha(self):
        return self.alpha


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************ChatLine*********************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#a chat message is a chatLine.  it contains text and however many surfaces are needed for the space provided in the chatboxes for wordwrap.
class ChatLine(object):
    def __init__(self, text, maxChars):
        self.text = text
        self.lines = []
        numSurfaces = 0
        if text is not None:
            numSurfaces = int(math.ceil(float(len(text)) / float(maxChars)))
            #print "num surfaces:"
            #print numSurfaces
            for i in range(0, numSurfaces):
                #print "i * maxChars = "
                #print i * maxChars
                #print len(text)
                if i * maxChars > len(text):
                    self.lines.append("    " + text[i * maxChars:])
                    #print "end"
                elif i != 0:
                    self.lines.append("    " + text[i * maxChars:(i + 1) * maxChars])
                else:
                    self.lines.append(text[i * maxChars:(i + 1) * maxChars])
                    #print "adding "
                    #print self.lines[-1]  # last element of list