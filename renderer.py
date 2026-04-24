
import pygame
import random
from settings import TERRAIN_TYPES, TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from buildings import BuildingsMixin
from utils import draw_text
class Renderer:
    def __init__(self, world_instance, gfx, ):
        self.world = world_instance
        self.font_small = pygame.font.SysFont("Arial", 12)
        self.font_main  = pygame.font.SysFont("Arial", 18)
        self.gfx = gfx # Zapisujemy grafikę lokalnie
        # --- DODAJ TO TUTAJ ---
        if not pygame.font.get_init():
            pygame.font.init()
        
        # Definiujemy czcionkę, której brakuje w linii 212
        self.font = pygame.font.SysFont("Arial", 24)
        # Możesz też dodać inne, jeśli będą potrzebne
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.buildings = BuildingsMixin()
        self.active_dropdown = None
        self.show_top_ui = False
        self.top_ui_full_area = pygame.Rect(0, 0, 1024, 55)

    def draw(self, screen):
        w = self.world
        b = self.buildings
        # Stoper powrotu
        if getattr(w, 'back_anim_timer', 0) > 0:
            elapsed = pygame.time.get_ticks() - w.back_anim_timer
            if elapsed > 700:
                w.screen = w.back_destination
                if w.screen == "map":
                    w.selected_castle = None
                w.back_anim_timer = 0
                return

        screen.fill((30, 30, 30))

        # Rysujemy mapę pod ekranami które tego wymagają
        screens_with_bg = ["map", "trap_info", "unit_info", "forge", "workshop"]
        if w.screen in screens_with_bg:
            self.draw_map(screen)

        # Wybieramy co rysować
        if w.screen == "map":
            self.draw_top_bar(screen)
            self.draw_ui(screen)

        elif w.screen == "trap_info":
            self.draw_top_bar(screen)
            self.draw_ui(screen)
            w.draw_trap_popup(screen)

        elif w.screen == "castle":
            w.draw_castle_interface(screen)
            if getattr(w, "menu_open", False):
                mx, my = pygame.mouse.get_pos()
                w.draw_castle_menu(screen, mx, my)

        elif b.screen in ("garrison", "Strażnica"):
            if b.selected_castle and getattr(b.selected_castle, 'building_type', "") == "Strażnica":
                b.draw_garrison_only(screen)
            else:
                b.draw_garrison(screen)

        elif b.screen == "recruitment":
            w.draw_recruitment(screen)

        elif self.court.screen == "court":
            self.court.draw_court(screen)

        elif w.screen == "peasants":
            w.draw_peasants(screen)

        elif b.screen in ["forge", "workshop", "hospital", "school"]:
            draw_func = getattr(w, f"draw_{b.screen}", None)
            if draw_func:
                draw_func(screen)

        elif w.screen == "unit_info":
            w.draw_unit_info(screen)

        # Nakładka statystyk jednostki
        if getattr(w, 'inspected_unit', None):
            stats_x = 300 if w.screen == "garrison" else 150
            stats_y = 380 if w.screen == "garrison" else 200
            w.draw_unit_stats_table(screen, stats_x, stats_y,
                                    w.inspected_unit.type, w.inspected_unit)

        if getattr(w, "demolish_confirm", False):
            w.draw_demolish_confirm(screen)

    def draw_map(self, screen):
        w = self.world

        # Teren
        self.gfx.draw_terrain(screen, self.world)
        # Siatka
        if getattr(w, 'show_grid', False):
            self.draw_grid_lines(screen)

        # Zamki
        for castle in w.castles:
            w.draw_castle_on_map(screen, castle)

        # Jednostki
        unit_font = pygame.font.SysFont(None, 24)
        for u in w.units:
            if u.x < 0 or u.y < 0:
                continue
            px = int(u.x) * TILE_SIZE - w.camera_x
            py = int(u.y) * TILE_SIZE - w.camera_y

            owner_color = u.owner.color if (u.owner and hasattr(u.owner, 'color')) else (200, 200, 200)
            pygame.draw.rect(screen, owner_color, (px + 4, py + 4, 24, 24))

            label = getattr(u, 'short_name', str(u.type)[:2].upper())
            txt_surface = unit_font.render(label, True, (255, 255, 255))
            text_rect = txt_surface.get_rect(center=(px + 16, py + 16))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(2, 2))
            screen.blit(txt_surface, text_rect)

            if u == w.selected_unit:
                pygame.draw.rect(screen, (255, 255, 255), (px, py, TILE_SIZE, TILE_SIZE), 2)

        # Kropki planowanej trasy
        if w.selected_unit and w.selected_unit in w.units:
            if getattr(w.selected_unit, 'planned_path', None):
                w.pathfinder.draw_path_dots(screen, w.selected_unit,
                                            w.selected_unit.planned_path)

        # Strzałki budowy drogi
        if getattr(w, 'road_build_mode', False):
            w.pathfinder.draw_road_arrows(screen)

        # Podgląd zasięgu pułapki
        if getattr(w, 'trap_build_mode', False):
            w.draw_build_system(screen)

        random.seed()

    def draw_grid_lines(self, screen):
        w = self.world
        offset_x = -(w.camera_x % TILE_SIZE)
        offset_y = -(w.camera_y % TILE_SIZE)
        for x in range(0, SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50),
                             (x + offset_x, 0), (x + offset_x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50),
                             (0, y + offset_y), (SCREEN_WIDTH, y + offset_y))
            
    def draw_castle(self, screen, castle):
        """Ta funkcja rysuje tylko OBIEKT na mapie świata."""
        # Obliczamy pozycję na ekranie względem kamery
        px = castle.x * TILE_SIZE - self.camera_x
        py = castle.y * TILE_SIZE - self.camera_y
        
        # Wybieramy obrazek (np. stan zniszczenia)
        s_idx = 3 # domyślny stan 'gotowy'
        if getattr(castle, 'destroyed', False): s_idx = 4
        
        # Rysujemy
        tiles = self.castle_tiles.get(s_idx, [])
        if len(tiles) == 4:
            offsets = [(0,0), (1,0), (0,1), (1,1)]
            for i in range(4):
                dx, dy = offsets[i]
                screen.blit(tiles[i], (px + dx*TILE_SIZE, py + dy*TILE_SIZE))

    def draw_unit(self, screen, u):
        """Rysuje jednostkę na mapie świata z uwzględnieniem kamery."""
        # 1. Obliczamy pozycję na ekranie
        px = int(u.x * TILE_SIZE) - self.camera_x
        py = int(u.y * TILE_SIZE) - self.camera_y

        # 2. Rysujemy grafikę jednostki (jeśli istnieje)
        # Zakładam, że u.walk_frames to lista obrazków dla animacji
        if hasattr(u, 'walk_frames') and u.walk_frames:
            # Prosta animacja oparta na czasie gry
            frame_idx = (pygame.time.get_ticks() // 150) % len(u.walk_frames)
            img = u.walk_frames[frame_idx]
            screen.blit(img, (px, py))
        else:
            # Failsafe: Jeśli jednostka nie ma grafiki, rysujemy kolorowy kwadrat
            # owner.color to kolor gracza (np. czerwony dla wroga, niebieski dla Ciebie)
            owner_color = (200, 200, 200)
            if hasattr(u, 'owner') and u.owner:
                owner_color = getattr(u.owner, 'color', (200, 200, 200))
            
            pygame.draw.rect(screen, owner_color, (px + 4, py + 4, 24, 24))
            pygame.draw.rect(screen, (0, 0, 0), (px + 4, py + 4, 24, 24), 1)

        # 3. Pasek życia (opcjonalnie)
        if hasattr(u, 'health') and hasattr(u, 'max_health'):
            health_pct = max(0, u.health / u.max_health)
            pygame.draw.rect(screen, (255, 0, 0), (px, py - 5, TILE_SIZE, 4))
            pygame.draw.rect(screen, (0, 255, 0), (px, py - 5, int(TILE_SIZE * health_pct), 4))

        # 4. Ramka zaznaczenia (jeśli to aktualnie wybrana jednostka)
        if u == getattr(self, 'selected_unit', None):
            pygame.draw.rect(screen, (255, 255, 255), (px, py, TILE_SIZE, TILE_SIZE), 2)

    def draw_top_bar(self, screen):
        mx, my = pygame.mouse.get_pos()
        
        # --- 1. LOGIKA POKAZYWANIA/CHOWANIA ---
        # Używamy self.world.show_top_ui, bo to stan gry
        if self.world.top_ui_trigger_area.collidepoint(mx, my):
            self.world.show_top_ui = True
        elif not self.world.top_ui_full_area.collidepoint(mx, my) and self.world.active_dropdown is None:
            self.world.show_top_ui = False

        # --- 2. RYSOWANIE PASKA ---
        if self.world.show_top_ui:
            # Tło paska
            pygame.draw.rect(screen, (40, 40, 40), (0, 0, 1024, 40))
            
            # Przycisk SYSTEM
            pygame.draw.rect(screen, (100, 100, 100), self.world.btn_system)
            screen.blit(self.font.render("System", True, (255, 255, 255)), (self.world.btn_system.x + 5, 10))

            # Przycisk MAPA
            pygame.draw.rect(screen, (100, 100, 100), self.world.btn_mapa)
            screen.blit(self.font.render("Mapa", True, (255, 255, 255)), (self.world.btn_mapa.x + 15, 10))

            # Przycisk KONIEC TURY
            pygame.draw.rect(screen, (139, 69, 19), self.world.next_turn_button)
            pygame.draw.rect(screen, (212, 175, 55), self.world.next_turn_button, 2)
            txt_turn = self.font.render(f"Koniec tury {self.world.turn}", True, (255, 255, 255))
            screen.blit(txt_turn, (self.world.next_turn_button.x + 10, 10))

            # --- 3. LOGIKA DROPDOWN (MENU ROZWIJANE) ---
            options = []  # BEZPIECZNIK: Inicjalizacja pustej listy
            start_x = 0

            if self.world.active_dropdown in self.world.menu_options:
                options = self.world.menu_options[self.world.active_dropdown]
                start_x = self.world.btn_system.x if self.world.active_dropdown == "System" else self.world.btn_mapa.x
                
                # CZYŚCIMY słowniki (są w Rendererze, bo służą do wykrywania kliknięć w UI)
                self.system_buttons = {}
                self.mapa_buttons = {}

                # Pętla rysująca opcje dropdowna
                for i, opt in enumerate(options):
                    rect = pygame.Rect(start_x, 40 + i * 30, 120, 30)
                    
                    # Zapisujemy Rect do odpowiedniego słownika dla ControlsHandlera
                    if self.world.active_dropdown == "System":
                        self.system_buttons[opt] = rect
                    else:
                        self.mapa_buttons[opt] = rect

                    # Rysowanie kafelka opcji
                    is_hovered = rect.collidepoint(mx, my)
                    color = (150, 150, 150) if is_hovered else (80, 80, 80)
                    
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (200, 200, 200), rect, 1) # Obramowanie
                    
                    txt_opt = self.font.render(opt, True, (255, 255, 255))
                    screen.blit(txt_opt, (rect.x + 10, rect.y + 5))

            
    def draw_button(self, screen, text, rect, color=(90, 90, 90), style=None):
        """
        style=None      -> zwykły przycisk (prostokąt z tekstem)
        style="castle"  -> grafika back_castlen/back_castlec
        style="bldg"    -> grafika back_normal/back_clicked
        """
        
        if style == "castle":
            img = self.back_img_castle_pressed if getattr(self, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.back_anim_timer < 500 \
                else self.back_img_castle_normal
            screen.blit(img, rect.topleft)
            return

        if style == "bldg":
            img = self.back_img_bldg_pressed if getattr(self, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.back_anim_timer < 500 \
                else self.back_img_bldg_normal
            screen.blit(img, rect.topleft)
            return

        # Zwykły przycisk
        mx, my = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mx, my)
        display_color = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255)) \
                        if is_hovered else color
        pygame.draw.rect(screen, display_color, rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1)
        txt_surface = pygame.font.SysFont(None, 20).render(text, True, (255, 255, 255))
        screen.blit(txt_surface, txt_surface.get_rect(center=rect.center))

    def draw_bottom_bar(self, screen):
        # FIX dla NameError: Pobieramy pozycję myszy
        mx, my = pygame.mouse.get_pos()
        
        # PADDING: O ile pikseli zmniejszyć grafikę z każdej strony wewnątrz ramki
        # Zwiększ tę wartość, jeśli ikony nadal wydają się za duże
        icon_padding = 14

        for i, rect in enumerate(self.world.action_buttons):
            # 1. Rysujemy grafikę przycisku z MapGraphics
            if i < len(self.gfx.button_images):
                image = self.gfx.button_images[i]
                
                # Obliczamy nową pozycję, aby wyśrodkować ikonę z marginesem
                # (Zakładamy, że ikona ma 70x70, a rect jest teraz szerszy)
                icon_x = rect.x + icon_padding
                icon_y = rect.y + icon_padding
                
                # Jeśli rect jest dużo szerszy, możemy chcieć wyśrodkować ikonę:
                # icon_x = rect.x + (rect.width - 70) // 2
                
                # Rysujemy ikonę z przesunięciem (padding)
                screen.blit(image, (icon_x, icon_y))
            
       

            # 3. Efekt najechania (podświetlenie krawędzi)
            if rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)
                
            # --- SEKCJA RYSOWANIA TEKSTU ZOSTAŁA USUNIĘTA ---
    def draw_unit_info(self, screen):
        # Historyczne informacje o jednostce w koszarach.
        screen.fill((20,20,20))
        0
        # Jeśli tekst jest pusty, zainicjuj go bezpiecznym komunikatem
        if not hasattr(self, 'unit_info_text') or not self.unit_info_text:
            self.unit_info_text = "Brak informacji\nNie wybrano jednostki."

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 28)

        lines = self.unit_info_text.split("\n")
        y = 120

        # Nagłówek (pierwsza linia)
        if lines:
            screen.blit(font_title.render(lines[0], True, (255,255,0)), (120, y)) # Zmieniłem na żółty, żeby się wyróżniał
            y += 80

        # Opis (reszta linii)
        for line in lines[1:]:
            # Proste zawijanie tekstu: jeśli linia jest za długa, można by ją dzielić, 
            # ale na razie renderujemy linia po linii.
            txt_surf = font_text.render(line, True, (200,200,200))
            screen.blit(txt_surf, (120, y))
            y += 35

        info = font_text.render("Kliknij dowolny klawisz lub przycisk myszy, aby wrócić", True, (120,120,120))
        screen.blit(info, (120, screen.get_height()-80))
    def draw_building_template(self, screen, title, lines, theme_color=(100, 100, 130), border_color=(180, 180, 220)):
        # Ogólny zarys każdego budynku w zamku
        # 1. Tło ogólne
        screen.fill((60, 60, 80))

        # 2. Czcionki (najlepiej zdefiniuj je raz w __init__ jako self.font_title itd.)
        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        # 3. Panel środkowy
        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, theme_color, panel)
        pygame.draw.rect(screen, border_color, panel, 6)

        # 4. Tytuł (zawsze wycentrowany)
        title_surface = font_title.render(title.upper(), True, border_color)
        screen.blit(title_surface, (panel.centerx - title_surface.get_width() // 2, panel.y - 40))

        # 5. Tekst (automatyczne linie)
        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # 6. Stopka (Twoje przyciski)
        self.world.draw_building_footer(screen)

    def draw_ui(self, screen):

        # 2. DOLNY PANEL ARMII (Tylko dla 2+ jednostek)
        u = self.world.selected_unit
        if u:
            garrison = getattr(u, 'garrison', [])
            display_units = [unit for unit in ([u] + garrison) if unit is not None]

            # Rysujemy sloty armii TYLKO jeśli jest grupa
            if len(display_units) >= 2:
                panel_rect = pygame.Rect(0, 610, 1024, 158)
                pygame.draw.rect(screen, (30, 20, 10), panel_rect) 
                pygame.draw.rect(screen, (100, 80, 60), panel_rect, 2)

                if not hasattr(self, 'army_slot_rects'):
                    self.army_slot_rects = [pygame.Rect(10 + i * 75, 620, 70, 140) for i in range(10)]

                for i in range(10):
                    rect = self.army_slot_rects[i]
                    pygame.draw.rect(screen, (60, 40, 30), rect)
                    pygame.draw.rect(screen, (150, 130, 100), rect, 1)

                    if i < len(display_units):
                        unit = display_units[i]
                        name_txt = self.font_small.render(str(unit.type), True, (255, 255, 255))
                        count = getattr(unit, 'count', 1)
                        count_txt = self.font_small.render(str(count), True, (255, 255, 0))
                        screen.blit(name_txt, (rect.x + 5, rect.y + 120))
                        screen.blit(count_txt, (rect.x + 5, rect.y + 100))

        # 3. PRZYCISKI AKCJI (Zawsze widoczne na ekranie)
        # Wyciągnięte poza "if u:", więc będą widoczne od startu gry
        self.draw_bottom_bar(screen)
    