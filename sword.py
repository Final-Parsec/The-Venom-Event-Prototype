import pygame
import pygame.mixer
from utilities import euclid


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************sword************************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#IDs of a sword has to start at 0 and go up from there for every sword in the game.
# at sword[IS_EQUIPPED] is the equipped sword
class Sword(pygame.sprite.Sprite):
    def __init__(self, image, start_position, length, height):
        pygame.sprite.Sprite.__init__(self)

        self.swordID = 997
        self.delay = .5
        self.damage = 100
        self.image = pygame.transform.scale(image, [int(length), int(height)])
        self.rect = image.get_rect()
        self.rect.center = euclid.Vector2(start_position.x + length / 2, start_position.y + height / 2)
        self.start_position = start_position

        #stupid
        self.ammo = 30
        self.max_ammo = 40

    def use(self, time_since_fire, player):
        if time_since_fire >= self.delay:
            player.is_slicing = True
        return None

    def hit(self, enemy_player):
        enemy_player.health -= self.damage
        #check if dead
        enemy_player.is_dead = enemy_player.health <= 0

#*************************************************************************************************
#*************************************************************************************************
#used to blit the image
    def update_weapon_image(self, player):

        self.rect.top = player.rect.top
        if player.right:
            self.rect.left = player.rect.left + 20
        else:
            self.rect.left = player.rect.left + -20


#***********************************************************************************************************************
#***********************************************************************************************************************
#******************************************************copper sword (IS A sword)****************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
#test sword
class CopperSword(Sword):
    def __init__(self, screen, image, start_position, length, height):
        Sword.__init__(self, image, start_position, length, height)
        self.screen = screen
        self.image = image
        self.delay = .4
        self.damage = 55
        self.swordVelocity = .1

        self.length = length
        self.height = height
        self.start_position = start_position
