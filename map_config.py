from background_object import GrandfatherClock
from globals import now
from world_objects.client.sprite_player import SpritePlayer
from sprite_sheet import SpriteSheet, get_image, get_sprite, sprite_definitions
from utilities import euclid
from world_objects.client.gun import Pistol, Predator, BigBertha, Buster, Shotgun, SuperMachineGun, MachineGun, \
    GrapplingGun, Viper, Rifle, GrenadeLauncher
from world_objects.client.pick_up import Ammo, HealthPack, LandMine, BeachBall
from world_objects.client.platform import Stairs, Platform, SpringPlatform, DestructiblePlatform, MovingPlatform

import operator
import pygame
import globals


runningMan = [get_image('man1.png'), get_image('man2.png'), get_image('man3.png'), get_image('man4.png'),
              get_image('man5.png'), get_image('man6.png'), get_image('man7.png'), get_image('man8.png'),
              get_image('man9.png'), get_image('man10.png'), get_image('man11.png'), get_image('man12.png'),
              get_image('man12.png'), get_image('man12.png'), get_image('man11.png'), get_image('man10.png')]
bulletImage = get_image('fireball.png')
berthaImage = [get_image('Da-Missile.png')]
grappleImage = get_image('Grapple Hook.png')
translocatorImage = get_image('translocator.png')
ammoImage = get_image('Ammo.png')
healthPackImage = get_image('HP.png')


