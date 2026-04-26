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
        self.active_dropdown = None
        self.show_top_ui = False
        self.top_ui_full_area = pygame.Rect(0, 0, 1024, 55)

    def draw(self, screen):
        w = self.world
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
            self.draw_trap_popup(screen)

        elif w.screen == "castle":
            self.draw_castle_interface(screen, self.world)
            if getattr(w, "menu_open", False):
                mx, my = pygame.mouse.get_pos()
                self.draw_castle_menu(screen, mx, my)

        # --- TUTAJ BYŁ BŁĄD. Zmienione wszystkie "b" na "w" ---
        elif w.screen in ("garrison", "Strażnica"):
            if w.selected_castle and getattr(w.selected_castle, 'building_type', "") == "Strażnica":
                self.draw_garrison_only(screen)
            else:
                self.draw_garrison(screen)

        elif w.screen == "recruitment":
            w.recruitment_manager.draw(screen)

        elif w.screen == "court":
            w.court.draw_court(screen)

        elif w.screen == "peasants":
            self.draw_peasants(screen)

        elif w.screen in ["forge", "workshop", "hospital", "school"]:
            draw_func = getattr(w, f"draw_{w.screen}", None)
            if draw_func:
                draw_func(screen)

        elif w.screen == "unit_info":
            self.draw_unit_info(screen, w)

        # Nakładka statystyk jednostki
        if getattr(w, 'inspected_unit', None):
            stats_x = 300 if w.screen == "garrison" else 150
            stats_y = 380 if w.screen == "garrison" else 200
            self.draw_unit_stats_table(screen, stats_x, stats_y,
                                    w.inspected_unit.type, w.inspected_unit)

        if getattr(w, "demolish_confirm", False):
            self.draw_demolish_confirm(screen)

    def draw_map(self, screen):
        w = self.world

        # Teren
        self.gfx.draw_terrain(screen, self.world)
        # Siatka
        if getattr(w, 'show_grid', False):
            self.draw_grid_lines(screen)

        # Zamki
        for castle in w.castles:
            self.draw_castle_on_map(screen, castle)

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
            self.draw_road_arrows(screen)

        # Podgląd zasięgu pułapki
        if getattr(w, 'trap_build_mode', False):
            self.draw_build_system(screen)

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
    
    def draw_castle_interface(self, screen, world):
        """Rysuje interfejs zamku. Wywoływane z Renderera, dane pobiera z world."""
        castle = world.selected_castle
        if not castle: 
            return
        
        # Pobieramy aktualną pozycję myszy
        mx, my = pygame.mouse.get_pos()

        # --- WARSTWA 1: DYNAMICZNA GRAFIKA ZAMKU ---
        # Zmieniamy self na world, bo tam siedzi castle_gfx
        if hasattr(world, 'castle_gfx'):
            world.castle_gfx.draw(screen, castle)
        else:
            screen.fill((60, 50, 40))

        # --- WARSTWA 3: STAŁY INTERFEJS ---
        font = pygame.font.SysFont(None, 28)
        title = font.render(f"{castle.building_type.upper()}", True, (255, 255, 255))
        screen.blit(title, (40, 40))

        # Przyciski funkcyjne
        if castle.building_type == "Zamek":
            # Definiujemy rect (możesz go trzymać w world lub rendererze, tutaj zakładam world)
            world.peasant_button = pygame.Rect(screen.get_width() - 200, screen.get_height() - 110, 160, 40)
            # Używamy self.draw_button, bo jesteśmy w Rendererze!
            self.draw_button(screen, "CHŁOPI", world.peasant_button, (160, 140, 60))

        # Debugowanie masek (world.castle_gfx i flaga z world)
        if hasattr(world, 'castle_gfx'):
            world.castle_gfx.draw(screen, castle, debug_mode=getattr(world, 'debug_show_masks', False))

        # --- WARSTWA 4: SYSTEM MENU ---
        mouse_over_ui = False
        
        # Sprawdzamy kolizję z przyciskiem (wszystkie recty są w world)
        if world.menu_button.collidepoint(mx, my):
            world.menu_open = True
            mouse_over_ui = True

        if getattr(world, 'menu_open', False):
            # Wywołujemy rysowanie menu (zakładam, że draw_castle_menu też jest w Rendererze)
            self.draw_castle_menu(screen, mx, my)
            
            # Sprawdzamy czy mysz jest nad opcjami menu
            for rect in world.menu_rects.values():
                if rect.collidepoint(mx, my): mouse_over_ui = True
            
            if getattr(world, 'build_open', False):
                for rect in world.build_rects.values():
                    if rect.collidepoint(mx, my): mouse_over_ui = True
            
            # Mostek bezpieczeństwa
            bridge_rect = pygame.Rect(world.menu_button.x - 20, world.menu_button.y, 30, 200)
            if bridge_rect.collidepoint(mx, my): mouse_over_ui = True

        # Logika zamykania menu (zmienia stan w world)
        if not mouse_over_ui:
            world.menu_open = False
            world.build_open = False

        # Rysujemy sam przycisk MENU
        self.draw_button(screen, "MENU", world.menu_button)

        # 6. STOPKA (zakładam, że ta funkcja też jest w Rendererze)
        self.draw_building_footer(screen)

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
        
        # Zmieniamy self. na self.world. przy grafikach i timerze!
        if style == "castle":
            img = self.world.back_img_castle_pressed if getattr(self.world, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.world.back_anim_timer < 500 \
                else self.world.back_img_castle_normal
            screen.blit(img, rect.topleft)
            return

        if style == "bldg":
            img = self.world.back_img_bldg_pressed if getattr(self.world, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.world.back_anim_timer < 500 \
                else self.world.back_img_bldg_normal
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
        mx, my = pygame.mouse.get_pos()
        m_pressed = pygame.mouse.get_pressed()[0] 
        w = self.world

        is_building = getattr(w, 'build_menu_open', False)
        current_icons = self.gfx.build_button_images if is_building else self.gfx.button_images

        for i, rect in enumerate(w.action_buttons):
            base_index = i * 2 
            img_index = base_index # Domyślnie NIEWCIŚNIĘTY
            
            is_hover = rect.collidepoint(mx, my)
            is_clicked = is_hover and m_pressed
            
            # --- ZARZĄDZANIE STANEM WCIŚNIĘCIA ---
            if is_building:
                # MENU BUDOWNICZEGO
                if i == 0 and getattr(w, 'road_build_mode', False):
                    img_index = base_index + 1 # Droga trwale wciśnięta
                elif i == 1 and getattr(w, 'trap_build_mode', False):
                    img_index = base_index + 1 # Pułapka trwale wciśnięta
                elif is_clicked:
                    img_index = base_index + 1 # Zwykłe kliknięcie (np. dla Zamku)
            else:
                # GŁÓWNE MENU (Kula / Namiot)
                if i == 0:
                    # Przycisk Trybu: Namiot (zaznaczona jednostka) lub Kula (brak jednostki)
                    if w.selected_unit is not None:
                        img_index = base_index + 1 # Pokazuje wciśnięty Namiot
                    else:
                        img_index = base_index     # Pokazuje odciśniętą Kulę ziemską
                elif i == 3 and getattr(w, 'merge_mode', False):
                    img_index = base_index + 1 # Połącz oddziały wciśnięte
                elif is_clicked:
                    img_index = base_index + 1

            # Zabezpieczenie
            if img_index >= len(current_icons):
                img_index = base_index
            
            image = current_icons[img_index]
            scaled_img = pygame.transform.scale(image, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)
            
    def draw_army_panel(self, screen):
        u = self.world.selected_unit
        if not u:
            return # Nie rysujemy, jeśli nic nie jest wybrane

        # Zbieramy jednostki do jednej listy
        garrison = getattr(u, 'garrison', [])
        display_units = [unit for unit in ([u] + garrison) if unit is not None]

        # Pokazujemy panel TYLKO jeśli to armia (minimum 2 oddziały)
        if len(display_units) >= 2:
            # Zakładam, że Twoje przyciski akcji zaczynają się od x=800
            # Więc panel armii zajmuje lewą stronę: od x=0 do x=800, od y=620 w dół
            panel_rect = pygame.Rect(0, 620, 800, 148) 
            
            # 1. Rysowanie drewnianego tła (Kafelkowanie MARKS_S32_35)
            bg_w = self.gfx.army_panel_bg.get_width()
            bg_h = self.gfx.army_panel_bg.get_height()
            
            for x in range(panel_rect.x, panel_rect.right, bg_w):
                for y in range(panel_rect.y, panel_rect.bottom, bg_h):
                    screen.blit(self.gfx.army_panel_bg, (x, y))

            # 2. Rysowanie slotów i ikon jednostek
            self.world.army_slot_rects = [] # Zapisujemy recty, żeby można było w nie klikać
            margin_x, margin_y = 20, 20
            slot_size = 50 # Przykładowy rozmiar ikony jednostki
            
            for i, unit in enumerate(display_units):
                # Obliczanie pozycji (np. w dwóch rzędach, tak jak na zdjęciu)
                col = i % 10 # Maksymalnie 10 jednostek w rzędzie
                row = i // 10
                
                slot_x = panel_rect.x + margin_x + col * (slot_size + 15)
                slot_y = panel_rect.y + margin_y + row * (slot_size + 20)
                
                slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
                self.world.army_slot_rects.append(slot_rect) # Zapisujemy dla handle_ui_click

                # Tutaj wywołujesz swoją funkcję rysującą ikonkę jednostki
                # np.: screen.blit(unit.image, (slot_x, slot_y))
                # Zastąp to tym, czego używasz do rysowania ikonek!
                pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2) # Pomocnicza ramka                

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
        self.draw_building_footer(screen)

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
    
    def draw_unit_info(self, screen, w):
        """Rysuje ekran z historycznym opisem jednostki (INFO)."""
        screen.fill((20, 20, 20))
        
        # Zabezpieczenie, gdyby tekst był pusty
        if not hasattr(w, 'unit_info_text') or not w.unit_info_text:
            w.unit_info_text = "Brak informacji\nNie wybrano jednostki."

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 28)

        lines = w.unit_info_text.split("\n")
        y = 120

        # Nagłówek (pierwsza linia na żółto)
        if lines:
            screen.blit(font_title.render(lines[0], True, (255, 255, 0)), (120, y))
            y += 80

        # Opis (reszta tekstu na szaro)
        for line in lines[1:]:
            txt_surf = font_text.render(line, True, (200, 200, 200))
            screen.blit(txt_surf, (120, y))
            y += 35

        # Informacja o powrocie na dole ekranu
        info = font_text.render("Kliknij dowolny klawisz lub przycisk myszy, aby wrócić", True, (120, 120, 120))
        screen.blit(info, (120, screen.get_height() - 80))
    
    def draw_garrison(self, screen):
        w = self.world
        castle = w.selected_castle
        if not castle: return

        slot_rects = w.garrison_gfx.draw(
            screen, castle,
            w.selected_units,
            w.inspected_unit
        )
        # Zapisujemy recty do świata
        w.garrison_slot_rects = slot_rects

        # Przyciski funkcyjne
        built = [b.lower() for b in castle.buildings]
        if "koszary" in built:
            self.draw_button(screen, "RECRUIT", w.recruit_button, (240, 120, 20))
        if "hospital" in built:
            self.draw_button(screen, "HEAL", w.heal_button, (80, 160, 80))
        if "school" in built:
            self.draw_button(screen, "TRAIN", w.train_button, (160, 160, 80))
            
        self.draw_button(screen, "WYPUŚĆ", w.button_send_army, (160, 120, 60))
        self.draw_building_footer(screen)
  
    def draw_castle_on_map(self, screen, castle):
        w = self.world
        TILE_SIZE = 32
        px = int(castle.x * TILE_SIZE) - w.camera_x
        py = int(castle.y * TILE_SIZE) - w.camera_y
        
        # Optymalizacja
        screen_w, screen_h = screen.get_size()
        if px < -100 or px > screen_w + 100 or py < -100 or py > screen_h + 100:
            return

        is_tower = getattr(castle, 'building_type', 'Zamek') == "Strażnica"
        
        if getattr(castle, 'destroyed', False):
            s_idx = 4
        elif getattr(castle, 'under_construction', False):
            s_idx = 0 
        else:
            s_idx = 3 

        if is_tower:
            img = w.tower_tiles.get(s_idx)
            if img:
                screen.blit(img, (px, py))
        else:
            tiles = w.castle_tiles.get(s_idx, [])
            if len(tiles) == 4:
                offsets = [(0,0), (1,0), (0,1), (1,1)]
                for i in range(4):
                    dx, dy = offsets[i]
                    screen.blit(tiles[i], (px + dx*TILE_SIZE, py + dy*TILE_SIZE))
     
    def draw_unit_stats_table(self, screen, x, y, unit_name, stats_source):
        w = self.world
        
        # --- BLOKADA: Rysuj globalne okienko TYLKO na mapie ---
        # Jeśli jesteśmy w koszarach, garnizonie lub menu, przerywamy funkcję!
        if getattr(w, 'screen', "map") != "map":
            return

        if not stats_source:
            return

        u_type = getattr(stats_source, 'type_code', None)
        if not u_type and isinstance(stats_source, dict):
            u_type = stats_source.get('type_code') 

        mode = "COMBAT"
        if u_type in ["GOLD", "PEAS", "SPECK", "SPECM"]:
            mode = "SIMPLE"

        w.unit_info_window.draw(screen, x, y, stats_source, mode)
                
    def draw_peasants(self, screen):
        w = self.world
        font = pygame.font.SysFont(None, 24)

        castle = w.selected_castle
        if not castle:
            return

        screen_w = screen.get_width()
        screen_h = screen.get_height()

        happiness_factor = 0.5 + (castle.happiness / 100) * 0.5
        tax_income = int(castle.peasants * 0.1 * castle.tax_rate * happiness_factor)

        screen.blit(font.render(f"Peasants: {castle.peasants}", True, (255,255,255)), (screen_w//2 - 60, 20))
        screen.blit(font.render(f"Happiness: {castle.happiness}%", True, (200,255,200)), (screen_w//2 - 70, 45))
        screen.blit(font.render(f"Gold: {castle.gold}", True, (255,215,0)), (screen_w - 120, 20))

        screen.blit(font.render("TAX", True, (255,255,255)), (60, screen_h//2 - 80))
        screen.blit(font.render(f"{castle.tax_rate:.1f}", True, (255,255,255)), (70, screen_h//2 - 20))
        screen.blit(font.render(f"+{tax_income}/turn", True, (255,255,0)), (40, screen_h//2 + 10))

        w.tax_minus_button.topleft = (20, screen_h//2 - 40)
        w.tax_plus_button.topleft = (140, screen_h//2 - 40)

        pygame.draw.rect(screen, (120,120,120), w.tax_minus_button)
        pygame.draw.rect(screen, (120,120,120), w.tax_plus_button)

        screen.blit(font.render("-", True, (0,0,0)), w.tax_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), w.tax_plus_button.move(12,5))

        panel_rect = pygame.Rect(screen_w//2 - 150, screen_h//2 - 60, 300, 120)
        pygame.draw.rect(screen, (70,50,40), panel_rect)

        owned = [c for c in w.castles if c.owner == w.players[w.current_player] and not getattr(c, 'destroyed', False)]
        visible = owned[w.castle_list_offset : w.castle_list_offset+3]

        for i, c in enumerate(visible):
            txt = f"Castle ({c.x},{c.y})  P:{c.peasants} G:{c.gold}"
            screen.blit(font.render(txt, True, (255,255,255)), (screen_w//2 - 130, screen_h//2 - 40 + i*30))

        w.castle_up_button.topleft = (screen_w//2 + 160, screen_h//2 - 60)
        w.castle_down_button.topleft = (screen_w//2 + 160, screen_h//2)

        pygame.draw.rect(screen,(120,120,120),w.castle_up_button)
        pygame.draw.rect(screen,(120,120,120),w.castle_down_button)

        screen.blit(font.render("^",True,(255,255,255)), w.castle_up_button.move(12,5))
        screen.blit(font.render("v",True,(255,255,255)), w.castle_down_button.move(12,5))

        w.peasants_minus_button.topleft = (screen_w - 180, screen_h//2 - 40)
        w.peasants_plus_button.topleft = (screen_w - 140, screen_h//2 - 40)

        w.gold_minus_button.topleft = (screen_w - 180, screen_h//2 + 10)
        w.gold_plus_button.topleft = (screen_w - 140, screen_h//2 + 10)

        w.send_button.center = (screen_w - 120, screen_h//2 + 80)

        pygame.draw.rect(screen, (120,120,120), w.peasants_minus_button)
        pygame.draw.rect(screen, (120,120,120), w.peasants_plus_button)
        pygame.draw.rect(screen, (120,120,120), w.gold_minus_button)
        pygame.draw.rect(screen, (120,120,120), w.gold_plus_button)
        pygame.draw.rect(screen, (80,140,80), w.send_button)

        screen.blit(font.render("-", True, (0,0,0)), w.peasants_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), w.peasants_plus_button.move(12,5))
        screen.blit(font.render("-", True, (0,0,0)), w.gold_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), w.gold_plus_button.move(12,5))
        screen.blit(font.render("SEND", True, (255,255,255)), w.send_button.move(30,10))
        screen.blit(font.render(f"P: {w.send_peasants_amount}", True, (255,255,255)), (screen_w-120, screen_h//2 - 60))
        screen.blit(font.render(f"G: {w.send_gold_amount}", True, (255,255,0)), (screen_w-120, screen_h//2 - 15))

        self.draw_building_footer(screen)

    def draw_demolish_confirm(self, screen):
        w = self.world
        font = pygame.font.SysFont(None, 28)
        win_w, win_h = 320, 160
        win_x = (screen.get_width() // 2) - (win_w // 2)
        win_y = (screen.get_height() // 2) - (win_h // 2)
        
        rect = pygame.Rect(win_x, win_y, win_w, win_h)
        pygame.draw.rect(screen, (40, 40, 40), rect) 
        pygame.draw.rect(screen, (255, 0, 0), rect, 2) 

        text = font.render("Zburzyć ten zamek?", True, (255, 255, 255))
        screen.blit(text, (win_x + 60, win_y + 30))

        w.demolish_yes = pygame.Rect(win_x + 40, win_y + 90, 100, 40)
        w.demolish_no = pygame.Rect(win_x + 180, win_y + 90, 100, 40)

        pygame.draw.rect(screen, (0, 150, 0), w.demolish_yes) 
        pygame.draw.rect(screen, (150, 0, 0), w.demolish_no)  

        screen.blit(font.render("TAK", True, (255,255,255)), (win_x + 70, win_y + 100))
        screen.blit(font.render("NIE", True, (255,255,255)), (win_x + 210, win_y + 100))
        
    def draw_castle_menu(self, screen, mx, my):
        w = self.world
        if w.screen != "castle":
            return 

        options = ["Buduj", "ZBURZ ZAMEK", "ROZBUDUJ MURY"]
        w.menu_rects.clear()

        menu_w, menu_h = 180, 35
        menu_x = w.menu_button.x
        menu_y = w.menu_button.y + 40

        for i, opt in enumerate(options):
            rect = pygame.Rect(menu_x, menu_y + i * menu_h, menu_w, menu_h)
            self.draw_button(screen, opt, rect)
            w.menu_rects[opt] = rect

        w.demolish_button = w.menu_rects.get("ZBURZ ZAMEK")
        w.wall_button = w.menu_rects.get("ROZBUDUJ MURY")

        buduj_rect = w.menu_rects.get("Buduj")
        if not buduj_rect: return
        
        safe_zone_to_submenu = pygame.Rect(menu_x - 165, menu_y, 170, 200)

        if buduj_rect.collidepoint(mx, my) or (getattr(w, "build_open", False) and safe_zone_to_submenu.collidepoint(mx, my)):
            w.build_open = True
            self.draw_build_submenu(screen, menu_x, menu_y)
        else:
            if mx > menu_x: 
                w.build_open = False
        
    def draw_build_submenu(self, screen, menu_x, menu_y):
        w = self.world
        castle = w.selected_castle
        if not castle: return

        sub_w, sub_h = 160, 40 
        sub_x = menu_x - sub_w
        sub_y = menu_y

        buildings = ["hospital", "school", "koszary", "forge", "workshop"]
        w.build_rects.clear()

        for i, b in enumerate(buildings):
            rect = pygame.Rect(sub_x, sub_y + i * sub_h, sub_w, sub_h)
            is_built = b in castle.buildings
            
            if is_built:
                pygame.draw.rect(screen, (50, 50, 50), rect) 
                pygame.draw.rect(screen, (80, 80, 80), rect, 1) 
                small_font = pygame.font.SysFont(None, 20)
                txt_surf = small_font.render(b, True, (100, 100, 100)) 
                screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
            else:
                self.draw_button(screen, b, rect)

            w.build_rects[b] = rect
    
    def draw_trap_popup(self, screen):
        w = self.world
        font = getattr(self, 'font', pygame.font.SysFont(None, 32))
        
        screen_w, screen_h = screen.get_size()
        box_w, box_h = 300, 200
        x = (screen_w - box_w) // 2
        y = (screen_h - box_h) // 2
        
        popup_rect = pygame.Rect(x, y, box_w, box_h)
        
        pygame.draw.rect(screen, (50, 50, 50), popup_rect) 
        pygame.draw.rect(screen, (255, 255, 255), popup_rect, 3) 
        
        title = font.render("PUŁAPKA", True, (255, 255, 255))
        screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 20))
        
        w.btn_trap_stop = pygame.Rect(x + 20, y + 100, 110, 50)
        w.btn_trap_dalej = pygame.Rect(x + 170, y + 100, 110, 50)
        
        pygame.draw.rect(screen, (150, 0, 0), w.btn_trap_stop) 
        pygame.draw.rect(screen, (0, 150, 0), w.btn_trap_dalej) 
        
        stop_txt = font.render("STOP", True, (255, 255, 255))
        dalej_txt = font.render("DALEJ", True, (255, 255, 255))
        
        screen.blit(stop_txt, (w.btn_trap_stop.centerx - stop_txt.get_width()//2, w.btn_trap_stop.centery - stop_txt.get_height()//2))
        screen.blit(dalej_txt, (w.btn_trap_dalej.centerx - dalej_txt.get_width()//2, w.btn_trap_dalej.centery - dalej_txt.get_height()//2))
    
    def draw_garrison_only(self, screen):
        w = self.world
        castle = w.selected_castle
        if not castle:
            w.screen = "map" 
            return

        screen.fill((30, 30, 35)) 
        font = pygame.font.SysFont(None, 32)
        
        title = font.render(f"GARNIZON: {castle.building_type.upper()}", True, (200, 200, 200))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        start_x = 150
        start_y = 200
        gap = 20
        slot_size = 120

        for i in range(10): 
            col = i % 5
            row = i // 5
            slot_rect = pygame.Rect(150 + col * 140, 200 + row * 140, 120, 120)
            
            pygame.draw.rect(screen, (50, 50, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
            
            if i < len(castle.garrison) and castle.garrison[i]:
                unit = castle.garrison[i]
                u_txt = font.render(unit.type[:5], True, (255, 255, 255))
                screen.blit(u_txt, (slot_rect.centerx - u_txt.get_width()//2, 
                                    slot_rect.centery - u_txt.get_height()//2))

                if unit in w.selected_units:
                    pygame.draw.rect(screen, (0, 255, 0), slot_rect, 4) 

        self.draw_building_footer(screen)

        w.release_tower = pygame.Rect(screen.get_width()//2 - 80, 650, 160, 45)
        self.draw_button(screen, "RELEASE", w.release_tower)
        
        w.destroy_button = pygame.Rect(screen.get_width()//2 + 90, 650, 160, 45)
        pygame.draw.rect(screen, (150, 0, 0), w.destroy_button)
        txt = font.render("ZNISZCZ", True, (255, 255, 255))
        screen.blit(txt, (w.destroy_button.centerx - txt.get_width()//2, 
                          w.destroy_button.centery - txt.get_height()//2))

    def draw_building_footer(self, screen):
        w = self.world
        if w.screen == "castle":
            self.draw_button(screen, "", w.back_button_castle, style="castle")
        else:
            self.draw_button(screen, "", w.back_button_bldg, style="bldg")

        if w.selected_castle and getattr(w.selected_castle, 'building_type', "") == "Strażnica":
            self.draw_button(screen, "ZBURZ", w.destroy_button, (100, 40, 40))

        if w.screen == "garrison":                         
            pass  

    def draw_build_system(self, screen):
        w = self.world
        if w.selected_unit and w.selected_unit.type == "Budowniczy":
            if hasattr(self, 'draw_grid_lines'):
                self.draw_grid_lines(screen)
            
            mx, my = pygame.mouse.get_pos()
            TILE_SIZE = 32
            gx = (mx + w.camera_x) // TILE_SIZE
            gy = (my + w.camera_y) // TILE_SIZE
            
            draw_x = gx * TILE_SIZE - w.camera_x
            draw_y = gy * TILE_SIZE - w.camera_y
            
            u = w.selected_unit
            dist_x = abs(gx - u.x)
            dist_y = abs(gy - u.y)
            
            is_in_range = dist_x <= 1 and dist_y <= 1 and not (dist_x == 0 and dist_y == 0)
            
            # Zapytania do świata/mapy:
            is_foundation = w.pathfinder.is_area_occupied_by_foundation(gx, gy)
            is_valid_terrain = w.pathfinder.can_build_trap(gx, gy) and not is_foundation

            preview_rect = pygame.Rect(draw_x, draw_y, TILE_SIZE, TILE_SIZE)

            if is_in_range and is_valid_terrain:
                pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2)
            else:
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill((255, 0, 0, 80)) 
                
                for dx in range(4, TILE_SIZE, 8):
                    for dy in range(4, TILE_SIZE, 8):
                        pygame.draw.circle(s, (150, 0, 0), (dx, dy), 1)
                
                screen.blit(s, (draw_x, draw_y))
                pygame.draw.rect(screen, (255, 0, 0), preview_rect, 2)

    def draw_road_arrows(self, screen):
        w = self.world
        u = w.selected_unit
        if not u:
            return

        # ZMIANA: Zwracamy się do obiektu pathfinder wewnątrz świata
        if getattr(w.pathfinder.__class__, '_arrow_imgs', None) is None:
            if hasattr(w.pathfinder, '_load_arrows'):
                w.pathfinder._load_arrows()

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            tx, ty = u.x + dx, u.y + dy
            
            # ZMIANA: Pytamy Pathfindera, czy można budować
            if not w.pathfinder.can_build_road(tx, ty):
                continue

            pos_x = tx * TILE_SIZE - w.camera_x
            pos_y = ty * TILE_SIZE - w.camera_y

            if pos_x < -TILE_SIZE or pos_x > SCREEN_WIDTH or \
               pos_y < -TILE_SIZE or pos_y > SCREEN_HEIGHT:
                continue

            # Rysowanie grafiki z pamięci Pathfindera
            img = w.pathfinder.__class__._arrow_imgs.get((dx, dy))
            if img:
                offset_x = (TILE_SIZE - img.get_width())  // 2
                offset_y = (TILE_SIZE - img.get_height()) // 2
                screen.blit(img, (pos_x + offset_x, pos_y + offset_y))


    # -------------------------------------------------------
    # RYSOWANIE TRASY — STOPY zamiast kropek
    # -------------------------------------------------------

    def draw_path_dots(self, screen, unit, path):
        w = self.world

        # ZMIANA: Sprawdzamy i ładujemy przez w.pathfinder
        if getattr(w.pathfinder.__class__, '_step_imgs', None) is None:
            if hasattr(w.pathfinder, '_load_steps'):
                w.pathfinder._load_steps()

        # Zabezpieczone pobieranie słowników z obrazkami
        step_imgs = getattr(w.pathfinder.__class__, '_step_imgs', {})
        black_imgs = step_imgs.get("black", {}) if step_imgs else {}
        red_imgs   = step_imgs.get("red", {}) if step_imgs else {}

        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0

        for px, py in path:
            dx = px - current_x
            dy = py - current_y

            # Koszt kroku
            tile_char = w.map[py][px]
            base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
            move_mod  = 1.41 if (dx != 0 and dy != 0) else 1.0
            accumulated_cost += base_cost * move_mod

            # Pozycja na ekranie — środek kafla
            screen_x = px * TILE_SIZE + TILE_SIZE // 2 - w.camera_x
            screen_y = py * TILE_SIZE + TILE_SIZE // 2 - w.camera_y

            # Poza ekranem — pomijamy
            margin = TILE_SIZE * 2
            if not (-margin < screen_x < SCREEN_WIDTH  + margin and
                    -margin < screen_y < SCREEN_HEIGHT + margin):
                current_x, current_y = px, py
                continue

            # Kierunek → normalizujemy do -1/0/1
            direction = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))

            in_range = accumulated_cost <= unit.move_points
            img      = (black_imgs if in_range else red_imgs).get(direction)

            if img:
                blit_x = screen_x - img.get_width()  // 2
                blit_y = screen_y - img.get_height() // 2
                screen.blit(img, (blit_x, blit_y))
            else:
                # Fallback: stare kółka (w razie braku grafiki dla danego kierunku)
                color = (0, 0, 0) if in_range else (255, 0, 0)
                pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), 5)
                pygame.draw.circle(screen, color,           (screen_x, screen_y), 4)

            current_x, current_y = px, py

        # -------------------------------------------------------
    # RYSOWANIE BUDYNKÓW (teksty opisowe)
    # -------------------------------------------------------

    def draw_forge(self, screen):
        lines = [
            "Dzień i noc słychać rytmiczne uderzenia żelaznych młotów –",
            "to ławrowni kowale w pocie czoła pokuwają bojowe rumaki.",
            "Dzięki ich wysiłkom będziesz mógł rozpocząć produkcję",
            "oddziałów konnych, bardzo przydatnych w bojowych zmaganiach.",
            "",
            "Jednocześnie łowisarze z górskich krain wytapiają tu stal",
            "na pancerze i wytwarzają broń palną.",
        ]
        self.draw_building_template(screen, "Kuźnia", lines,
                                    (120, 90, 60), (200, 170, 90))

    def draw_workshop(self, screen):
        lines = [
            "Pracują tu znakomici rzemieślnicy ze starego kraju.",
            "Dzięki ich kunsztowi staniesz się posiadaczem łuków, kusz,",
            "oszczepów oraz strzał niespotykanych wcześniej w tej części",
            "kontynentu.",
        ]
        self.draw_building_template(screen, "Warsztat", lines)

    def draw_hospital(self, screen):
        lines = [
            "Zapach rozcieranych ziół da się odczuć we wszystkich zakamarkach.",
            "Powstające tu specyfiki i mikstury robione są według starych receptur.",
            "Owe lekarstwa pomogą odzyskać Twoim rycerzom pełnię sił.",
            "Ponadto troskliwi kapłani roztoczyli swą opiekę nad wsiami.",
        ]
        self.draw_building_template(screen, "Szpital", lines)

    def draw_school(self, screen):
        lines = [
            "Dzięki wykładanym tu naukom możliwe będzie szkolenie",
            "Twoich wojsk w rzemiośle rycerskim.",
            "",
            "Ponadto uczeni waldzcy umożliwią osiągnięcie wyższego",
            "poziomu technologii w Twoim królestwie.",
        ]
        self.draw_building_template(screen, "Szkoła", lines)

    def draw_building_template(self, screen, title, lines,
                                theme_color=(100, 100, 130),
                                border_color=(180, 180, 220)):
        screen.fill((60, 60, 80))
        font_title = pygame.font.SysFont(None, 48)
        font_text  = pygame.font.SysFont(None, 24)

        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, theme_color, panel)
        pygame.draw.rect(screen, border_color, panel, 6)

        title_surface = font_title.render(title.upper(), True, border_color)
        screen.blit(title_surface,
                    (panel.centerx - title_surface.get_width() // 2, panel.y - 40))

        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        self.draw_building_footer(screen)        

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])