import main
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
p1 = Player(1, "Gracz 1", (255, 50, 50))
p2 = Player(2, "Gracz 2", (50, 150, 255))
world.add_player(p1)
world.add_player(p2)

# --- KLUCZOWA ZMIANA TUTAJ ---
# Podajemy samą nazwę bazową ("final_map1") i plik FAC ("0.FAC")
world.load("final_map1", "0.FAC") 
# -----------------------------

world.spawn_test_builder()

start_unit = Unit("Pikinier", 10, 10, p1) 
world.units.append(start_unit)
p1.units.append(start_unit)

running = True
while running:
    world.update()  
    world.handle_events() 
    world.handle_camera()

    screen.fill((0, 0, 0))    
    world.draw(screen)        
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()