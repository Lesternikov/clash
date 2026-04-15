import main
import pygame
import sys
from world import World
from player import Player
from unit import Unit
from castle_graphics import CastleGraphics # <--- NASZ NOWY WIDOK ZAMKU

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

start_unit = Unit("Pikinier", 10, 10, p1) 
world.units.append(start_unit)
p1.units.append(start_unit)

# --- INICJALIZACJA WIDOKU ZAMKU ---
# Zakładam, że tło zamku (Z_01_GFX.jpg) leży w folderze np. "assets" albo "gfx"


# --- MASZYNA STANÓW ---
current_state = "MAP"      # Na start pokazujemy mapę
active_castle = None       # Zmienna przechowująca zamek, do którego weszliśmy

running = True
while running:
    # 1. GŁÓWNA PĘTLA ZDARZEŃ
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        # --- TESTOWE WEJŚCIE DO ZAMKU (KLAWISZ 'C') ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and current_state == "MAP":
                # Szukamy pierwszego zamku na liście światowej
                if len(world.castles) > 0:
                    active_castle = world.castles[0] 
                    current_state = "CASTLE"
                    print("Wchodzimy do zamku na koordynatach:", active_castle.x, active_castle.y)
            
            # --- WYJŚCIE Z ZAMKU (KLAWISZ 'ESC') ---
            elif event.key == pygame.K_ESCAPE and current_state == "CASTLE":
                current_state = "MAP"
                active_castle = None
                print("Wracamy na mapę!")



        # --- JESTEŚMY NA MAPIE ---
        # Ważne: Jeśli twój world.handle_events() w środku też ma "pygame.event.get()",
        # to te dwie pętle będą sobie podkradać eventy! W profesjonalnych grach
        # eventy czyta się raz w main.py i przekazuje w dół, np: world.handle_events(events)
        world.handle_events(events) 
        world.update()  
        world.handle_camera()
            # 2. AKTUALIZACJA I RYSOWANIE ZALEŻNE OD STANU
        screen.fill((0, 0, 0))
        world.draw(screen)
        

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()