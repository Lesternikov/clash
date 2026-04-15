import main
import pygame
import sys
from world import World
from player import Player

pygame.init()
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Clash Reverse")
clock = pygame.time.Clock()

# --- INICJALIZACJA GRY ---
world = World()
p1 = Player(1, "Gracz 1", (255, 50, 50))
p2 = Player(2, "Gracz 2", (50, 150, 255))
world.add_player(p1)
world.add_player(p2)

# --- KLUCZOWA ZMIANA TUTAJ ---
# Podajemy samą nazwę bazową ("final_map1") i plik FAC ("0.FAC")
world.load("final_map1", "0.FAC") 
world.spawn_test_builder()

# Zakładam, że masz już tę funkcję w world.py, więc używamy jej zamiast Pikiniera
world.setup_starting_units() 

running = True
while running:
    # 1. ZBIERAMY ZDARZENIA
    events = pygame.event.get()
    
    # Ta pętla służy TYLKO do zamykania gry krzyżykiem na oknie
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    # =========================================================
    # UWAGA: Te funkcje są teraz WYCIĄGNIĘTE z pętli 'for'!
    # Wykonają się dokładnie JEDEN RAZ na klatkę obrazu.
    # =========================================================
    world.handle_events(events) 
    world.update()  
    world.handle_camera()

    # Rysowanie
    screen.fill((0, 0, 0))
    world.draw(screen)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()