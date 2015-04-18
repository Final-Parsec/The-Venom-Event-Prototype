import pygame
import pygame.mixer
from pygame.locals import*
from globals import now
import globals
from world_objects import *


#Player Inputs
LEFT = K_a
RIGHT = K_d
UP = K_SPACE
DOWN = K_s
GRAPPLE = K_e
LOAD_GUN = K_r
DASH_RIGHT = 1001
DASH_LEFT = 1002
SHOOT = 1003
MELEE = 1004

#menu inputs
NEXT_WEAPON = K_q
PREVIOUS_WEAPON = K_g
ESC = K_ESCAPE
W = K_w
S = K_s
UP_ARROW = K_UP
DOWN_ARROW = K_DOWN
RIGHT_ARROW = K_RIGHT
LEFT_ARROW = K_LEFT
ENTER = K_RETURN
MOUSE_SCROLL_UP = 8997
MOUSE_SCROLL_DOWN = 8999
MOUSE_X = 9000
MOUSE_Y = 9001
RIGHT_CLICK = 2
LEFT_CLICK = 1
LEFT_CLICK_UP = 10
RETURN = 9005
INPUT_STRING = 9006
#still menu inputs but used by player
LEFT_DOWN = K_a
RIGHT_DOWN = K_d



class Keystore:

    def __init__(self):

        self.user_input = {RIGHT: False}
        self.user_input[GRAPPLE] = False
        self.user_input[LOAD_GUN] = False
        self.user_input[DOWN] = False
        self.user_input[UP] = False
        self.user_input[LEFT] = False
        self.user_input[SHOOT] = False
        self.user_input[MELEE] = False
        self.user_input[ESC] = False

        self.menu_input = {RIGHT_CLICK: False}
        self.menu_input[NEXT_WEAPON] = False        # put this here so we get true on presses not holds
        self.menu_input[PREVIOUS_WEAPON] = False    # put this here so we get true on presses not holds
        self.menu_input[LEFT_CLICK] = False
        self.menu_input[LEFT_CLICK_UP] = False
        self.menu_input[ESC] = False
        self.menu_input[W] = False
        self.menu_input[S] = False
        self.menu_input[UP_ARROW] = False
        self.menu_input[DOWN_ARROW] = False
        self.menu_input[LEFT_ARROW] = False
        self.menu_input[RIGHT_ARROW] = False
        self.menu_input[ENTER] = False
        self.menu_input[MOUSE_SCROLL_UP] = False
        self.menu_input[MOUSE_SCROLL_DOWN] = False
        self.menu_input[RETURN] = False
        self.menu_input[MOUSE_X] = 0.0
        self.menu_input[MOUSE_Y] = 0.0
        self.menu_input[INPUT_STRING] = ""

        self.exit = False  # if the player pressed esc or clicked the X

        #local variables
        self.delta_time = 0.0
        self.shift_is_pressed = False
        self.double_tap_max = .1  # time in seconds for a double tap to occure
                                  # max is self.delta_time
        self.right_time = 0.0
        self.left_time = 0.0
        self.events = None

    def set_pressed(self, events):
        self.clearmenu_input()

        self.events = events
        for event in events:

            if event.type == pygame.QUIT:
                return False
            #elif event.type == KEYDOWN and event.key == K_ESCAPE:
                #return False
            elif event.type == VIDEORESIZE:  # when the screen is being moved
                if hasattr(globals, 'camera'):
                    globals.screen = pygame.display.set_mode(event.dict['size'], RESIZABLE | DOUBLEBUF)
                    globals.camera.rect = globals.screen.get_rect()
                    pygame.display.flip()

            elif event.type == MOUSEMOTION:
                self.mposx, self.mposy = event.pos
                self.menu_input[MOUSE_X] = self.mposx
                self.menu_input[MOUSE_Y] = self.mposy

