from utilities import euclid
from world_objects.server.plaftorms import ServerMovingPlatform
from world_objects.client.sprite_player import SpritePlayer
from world_objects.server.guns import IS_EQUIPPED


class ServerPickUp(ServerMovingPlatform):
    """inheriting from ServerMovingPlatform makes
        the pick ups float and bob in the air"""
    def __init__(self, start_position, width, height, velocity=euclid.Vector2(0.0, 10.0),
                 max_displacement=euclid.Vector2(0, 5)):
        ServerMovingPlatform.__init__(self, start_position, width, height, velocity, max_displacement)
        #overrides
        self.is_solid = False


class ServerAmmo(ServerPickUp):
    """Fills your remaining_ammo to max_ammo, fills ammo to magazine_size"""
    def __init__(self, start_position, width, height):
        ServerPickUp.__init__(self, start_position, width, height)

    def on_collision(self, player, direction):
        """refill ammo if player"""
        if type(player) is SpritePlayer:
            current_gun = player.weapons[IS_EQUIPPED]
            current_gun.remaining_ammo = current_gun.max_ammo
            current_gun.ammo = current_gun.magazine_size
            player.update_ammo_hud()
            self.is_alive = False
            #TODO: make these two lines a method in spritePlayer


class ServerHealthPack(ServerPickUp):
    """if restores is infinity it restores player's
        health to full... obviously
        NOTE: defaults to infinity"""
    def __init__(self, start_position, width, height, restores=float("inf")):
        ServerPickUp.__init__(self, start_position, width, height)
        self.restores = restores

    def on_collision(self, player, direction):
        """heals for self.restores"""
        if type(player) is SpritePlayer:
            player.health += self.restores
            if player.health > player.max_health:
                player.health = player.max_health
            player.update_ammo_hud()
            self.is_alive = False
            #TODO: make these two lines a method in spritePlayer


class ServerLandMine(ServerPickUp):
    def __init__(self, start_position, width, height, damage=50):
        ServerPickUp.__init__(self, start_position, width, height)
        self.damage = damage

    def on_collision(self, player, direction):
        """damages for self.damage"""
        if type(player) is SpritePlayer:
            player.health -= self.damage
            player.update_ammo_hud()
            self.is_alive = False
            #TODO: make a damage method in the player class