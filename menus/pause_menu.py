import pygame

from colors import BLACK, OFF_GREY_BLUE_TINT, WHITE
from utilities.euclid import Vector2
from key_store import *
from world_objects import WorldObject
import globals


class PauseMenu(WorldObject):
    """
    While the game is paused, input is diverted to the pause menu.
    Stuff still goes on in the game except there is an overlay with pause menu text on top of it.

    Menus now have 2 key structures: a list of dictionaries and a list of lists of strings.
    The dictionaries hold methods for each option listed in the string arrays.

    For example:
        The value menuText[0][0] holds "resume".
        The value for the key in options[0][0](self) is the function resume(self).

    The first number denotes the sub menu.
    The second number denotes what position in the sub menu you want.
    """

    def __init__(self, font, screen_size_x, screen_size_y, screen, start_position=Vector2(0.0, 0.0), velocity=0):
        self.pause_surface = pygame.image.load('resources/images/jimi.png')
        self.pause_surface = pygame.transform.scale(self.pause_surface, (screen_size_x, screen_size_y))
        self.image = self.pause_surface
        image_list = [self.pause_surface]
        WorldObject.__init__(self, start_position, screen_size_x, screen_size_y, velocity, image_list)

        self.screen = screen
        self.selected_option = 0
        self.font = font
        self.is_paused = False

        #Instantiate menus
        self.main_pause_menu = SubMenu(0, False)
        self.options_menu = SubMenu(1, False)
        self.resolution_options = SubMenu(2, True)

        # Populate menus and attach an action.
        # If you make a new menu option, be sure to add its function to the PauseMenu class.
        self.main_pause_menu.menu_item_list.extend((MenuItem(self.resume, "Resume"),
                                                    MenuItem(self.switch_to_options_menu, "Options"),
                                                    MenuItem(self.quit, "Quit")))
        self.options_menu.menu_item_list.extend((MenuItem(self.switch_to_resolution_menu, "Screen Resolution"),
                                                 MenuItem(self.back, "Back")))
        self.resolution_options.menu_item_list.extend(self.generate_resolution_options())

        # This gets set to main_pause_menu when the game gets paused.
        self.current_sub_menu = self.main_pause_menu

        # Calculate start position for first menu item.
        self.x_displacement = 3.8
        self.y_displacement = 12.8
        self.text_position_x = (screen_size_x / 2) - (screen_size_x / self.x_displacement)
        self.text_position_y = (screen_size_y / 2) - (screen_size_y / self.y_displacement)
        self.pause_surface = pygame.Surface((screen_size_x, screen_size_y))

        self.menu_negative_space = screen_size_y / 24  # space between options

        self.update()

        self.return_to_main_menu = False

    def back(self):
        """
        Move up one level in the menu.
        If the method can't identify current sub menu, return to main pause menu.
        """

        if self.current_sub_menu == self.options_menu:
            self.current_sub_menu = self.main_pause_menu
        elif self.current_sub_menu == self.resolution_options:
            self.current_sub_menu = self.options_menu
        else:
            self.current_sub_menu = self.main_pause_menu

        self.selected_option = 0

    def build_menu(self):
        """
        Blit text surface slices onto a bigger surface to build the menu.
        """

        #first account for whether the screen has changed size
        self.align_text()
        for current_index, menu_item in enumerate(self.current_sub_menu.menu_item_list):
            # Selected item is white. Others are off grey with blue tint.
            text_color = WHITE if current_index == self.selected_option else OFF_GREY_BLUE_TINT
            temporary_slice = self.font.render(menu_item.text, True, text_color)

            # Turn temporary_slice surface into WorldObject and add it to menu_item_list[current_index].
            if self.current_sub_menu.does_scroll:
                y_offset = (temporary_slice.get_height() + self.menu_negative_space) * \
                           (current_index - self.selected_option)
            else:
                y_offset = (temporary_slice.get_height() + self.menu_negative_space) * current_index
            start_position = Vector2(self.text_position_x, self.text_position_y + y_offset)
            new_world_object = WorldObject(start_position,
                                           temporary_slice.get_width(),
                                           temporary_slice.get_height(),
                                           0,
                                           [temporary_slice])
            self.current_sub_menu.menu_item_list[current_index].text_surface_slice = new_world_object

            # Blit each stripe onto pause_surface.
            self.pause_surface.blit(self.current_sub_menu.menu_item_list[current_index].text_surface_slice.image,
                                    (self.text_position_x, self.text_position_y + y_offset))

    def clear_pause_surface(self):
        """
        Clears the pause surface so it doesn't leave old blits on there.
        """
        self.pause_surface.fill(BLACK)

    def generate_resolution_options(self):
        resolution_options = []
        for mode in pygame.display.list_modes():
            resolution_string = str(mode[0]) + ", " + str(mode[1])
            resolution_options.append(MenuItem(self.resolution_selected, resolution_string))

        resolution_options.append(MenuItem(self.back, "Back"))
        return resolution_options

    def mouse_menu_collision_check(self, user_input):
        """
        Returns the option that the mouse is hovering over. If none, it returns the current selected option.

        This iterates through each open menu's menuTextSlice, and works even with menu text in a weird place on screen.
        """
        for x in range(0, len(self.current_sub_menu.menu_item_list)):
            if not self.current_sub_menu.menu_item_list[x].text_surface_slice:
                # Menu item doesn't have a text surface slice, so don't check for hover.
                continue

            menu_item_height = self.current_sub_menu.menu_item_list[x].text_surface_slice.image.get_height()
            menu_item_width = self.current_sub_menu.menu_item_list[x].text_surface_slice.image.get_width()
            menu_item_x = self.current_sub_menu.menu_item_list[x].text_surface_slice.start_position.x
            menu_item_y = self.current_sub_menu.menu_item_list[x].text_surface_slice.start_position.y

            # If mouse position is within the menu item rectangle.
            if menu_item_x + menu_item_width > user_input[MOUSE_X] > menu_item_x and \
               menu_item_y + menu_item_height > user_input[MOUSE_Y] > menu_item_y:
                return x

        # User is not hovering over any item. Return current selected option.
        return self.selected_option

    def pause(self):
        self.is_paused = True
        self.current_sub_menu = self.main_pause_menu

    def quit(self):
        self.return_to_main_menu = True
        globals.current_screen = 'main menu'  # todo: remove this once all scenes are complete

    def react(self, user_input):
        """
        Reacts to input.

        user_input is a dictionary of key presses.  constants come from key_store.py
        """

        # Escape
        if user_input[ESC]:
            self.resume()
            self.selected_option = 0
        # W / Up
        elif user_input[W] or user_input[UP_ARROW]:
            self.select_previous_option()
        # S / Down
        elif user_input[S] or user_input[DOWN_ARROW]:
            self.select_next_option()
        # Enter / Left Mouse Button
        elif user_input[ENTER] or user_input[LEFT_CLICK]:
            self.select_current_option()

        # Possible mouse movement. Check if user is hovering over a menu item.
        self.selected_option = self.mouse_menu_collision_check(user_input)

    def resolution_selected(self):
        globals.screen.fill(BLACK)
        globals.screen = pygame.display.set_mode(pygame.display.list_modes()[self.selected_option],
                                                 RESIZABLE | DOUBLEBUF)
        globals.camera.rect = globals.screen.get_rect()
        pygame.display.flip()
        self.main_pause_menu.menu_item_list[0].action()  # resumeGame
        self.selected_option = 0

    def resume(self):
        self.is_paused = False

    def select_current_option(self):
        self.current_sub_menu.menu_item_list[self.selected_option].action()

    def select_next_option(self):
        if self.selected_option != len(self.current_sub_menu.menu_item_list) - 1:
            self.selected_option += 1
        else:
            self.selected_option = 0

    def select_previous_option(self):
        if self.selected_option != 0:
            self.selected_option -= 1
        else:
            self.selected_option = len(self.current_sub_menu.menu_item_list) - 1

    def switch_to_options_menu(self):
        self.current_sub_menu = self.options_menu
        self.selected_option = 0

    def switch_to_resolution_menu(self):
        self.current_sub_menu = self.resolution_options
        self.selected_option = 0

    def update(self):
        """ Updates the pause_menu image. """

        self.clear_pause_surface()

        # Blit pause menu background picture.
        self.pause_surface.blit(self.pause_surface, (0, self.image.get_height() / 5.4))
        self.pause_surface.set_alpha(200)  # 0-255; 0 is transparent, 255 is opaque.
        self.build_menu()
        self.pause_surface = pygame.transform.scale(self.pause_surface,
                                                    (globals.screen.get_width(),
                                                     globals.screen.get_height()))

        self.image = self.pause_surface

    def align_text(self):
        """align menu text to middle of screen to account for changing resolutions"""

        self.text_position_x = (globals.screen.get_width() / 2) - (globals.screen.get_width() / self.x_displacement)
        self.text_position_y = (globals.screen.get_height() / 2) - (globals.screen.get_height() / self.y_displacement)


class SubMenu(object):
    """
    A SubMenu has a unique id and a list of MenuItems.
    """

    def __init__(self, unique_id, does_scroll=True):
        self.id = unique_id
        self.menu_item_list = []
        self.does_scroll = does_scroll  # keeps the selected option in the middle of the screen for large menus.


class MenuItem(object):
    """
    A MenuItem is owned by a SubMenu and has a string representing its text to be displayed.
    """

    def __init__(self, action, text):
        """
        action is a method defined in PauseMenu which is executed when the menu item is selected.
        """
        self.text = text
        self.action = action
        self.text_surface_slice = None  # This is a WorldObject.