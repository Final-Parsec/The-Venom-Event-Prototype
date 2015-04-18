import pygame
from colors import BLACK
from chat_box import ChatBox
from utilities.euclid import Vector2
from sprite_sheet import SpriteSheet
from key_store import MOUSE_X, MOUSE_Y
import globals
from menu_elements.UI_frame import UIFrame


class PlayerHUD(UIFrame):
    """
    Holds the variables and methods for the player's heads up display (HUD).
    """

    def __init__(self, parent, start_position=Vector2(0.0, 0.0)):
        self.width = globals.screen.get_width()
        self.height = globals.screen.get_height()
        self.font = pygame.font.SysFont('arial', 12)

        UIFrame.__init__(self, start_position, self.width, self.height, parent)
        #WorldObject.__init__(self, start_position, self.screen_size_x, self.screen_size_y, velocity, image_list)

        #self.pause_menu = PauseMenu(font, self.screen_size_x, self.screen_size_y, screen)

        # # Make a chat box.
        # self.chat_box = ChatBox(player_heads_up_display=self)

        # Load sprite sheets.
        self.health = 0
        self.max_health = 0
        crosshair_sheet = SpriteSheet("resources/images/Crosshair Sheet.png")
        sprite_sheet = SpriteSheet("resources/images/Sprite Sheet1.png")

        # Load crosshair.
        self.crosshair = BlitData(crosshair_sheet.imageAt(pygame.Rect(176, 158, 46, 48)))

        # load health bar info
        self.hp_overlay = BlitData(sprite_sheet.imageAt(pygame.Rect(652, 373, 290, 90)), (0, 0))
        self.hp_bar = BlitData(sprite_sheet.imageAt(pygame.Rect(722, 485, 213, 40)), (64, 22))
        self.mana_bar = BlitData(sprite_sheet.imageAt(pygame.Rect(722, 529, 146, 20)), (68, 65), (0, 0, 159, 20))

        # set colorkey so black pixels will be transparent
        # self.image.set_colorkey(BLACK)  # set black to transparent
        # self.image.fill(BLACK)

        # ammo and weapon data
        self.ammo_string = "send me text"
        self.weapon_string = "send me text"
        self.ammo_string_surface = self.font.render(self.ammo_string, True, [255, 255, 255])
        self.weapon_string_surface = self.font.render(self.weapon_string, True, [255, 255, 255])
        self.ammo_blit = BlitData(self.ammo_string_surface,
                                  (globals.screen.get_width() / 1.16, globals.screen.get_height() / 1.11))
        self.weapon_blit = BlitData(self.weapon_string_surface,
                                    (globals.screen.get_width() / 1.16, globals.screen.get_height() / 1.066))
        # order this list in which one you want blit first.  top picture = last in the list.
        #self.blit_list = [self.hp_overlay, self.hp_bar, self.ammo_blit, self.weapon_blit, self.crosshair]
        self.blit_list = [self.hp_overlay, self.hp_bar, self.mana_bar, self.ammo_blit, self.weapon_blit, self.crosshair]

    def update(self, user_input):
        self.image.fill(0)
        self.update_elements(user_input)
        for blit_data in self.blit_list:
            if blit_data.area is not None:
                self.image.blit(blit_data.surface, blit_data.position, blit_data.area)
            else:
                self.image.blit(blit_data.surface, blit_data.position)

    def draw(self):
        self.image.fill(0)
        # self.image.set_colorkey(BLACK)  # set black to transparent
        # for blit_data in self.blit_list:
        #     if blit_data.area is not None:
        #         globals.screen.blit(blit_data.surface, blit_data.position, blit_data.area)
        #     else:
        #         globals.screen.blit(blit_data.surface, blit_data.position)

    def update_elements(self, user_input):
        self.weapon_string = self.frame_parent.player1.weapon_string
        self.ammo_string = self.frame_parent.player1.ammo_string
        self.health = self.frame_parent.player1.health
        self.max_health = self.frame_parent.player1.max_health
        self.hp_bar.area = (0, 0, float(self.health / self.max_health) * 220, 40)
        self.ammo_blit.surface = self.font.render(self.ammo_string, True, [255, 255, 255])
        self.weapon_blit.surface = self.font.render(self.weapon_string, True, [255, 255, 255])
        self.crosshair.position = (user_input[MOUSE_X] - self.crosshair.surface.get_width() * .5,
                                   user_input[MOUSE_Y] - self.crosshair.surface.get_height() * .5)


class BlitData(object):
    """
    holds data to blit playerHUD objects
    """
    def __init__(self, surface=None, position=(0, 0), area=None):
        self.surface = surface  # image of object
        self.position = position  # tuple of location
        self.area = area  # rect that defines what part of the image to blit.