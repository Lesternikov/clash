import pygame
from world import World
from player import Player
from unit import Unit
import sys

pygame.init()
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Clash Reverse")
clock = pygame.time.Clock()

world = World()
p1 = Player(1, "Gracz 1", (255, 50, 50))   # Soczysty czerwony
p2 = Player(2, "Gracz 2", (50, 150, 255))  # Jasny niebieski
world.add_player(p1)
world.add_player(p2)
world.load("map.txt", "0.FAC")

start_unit = Unit("pikinier", 10, 10, p1) 
world.units.append(start_unit)
p1.units.append(start_unit)

running = True
while running:
    # 1. OBSŁUGA ZDARZEŃ - Delegujemy WSZYSTKO do World
    # To pozwoli działać Twoim returnom i zmianom stanów
    world.handle_events() 

    # 2. LOGIKA
    world.handle_camera()

    # 3. RYSOWANIE - Kolejność jest krytyczna!
    screen.fill((0, 0, 0))    # 1. Najpierw czyścimy na czarno
    world.draw(screen)        # 2. Rysujemy mapę, zamki i EKRANY (Garrison, Info itp.)
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()