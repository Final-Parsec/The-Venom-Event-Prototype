from colors import BLACK, OFF_WHITE
from networking.configuration import user_name
from networking.game import leave_game
from pygame.locals import DOUBLEBUF
from scene import Scene
from sys import exit
from key_store import LEFT_ARROW, RIGHT_ARROW, ENTER

import globals
import pygame


class MainMenu(Scene):

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF)

        # Load resources.
        self.background_surface = pygame.image.load('resources/images/main_menu_background_900x675.png')
        self.logo = pygame.image.load('resources/images/white_logo.gif')
        self.menu_title_font = pygame.font.Font("resources/fonts/Zebulon.ttf", 30)
        self.menu_option_font = pygame.font.SysFont("arial", 40)

        # Menu configuration.
        self.menu = ['Join Game', 'Options', 'Exit']

        # Determine menu option widths.
        self.menu_widths = []
        for menu_option in self.menu:
            text_surface = self.menu_option_font.render('    %s    ' % menu_option, True, OFF_WHITE)
            self.menu_widths.append(text_surface.get_width())

        # Generate text surfaces as they are static. No need to do this each frame.
        self.logo_title_surfaces = [
            self.menu_title_font.render("Space", True, OFF_WHITE),
            self.menu_title_font.render("Snakes", True, OFF_WHITE)
        ]

        combined_options = ''.join(['    %s    ' % f for f in self.menu])
        self.menu_text_surface = self.menu_option_font.render(combined_options, True, OFF_WHITE)

        # Ensure the user has left any online game they were in.
        if hasattr(globals, 'online_game') and globals.online_game is not None:
            leave_game(
                game_name=globals.online_game.name,
                server=globals.online_game.server,
                server_port=globals.online_game.server_port,
                user_name=user_name
            )
            globals.online_game = None

        # Menu position and transition state.
        self.selected_menu = 0
        self.background_x = -50
        self.text_x = self.__center_text_x()
        self.animating_left = False
        self.animating_right = False
        self.end_text_animation = 0
        self.end_background_animation = 0

        pygame.mouse.set_visible(True)

    def draw(self):
        # Order of layers back to front: menu, semi-transparent background, title.
        self.screen.fill(BLACK)
        self.screen.blit(self.menu_text_surface, (self.text_x, 280))
        self.screen.blit(self.background_surface, (self.background_x, -35))
        for i, logo_title_surface in enumerate(self.logo_title_surfaces):
            self.screen.blit(logo_title_surface, (600, i * 30 + 10))
        self.screen.blit(self.logo, (500, 10))

    def handle(self, key_store):
        key_store.set_pressed(pygame.event.get())
        menu_input = key_store.menu_input

        if menu_input[LEFT_ARROW] and not (self.animating_left or self.animating_right):
            if self.selected_menu == 0:
                self.selected_menu = len(self.menu) - 1
                self.text_x = self.__center_text_x()
                self.background_x = len(self.menu) * -20 - 50
            else:
                self.animating_left = True
                self.end_background_animation = self.background_x + 20
                self.selected_menu -= 1
                self.end_text_animation = self.__center_text_x()
        if menu_input[RIGHT_ARROW] and not (self.animating_left or self.animating_right):
            if self.selected_menu == len(self.menu) - 1:
                self.selected_menu = 0
                self.text_x = self.__center_text_x()
                self.background_x = -50
            else:
                self.animating_right = True
                self.end_background_animation = self.background_x - 20
                self.selected_menu += 1
                self.end_text_animation = self.__center_text_x()
        if menu_input[ENTER]:
            return self.select()

    def select(self):
        selected_option = self.menu[self.selected_menu]

        if selected_option == 'Join Game':
            from join_game_lobby import JoinGameLobby

            globals.current_screen = 'join game lobby'  # todo: remove this once all scenes are complete
            return JoinGameLobby()
        if selected_option == 'Options':
            pass
        if selected_option == 'Exit':
            pygame.quit()
            exit()

    def update(self):
        if self.animating_right:
            if self.end_background_animation < self.background_x:
                self.background_x -= 1
            if self.end_text_animation < self.text_x:
                self.text_x -= 12
            if self.end_background_animation >= self.background_x and self.end_text_animation >= self.text_x:
                self.animating_right = False

        if self.animating_left:
            if self.end_background_animation > self.background_x:
                self.background_x += 1
            if self.end_text_animation > self.text_x:
                self.text_x += 12
            if self.end_background_animation <= self.background_x and self.end_text_animation <= self.text_x:
                self.animating_left = False

    def __center_text_x(self):
        """
        Computes x value to center the menu text string based on the currently selected menu item.
        """
        centered_x = 380 - sum([width for i, width in enumerate(self.menu_widths) if i <= self.selected_menu])
        return centered_x + self.menu_widths[self.selected_menu] / 2