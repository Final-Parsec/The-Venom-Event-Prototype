import pygame
import pygame.mixer

from colors import BLACK
from world_objects.client.gun import IS_EQUIPPED
from utilities import euclid


class Camera(object):
    """
    Class for centering screen on the player.
    """
    def __init__(self, player, level_width, level_height, screen):
        self.player = player
        self.screen = screen
        self.rect = self.screen.get_rect()
        self.rect.center = self.player.rect.center
        padding = 250
        self.world_rect = pygame.Rect(-padding, -padding, level_width + padding * 2, level_height + padding * 2)

    def update(self):
        if self.player.rect.centerx > self.rect.centerx + 25:
            self.rect.centerx = self.player.rect.centerx - 25
        if self.player.rect.centerx < self.rect.centerx - 25:
            self.rect.centerx = self.player.rect.centerx + 25
        if self.player.rect.centery > self.rect.centery + 25:
            self.rect.centery = self.player.rect.centery - 25
        if self.player.rect.centery < self.rect.centery - 25:
            self.rect.centery = self.player.rect.centery + 25
        rect = self.RelRect(self.player.rect)
        self.player.window_position = euclid.Vector2(rect.left, rect.top)
        #self.rect.center = self.player.rect.center
        self.rect.clamp_ip(self.world_rect)

    def draw_sprites(self, background, foreground, players):
        #screen.blit(gameBG, (-self.rect.left, -self.rect.top))
        #screen.blit(gameBG, (0, 0), self.rect)
        self.screen.fill(BLACK)
        for s in background:
            if self.rect.colliderect(s.rect):
                self.screen.blit(s.image, self.RelRect(s.rect))

        for player in players:
            if self.rect.colliderect(player.rect):
                player_rel_rect = self.RelRect(player.rect)
                self.screen.blit(player.image, self.RelRect(player.rect))
                gun_rel_rect = self.RelRect(self.player.weapons[IS_EQUIPPED].rect)
                self.player.weapons[IS_EQUIPPED].window_position_center = euclid.Vector2(gun_rel_rect.center[0], gun_rel_rect.center[1])
                self.player.window_position_center = euclid.Vector2(player_rel_rect.center[0], player_rel_rect.center[1])
                self.screen.blit(self.player.weapons[IS_EQUIPPED].image, gun_rel_rect)

        for s in foreground:
            if self.rect.colliderect(s.rect):
                self.screen.blit(s.image, self.RelRect(s.rect))

    def RelRect(self, actor_rect):
        return pygame.Rect(actor_rect.left - self.rect.left, actor_rect.top - self.rect.top, actor_rect.width,
                           actor_rect.height)

