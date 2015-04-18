from chat_box import *
from colors import BLACK, OFF_WHITE
from collections import OrderedDict
from utilities.euclid import Vector2
from menu_elements.button import Button, TextButton
from menu_elements.label import Label
from menu_elements.text_field import TextField
from menu_elements.cycle_button import CycleButton
from networking.configuration import remote_server_name, remote_server_port, reserved_games, user_name
from networking.game import chat_message, Game, GameSettings, join_game, list_available_games
from menu_elements.UI_frame import UIFrame, TabFrame
from menus.equipment_menu import EquipmentFrame
from scene import Scene
from utilities.threading_helper import RepeatTask

import globals
import pygame


BUTTON_WIDTH = 500
BUTTON_HEIGHT = 50


class JoinGameLobby(Scene):
    """
    Where a player finds or creates a game.
    """

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF)
        screen_width, screen_height = self.screen.get_size()
        self.scene = None
        self.input = {}

        # Build frames.
        self.rooms_frame = RoomsFrame(Vector2(0, 20), screen_width, screen_height - 20 - 100, self)
        self.equipment_frame = EquipmentFrame(Vector2(0, 20), screen_width, screen_height - 20 - 100, self)
        names_frames = OrderedDict([('Rooms', self.rooms_frame), ('Equipment', self.equipment_frame)])
        self.tab_frame = TabFrame(Vector2(0, 0), 223, 20, names_frames, self)

        self.all_frames = [self.tab_frame, self.rooms_frame, self.equipment_frame]

        # Configuration
        globals.online_game = join_game(
            reserved_games['join_game_lobby'],
            remote_server_name,
            remote_server_port,
            user_name
        )

        # Init chat box.
        self.chat_box = ChatBox(always_visible=True, box_width=self.screen.get_width(), x_offset=20, y_offset=0,
                                box_height=100, max_chars=100, screen=self.screen)  # draws itself/loads it's own image

        self.menu_title_font = pygame.font.Font("resources/fonts/Zebulon.ttf", 30)
        self.logo = pygame.image.load('resources/images/white_logo.gif')
        self.logo_title_surfaces = [
            self.menu_title_font.render("Space", True, OFF_WHITE),
            self.menu_title_font.render("Snakes", True, OFF_WHITE)
        ]

    def draw(self):
        self.screen.fill(BLACK)
        if self.input:
            # Update chat box with user input and handle messages.
            chat_msg = self.chat_box.update(self.input)
            chat_message(
                chat_msg,
                globals.online_game.server,
                globals.online_game.server_port,
                user_name,
                globals.online_game.name
            )

        for i, logo_title_surface in enumerate(self.logo_title_surfaces):
            self.screen.blit(logo_title_surface, (600, i * 30 + 10))
        self.screen.blit(self.logo, (500, 10))

        # Blit frames to screen.
        for frame in self.all_frames:
            if frame.is_active:
                self.screen.blit(frame.image, frame.rect)

        chat_box_blit_dict = self.chat_box.get_blit_info()
        for key in chat_box_blit_dict:
            self.screen.blit(key, chat_box_blit_dict[key])

        chat_box_alpha_blit_dict = self.chat_box.get_alpha_blit_info()
        for key in chat_box_alpha_blit_dict:
            self.screen.blit(key, chat_box_alpha_blit_dict[key])

    def handle(self, key_store):
        key_store.set_pressed(pygame.event.get())
        self.input = key_store.menu_input

        return self.scene

    def update(self):
        if self.input:
             # Update frames.
            for frame in self.all_frames:
                if frame.is_active:
                    frame.update(self.input)


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************rooms frame************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#Where a player finds a game
class RoomsFrame(UIFrame):

    def __init__(self, start_position, width, height, frame_parent):
        #images
        UIFrame.__init__(self, start_position, width, height, frame_parent)

        #room frame and nav buttons
        self.room_frame = PageButton(Vector2(170, 150), 600, 300, self)

        #create game and search game
        self.make_game_frame = MakeGameSurface(Vector2(0, 150), self.room_frame.rect.left - 10,
                                               self.room_frame.get_height(), self)

        self.all_elements = [self.room_frame, self.make_game_frame]


class MakeGameSurface(UIFrame):
    """
    Player can create a new game here.

    Interface allows player to specify game attributes.
    """

    def __init__(self, start_position, width, height, parent_frame=None):
        #images
        UIFrame.__init__(self, start_position, width, height, parent_frame)

        #elements
        self.create_button = TextButton(Vector2(0, height - 23), width, 25,
                                        list(globals.button_img_list), "Create Game",
                                        self, self.create_pressed,
                                        text_pos=(29, 6))
        self.game_name_label = Label(Vector2(5, 0), "Room Name")
        self.game_name_text_field = TextField(Vector2(25, 15), width - 25, 15, "", list(globals.text_field_img_list),
                                              10, self)
        self.cycle_button = CycleButton(Vector2(5, self.game_name_text_field.start_position.y + 30.0), width - 10, 15,
                                        globals.map_names, self)

        self.all_elements = [self.create_button, self.game_name_label, self.cycle_button,
                             self.game_name_text_field]

    #*************************************************************************************************
    #*************************************************************************************************
    #if create is pressed
    def create_pressed(self):

        game_settings = GameSettings(server=remote_server_name,
                                     server_port=remote_server_port,
                                     name=self.game_name_text_field.text,
                                     user_name=user_name,
                                     map_name=self.cycle_button.get_selection())
        globals.online_game = Game(game_settings)
        #globals.current_screen = "game lobby"
        first_parent = self.main_frame_parent()
        from lobby import GameLobby
        first_parent.scene = GameLobby(globals.online_game.name)


