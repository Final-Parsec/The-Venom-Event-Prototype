from os import path
from pygame import error, image, Rect, Surface, RLEACCEL


__images = {}
__images_path = 'resources/images/'


def get_image(file_name, force_reload=0):
    """
    Call this function instead of pygame.image.load()

    It will load the image from the disk the first time, then just return a reference to the copy each subsequent time.
    This function does no colorkey setting or pixel format conversion; you'll have to do that manually, if you wish.
    """

    if force_reload == 1 or file_name not in __images.keys():
        try:
            surface = image.load(path.join(__images_path, file_name))
        except error:
            raise Exception('File ' + file_name + ' not found.')
        __images[file_name] = surface
        return surface
    else:
        return __images[file_name]


sprites = {}
sprite_definitions = {
    'a': ('spacestation.png', Rect(62, 59, 65, 25), None),  # air box
    'air_box2': ('spacestation.png', Rect(287, 339, 130, 54), None),
    'b': ('spacestation.png', Rect(464, 331, 62, 64), None),  # box
    'box2': ('spacestation.png', Rect(63, 361, 64, 64), None),
    'box3': ('spacestation.png', Rect(176, 360, 64, 64), None),
    'concrete_column': ('spacestation.png', Rect(311, 65, 32, 95), None),
    'd': ('spacestation.png', Rect(280, 582, 374, 134), None),  # doodad
    'destructible_1': ('Map Sprites1.png', Rect(35, 25, 20, 20), None),
    'destructible_2': ('Map Sprites1.png', Rect(101, 26, 20, 20), None),
    'doodad2': ('spacestation.png', Rect(45, 604, 173, 67), None),
    'g': ('spacestation.png', Rect(563, 340, 66, 56), None),  # grate
    'green_computer': ('spacestation.png', Rect(58, 159, 80, 31), None),
    'half_box': ('spacestation.png', Rect(48, 504, 31, 31), None),
    'i_beam': ('spacestation.png', Rect(43, 266, 107, 31), None),
    'l': ('spacestation.png', Rect(648, 339, 66, 56), None),  # grate and lamp
    'single_gun_rack': ('spacestation.png', Rect(317, 228, 22, 62), None),
    'stairs_left': ('spacestation.png', Rect(288, 457, 31, 16), None),
    'thin_column': ('spacestation.png', Rect(386, 68, 6, 87), None)
}


def get_sprite(sprite_name):
    """
    Returns sprite picking a cached image if it exists. If not, cuts a new sprites based on info in sprite_definitions.
    """
    if sprite_name in sprites:
        return sprites[sprite_name]
    else:
        sprite_definition = sprite_definitions[sprite_name]
        file_name = sprite_definition[0]
        rect = sprite_definition[1]
        color_key = sprite_definition[2]
        sprite = Surface(rect.size).convert()
        sprite.blit(get_image(file_name), (0, 0), rect)
        if color_key is not None:
            if color_key is -1:
                color_key = sprite.get_at((0, 0))
            sprite.set_colorkey(color_key, RLEACCEL)
        sprites[sprite_name] = sprite
        return sprite


class SpriteSheet(object):
    """
    This class handles sprite sheets.
    """

    def __init__(self, filename):
        try:
            self.sheet = image.load(filename).convert()
        except error:
            print 'Unable to load sprite sheet image:', filename
            raise error

    # Load a specific image from a specific rectangle
    def imageAt(self, rectangle, colorkey=-1):
        """
        Note: When calling images_at the rect is the format: (x, y, x + offset, y + offset)
        """
        "Loads image from x,y,x+offset,y+offset"
        rect = Rect(rectangle)
        image = Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image