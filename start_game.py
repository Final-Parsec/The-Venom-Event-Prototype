from menus.main_menu import MainMenu
from key_store import Keystore
from utilities.threading_helper import RepeatTask

import gc
import globals
import pygame


if __name__ == '__main__':
    pygame.init()

    # Initial set up.
    fps_limit = 60
    clock = pygame.time.Clock()
    globals.init()  # initializes variables
    pygame.display.set_caption('Space Snakes')
    key_store = Keystore()
    scene = MainMenu()

    # Main game loop.
    while True:
        key_store.delta_time = clock.tick(fps_limit) / 1000.0

        if pygame.event.get(pygame.QUIT):
            break

        scene = scene.handle(key_store) or scene
        scene = scene.update() or scene
        scene.draw()
        pygame.display.flip()

    # Kill any RepeatTask threads and exit the game.
    for obj in gc.get_objects():
        if isinstance(obj, RepeatTask):
            obj.stop()
    pygame.quit()
    exit()