# mouse clicks
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == LEFT_CLICK:
                    self.menu_input[LEFT_CLICK] = True
                    self.user_input[SHOOT] = True
                if event.button == RIGHT_CLICK:
                    self.menu_input[RIGHT_CLICK] = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == LEFT_CLICK:
                    self.menu_input[LEFT_CLICK_UP] = True
                    self.user_input[SHOOT] = False
                if event.button == 4:
                    self.menu_input[MOUSE_SCROLL_UP] = True
                if event.button == 5:
                    self.menu_input[MOUSE_SCROLL_DOWN] = True

#text typing
            elif event.type == pygame.KEYDOWN:
                if event.key in self.menu_input:
                    self.menu_input[event.key] = True

                self.menu_input[INPUT_STRING] = self.menu_input[INPUT_STRING] or ''  # makes sure self.user_input[INPUT_STRING] is a string
                if event.key == 303 or event.key == 304:
                    self.shift_is_pressed = True
                if 32 <= event.key <= 126 and not self.shift_is_pressed:
                    self.menu_input[INPUT_STRING] += chr(event.key)
                elif self.shift_is_pressed:
                    if 97 <= event.key <= 122:  # capital letters
                        self.menu_input[INPUT_STRING] += chr(event.key - 32)
                    if event.key == 32:  # space
                        self.menu_input[INPUT_STRING] += chr(event.key)
                    if event.key >= 48 and event.key <= 57:  # shift + numbers
                        self.menu_input[INPUT_STRING] += chr(event.key - 16)
                    if event.key == 47:  # question mark
                        self.menu_input[INPUT_STRING] += chr(63)
                elif event.key == pygame.K_BACKSPACE and self.menu_input[INPUT_STRING] is not None:
                    self.menu_input[INPUT_STRING] = self.menu_input[INPUT_STRING][0:-1]
                elif event.key == pygame.K_RETURN:  # enter
                    self.menu_input[RETURN] = True
            elif event.type == pygame.KEYUP and event.key:
                #for event in events:
                if event.key == 303 or event.key == 304:  # try not to press both shifts at once.
                    self.shift_is_pressed = False

        pressed_list = pygame.key.get_pressed()
        for key in range(len(pressed_list)):
            if key in self.user_input:
                self.user_input[key] = pressed_list[key]

        pygame.event.clear()
        pygame.event.pump()

        self.updateuser_input()

        return True

    def getVelocityToMouse(self, window_position):

        if self.mposx - window_position.x != 0:
            theta = math.atan2((self.mposy - window_position.y), (self.mposx - window_position.x))
            xcomp = math.cos(theta)
            ycomp = math.sin(theta)
        else:
            theta = ((self.mposy - window_position.y) / math.fabs((self.mposy - window_position.y)))
            xcomp = math.cos(theta)
            ycomp = math.sin(theta)
        return euclid.Vector2(xcomp, ycomp)

    def getKeyValue(self, key):
        if key in self.keyboard.keys():
            return self.keyboard[key]
        else:
            return -1

    def getMouseValue(self, key):
        if key in self.mouse.keys():
            return self.mouse[key]
        else:
            return -1

    def updateuser_input(self):
        cur_time = now()
        if self.user_input[LEFT]:
            time = cur_time - self.left_time
            if self.delta_time * 2.0 <= time <= self.double_tap_max and self.right_time < self.left_time:

                self.user_input[DASH_LEFT] = True

            else:
                self.user_input[DASH_LEFT] = False
            self.left_time = cur_time

        if self.user_input[RIGHT]:
            time = cur_time - self.right_time
            if self.delta_time * 2.0 <= time <= self.double_tap_max and self.left_time < self.right_time:
                self.user_input[DASH_RIGHT] = True
            else:
                self.user_input[DASH_RIGHT] = False
            self.right_time = cur_time

    def clearmenu_input(self):
        for key in self.menu_input.keys():
            if not (key == MOUSE_X or key == MOUSE_Y or key == INPUT_STRING):
                self.menu_input[key] = False