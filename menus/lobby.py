from chat_box import *
from colors import BLACK, OFF_WHITE
from utilities.euclid import Vector2
from menu_elements.button import TextButton
from menu_elements.label import Label
from menu_elements.ready_status_indicator import ReadyStatusIndicator
from menu_elements.UI_frame import UIFrame, TabFrame
from networking.player import PlayerNetworking
from networking.game import chat_message
from utilities.threading_helper import RepeatTask
from menus.equipment_menu import EquipmentFrame
from collections import OrderedDict
from scene import Scene

import globals
import pygame


class GameLobby(Scene):
    """
    A GameLobby contains all of the necessary items to start a game.

    A chat, a lobby UI, players in the lobby, and the lobby information itself.
    """

    def __init__(self, game_name):
        self.input = {}
        self.scene = None
        self.background_surface = pygame.image.load('resources/images/game_lobby_background_blue.png')
        self.game_name = game_name
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF)
        self.chat_box = ChatBox(always_visible=True, box_width=self.screen.get_width(),
                                x_offset=20, y_offset=0, box_height=100, max_chars=100,
                                screen=self.screen)  # draws itself/loads it's own image

        # Set screen size.
        screen_width, screen_height = self.screen.get_size()

        #lobby_frame
        self.lobby_frame = LobbyFrame(Vector2(0, 20), screen_width, screen_height - 20 - 100, self)
        #equipment frame
        self.equipment_frame = EquipmentFrame(euclid.Vector2(0, 20), screen_width, screen_height - 20 - 100, self)
        #tab frame
        names_frames = OrderedDict([('Lobby', self.lobby_frame), ('Equipment', self.equipment_frame)])
        self.tab_frame = TabFrame(euclid.Vector2(0, 0), 223, 20, names_frames, self)

        self.all_frames = [self.tab_frame, self.lobby_frame, self.equipment_frame]

        self.menu_title_font = pygame.font.Font("resources/fonts/Zebulon.ttf", 30)
        self.logo = pygame.image.load('resources/images/white_logo.gif')
        self.logo_title_surfaces = [
            self.menu_title_font.render("Space", True, OFF_WHITE),
            self.menu_title_font.render("Snakes", True, OFF_WHITE)
        ]

        pygame.mouse.set_visible(True)

    def draw(self):
        self.screen.fill(BLACK)

        # background
        self.screen.blit(self.background_surface, (0, 0))

        #TODO fix chatBox so it doesn't blit in it's update method...
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

        # logo
        for i, logo_title_surface in enumerate(self.logo_title_surfaces):
            self.screen.blit(logo_title_surface, (600, i * 30 + 10))
        self.screen.blit(self.logo, (500, 10))

        # Blit frames to screen.
        for frame in self.all_frames:
            if frame.is_active:
                self.screen.blit(frame.image, frame.rect)

    def handle(self, key_store):

        key_store.set_pressed(pygame.event.get())
        self.input = key_store.menu_input

        return self.scene

    def update(self):
        """
        Updates the lobby. This should be run every frame.

        We need events for the raw text input (from menu_input) for writing in self.chat_box.
        """
        if globals.online_game.status == 'in_game':
            from in_game import InGame
            self.scene = InGame()

        if self.input:
            for frame in self.all_frames:
                if frame.is_active:
                    frame.update(self.input)

    @staticmethod
    def start_game_pressed():
        globals.online_game.set_status('in_game')


class LobbyFrame(UIFrame):
    """
    Main UIFrame for the pre-game lobby. Contains ready & start buttons, player list, etc.
    """

    def __init__(self, start_position, width, height, parent_frame):
        UIFrame.__init__(self, start_position, width, height, parent_frame)

        self.parent_frame = parent_frame

        #butons_frame
        self.buttons_frame = ButtonsFrame(Vector2(0, 60), width, height - 60, self, parent_frame)
        self.player_list_frame = PlayerListFrame(Vector2(0, 50), 250, height - 100, self)

        self.all_elements = [self.buttons_frame, self.player_list_frame]


class ButtonsFrame(UIFrame):
    """
    UIFrame for ready and start buttons.
    """

    def __init__(self, start_position, width, height, parent_frame, game_lobby):
        UIFrame.__init__(self, start_position, width, height, parent_frame)
        #buttons
        self.ready_button = TextButton(Vector2(0, 0), 157, 38,
                                       list(globals.ready_button_img_list),
                                       "",
                                       self,
                                       function=PlayerNetworking().set_player_ready_status)
        self.start_game_button = TextButton(Vector2(160, 0), 145, 23,
                                            list(globals.button_img_list), "Start Game", self,
                                            game_lobby.start_game_pressed,
                                            text_pos=(25, 6))

        self.all_elements = [self.ready_button, self.start_game_button]

    def update(self, menu_input):
        """
        updates the frame image and all of its components
        """

        for element in self.all_elements:
            element.update(menu_input)
            self.image.blit(element.image, element.rect)


class PlayerListFrame(UIFrame):
    """
    UIFrame for showing players and their ready statuses.
    """

    def __init__(self, start_position, width, height, parent_frame):
        UIFrame.__init__(self, start_position, width, height, parent_frame)

        self.list_padding = 30
        self.parent_frame = parent_frame
        self.height = height
        self.width = width
        self.background_surface = pygame.image.load('resources/images/game_lobby_background_blue.png')

        self.all_elements = []

        self.update_player_list_thread = None
        self.__update_player_list()

    def update(self, menu_input):
        self.image.blit(self.background_surface, self.start_position, pygame.Rect(0, 0, self.width, self.height))

        for element in self.all_elements:
            element.update()
            self.image.blit(element.image, element.rect)

    def __update_player_list(self):
        self.update_player_list_thread = RepeatTask(.5, self.update_player_list)
        self.update_player_list_thread.start()

    def update_player_list(self, height_for_player_name=30):
        """
        Updates players in the lobby from the server.
        """

        if hasattr(globals, 'online_game') and globals.online_game is not None:
            players = globals.online_game.get_players()
            temp_elements = []
            for offset, player in enumerate(players):
                location = (self.list_padding,
                            ((height_for_player_name * offset + 1) + self.list_padding / 2) + self.start_position[1])
                temp_elements.append(Label(Vector2(location[0], location[1]), player.user_name, font_size=14))
                temp_elements.append(ReadyStatusIndicator(Vector2(location[0] - 20, location[1]), player.ready))

            self.all_elements = list(temp_elements)  # make a copy. this prevents flicker as the list populates.