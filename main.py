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

p1 = Player(1, "Gracz 1", "red")
p2 = Player(2, "Gracz 2", "blue")

world.add_player(p1)
world.add_player(p2)

world.load("map.txt", "0.FAC")
# --- DODAJ TO TUTAJ ---
# Tworzymy jednostkę na polu (10, 10) - upewnij się, że to wolne pole (trawa ".")
start_unit = Unit("pikinier", 10, 10, p1) 

# Musimy dodać ją w TRZY miejsca, żeby wystko działało:
world.units.append(start_unit)      # 1. Żeby świat ją widział
p1.units.append(start_unit)         # 2. Żeby gracz ją posiadał
# ----------------------

running = True
running = True
while running:
# 1. OBSŁUGA ZDARZEŃ
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- KLIKNIĘCIE (Wciśnięcie przycisku) ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            world.handle_mouse_click(mx, my)

        # --- PUSZCZENIE (To musisz dodać tutaj!) ---
        if event.type == pygame.MOUSEBUTTONUP:
            mx, my = pygame.mouse.get_pos()
            world.handle_mouse_up(mx, my)
    world.handle_camera()  # Aktualizacja pozycji kamery
    world.draw_pygame(screen)  # Rysowanie z uwzględnieniem nowej kamery
    screen.fill((0, 0, 0))
    world.draw(screen)
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
