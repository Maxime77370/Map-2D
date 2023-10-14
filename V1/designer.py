from ctypes import resize
from pathlib import PosixPath
import pygame
import importlib.util
import sys
from pygame.locals import *
import numpy as np
from math import *

file = 'minecraft'

class Game:
    W = 640
    H = 240
    SIZE = W, H

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(Game.SIZE)
        pygame.display.set_caption("Pygame Tiled Demo")
        self.running = True

        self.tileset = Tileset(file)
        self.tilemap = Tilemap(self.tileset, size=(80, 120), resize = 0.5)
        del self.tileset
        self.tilemap.set_reset()

        self.menuset = Tileset(file) 
        self.menumap = Tilemap(self.menuset, resize = 1)
        del self.menuset
        self.menumap.set_enumerate()

        self.load_image(self.tilemap)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self.tilemap.set_reset()
                        self.load_image(self.tilemap)
                    elif event.key == K_a:
                        self.tilemap.set_random()
                        self.load_image(self.tilemap)
                    elif event.key == K_m:
                        self.load_image(self.menumap)
                    elif event.key == K_v:
                        self.load_image(self.tilemap)
                    elif event.key == K_g:
                        self.tilemap.grid_activate = False if self.tilemap.grid_activate else True
                        self.menumap.grid_activate = False if self.menumap.grid_activate else True
                        self.tilemap.render()
                        self.menumap.render()
                        self.load_image(self.tilemap)
                    elif event.key == K_p:
                        self.tilemap.back()
                        self.load_image(self.tilemap)
                    elif event.key == K_s:
                        self.tilemap.new_save()
                    elif event.key == K_l:
                        self.tilemap.get_save()
                        self.load_image(self.tilemap)
                    elif event.key == K_c:
                        self.tilemap.set_generator()
                        self.load_image(self.tilemap)
                    elif event.key == K_2:
                        self.tilemap.set_scale(1.2)
                        self.menumap.set_scale(1.2)
                        self.load_image(self.tilemap)
                    elif event.key == K_1:
                        self.tilemap.set_scale(0.8)
                        self.menumap.set_scale(0.8)
                        self.load_image(self.tilemap)
                    elif event.key == K_UP:
                        self.tilemap.set_overlay(1)
                    elif event.key == K_DOWN:
                        self.tilemap.set_overlay(-1)


                if event.type == pygame.MOUSEBUTTONDOWN:
                    x0, y0 = self.tilemap.get_pos()
                    event_happened = False
                    while not event_happened:
                        event = pygame.event.wait()
                        if event.type == pygame.MOUSEBUTTONUP:
                            x1, y1 = self.tilemap.get_pos()
                            tile_pos = []
                            for i in range(x1-x0 if x1 < x0 else 0, x1-x0+1 if x1 > x0 else 1):
                                for j in range(y1-y0 if y1 < y0 else 0, y1-y0+1 if y1 > y0 else 1):
                                    tile_pos.append((self.tilemap.overlay,x0+i, y0+j))

                            self.load_image(self.menumap)

                            while not event_happened:
                                event = pygame.event.wait()
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    x, y = self.menumap.get_pos()
                                    tile = x*self.menumap.sprite_size[1]+y
                                    print(tile)
                                    self.tilemap.set_modify(tile_pos, tile)
                                    self.load_image(self.tilemap)
                                elif event.type == pygame.MOUSEBUTTONUP:
                                    event_happened = True
                                elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                                    event_happened = True
                                    self.load_image(self.tilemap)

        pygame.quit()

    def load_image(self, tilemap):
        self.screen.fill((0, 0, 0))
        self.rect = tilemap.image.get_rect()
        print(self.rect)
        self.screen = pygame.display.set_mode(self.rect.size)
        pygame.display.set_caption(f'size:{self.rect.size}')
        self.screen.blit(tilemap.image, self.rect)
        pygame.display.update()


class Tileset:
    def __init__(self, file):
        self.get_info(file)
        self.image = pygame.image.load(self.file).convert_alpha()
        self.rect = self.image.get_rect()
        self.tiles = []
        self.load()
    
    def get_info(self, file):

        spec = importlib.util.spec_from_file_location("const","texture/" + file + "/" + file + "_const.py")
        const = importlib.util.module_from_spec(spec)
        sys.modules["const"] = const
        spec.loader.exec_module(const)

        self.file = const.FILE
        self.sprite_size = const.SPRITE_SIZE
        self.size = const.SIZE
        self.margin = const.MARGIN
        self.spacing = const.SPACING

    def load(self):

        self.tiles = []
        x0 = y0 = self.margin
        w, h = self.rect.size
        dx = self.sprite_size[0] + self.spacing
        dy = self.sprite_size[1] + self.spacing

        for y in range(x0, w, dx):
            for x in range(y0, h, dy):
                tile = pygame.Surface((self.sprite_size[0],self.sprite_size[1])).convert_alpha()
                tile.blit(self.image, (0, 0), (x, y, *(self.sprite_size[0],self.sprite_size[1])))
                self.tiles.append(tile)

    def __str__(self):
        return f'{self.__class__.__name__} file:{self.file} tile:{self.sprite_size}'


