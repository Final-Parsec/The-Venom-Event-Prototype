import pygame
from utilities import euclid
from pygame.locals import*
from sprite_sheet import SpriteSheet
from menu_elements.label import Label


#***************************************************************************************
#***************************************************************************************
#stores all the globals used by the game
def init():
    global camera
    global current_screen
    global online_game
    global screen

    #menu images
    global button_img_list
    global join_game_img_list
    global forward_button_img_list
    global back_button_img_list
    global text_field_img_list
    global ready_button_img_list
    global small_forward_button_img_list
    global small_back_button_img_list
    global close_button_img_list

    #cycle button contents
    global map_names

    #sounds
    global button_1_sound

    current_screen = "main menu"
    screen_size = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode(screen_size, DOUBLEBUF)

    #import button images
    button_sheet = SpriteSheet("resources/images/ButtonSpriteSheet.png")
    button_img_list = [button_sheet.imageAt(pygame.Rect(475, 306, 80, 19), None)]
    join_game_img_list = [button_sheet.imageAt(pygame.Rect(497, 281, 33, 10))]
    forward_button_img_list = [button_sheet.imageAt(pygame.Rect(0, 76, 50, 278), None)]
    back_button_img_list = [button_sheet.imageAt(pygame.Rect(54, 76, 50, 278), None)]
    small_forward_button_img_list = [button_sheet.imageAt(pygame.Rect(494, 226, 18, 15)),
                                     button_sheet.imageAt(pygame.Rect(494, 243, 18, 15))]
    small_back_button_img_list = [button_sheet.imageAt(pygame.Rect(516, 242, 18, 15)),
                                  button_sheet.imageAt(pygame.Rect(516, 225, 18, 15))]
    text_field_img_list = [button_sheet.imageAt(pygame.Rect(479, 278, 75, 12), None),
                           button_sheet.imageAt(pygame.Rect(479, 293, 75, 12), None)]
    ready_button_img_list = [button_sheet.imageAt(pygame.Rect(0, 0, 157, 38), None),
                             button_sheet.imageAt(pygame.Rect(0, 38, 157, 38), None)]
    close_button_img_list = [button_sheet.imageAt(pygame.Rect(108, 77, 44, 44), None)]

    #populate cycle_button elements
    map_names = [Label(euclid.Vector2(0, 0), "Matt World"),
                 Label(euclid.Vector2(0, 0), "Fun Zone"),
                 Label(euclid.Vector2(0, 0), "Snake Juice")]

    #sounds
    button_1_sound = pygame.mixer.Sound("resources/sounds/menu_button.wav")


def blit_alpha(source, location, target, opacity=255, clip=None):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)

        if clip is not None:
            source.set_clip(clip)

        target.blit(temp, location)


#*************************************************************************************************
#*************************************************************************************************
#scales all the images for the object
def scale_image_list(width, height, image_list, range_top=None, range_bottom=None):
    if range_top is None or range_bottom is None:
        range_top = len(image_list)
        range_bottom = 0
    for a in range(range_bottom, range_top):
        #print self.image_list[a], a
        image_list[a] = pygame.transform.scale(image_list[a], [int(width), int(height)])


def now():
    return pygame.time.get_ticks() / 1000.0