#*****************************************************************************************************
#*****************************************************************************************************
#******************************************************PageButton*************************************
#*****************************************************************************************************
#*****************************************************************************************************
#Where a player finds a game
class PageButton(UIFrame):

    def __init__(self, start_position, width, height, parent_frame):
        UIFrame.__init__(self, start_position, width, height, parent_frame)

        self.buttons_per_page = height / BUTTON_HEIGHT
        self.current_page = 0
        self.start_position = start_position
        self.back_button = Button(Vector2(0, 0), 50, height,
                                     list(globals.forward_button_img_list), self, self.back_pressed)
        self.forward_button = Button(Vector2(width - 50, 0), 50, height,
                                  list(globals.back_button_img_list), self, self.forward_pressed)
        self.game_button_list = []

        #begin polling for rooms
        self.update_game_list_thread = RepeatTask(5, self.update_game_list)
        self.update_game_list_thread.start()

        #NOTE: this class dosn't use self.all_elements

    #*************************************************************************************************
    #*************************************************************************************************
    #returns a list of all the buttons in the frame
    def get_all_buttons(self):
        value = list(self.game_button_list)
        value.append(self.back_button)
        value.append(self.forward_button)
        return value

    #*************************************************************************************************
    #*************************************************************************************************
    #returns a list of all the buttons being displayed
    def get_displayed_objects(self):
        if len(self.game_button_list) - (self.buttons_per_page * self.current_page) >= self.buttons_per_page:
            value = self.game_button_list[self.buttons_per_page * self.current_page: self.buttons_per_page * (self.current_page + 1)]
        else:
            value = self.game_button_list[self.buttons_per_page * self.current_page: len(self.game_button_list)]

        value.append(self.back_button)
        value.append(self.forward_button)
        return value

    #*************************************************************************************************
    #*************************************************************************************************
    #if forward is pressed
    def back_pressed(self):
        if self.current_page != 0 and len(self.game_button_list) != 0:
            self.current_page -= 1

    #*************************************************************************************************
    #*************************************************************************************************
    #if back is pressed
    def forward_pressed(self):
        if math.ceil(float(len(self.game_button_list)) / float(self.buttons_per_page)) != self.current_page + 1 and\
           len(self.game_button_list) != 0:
            self.current_page += 1
        self.back_button.is_pressed = False

    #*************************************************************************************************
    #*************************************************************************************************
    #returns true if the given button is in the game_buttons list
    def is_game_button(self, button):
        return button in self.game_button_list

    #*************************************************************************************************
    #*************************************************************************************************
    #blits buttons to the frame
    def update(self, user_input):
        self.rect.center = self.get_center_frame_pov()
        self.image.fill(BLACK)
        for button in self.get_displayed_objects():
            button.update(user_input)
            self.image.blit(button.image, button.rect)

    #*************************************************************************************************
    #*************************************************************************************************
    #makes the game list
    def update_game_list(self):

        temp_game_button_list = self.game_button_list
        self.game_button_list = []

        game_name_list = list_available_games(remote_server_name, remote_server_port)

        ix = 0
        for button in temp_game_button_list:
            if button.text in game_name_list:
                if ix == 0 or ix % self.buttons_per_page == 0:
                    button.start_position = Vector2(self.back_button.rect.right, 0)
                    self.game_button_list.append(button)
                else:
                    button.start_position = Vector2(self.game_button_list[-1].start_position.x,
                                                    self.game_button_list[-1].start_position.y +
                                                    self.game_button_list[-1].get_height())
                    self.game_button_list.append(button)

                game_name_list.remove(button.text)
            ix += 1

        for new_game_name in game_name_list:
            if ix == 0 or ix % self.buttons_per_page == 0:
                self.game_button_list.append(TextButton(Vector2(self.back_button.rect.right, 0),
                                             BUTTON_WIDTH,
                                             BUTTON_HEIGHT,
                                             list(globals.join_game_img_list),
                                             new_game_name,
                                             self,
                                             self.enter_lobby,
                                             (40, 22)))
            else:
                self.game_button_list.append(TextButton(Vector2(self.game_button_list[-1].start_position.x,
                                                                self.game_button_list[-1].start_position.y +
                                                                self.game_button_list[-1].get_height()),
                                             BUTTON_WIDTH,
                                             BUTTON_HEIGHT,
                                             list(globals.join_game_img_list),
                                             new_game_name,
                                             self,
                                             self.enter_lobby,
                                             (40, 22)))
            ix += 1

    #*************************************************************************************************
    #*************************************************************************************************
    #makes the game list
    def enter_lobby(self, button):
        globals.online_game = join_game(button.text, remote_server_name, remote_server_port, user_name)
        #globals.current_screen = "game lobby"
        first_parent = self.main_frame_parent()
        from lobby import GameLobby
        first_parent.scene = GameLobby(globals.online_game.name)