import pygame
import os

class TacticalCombat:
    def __init__(self, world, attacker, defender):
        self.world = world
        self.attacker = attacker
        self.defender = defender
        
        # =========================================================
        # 🟢 PANEL STEROWANIA ARENĄ (ORIENTACJA POZIOMA)
        # =========================================================
        self.grid_width = 16   # Ilość kratek w poziomie (Zmiejszona by zrobić miejsce na UI)
        self.grid_height = 8  # Ilość kratek w pionie
        self.tile_size = 46    # Kratka idealnie dopasowana wielkością do jednostki
        
        self.arena_offset_x = 0 
        self.arena_offset_y = 0 
        
        # 🟢 PANEL BOKU (Interfejs sklejony z FRAME_1 i FRAME_3)
        self.panel_x = self.grid_width * self.tile_size # Prawy panel zaczyna się zaraz za areną (ok. 644 px)
        self.panel_y = 0
        self.panel_scale = 1.0 # Jeśli okiennice są za małe, zmień na np. 1.1 lub 1.2
        # =========================================================
        
        # 1. ŁADOWANIE CZĘŚCI INTERFEJSU (Góra i Dół)
        self.panel_top = self._load_and_scale(
            ["assets/minimum/FRAME_S32/FRAME_S32_1.png"], self.panel_scale)
            
        self.panel_bottom = self._load_and_scale(
            ["assets/minimum/FRAME_S32/FRAME_S32_3.png"], self.panel_scale)
        
        # 2. ŁADOWANIE PRZYCISKU ODWROTU (Kotwica/Hak - BUTTONS_S32_1.png)
        self.btn_retreat = self._load_and_scale(
            ["assets/minimum/BUTTONS_S32/BUTTONS_S32_1.png"], self.panel_scale)

        # Pozycja przycisku Kotwicy wewnątrz dolnego panelu (Na oko w białym kwadracie)
        if self.btn_retreat and self.panel_top:
            bw, bh = self.btn_retreat.get_width(), self.btn_retreat.get_height()
            top_h = self.panel_top.get_height()
            # Ustawiamy kotwicę na dole, pod statystykami
            self.rect_retreat = pygame.Rect(self.panel_x + int(140 * self.panel_scale), self.panel_y + top_h + int(140 * self.panel_scale), bw, bh)
        else:
            self.rect_retreat = pygame.Rect(self.panel_x + 100, 600, 100, 40) # Failsafe
        
        # 3. Generowanie "Pustyni"
        self.bg_tile = self._create_desert_tile()
        
        # 4. Zbieranie pełnych armii
        self.att_army = self._get_full_army(attacker)
        self.def_army = self._get_full_army(defender)
        
        # 5. Słownik trzymający pozycje jednostek na siatce
        self.arena_units = {}
        self._deploy_armies()

    def _load_and_scale(self, paths, scale):
        for p in paths:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    if scale != 1.0:
                        new_w = int(img.get_width() * scale)
                        new_h = int(img.get_height() * scale)
                        img = pygame.transform.smoothscale(img, (new_w, new_h))
                    return img
                except Exception as e: 
                    print(f"Nie udało się załadować {p}: {e}")
        return None

    def _get_tactical_unit_image(self, unit):
        """Wyszukuje grafikę jednostki (np. assets/normal/BUDOW2_S32/BUDOW2_0.png)"""
        # 1 dla Czerwonego (Don Marek), 2 dla Niebieskiego (Lech VI)
        color_id = "1" if unit.owner and getattr(unit.owner, 'color_name', 'red') == "red" else "2"
        
        # Skracamy nazwę do formatu z Clasha (np. "BUDOW", "INFL")
        prefix = unit.type.upper()[:5] 
        if unit.type == "Budowniczy": prefix = "BUDOW"
        if unit.type == "Generał": prefix = "GENER" # Zakładam skrót dla generała
        
        # Dokładnie według Twojego opisu:
        folder_name = f"{prefix}{color_id}_S32"   # np. BUDOW1_S32 lub BUDOW2_S32
        file_name = f"{prefix}{color_id}_16.png"   # np. BUDOW1_0.png lub BUDOW2_0.png
        
        # Sklejamy to w pełną ścieżkę
        path = os.path.join("assets", "normal", folder_name, file_name)
        
        # Alternatywna nazwa (gdyby jednak miał dopisek S32 w pliku, jak na jednym z Twoich zrzutów)
        path_alt = os.path.join("assets", "normal", folder_name, f"{prefix}{color_id}_S32_16.png")
        
        for p in [path, path_alt]:
            if os.path.exists(p):
                return pygame.image.load(p).convert_alpha()
                
        # --- ZAPASOWE: Jeśli brak pliku na dysku, bierzemy to, co jest w pamięci z mapy
        if hasattr(unit, 'walk_frames') and unit.walk_frames:
            return unit.walk_frames[0]
        elif hasattr(unit, 'sprites') and unit.sprites:
            return unit.sprites[0]
            
        return None

    def _create_desert_tile(self):
        """Tworzy kafel pustyni"""
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill((200, 120, 50)) # Pomarańczowy piach
        pygame.draw.rect(surface, (150, 80, 30), (0, 0, self.tile_size, self.tile_size), 1)
        pygame.draw.arc(surface, (150, 80, 30), (5, 5, self.tile_size-10, self.tile_size-10), 0, 1.5, 1)
        return surface

    def _get_full_army(self, leader):
        army = [leader]
        if hasattr(leader, 'garrison') and leader.garrison:
            army.extend([u for u in leader.garrison if u is not None])
        return army

    def _deploy_armies(self):
        """Rozstawia armie horyzontalnie: Atakujący po lewej, Obrońca po prawej."""
        # ATAKUJĄCY: Zaczyna od środka lewej krawędzi
        start_y = max(0, (self.grid_height - len(self.att_army)) // 2)
        idx = 0
        for x in range(3): # Maks 3 kolumny
            for y in range(start_y, self.grid_height):
                if idx < len(self.att_army):
                    self.arena_units[(x, y)] = self.att_army[idx]
                    idx += 1
                else: break
        
        # OBROŃCA: Zaczyna od środka prawej krawędzi areny
        start_y_def = max(0, (self.grid_height - len(self.def_army)) // 2)
        idx = 0
        for x in range(self.grid_width - 1, self.grid_width - 4, -1):
            for y in range(start_y_def, self.grid_height):
                if idx < len(self.def_army):
                    self.arena_units[(x, y)] = self.def_army[idx]
                    idx += 1
                else: break

    def draw(self, screen):
        screen.fill((10, 10, 10))
        
        # 1. RYSOWANIE ARENY PUSTYNI
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                px = self.arena_offset_x + x * self.tile_size
                py = self.arena_offset_y + y * self.tile_size
                screen.blit(self.bg_tile, (px, py))
                
        # 2. RYSOWANIE JEDNOSTEK NA ARENIE
        for (x, y), unit in self.arena_units.items():
            px = self.arena_offset_x + x * self.tile_size
            py = self.arena_offset_y + y * self.tile_size
            
            # Magiczne wyciąganie Twojej oryginalnej grafiki z numerem frakcji (1/2)
            img = self._get_tactical_unit_image(unit)
                
            if img:
                skala_ludzika = self.tile_size / max(img.get_width(), img.get_height()) * 0.95
                new_w = int(img.get_width() * skala_ludzika)
                new_h = int(img.get_height() * skala_ludzika)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
                
                # Zwrócenie Obrońcy twarzą w lewą stronę (Lustrzane odbicie dla naturalnego efektu)
                if unit in self.def_army:
                    img = pygame.transform.flip(img, True, False)
                    
                img_x = px + (self.tile_size - new_w) // 2
                img_y = py + (self.tile_size - new_h) // 2
                screen.blit(img, (img_x, img_y))
            else:
                # Awaryjnie - kwadracik
                color = unit.owner.color if unit.owner else (255, 255, 255)
                pygame.draw.rect(screen, color, (px + 4, py + 4, self.tile_size - 8, self.tile_size - 8))

        # 3. RYSOWANIE SKLEJONEGO PANELU BITEWNEGO
        curr_y = self.panel_y
        
        # Najpierw górna część z pięcioma slotami (Miecz, Bieg, Biceps, Łuk, Tarcza)
        if self.panel_top:
            screen.blit(self.panel_top, (self.panel_x, curr_y))
            curr_y += self.panel_top.get_height()
            
        # Potem dolna część doczepiona idealnie pod spodem (Magia, Morale i duże okno)
        if self.panel_bottom:
            # Nakładamy z delikatnym przesunięciem o -1px na wszelki wypadek, by usunąć czarną szparę
            screen.blit(self.panel_bottom, (self.panel_x, curr_y - 1))
            
        # 4. RYSOWANIE PRZYCISKU ODWROTU (Kotwica)
        if self.btn_retreat:
            screen.blit(self.btn_retreat, self.rect_retreat.topleft)
            mx, my = pygame.mouse.get_pos()
            if self.rect_retreat.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 215, 0), self.rect_retreat, 2)

    def handle_click(self, mx, my):
        # Kliknięcie w kotwicę zamyka bitwę
        if self.rect_retreat.collidepoint(mx, my):
            print("Zarządzono odwrót! Wracamy na mapę.")
            self.world.combat_attacker = None
            self.world.combat_defender = None
            self.world.screen = "map"

if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])