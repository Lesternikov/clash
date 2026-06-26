import pygame
import sys
import os

# --- 1. BEZPIECZNE USTAWIANIE FOLDERU ROBOCZEGO ---
if getattr(sys, 'frozen', False):
    # Jeśli uruchomione jako skompilowany plik .exe
    os.chdir(os.path.dirname(sys.executable))
else:
    # Jeśli uruchomione jako zwykły plik .py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Importy z Twoich plików muszą być po ustawieniu ścieżki (jeśli cokolwiek ładują)!
from world import World
from player import Player
from controls import ControlsHandler
from renderer import Renderer
from pathfinding import Pathfinder
from map_graphics import MapGraphics

if __name__ == "__main__":
    # --- 2. INICJALIZACJA (Tylko JEDEN RAZ!) ---
    pygame.init()
    screen = pygame.display.set_mode((1026, 766))
    pygame.display.set_caption("Clash Reverse")
    clock = pygame.time.Clock()

    # --- INICJALIZACJA GRY ---
    # 1. Tworzysz świat
    world = World()

# 2. Tworzysz grafikę i WSTRZYKUJESZ do niej świat
gfx = MapGraphics(world)
# 2. Tworzysz renderer i dajesz mu dostęp do świata
renderer = Renderer(world, gfx) # Dodajemy gfx jako drugi argument
world.renderer = renderer
pathfinding = Pathfinder(world)
world.pathfinder = pathfinding
# 3. Tworzysz kontroler
controls = ControlsHandler(world)
world.map_gfx= gfx


# --- KLUCZOWA ZMIANA TUTAJ ---
# Podajemy samą nazwę bazową ("final_map1") i plik FAC ("0.FAC")
pathfinding.load("final_map1", "0.FAC") 

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
    controls.handle_events(events) 
    controls.handle_camera()
    # Rysowanie
    screen.fill((0, 0, 0))
    renderer.draw(screen)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()