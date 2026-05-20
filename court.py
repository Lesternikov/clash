import pygame
from utils import draw_text  

class PrisonSlot:
    def __init__(self, general=None):
        self.general = general
        self.turns_in_prison = 0
        
class CourtHandler:
    def __init__(self, world_instance):
        self.world = world_instance  
        
        self.prison_slots = [PrisonSlot("Jan"), PrisonSlot(), PrisonSlot()]
        self.victories = 0
        self.defeats = 0
        
        self.selected_prison_action = None 

        # =========================================================
        # --- MATEMATYKA SKALOWANIA ---
        # Zakładamy, że mierzyłeś to na oryginalnym obrazku 800x600
        # =========================================================
        orig_w = 800
        orig_h = 600
        
        ekran_w = pygame.display.get_surface().get_width()
        ekran_h = pygame.display.get_surface().get_height()
        
        sx = ekran_w / orig_w
        sy = ekran_h / orig_h

        # Przycisk powrotu - teraz idealnie trafia w czarną ramkę nad umięśnionym ramieniem!
        self.court_back_button = pygame.Rect(int(7*sx), int(72*sy), int(93*sx), int(53*sy))

        # --- IDEALNE WSPÓŁRZĘDNE WZGLĘDEM TŁA (800x600) ---
        self.prison_ui_rects = []
        
        base_portret_x = 24; base_portret_y = 494
        base_kolor_x = 49;   base_kolor_y = 480
        base_btn_x = 117;    base_btn_y = 454
        
        przeskok_x = 242
        
        # ==========================================
        # --- POWIĘKSZANIE PRZYCISKÓW ---
        # 1.0 to rozmiar oryginalny. 
        # 1.4 oznacza, że przyciski są o 40% większe! (Zmień to, jeśli wciąż za małe)
        powiekszenie = 1.2 
        # ==========================================
        
        w_kat = int(77 * powiekszenie * sx)
        h_kat = int(37 * powiekszenie * sy)
        
        w_kup = int(88 * powiekszenie * sx)
        h_kup = int(37 * powiekszenie * sy)
        # ==========================================
        # RĘCZNE PRZESUNIĘCIA DLA KAŻDEJ CELI (oś X)
        # [Cela 1, Cela 2, Cela 3]
        # ==========================================
        # Pierwsza cela to 0 (bo leży na pozycjach "base_...").
        # Druga to 290 (wynik z Twojego 1.2 * 242).
        # Trzecią musisz dostroić! Wpisałem 580, ale zmień to według potrzeb.
        przesuniecia_x = [0, 290.85, 572]

        for i in range(3):
            przesuniecie = przesuniecia_x[i]
            
            rects = {
                "PORTRET": pygame.Rect(int((base_portret_x + przesuniecie)*sx), int(base_portret_y*sy), int(68*sx), int(78*sy)),
                "KOLOR":   pygame.Rect(int((base_kolor_x + przesuniecie)*sx), int(base_kolor_y*sy), int(25*sx), int(12*sy)),
                
                # Dodajemy automatyczne odstępy na osi Y, żeby powiększone przyciski nie weszły na siebie
                "KAT":     pygame.Rect(int((base_btn_x + przesuniecie)*sx), int(base_btn_y*sy), w_kat, h_kat),
                "TORTURY": pygame.Rect(int((base_btn_x + przesuniecie)*sx), int((base_btn_y + 42 * powiekszenie)*sy), w_kat, h_kat),
                "KUP":     pygame.Rect(int((base_btn_x - 12 + przesuniecie)*sx), int((base_btn_y + 81 * powiekszenie)*sy), w_kup, h_kup)
            }
            self.prison_ui_rects.append(rects)
    # --- LOGIKA OBLICZEŃ (Twoja stara) ---
    def calculate_army_power(self, player):
        power = 0
        for u in player.units:
            exp = getattr(u, 'experience', 0)
            power += u.attack + u.defense + exp
        return power

    def calculate_gold(self, player):
        return sum(castle.gold for castle in player.castles)

    # --- OBSŁUGA KLIKNIĘĆ ---
    # --- OBSŁUGA KLIKNIĘĆ ---
    def handle_court_click(self, mx, my):
        
        # 1. Przycisk Powrotu
        if self.court_back_button.collidepoint(mx, my) or (hasattr(self.world, 'back_button_castle') and self.world.back_button_castle.collidepoint(mx, my)):
            
            # USUŃ LUB ZAKOMENTUJ TĘ LINIJĘ, JEŚLI JĄ MASZ:
            # self.world.screen = "castle" 
            
            # Włączamy stoper! (Gra narysuje wciśnięty przycisk i poczeka)
            self.world.back_anim_timer = pygame.time.get_ticks()
            self.world.back_destination = "castle"
            
            print("Przycisk powrotu wciśnięty! Czekam na animację...")
            return

        # 2. Akcje Więzienia (Mechanika wykluczania)
        for i, slot in enumerate(self.prison_slots):
            if not slot.general:
                continue # Cela jest pusta, ignorujemy kliknięcia!
            
            rects = self.prison_ui_rects[i]
            
            # Jeśli klikniesz, nadpisujemy globalny wybór (anulując poprzedni)!
            if rects["KAT"].collidepoint(mx, my):
                self.selected_prison_action = {"slot": i, "action": "KAT"}
                print(f"Zlecono ŚCIĘCIE w celi nr {i+1}. Czeka na koniec tury.")
                return
            if rects["TORTURY"].collidepoint(mx, my):
                self.selected_prison_action = {"slot": i, "action": "TORTURY"}
                print(f"Zlecono TORTURY w celi nr {i+1}. Czeka na koniec tury.")
                return
            if rects["KUP"].collidepoint(mx, my):
                self.selected_prison_action = {"slot": i, "action": "KUP"}
                print(f"Zlecono PRZEKUPSTWO w celi nr {i+1}. Czeka na koniec tury.")
                return

    def execute_general(self, slot):
        if slot.general:
            print(f"DEBUG: Generał {slot.general.name} został stracony.")
            slot.general = None

    def torture_general(self, slot):
        if slot.general:
            print(f"DEBUG: Torturowanie {slot.general.name} - informacje zdobyte.")
        
    def bribe_general(self, slot):
        if slot.general:
            print(f"DEBUG: {slot.general.name} przekupiony!")

    # --- RYSOWANIE (UI) ---
    def draw_court(self, screen):
        self.draw_court_players_header(screen)
        self.draw_queen_panel(screen)
        self.draw_court_stats(screen)
        self.draw_prison_sections(screen)
        
        # Wywołujemy draw_button z World, bo tam pewnie została ta metoda
        self.world.renderer.draw_button(screen, "<-", 
        self.court_back_button, (140, 40, 40))
    def draw_court_players_header(self, screen):
        start_x = 140
        start_y = 20
        slot_w = 240
        slot_h = 90
        
        # Używamy self.world.players zamiast self.players!
        for i in range(5):
            row = i // 3
            col = i % 3 
            current_x = start_x + col * slot_w 
            if row == 1: current_x += slot_w // 2
            current_y = start_y + row * slot_h
            
            rect = pygame.Rect(current_x, current_y, 200, 60)
            pygame.draw.rect(screen, (120, 120, 120), rect)

            if i < len(self.world.players): # KLUCZOWA ZMIANA
                p = self.world.players[i]   # KLUCZOWA ZMIANA
                pygame.draw.rect(screen, p.color, rect)
                draw_text(screen, p.name, rect.x + 10, rect.y + 5)

    def draw_queen_panel(self, screen):
        w = screen.get_width()
        rect = pygame.Rect(w//2 - 290, 370, 600, 180)
        pygame.draw.rect(screen, (210,200,160), rect)
        draw_text(screen, "Nie ma królowej", rect.x + 250, rect.y + 20)

    def draw_court_stats(self, screen):
        screen_w = screen.get_width()
        section_width = screen_w // 3
        top_y = 190
        font_title = pygame.font.SysFont(None, 28)
        font = pygame.font.SysFont(None, 22)
        titles = ["SIŁA ARMII", "ZŁOTO", "BILANS"]

        for i in range(3):
            x = 120 + i * section_width
            title_surface = font_title.render(titles[i], True, (255,255,255))
            screen.blit(title_surface, (x - 100, top_y + 100))

            for index in range(5):
                player_y = top_y + 40 + index * 28
                if index < len(self.world.players): # KLUCZOWA ZMIANA
                    player = self.world.players[index]
                    if i == 0: value = self.calculate_army_power(player)
                    elif i == 1: value = self.calculate_gold(player)
                    elif i == 2: value = player.wins - player.losses if hasattr(player, "wins") else 0
                    text = f"{player.name}: {value}"
                else:
                    text = "-"
                
                surface = font.render(text, True, (200,200,200))
                screen.blit(surface, (x + 20, player_y))

    def draw_prison_sections(self, screen):
        start_y = 600
        section_w = 250
        gap = 40
        start_x = 60

        for i, slot in enumerate(self.prison_slots):
            x = start_x + i*(section_w + gap)
            y = start_y
            pygame.draw.rect(screen, (90,90,90), (x, y, section_w, 120))

            if slot.general:
                draw_text(screen, slot.general.name, x+10, y+10)
                draw_text(screen, "Okup: 500", x+10, y+40)
            else:
                draw_text(screen, "Brak więźnia", x+10, y+10)

            # Przyciski - wywołujemy draw_button z World
            self.world.renderer.draw_button(screen, "SCIECIE", pygame.Rect(x+130, y+10, 100, 25))
            self.world.renderer.draw_button(screen, "TORTURY", pygame.Rect(x+130, y+45, 100, 25))
            self.world.renderer.draw_button(screen, "PRZEKUP", pygame.Rect(x+130, y+80, 100, 25))

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])