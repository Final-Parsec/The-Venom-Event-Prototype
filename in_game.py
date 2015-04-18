from camera import Camera
from map_config import MapConfig
from world_objects.server.projectiles import ServerProjectile
from world_objects.client.sprite_player import SpritePlayer
from menu_elements.UI_frame import UIFrame
from menu_elements.button import TextButton, Button
from key_store import ESC, MOUSE_X, MOUSE_Y
from scene import Scene
from player_HUD import PlayerHUD
import pygame
from pygame import RESIZABLE
import globals
from colors import BLACK, GRAY
from utilities import euclid
from menu_elements.menu_object import MenuObject
from menus.join_game_lobby import JoinGameLobby
from menus.lobby import GameLobby

fps_limit = 60
clock = pygame.time.Clock()


class InGame(Scene):

    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720), RESIZABLE)
        globals.screen = self.screen
        self.scene = None
        self.input = {}

        # init player heads up display.  This is a frame
        self.player_hud_frame = PlayerHUD(self)
        self.pause_menu_frame = GamePauseMenu(euclid.Vector2(0, 0), self.screen.get_width(), self.screen.get_height(),
                                              self)
        self.all_frames = [self.player_hud_frame, self.pause_menu_frame]

        map_name = globals.online_game.map_name
        self.map = MapConfig("resources/maps/" + map_name + "/" + map_name + ".csv")
        self.player1 = self.map.world_object_list_dictionary["players"][0]
        globals.camera = Camera(self.player1, globals.worldSize[0], globals.worldSize[1], self.screen)

    def draw(self):
        if self.input:
            globals.camera.draw_sprites(self.map.get_background_objects(),
                                        self.map.get_foreground_objects(),
                                        self.map.world_object_list_dictionary["players"])

            for frame in self.all_frames:
                if frame.is_active:
                    self.screen.blit(frame.image, frame.rect)

    def handle(self, key_store):
        events = pygame.event.get()
        key_store.set_pressed(events)
        self.input = dict(key_store.user_input, **key_store.menu_input)

        if key_store.delta_time > .25:
            # This should fix the problem with the player teleporting outside of the world when the screen is moved.
            # It shouldn't be a problem once we get the server portion of the game working.
            pass
        else:

            if not self.pause_menu_frame.is_active:
                self.player1.react(dict(key_store.user_input.items() + key_store.menu_input.items()))

            for list_key in self.map.world_object_list_dictionary:
                for world_object in self.map.world_object_list_dictionary[list_key]:
                    world_object.move(key_store.delta_time)

            for list_key in self.map.world_object_list_dictionary:
                for world_object in self.map.world_object_list_dictionary[list_key]:
                    if isinstance(world_object, ServerProjectile):
                        world_object.detect_collision(self.map.world_object_list_dictionary["platforms"])
                    elif type(world_object) is SpritePlayer:
                        world_object.detect_collision(self.map.world_object_list_dictionary["platforms"] +
                                                      self.map.world_object_list_dictionary["pickups"])

            if self.input[ESC]:
                self.pause_menu_frame.is_active = not self.pause_menu_frame.is_active

        return self.scene

    def update(self):
        if self.input:
            for list_key in self.map.world_object_list_dictionary:
                living_objects = []
                for world_object in self.map.world_object_list_dictionary[list_key]:
                    world_object.update()
                    if world_object.is_alive:
                        living_objects.append(world_object)
                self.map.world_object_list_dictionary[list_key] = living_objects

            for frame in self.all_frames:
                if frame.is_active:
                    frame.update(self.input)

            globals.camera.update()

    def quit_game(self):
        self.scene = JoinGameLobby()

    def quit_to_lobby(self):
        self.scene = GameLobby(globals.online_game.name)


class GamePauseMenu(UIFrame):
    def __init__(self, start_position, width, height, frame_parent):
        #images
        UIFrame.__init__(self, start_position, width, height, frame_parent)
        self.background = Background(start_position, self, width, height)
        self.main_frame = MainFrame(start_position, 800, 600, self)

        self.is_active = False

        self.all_elements = [self.background, self.main_frame]

    def update(self, user_input):
        self.rect.width = self.main_frame_parent().screen.get_width()
        self.rect.height = self.main_frame_parent().screen.get_height()
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA, 32).convert_alpha()
        for element in self.all_elements:
            element.update(user_input)
            self.image.blit(element.image, element.rect)

    def close_pause_menu(self):
        self.is_active = False


class Background(MenuObject):
    def __init__(self, start_position, frame_parent, width, height):
        MenuObject.__init__(self, start_position, frame_parent, width, height)

    def update(self, user_input):
        self.rect.width = self.main_frame_parent().screen.get_width()
        self.rect.height = self.main_frame_parent().screen.get_height()
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(BLACK)
        self.image.set_alpha(150)


class MainFrame(UIFrame):
    def __init__(self, start_position, width, height, frame_parent):
        UIFrame.__init__(self, start_position, width, height, frame_parent)
        self.rect.center = self.frame_parent.rect.center

        self.close_button = Button(euclid.Vector2(width - 35, 5), 30, 30,
                                   list(globals.close_button_img_list), self, self.frame_parent.close_pause_menu)

        self.quit_game_button = TextButton(euclid.Vector2(5, 100), 145, 25,
                                    list(globals.button_img_list), "Quit Game", self,
                                    self.main_frame_parent().quit_game,
                                    text_pos=(25, 6))

        self.quit_to_lobby_button = TextButton(euclid.Vector2(5, 130), 160, 25,
                                    list(globals.button_img_list), "Quit to Lobby", self,
                                    self.main_frame_parent().quit_to_lobby,
                                    text_pos=(25, 6))

        self.all_elements = [self.close_button, self.quit_game_button, self.quit_to_lobby_button]

    def update(self, user_input):
        self.image.fill(GRAY)
        self.rect.center = self.frame_parent.rect.center
        for element in self.all_elements:
            element.update(user_input)
            self.image.blit(element.image, element.rect)