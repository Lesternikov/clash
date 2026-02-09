import pygame
from world import World
from player import Player
from unit import Unit

pygame.init()

# okno gry
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Clash Reverse")

clock = pygame.time.Clock()

# world
world = World()

p1 = Player("Gracz 1", "red")
p2 = Player("Gracz 2", "blue")

world.add_player(p1)
world.add_player(p2)

world.load("map.txt", "0.FAC")

running = True
while running:
    result = world.handle_events()
    if result == "quit":
        running = False

    screen.fill((0, 0, 0))
    world.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