class Tilemap:
    def __init__(self, tileset, size=(32, 32), grid_activate=True, resize = 1):
        self.resize = resize
        self.sprite_size = size
        self.tileset = tileset
        self.save = []
        self.overlay = 0
        self.grid_activate = grid_activate

        self.set_surface()

    def set_scale(self, resize):

        self.resize = self.resize * resize
        self.set_surface()
        self.render()

    def set_surface(self):

        h, w = self.sprite_size
        self.image = pygame.Surface(
            (ceil(self.tileset.sprite_size[0]*w*self.resize), ceil(self.tileset.sprite_size[0]*h*self.resize))).convert_alpha()
        
        self.rect = self.image.get_rect()

    def render(self, save_activate=True):

        self.image.fill((0, 0, 0, 0))

        for mask in range(self.map.shape[0]):
            m, n = self.map.shape[1:3]
            for i in range(m):
                for j in range(n):
                    tile = pygame.transform.scale(self.tileset.tiles[self.map[mask][i, j]], (ceil(self.tileset.sprite_size[0]*self.resize), ceil(self.tileset.sprite_size[1]*self.resize)))
                    self.image.blit(tile, (ceil(j*self.tileset.sprite_size[0]*self.resize), ceil(i*self.tileset.sprite_size[0]*self.resize)))
                    
        if self.grid_activate:
            self.grid()

        if save_activate:
            self.save_local()

    def set_reset(self):
        self.map = np.array([np.full(self.sprite_size, 602, dtype=int)])
        self.render()

    def set_random(self):
        n = len(self.tileset.tiles)
        self.map = np.array([np.random.randint(n, size=self.sprite_size)])
        self.render()

    def set_enumerate(self):
        self.map = np.array([np.arange(0, self.sprite_size[0]*self.sprite_size[1], dtype=int).reshape(self.sprite_size)])
        self.render()

    def set_modify(self, tiles_pos, tile):
        for tile_pos in tiles_pos:
            self.map[tile_pos] = tile
        self.render()

    def set_generator(self, seed = np.random.randint(0,10000)):
        self.set_reset()
        
        offset = 8
        lissage = 8
        start = 20

        iron_coef = 0.01
        coal_coef = 0.03
        diamond_coef = 0.001


        for x in range(self.sprite_size[1]):
            self.map[0, ceil(start), x] = 332
            start += np.random.randint(-offset,offset+1)/lissage

        for x in range(self.sprite_size[1]):
            for y in range(1, self.sprite_size[0]):
                if self.map[0,y-1, x] == 332 or self.map[0,y-1, x] == 200:
                    for n in range(0, np.random.randint(2,4)):
                        self.map[0, y+n, x] = 200
                    break

        for x in range(self.sprite_size[1]):
            for y in range(1, self.sprite_size[0]):
                if self.map[0,y-1, x] == 200:
                    if self.map[0,y,x] != 200:
                        for n in range(self.sprite_size[0]-y):
                            rand = np.random.random()
                            if rand < iron_coef:
                                self.map[0,y+n,x] = 395
                            elif iron_coef < rand < iron_coef+coal_coef:
                                self.map[0,y+n,x] = 161
                            elif iron_coef+coal_coef < rand < diamond_coef+iron_coef+coal_coef and y+n > 30:
                                self.map[0,y+n,x] = 168
                            else:
                                self.map[0,y+n,x] = 308
                        break
        

        self.render()

    def set_overlay(self, overlay):
        self.overlay += overlay
        if self.overlay >= self.map.shape[0]:
            self.map = np.append(self.map, [np.full(self.sprite_size, 602, dtype=int)], axis=0)
            print(self.map.shape)

    def grid(self):
        m, n = self.map.shape[1:3]
        x, y = self.image.get_size()
        for i in range(m+1):
            pygame.draw.line(self.image, (255, 255, 255),
                             (0, y/m*i), (x, y/m*i))
        for j in range(n):
            pygame.draw.line(self.image, (255, 255, 255),
                             (x/n*j, 0), (x/n*j, y))

    def get_pos(self):
        pos = pygame.mouse.get_pos()
        return int(pos[1]/self.rect.height * self.sprite_size[0]//1), int(pos[0]/self.rect.width * self.sprite_size[1]//1)

    def save_local(self):
        self.save.append(self.map.tolist())

    def back(self):
        if len(self.save) > 1:
            np.array(self.save.pop())
            self.map = np.array(self.save.pop())
            self.render()

    def new_save(self):
        name = input('name: ')
        np.save('game_1/save/'+name+'.npy', self.map)

    def get_save(self):
        name = input('name: ')
        self.map = np.load('game_1/save/'+name+'.npy')
        self.render()

    def __str__(self):
        return f'{self.__class__.__name__} {self.sprite_size}'


game = Game()
game.run()
