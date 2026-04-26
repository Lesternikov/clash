import pygame

class RecruitmentManager:
    def __init__(self, world):
        self.world = world
        self.screen_res = (1026, 786)
        
        # 1. Ładowanie głównego tła
        try:
            self.bg = pygame.image.load("assets\DW_13_GFX.png").convert_alpha()
            self.bg = pygame.transform.scale(self.bg, self.screen_res)
        except:
            self.bg = pygame.Surface(self.screen_res)
            self.bg.fill((50, 20, 20))

        # 2. Definicja slotów na jednostki (10 slotów: 5 góra, 5 dół)
        # Współrzędne (x, y, szerokość, wysokość) - dopasuj do swojej grafiki!
        self.slots = []
        start_x, start_y = 50, 150
        gap_x, gap_y = 145, 180
        
        for row in range(2):
            for col in range(5):
                rect = pygame.Rect(start_x + col * gap_x, start_y + row * gap_y, 120, 160)
                self.slots.append(rect)

        # 3. Przycisk powrotu (często w prawym dolnym rogu na takich grafikach)
        self.btn_back = pygame.Rect(650, 530, 120, 40)
        
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, screen):
        # Rysujemy tło
        screen.blit(self.bg, (0, 0))
        
        # Rysujemy surowce gracza (na górze grafiki są na to miejsca)
        p = self.world.players[self.world.current_player]
        self._draw_resources(screen, p)

        # Rysujemy sloty jednostek
        castle = self.world.selected_castle
        if castle:
            # Zakładamy, że castle.available_units to lista dostępnych typów jednostek
            units_to_show = getattr(castle, 'available_units', [])
            
            for i, rect in enumerate(self.slots):
                # Opcjonalnie: ramka debugowania slotu
                # pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
                if i < len(units_to_show):
                    unit_data = units_to_show[i]
                    self._draw_unit_slot(screen, rect, unit_data)

    def _draw_resources(self, screen, player):
        # Przykładowe pozycje dla złota, drewna, kamienia (dostosuj do PNG)
        gold_txt = self.font.render(f"{player.gold}", True, (255, 215, 0))
        screen.blit(gold_txt, (600, 25)) 
        # itd. dla innych surowców

    def _draw_unit_slot(self, screen, rect, unit_data):
        # Tutaj rysujemy ikonę jednostki, jej nazwę i cenę
        name_txt = self.font.render(unit_data['name'], True, (255, 255, 255))
        screen.blit(name_txt, (rect.x + 5, rect.y + 5))
        
        cost_txt = self.font.render(f"Koszt: {unit_data['cost']}", True, (0, 255, 0))
        screen.blit(cost_txt, (rect.x + 5, rect.y + 130))

    def handle_click(self, mx, my):
        # 1. Powrót
        if self.btn_back.collidepoint(mx, my):
            self.world.screen = "garrison"
            return

        # 2. Kliknięcie w slot jednostki
        for i, rect in enumerate(self.slots):
            if rect.collidepoint(mx, my):
                print(f"Próba zakupu jednostki ze slotu {i}")
                self.buy_unit(i)
                break

    def buy_unit(self, slot_index):
        # Tutaj wstawiasz logikę odejmowania złota i dodawania jednostki do garnizonu
        pass

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])