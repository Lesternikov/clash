import pygame
from utils import draw_text  # Zakładam, że tu masz funkcję draw_text

class PrisonSlot:
    def __init__(self, general=None):
        self.general = general
        self.turns_in_prison = 0
        
class CourtHandler:
    def __init__(self, world_instance):
        self.world = world_instance  # To jest nasz łącznik z resztą gry
        self.selected_prison_slot = None
        
        # Elementy specyficzne dla dworu zostają tutaj
        self.prison_slots = [PrisonSlot(), PrisonSlot(), PrisonSlot()]
        self.victories = 0
        self.defeats = 0
        self.court_back_button = pygame.Rect(15, 125, 105, 55)

    # --- LOGIKA OBLICZEŃ ---
    def calculate_army_power(self, player):
        power = 0
        for u in player.units:
            power += u.attack + u.defense + u.experience
        return power

    def calculate_gold(self, player):
        # Pobieramy zamki z gracza
        return sum(castle.gold for castle in player.castles)

    # --- OBSŁUGA KLIKNIĘĆ ---
    def handle_court_click(self, mx, my):
        # Powrót - musimy zmienić screen w GŁÓWNYM świecie
        if self.court_back_button.collidepoint(mx, my):
            self.world.screen = "castle"  # Zmieniamy w world_instance
            return

        # Kliknięcia w przyciski więzienia
        # Uwaga: Tutaj warto użyć rectów zdefiniowanych w draw_prison_sections
        # Dla uproszczenia na razie zostawiam Twoją logikę:
        start_y = 600
        section_w = 250
        gap = 40
        start_x = 60
        
        for i, slot in enumerate(self.prison_slots):
            x = start_x + i*(section_w + gap)
            if pygame.Rect(x+130, start_y+10, 100, 25).collidepoint(mx, my):
                self.execute_general(slot)
            if pygame.Rect(x+130, start_y+45, 100, 25).collidepoint(mx, my):
                self.torture_general(slot)
            if pygame.Rect(x+130, start_y+80, 100, 25).collidepoint(mx, my):
                self.bribe_general(slot)

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