class MapConfig():
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #makes the map
    #TODO: eventually make platforms and players variables in MapConfig
    def __init__(self, map_file):

        self.world_object_list_dictionary = {'platforms': [], 'players': [], 'pickups': [], 'projectiles': [],
                                             'background': [], 'foreground': []}

        #image lists using SpriteSheets
        self.grandfather_clock = []
        self.plat_image_destructible = [get_sprite('destructible_1'), get_sprite('destructible_2')]
        self.lightning_animation = []
        self.lunar_pioneer_images = []
        self.dust_cloud = []

        self.load_sprite_images()
        level = []
        f = open(map_file)
        lines = f.readlines()

        for y in xrange(len(lines)):
            lines[y].strip()
            level.append(lines[y].split(","))

        pixel_height = len(level) - 1
        pixel_width = len(level[0]) - 1
        self.pixel_multiplier = float(level[pixel_height][pixel_width])
        map_height = pixel_height * self.pixel_multiplier
        map_width = pixel_width * self.pixel_multiplier
        globals.worldSize = (map_width, map_height)

        # world boundaries. Don't mess with this
        # makes the boundaries based off the size of the text file
        thickness = 500
        self.world_object_list_dictionary["platforms"].append(
            Platform(euclid.Vector2(-500, 0), thickness, map_height, self.get_image("p")))  # left
        self.world_object_list_dictionary["platforms"].append(
            Platform(euclid.Vector2(map_width, 0), thickness, map_height, self.get_image("p")))  # right
        self.world_object_list_dictionary["platforms"].append(
            Platform(euclid.Vector2(-500, -500), map_width+1000, thickness, self.get_image("p")))  # top
        self.world_object_list_dictionary["platforms"].append(
            Platform(euclid.Vector2(-500, map_height), map_width+1000, thickness, self.get_image("p")))  # bottom

        #this makes the rest of the world
        for yIndex in range(0, len(level)):
            row = level[yIndex]
            for xIndex in range(len(level[yIndex])):
                col = row[xIndex]

                if col == "x":  # platform
                    self.world_object_list_dictionary["platforms"].append(
                        self.find_platform(self.get_info(level, yIndex, xIndex, col)))

                if col == "s":  # player
                    self.world_object_list_dictionary["players"].append(
                        self.find_player(self.get_info(level, yIndex, xIndex, col)))

                if col == "o":  # background object
                    self.world_object_list_dictionary["background"].append(
                        self.find_object(self.get_info(level, yIndex, xIndex, col)))

                if col == "p":  # pickup
                    self.world_object_list_dictionary["pickups"].append(
                        self.find_pickup(self.get_info(level, yIndex, xIndex, col)))

    def get_info(self, level, y_index, x_index, code):
        """
        Gets the basic info of the world_object.
        """
        start_position = euclid.Vector2(int(x_index * self.pixel_multiplier), int(y_index * self.pixel_multiplier))
        end_position = euclid.Vector2(0.0, 0.0)
        last_x_position = 0.0
        last_y_position = 0.0

        for last_x_position in range(x_index + 1, len(level[y_index])):
            col = level[y_index + 1][last_x_position]
            if col == code:
                end_position.x = last_x_position * self.pixel_multiplier
                break

        for last_y_position in range(y_index + 1, len(level)):
            row = level[last_y_position][x_index + 1]
            if row == code:
                end_position.y = last_y_position * self.pixel_multiplier
                break

        width = end_position.x - start_position.x + self.pixel_multiplier
        height = end_position.y - start_position.y + self.pixel_multiplier

        if level[last_y_position][last_x_position] != code:
            data = level[last_y_position][last_x_position].split("-")
        else:
            data = level[last_y_position][x_index].split("-")

        self.clearArea(level, start_position, end_position)

        return Info(start_position, width, height, data)

    def find_platform(self, platform_info):
        """
        Finds a platform in the file.
        """

        # platform_info.data = 0-image id, 1-platform type .. for stairs: 2-number of steps, 3-direction

        image = self.get_image(platform_info.data[0])

        if platform_info.data[1] == "1":
            return Platform(platform_info.start_position, platform_info.width, platform_info.height, image)
        if platform_info.data[1] == "2":
            return MovingPlatform(platform_info.start_position, platform_info.width, platform_info.height, image)
        if platform_info.data[1] == "3":
            if platform_info.data[2] == "":
                launch_velocity = euclid.Vector2(float(platform_info.data[3]), float(platform_info.data[4]))
            else:
                launch_velocity = euclid.Vector2(float(platform_info.data[2]) * -1, float(platform_info.data[3]))
            return SpringPlatform(platform_info.start_position, platform_info.width, platform_info.height, image,
                                  launch_velocity)
        if platform_info.data[1] == "4":
            #TODO import DestructiblePlatform health from the map
            image_list = [get_image('platform.jpg')]
            return DestructiblePlatform(platform_info.start_position, platform_info.width, platform_info.height,
                                        image_list + image)
        if platform_info.data[1] == "stairs":
            return Stairs(platform_info.start_position, platform_info.width, platform_info.height, image,
                          int(platform_info.data[2]), platform_info.data[3])

        raise Exception('This method should not get this far. Unknown platform type.')

    def find_player(self, player_info):
        """
        finds the starting location of the players
        will not specify the players size. That remains in the program.
        """

        image_list = self.get_image("pioneer")  # move "pioneer" to player's options as selected race
        image_list.extend(self.dust_cloud)  # [15:22]

        #Make 'dem swords
        #testSword = CopperSword(None, swordImage, euclid.Vector2(50, 350), 380, 450)
        #make a gun *******************************
        pistol = Pistol([bulletImage])
        grapple = GrapplingGun([grappleImage])
        rifle = Rifle([bulletImage])
        machine_gun = MachineGun([bulletImage])
        super_machine_gun = SuperMachineGun([bulletImage])
        shotgun = Shotgun([bulletImage])
        viper = Viper([bulletImage])
        big_bertha = BigBertha(berthaImage)
        grenade_launcher = GrenadeLauncher(berthaImage)
        predator = Predator(berthaImage)
        buster = Buster([bulletImage], self.lightning_animation)

        weapons = {
            pistol.gun_id: pistol,
            grapple.gun_id: grapple,
            shotgun.gun_id: shotgun,
            rifle.gun_id: rifle,
            machine_gun.gun_id: machine_gun,
            super_machine_gun.gun_id: super_machine_gun,
            viper.gun_id: viper,
            big_bertha.gun_id: big_bertha,
            grenade_launcher.gun_id: grenade_launcher,
            predator.gun_id: predator,
            buster.gun_id: buster
        }

        # make player
        gravity = euclid.Vector2(0.0, 2000.0)
        return SpritePlayer(player_info.start_position, 80.0, 50.0, image_list, weapons,
                            self.world_object_list_dictionary, self.spawn_animation, euclid.Vector2(0.0, 0.0), gravity)

    def find_object(self, object_info):
        # object_info.data = 0-image id

        image = self.get_image(object_info.data[0])

        return GrandfatherClock(object_info.start_position, object_info.width, object_info.height, image)

    def find_pickup(self, object_info):
        """
        finds a pickup in the file
        """

        #object_info.data = 0-image id, 1-pickup type
        image = self.get_image(object_info.data[0])

        if object_info.data[1] == "healthpack":
            return HealthPack(object_info.start_position, object_info.width, object_info.height, image)
        if object_info.data[1] == "land_mine":
            return LandMine(object_info.start_position, object_info.width, object_info.height, image)
        if object_info.data[1] == "ammo":
            return Ammo(object_info.start_position, object_info.width, object_info.height, image)

        raise Exception('This method should not get this far. Unknown pickup type.')

    def load_sprite_images(self):
        """
        gets images from sprite sheets
        """

        # sprite sheets
        effectSheet = SpriteSheet("resources/images/Effects Spritesheet.png")
        explosionSheet = SpriteSheet("resources/images/explosion.png")
        lunar_pioneer_sheet = SpriteSheet("resources/images/lunar pioneer.png")
        background_objects_sheet = SpriteSheet("resources/images/grandfather clock.png")
        dust_sheet = SpriteSheet("resources/images/Dust Spritesheet.png")

        #lightning
        self.lightning_animation = [effectSheet.imageAt(pygame.Rect(654, 886, 34, 14)),
                                    effectSheet.imageAt(pygame.Rect(705, 885, 32, 14)),
                                    effectSheet.imageAt(pygame.Rect(750, 872, 62, 40)),
                                    effectSheet.imageAt(pygame.Rect(826, 871, 68, 37)),
                                    effectSheet.imageAt(pygame.Rect(911, 881, 72, 29))]
        #putting explosion into big bertha
        berthaImage.append(explosionSheet.imageAt(pygame.Rect(22, 115, 72, 63)))
        berthaImage.append(explosionSheet.imageAt(pygame.Rect(110, 108, 99, 81)))
        berthaImage.append(explosionSheet.imageAt(pygame.Rect(384, 116, 103, 88)))
        berthaImage.append(explosionSheet.imageAt(pygame.Rect(509, 27, 110, 80)))
        berthaImage.append(explosionSheet.imageAt(pygame.Rect(650, 29, 84, 72)))

        #lunar pioneer images
        self.lunar_pioneer_images = [lunar_pioneer_sheet.imageAt(pygame.Rect(35, 25, 20, 20)),
                                     lunar_pioneer_sheet.imageAt(pygame.Rect(101, 26, 20, 20))]
        #grandfather clock images
        self.grandfather_clock = [background_objects_sheet.imageAt(pygame.Rect(7, 12, 18, 71)),
                                  background_objects_sheet.imageAt(pygame.Rect(39, 12, 18, 71)),
                                  background_objects_sheet.imageAt(pygame.Rect(71, 12, 18, 71)),
                                  background_objects_sheet.imageAt(pygame.Rect(39, 12, 18, 71))]
        #spawn images
        self.spawn_animation = [effectSheet.imageAt(pygame.Rect(291, 695, 2, 217)),
                                effectSheet.imageAt(pygame.Rect(281, 695, 2, 217)),
                                effectSheet.imageAt(pygame.Rect(270, 695, 2, 217)),
                                effectSheet.imageAt(pygame.Rect(270, 695, 2, 217)),
                                effectSheet.imageAt(pygame.Rect(260, 695, 4, 217)),
                                effectSheet.imageAt(pygame.Rect(242, 695, 12, 216)),
                                effectSheet.imageAt(pygame.Rect(215, 695, 22, 217)),
                                effectSheet.imageAt(pygame.Rect(180, 695, 30, 217)),
                                effectSheet.imageAt(pygame.Rect(148, 695, 22, 217)),
                                effectSheet.imageAt(pygame.Rect(108, 695, 30, 217)),
                                effectSheet.imageAt(pygame.Rect(53, 695, 48, 217)),
                                effectSheet.imageAt(pygame.Rect(4, 695, 46, 217))]

        self.spawn_animation = normalize_rects(self.spawn_animation)
        #dust cloud
        #dust_sheet.imageAt(pygame.Rect(544, 250, 82, 17))  # this image is just broken for no reason.
        self.dust_cloud = [dust_sheet.imageAt(pygame.Rect(156, 28, 150, 41)),
                           dust_sheet.imageAt(pygame.Rect(351, 20, 189, 58)),
                           dust_sheet.imageAt(pygame.Rect(2, 130, 196, 61)),
                           dust_sheet.imageAt(pygame.Rect(257, 141, 194, 57)),
                           dust_sheet.imageAt(pygame.Rect(3, 230, 198, 57)),
                           dust_sheet.imageAt(pygame.Rect(257, 253, 197, 57))]


    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #clears the Xs that make up the platform in the file
    def clearArea(self, level, start_position, endPos):
        for y in range(int(start_position.y / self.pixel_multiplier), int(endPos.y / self.pixel_multiplier) + 1):
            for x in range(int(start_position.x / self.pixel_multiplier), int(endPos.x / self.pixel_multiplier) + 1):
                level[y][x] = ""

    def get_image(self, image_code):
        """
        get image based on the image code
        """

        if image_code in sprite_definitions:
            return [get_sprite(image_code)]
        elif image_code == "p":
            return [get_image('platform.jpg')]
        elif image_code == "s":
            return [get_image('springplatform.png')]
        elif image_code == "destructible":
            return self.plat_image_destructible
        elif image_code == "pioneer":
            return runningMan
        elif image_code == "grandfather_clock":
            return self.grandfather_clock
        elif image_code == "dust_cloud":
            return self.dust_cloud
        elif image_code == "health":
            return [healthPackImage]
        elif image_code == "ammo":
            return [ammoImage]
        else:
            print image_code

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #clears the Xs that make up the platform in the file
    def all_objects(self):
        return self.world_object_list_dictionary["background"] + self.world_object_list_dictionary["platforms"] + \
               self.world_object_list_dictionary["projectiles"] + self.world_object_list_dictionary["pickups"] + \
               self.world_object_list_dictionary["players"] + self.world_object_list_dictionary["foreground"]

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #clears the Xs that make up the platform in the file
    def get_background_objects(self):
        return self.world_object_list_dictionary["background"] + self.world_object_list_dictionary["platforms"] + \
               self.world_object_list_dictionary["projectiles"] + self.world_object_list_dictionary["pickups"]

    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #clears the Xs that make up the platform in the file
    def get_foreground_objects(self):
        return self.world_object_list_dictionary["foreground"]


#*************************************************************************************************
#find which rect is biggest
#edit all rects to be that big
def normalize_rects(image_list):
    #first find the biggest rect
    original_list = list(image_list)
    return_image_list = []
    area_dict = {}
    for img in original_list:
        temp_rect = img.get_rect()
        area_dict[img] = (temp_rect.width * temp_rect.height)
    sorted_area_list = sorted(area_dict.iteritems(), key=operator.itemgetter(1))
    biggest_img = sorted_area_list[-1][0]  # need the first element of the last tuple. sort() is ascending.
    # now get how far off the other images are from the biggest one and store it in a list
    big_width = biggest_img.get_rect().width
    big_height = biggest_img.get_rect().height
    for x in original_list:
        surface = pygame.Surface((big_width, big_height))
        surface.set_colorkey([0, 0, 0])  # set black to transparent
        surface.blit(x, (surface.get_width() / 2.0 - x.get_width() / 2.0, 0))
        return_image_list.append(surface)
    return return_image_list


class Info():
    #*******************************************************************************************************************
    #*******************************************************************************************************************
    #makes up the basic info of a world_object
    def __init__(self, start_position, width, height, data):
        self.start_position = start_position
        self.width = width
        self.height = height
        self.data = data