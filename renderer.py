import pygame
import os
import random
from settings import TERRAIN_TYPES, TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from buildings import BuildingsMixin

from utils import draw_text
from custom_font import BitmapFont
class Renderer:
    def __init__(self, world_instance, gfx, ):
        self.custom_font = BitmapFont("assets/minimum/RED_S32/") # Ścieżka do Twoich plików RED_S32_
        # 1. Definiujesz swoją paletę z posta (Złota)
        GOLDEN_COLOR_MAP = {
            (255, 255, 255, 255): (0, 0, 0, 255),
            (10, 0, 0, 255): (36, 24, 16, 255),
            (33, 17, 0, 255): (215, 203, 158, 255),
            (16, 48, 0, 255): (24, 16, 12, 255),
            (66, 57, 0, 255): (16, 8, 0, 255),
            (0, 0, 0, 255): (69, 56, 48, 255),
            (18, 9, 0, 255): (255, 243, 199, 255),
            (43, 31, 0, 255): (154, 142, 105, 255),
            (26, 57, 0, 255): (255, 243, 199, 255),
            (69, 56, 48, 255): (89, 65, 69, 255)
            # USUNĄŁEM OSTATNI KLUCZ (66, 57, 0, 255), bo powtarzał się z tym wyżej 
            # (w słowniku klucz musi być unikalny)
        }
        # 2. Generujesz gotowe literki pod nazwą 'golden'
        self.custom_font.add_palette("golden", GOLDEN_COLOR_MAP)
        
        # W PRZYSZŁOŚCI MOŻESZ DODAĆ KOLEJNĄ:
        # self.custom_font.add_palette("evil_red", RED_COLOR_MAP)

        self.world = world_instance
        self.world.renderer = self  # <--- To pozwala jednostce narysować krok podczas marszu!
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
        self.img_army_slots = pygame.image.load("assets//minimum/MARKS_S32/MARKS_S32_35.png").convert_alpha()
        # To jest pasek 12 slotów (384x32 px)
        # --- TŁO BUDYNKÓW INFO ---
        try:
            self.bldg_bg = pygame.image.load("assets/budynki_tlo.png").convert()
        except Exception as e:
            print(f"Błąd ładowania tła budynków: {e}")
            self.bldg_bg = None
            # --- GRAFIKI GÓRNEGO MENU (Pergaminy) ---
        try:
            self.top_bar_img = pygame.image.load(os.path.join("assets","minimum","MENU_S32", "MENU_S32_0.png")).convert_alpha()
            self.menu_bg_img = pygame.image.load(os.path.join("assets","minimum","MENU_S32", "MENU_S32_3.png")).convert_alpha()
            
            # Przywracamy naturalną przezroczystość pliku, żeby zachować pikselowy cień!
            self.menu_bottom_img = pygame.image.load(os.path.join("assets","minimum","MENU_S32", "MENU_S32_4.png")).convert_alpha()
            
        except Exception as e:
            print(f"Błąd ładowania grafik górnego menu: {e}")
            self.top_bar_img = None
            self.menu_bg_img = None
            self.menu_bottom_img = None

        # --- ŁADOWANIE ZNACZNIKÓW WIELKOŚCI ARMII (2 do 10) ---
        self.army_size_marks = {}
        for i in range(2, 11):
            # Plik MARKS_S32_7 to cyfra "2", MARKS_S32_8 to "3", itd.
            file_idx = i + 5
            sciezka = os.path.join("assets", "minimum", "MARKS_S32", f"MARKS_S32_{file_idx}.png")
            try:
                img = pygame.image.load(sciezka).convert_alpha()
                # Zmniejszamy je lekko do 18x18 pikseli, żeby idealnie pasowały nad kafelkiem
                self.army_size_marks[i] = pygame.transform.smoothscale(img, (12, 15))
            except Exception as e:
                print(f"Nie udało się załadować grafiki armii {i}: {e}")

        self.mark_red = pygame.image.load("assets/minimum/MARKS_S32/MARKS_S32_4.png").convert_alpha()
        self.mark_grey = pygame.image.load("assets/minimum/MARKS_S32/MARKS_S32_5.png").convert_alpha()

        # =========================================================
        # ŁADOWANIE KURSORÓW MAPY GŁÓWNEJ
        # =========================================================
        self.cursors = {}
        c_scale = 1.2 # Możesz zwiększyć/zmniejszyć kursory!
        
        def load_c(name):
            path = os.path.join("assets", "minimum", "MOUSE_S32", f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_size()
                return pygame.transform.smoothscale(img, (int(w * c_scale), int(h * c_scale)))
            return None

        # Numery dokładnie z Twojego opisu!
        self.cursors["mace"] = load_c("MOUSE_S32_2")          # 1. Buława
        self.cursors["sword"] = load_c("MOUSE_S32_3")         # 2. Zwykły Miecz
        self.cursors["attack"] = load_c("MOUSE_S32_4")        # 3. Skrzyżowane Miecze
        self.cursors["castle"] = load_c("MOUSE_S32_5")        # 4. Wejście do Zamku/Portu
        self.cursors["merge"] = load_c("MOUSE_S32_39")        # 5. Połączenie Jednostek
        self.cursors["attack_castle"] = load_c("MOUSE_S32_40")# 6. Atak na Zamek
        self.cursors["no_attack"] = load_c("MOUSE_S32_41")    # 7. Chłop nie może bić jednostki
        self.cursors["no_castle"] = load_c("MOUSE_S32_42")    # 8. Chłop nie zaatakuje Zamku
        self.cursors["no_temple"] = load_c("MOUSE_S32_43")    # 9. Chłop nie wejdzie do Świątyni
        # --- NOWOŚCI ---
        self.cursors["go"] = load_c("MOUSE_S32_51")           # 10. GO (Potwierdzenie ruchu)
        self.cursors["castle_anim"] = [load_c(f"MOUSE_S32_{i}") for i in range(31, 39)] # Animacja wchodzenia!

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

        # --- DODAJ TO: Stoper animacji przejścia do Koszar ---
        if getattr(w, 'prod_anim_timer', 0) > 0:
            elapsed = pygame.time.get_ticks() - w.prod_anim_timer
            if elapsed > 200:
                w.screen = "recruitment"
                w.recruitment_open = True
                w.recruitment_scroll = -2  
                w.selected_unit_type = 0   
                w.selected_patent_index = None
                w.prod_anim_timer = 0
                return
            
        if w.screen not in ["map", "Strażnica"]:
            screen.fill((30, 30, 30))

        # Rysujemy mapę pod ekranami które tego wymagają
        screens_with_bg = ["map", "trap_info", "unit_info", "forge", "workshop", "Strażnica"]
        if w.screen in screens_with_bg:
            self.draw_map(screen)

        # Wybieramy co rysować
        if w.screen == "map":
            self.draw_top_bar(screen)
            self.draw_ui(screen)
        
        elif w.screen == "temple_event":
            self.draw_map(screen) # Najpierw rysujemy mapę w tle
            self.draw_temple_event(screen) # Na to nakładamy nasz pergamin

        elif w.screen == "combat_setup":
            self.draw_map(screen) # Zostawiamy mapę w tle
            w.combat_menu.draw(screen, w, self.gfx) # Rysujemy nowe okno walki na wierzchu!

        # ---> DODAJ TEN BLOK <---
        elif w.screen == "combat_tactical":
            if hasattr(w, 'tactical_combat'):
                w.tactical_combat.draw(screen)
                
        elif w.screen == "trap_info":
            self.draw_top_bar(screen)
            self.draw_ui(screen)
            self.draw_trap_popup(screen)

        elif w.screen == "castle":
            self.draw_castle_interface(screen, self.world)
            if getattr(w, "menu_open", False):
                mx, my = pygame.mouse.get_pos()
                self.draw_castle_menu(screen, mx, my)

        # Rysowanie wnętrza budynków
        elif w.screen == "Strażnica":
            self.draw_watchtower_interior(screen, w)
            
        elif w.screen == "garrison":
            # Ten blok obsługuje stary ekran zamku (ze wszystkimi budynkami)
            self.draw_garrison(screen)

        elif w.screen == "recruitment":
            w.recruitment_manager.draw(screen)

        elif w.screen == "court":
            mx, my = pygame.mouse.get_pos()
            w.court_gfx.draw_screen(screen, w, mx, my)

        elif w.screen == "peasants":
            w.peasant_menu.draw(screen, w)

        elif w.screen in ["forge", "workshop", "hospital", "school"]:
            # ZMIANA Z getattr(w, ...) NA getattr(self, ...) !!!
            draw_func = getattr(self, f"draw_{w.screen}", None) 
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
        
        # Rysowanie okienka portu (na samym wierzchu)
        if getattr(w, 'inspected_port', None):
            self.draw_port_ui(screen)

        # =========================================================
        # RYSOWANIE KURSORA (Zawsze rysowany na samym końcu!)
        # =========================================================
        mx, my = pygame.mouse.get_pos()
        cursor_img = self.get_map_cursor(mx, my)
        
        if cursor_img:
            pygame.mouse.set_visible(False)
            screen.blit(cursor_img, (mx, my))
        else:
            # Upewniamy się, że jeśli funkcja zwraca None, wraca myszka Windows
            if w.screen not in ["combat_tactical"]:
                pygame.mouse.set_visible(True)

    def draw_map(self, screen):
        w = self.world

        # Teren
        self.gfx.draw_terrain(screen, self.world)
        # Place budowy (Na wierzchu nad trawą)
        self.gfx.draw_construction_sites(screen, self.world)
        # Siatka
        if getattr(w, 'show_grid', False):
            self.draw_grid_lines(screen)

        # Zamki
        for castle in w.castles:
            self.draw_castle_on_map(screen, castle)

        self.draw_ports_on_map(screen)

        # Jednostki
        unit_font = pygame.font.SysFont(None, 24)
        for u in w.units:
            if u.x < 0 or u.y < 0:
                continue
            px = int(u.x * TILE_SIZE) - w.camera_x
            py = int(u.y * TILE_SIZE) - w.camera_y

            # ========================================================
            # NOWY SYSTEM RYSOWANIA (PEŁNA ANIMACJA KIERUNKOWA)
            # ========================================================
            if hasattr(u, 'sprites') and len(u.sprites) == 64:
                # 1. Pobieramy kierunek bazowy (0, 8, 16, 24, 32, 40, 48, 56)
                base_frame = getattr(u, 'facing', 32)
                
                # 2. ZMIANA: Sprawdzamy czy jednostka FAKTYCZNIE się rusza (flaga z move_along_path)
                if getattr(u, 'is_moving', False):
                    anim_offset = (pygame.time.get_ticks() // 120) % 8
                    current_frame = base_frame + anim_offset
                else:
                    # Jednostka tylko sobie stoi lub gracz jej wyznacza ścieżkę
                    current_frame = base_frame 
                    
                # 3. ZMIANA: Usunięto podrzucanie jednostki do góry (-10). 
                # Dodano +2, aby idealnie osadzić jej stopy na środku kratki.
                img = u.sprites[current_frame]
                img_x = px + (TILE_SIZE - img.get_width()) // 2
                img_y = py + (TILE_SIZE - img.get_height()) // 2 + 2         
                
                #img_y = py + (TILE_SIZE - img.get_height()) // 2 - 10 # Jednostka jest trochę wyższa           

                #owner_color = u.owner.color if (u.owner and hasattr(u.owner, 'color')) else (200, 200, 200)
                # Kółko (elipsa) pod nogami
                #pygame.draw.ellipse(screen, owner_color, (px + 4, py + 22, 24, 10), 2)
                
                # Samo wojsko
                screen.blit(img, (img_x, img_y))
            else:
                # ========================================================
                # STARY SYSTEM (AWARYJNY) - Używany, gdy brakuje plików png
                # ========================================================
                owner_color = u.owner.color if (u.owner and hasattr(u.owner, 'color')) else (200, 200, 200)
                pygame.draw.rect(screen, owner_color, (px + 4, py + 4, 24, 24))

                label = getattr(u, 'short_name', str(u.type)[:2].upper())
                txt_surface = unit_font.render(label, True, (255, 255, 255))
                text_rect = txt_surface.get_rect(center=(px + 16, py + 16))
                pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(2, 2))
                screen.blit(txt_surface, text_rect)

            # Rysowanie białej ramki po zaznaczeniu
            if u == w.selected_unit:
                pygame.draw.rect(screen, (255, 255, 255), (px, py, TILE_SIZE, TILE_SIZE), 2)

            # ==========================================
            # ZNACZNIK ILOŚCI ARMII (Na swoim starym miejscu!)
            # ==========================================
            garrison = getattr(u, 'garrison', [])
            pasażerowie = [pas for pas in garrison if pas is not None]
            wielkosc_armii = len(pasażerowie) + 1 
            
            if wielkosc_armii >= 2:
                index_grafiki = min(wielkosc_armii, 10)
                znacznik = getattr(self, 'army_size_marks', {}).get(index_grafiki)
                if znacznik:
                    screen.blit(znacznik, (px + TILE_SIZE - 12, py - 8))

        # W funkcji draw_map, pod pętlą rysowania jednostek
        if hasattr(w, 'units_to_split') and len(w.units_to_split) > 0:
            self.draw_split_preview(screen)

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
        cam_x = int(w.camera_x)
        cam_y = int(w.camera_y)
        
        # 1. Obliczamy, nad którymi kafelkami (kolumnami i wierszami) wisi teraz kamera
        start_col = cam_x // TILE_SIZE
        end_col = (cam_x + SCREEN_WIDTH) // TILE_SIZE + 1
        
        start_row = cam_y // TILE_SIZE
        end_row = (cam_y + SCREEN_HEIGHT) // TILE_SIZE + 1
        
        # 2. Rysujemy PIONOWE linie bazując dokładnie na pozycji KAFELKÓW
        for col in range(start_col, end_col + 1):
            # Dokładnie ten sam wzór, którego używa grafika mapy!
            x = (col * TILE_SIZE) - cam_x
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
            
        # 3. Rysujemy POZIOME linie bazując na wierszach mapy
        for row in range(start_row, end_row + 1):
            y = (row * TILE_SIZE) - cam_y
            pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))
    
    def draw_castle_interface(self, screen, world):
        """Rysuje interfejs zamku."""
        castle = world.selected_castle
        if not castle: 
            return
        
        mx, my = pygame.mouse.get_pos()
        mouse_over_ui = False # Do śledzenia, czy trzymać otwarte menu

        # --- WARSTWA 1: DYNAMICZNA GRAFIKA ZAMKU (Budynki) ---
        if hasattr(world, 'castle_gfx'):
            world.castle_gfx.draw(screen, castle)
        else:
            screen.fill((60, 50, 40))

        # --- WARSTWA 2: TYTUŁ ZAMKU ---
        font_main = pygame.font.SysFont("Arial", 28, bold=True)
        title = font_main.render(f"{castle.building_type.upper()}", True, (255, 255, 255))
        screen.blit(title, (40, 40))

        # --- WARSTWA 3: NAPISY INFORMACYJNE (NA WYPALONYM PASKU) ---
        bldg_code = None
        if hasattr(world, 'castle_gfx'):
            bldg_code = world.castle_gfx.get_building_at_pos(mx, my, castle)
        
        slownik_nazw = {
            "court": "DWÓR", "koszary": "BARAKI", "hospital": "SZPITAL",
            "workshop": "WARSZTAT", "school": "SZKOŁA", "forge": "KUŹNIA",
            "peasants": "CHŁOPI"
        }
        
        hovered_text = slownik_nazw.get(bldg_code, "")
        if hovered_text:
            font_info = pygame.font.SysFont("Arial", 22, bold=True)
            txt_surf = font_info.render(hovered_text, True, (230, 210, 170))
            txt_shadow = font_info.render(hovered_text, True, (0, 0, 0))
            txt_x = screen.get_width() // 2 - txt_surf.get_width() // 2
            txt_y = screen.get_height() - 40  
            screen.blit(txt_shadow, (txt_x + 2, txt_y + 2))
            screen.blit(txt_surf, (txt_x, txt_y))

        # ==========================================================
        # WARSTWA 4: ANIMOWANE ZIELONE MENU NA ŁAŃCUCHACH
        # ==========================================================
        if not hasattr(world, 'menu_anim_frame'):
            world.menu_anim_frame = 0.0

        # Ustalamy obszar MENU (Prawy Górny Róg)
        ban_w, ban_h = 130 * 1.4, 72 * 1.5 # Powiększamy (ok. 169x93 px)
        ban_x = screen.get_width() - ban_w - 20
        ban_y = 0
        banner_rect = pygame.Rect(ban_x, ban_y, ban_w, ban_h)

        # Sprawdzamy najechanie myszką na baner
        if banner_rect.collidepoint(mx, my):
            world.menu_open = True
            mouse_over_ui = True

        # Płynna animacja zwijania/rozwijania (zmienia klatki od 0.0 do 5.0)
        if getattr(world, 'menu_open', False):
            world.menu_anim_frame = min(5.0, world.menu_anim_frame + 0.4)
        else:
            world.menu_anim_frame = max(0.0, world.menu_anim_frame - 0.4)

        current_frame = int(world.menu_anim_frame)

        # Rysowanie Banera
        if hasattr(world, 'menu_frames') and len(world.menu_frames) == 6:
            banner_scaled = pygame.transform.scale(world.menu_frames[current_frame], (int(ban_w), int(ban_h)))
            screen.blit(banner_scaled, (ban_x, ban_y))
            
            # Zapisujemy pozycję dla rozwijanych opcji (aby zaczynały się dokładnie POD banerem)
            world.menu_options_start_y = ban_y + int(ban_h) - 15 
            world.menu_options_start_x = ban_x
        else:
            # Fallback - stary przycisk, gdyby grafiki się nie załadowały
            world.menu_button = pygame.Rect(ban_x, ban_y, 100, 40)
            self.draw_button(screen, "MENU", world.menu_button)
            if world.menu_button.collidepoint(mx, my): mouse_over_ui = True
            world.menu_options_start_y = ban_y + 40
            world.menu_options_start_x = ban_x

        # --- WARSTWA 5: OPCJE MENU (Dropdown) ---
        if getattr(world, 'menu_open', False):
            self.draw_castle_menu(screen, mx, my)
            
            # Podtrzymujemy otwarte menu, jeśli myszka zjedzie na rozwinięte przyciski
            for rect in world.menu_rects.values():
                if rect.collidepoint(mx, my): mouse_over_ui = True
                
            if getattr(world, 'build_open', False):
                for rect in world.build_rects.values():
                    if rect.collidepoint(mx, my): mouse_over_ui = True
                    
                # Gwarantuje że bycie GDZIEKOLWIEK w obrębie podmenu budowy trzyma je otwarte
                submenu_bg_rect = pygame.Rect(world.menu_options_start_x - 180, ban_y, 180, 300)
                if submenu_bg_rect.collidepoint(mx, my): mouse_over_ui = True
            
            # "Mostek bezpieczeństwa" pod głównym banerem
            bridge_rect = pygame.Rect(world.menu_options_start_x, ban_y, ban_w, 300)
            if bridge_rect.collidepoint(mx, my): mouse_over_ui = True

        # Automatyczne zamykanie menu
        if not mouse_over_ui:
            world.menu_open = False
            world.build_open = False

        # --- WARSTWA 6: STOPKA (Kamienny przycisk Powrotu) ---
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
        w = self.world
        
        # --- 1. LOGIKA POKAZYWANIA/CHOWANIA ---
        if w.top_ui_trigger_area.collidepoint(mx, my):
            w.show_top_ui = True
        elif not w.top_ui_full_area.collidepoint(mx, my) and w.active_dropdown is None:
            w.show_top_ui = False

        # --- 2. RYSOWANIE GÓRNEGO PASKA ---
        if w.show_top_ui:
            bar_h = 45 # Wysokość paska górnego
            
            # --- AKTUALIZACJA STREF KLIKANIA ---
            w.btn_system = pygame.Rect(10, 0, 150, bar_h)
            w.btn_mapa = pygame.Rect(170, 0, 150, bar_h)
            w.next_turn_button = pygame.Rect(screen.get_width() - 220, 0, 210, bar_h)

            if hasattr(self, 'top_bar_img') and self.top_bar_img:
                scaled_top_bar = pygame.transform.scale(self.top_bar_img, (screen.get_width(), bar_h))
                screen.blit(scaled_top_bar, (0, 0))
                
                font_turn = pygame.font.SysFont("Times New Roman", 24, bold=True)
                turn_txt = font_turn.render(str(w.turn), True, (30, 20, 10))
                tx = screen.get_width() - 58
                ty = 5
                screen.blit(turn_txt, (tx, ty))
            else:
                pygame.draw.rect(screen, (40, 40, 40), (0, 0, screen.get_width(), bar_h))

            # =========================================================
            # --- 3. RYSUJEMY ZWÓJ (Na wierzchu)
            # =========================================================
            if w.active_dropdown in getattr(w, 'menu_options', {}):
                options = w.menu_options[w.active_dropdown]
                
                if not hasattr(w, 'system_buttons'): w.system_buttons = {}
                if not hasattr(w, 'mapa_buttons'): w.mapa_buttons = {}
                target_dict = w.system_buttons if w.active_dropdown == "System" else w.mapa_buttons
                target_dict.clear() 

                # Obydwa zwoje mają TĘ SAMĄ szerokość (165) i ten sam styl!
                start_x = w.btn_system.x - 10 if w.active_dropdown == "System" else w.btn_mapa.x - 0
                
                # Zaczynamy od wysokości 36, co ładnie połączy wałek z belką
                self.draw_parchment_menu(screen, start_x, 20, 200, options, target_dict, mx, my)
 
    def draw_parchment_menu(self, screen, x, y, width, options, buttons_dict, mx, my, disabled_options=None):
        """Uniwersalne rysowanie menu - inteligentne wycinanie i dopasowanie."""
        if not options or not getattr(self, 'menu_bg_img', None):
            return

        if disabled_options is None:
            disabled_options = []

        item_h = 32 
        padding_top = 12
        body_h = (len(options) * item_h) + padding_top + 5
        
        original_h = self.menu_bg_img.get_height()
        target_h = max(body_h, original_h)
        bg_scaled = pygame.transform.scale(self.menu_bg_img, (width, target_h))
        bg_cutout = bg_scaled.subsurface(pygame.Rect(0, 0, width, body_h))
        screen.blit(bg_cutout, (x, y))
        
        if getattr(self, 'menu_bottom_img', None):
            roller_scaled = pygame.transform.scale(self.menu_bottom_img, (width, 30))
            screen.blit(roller_scaled, (x, y + body_h - 14))

        # =========================================================
        # 3. Rysowanie opcji i hitboxów
        # =========================================================
        font_scroll = pygame.font.SysFont("Times New Roman", 20, bold=True)

        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y + padding_top + (i * item_h), width, item_h)
            is_disabled = opt in disabled_options # Sprawdzamy czy budynek jest na liście "zbudowanych"

            if is_disabled:
                is_hover = False
                color = (130, 130, 130) # Ciemnoszary dla wybudowanych
                # Celowo NIE dodajemy do buttons_dict, by nie można było w to kliknąć!
            else:
                buttons_dict[opt] = rect 
                is_hover = rect.collidepoint(mx, my)
                color = (255, 255, 100) if is_hover else (255, 255, 255)
            
            if is_hover:
                hover_surf = pygame.Surface((width - 20, item_h), pygame.SRCALPHA)
                hover_surf.fill((255, 255, 255, 30))
                screen.blit(hover_surf, (rect.x + 10, rect.y))
                
            txt_shadow = font_scroll.render(opt.lower(), True, (0, 0, 0))
            txt = font_scroll.render(opt.lower(), True, color)
            
            txt_x = rect.x + 30 
            txt_y = rect.y + (item_h // 2) - (txt.get_height() // 2)
            
            screen.blit(txt_shadow, (txt_x + 2, txt_y + 2))
            screen.blit(txt, (txt_x, txt_y))
            # Możesz to odkomentować (# usuwając hash), jeśli znów będziesz chciał diagnozować klikanie
            # pygame.draw.rect(screen, (255, 0, 0), rect, 1)

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
            
            # --- ROZCIĄGANIE GRAFIKI DO ROZMIARU RECT ---
            scaled_img = pygame.transform.smoothscale(img, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)
            return

        if style == "bldg":
            img = self.world.back_img_bldg_pressed if getattr(self.world, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.world.back_anim_timer < 500 \
                else self.world.back_img_bldg_normal
                
            # ==========================================
            # --- RĘCZNE USTAWIENIA GRAFIKI PRZYCISKU ---
            # ==========================================
            # Zmień na True, żeby "odpiąć" grafikę od obszaru klikania 
            # i samodzielnie zdecydować o jej wyglądzie i miejscu:
            WLASNE_USTAWIENIA = True 
            
            if WLASNE_USTAWIENIA:
                # Tu wpisz sztywne wymiary, jakie ma mieć sam obrazek:
                GRAFIKA_SZEROKOSC = 155 
                GRAFIKA_WYSOKOSC = 84
                
                # Tu wpisz, gdzie dokładnie na ekranie ma zostać narysowany:
                GRAFIKA_X = 62 
                GRAFIKA_Y = 679 
                
                scaled_img = pygame.transform.smoothscale(img, (GRAFIKA_SZEROKOSC, GRAFIKA_WYSOKOSC))
                screen.blit(scaled_img, (GRAFIKA_X, GRAFIKA_Y))
            else:
                # Domyślne zachowanie: grafika idealnie dopasowuje się do strefy klikania (rect)
                scaled_img = pygame.transform.smoothscale(img, (rect.width, rect.height))
                screen.blit(scaled_img, rect.topleft)
            return
            
        elif style == "garrison_back":
            img = self.world.back_img_garrison_pressed if getattr(self.world, 'back_anim_timer', 0) > 0 and \
                pygame.time.get_ticks() - self.world.back_anim_timer < 500 \
                else self.world.back_img_garrison_normal
                
            # UPROSZCZENIE: Grafika sama dopasowuje się do rozmiaru i pozycji Recta z world.py!
            scaled_img = pygame.transform.smoothscale(img, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)
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

    def draw_temple_event(self, screen):
        w = self.world
        
        # 1. Ciemne tło
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # ==========================================
        # 2. SKALOWANIE I SKLEJANIE PERGAMINU
        # ==========================================
        skala = 1.4  
        
        lw, lh = w.temple_scroll_l.get_size()
        rw, rh = w.temple_scroll_r.get_size()
        
        new_lw, new_lh = int(lw * skala), int(lh * skala)
        new_rw, new_rh = int(rw * skala), int(rh * skala)
        
        # Używamy zwykłego 'scale', by ostre krawędzie łączeń lepiej do siebie pasowały
        scroll_l_scaled = pygame.transform.scale(w.temple_scroll_l, (new_lw, new_lh))
        scroll_r_scaled = pygame.transform.scale(w.temple_scroll_r, (new_rw, new_rh))
        
        # ZAKŁADKA POZIOMA: Wsuwamy prawą część w lewą, by ukryć białą linię cięcia
        zakladka_x = int(3 * skala) 
        
        total_w = new_lw + new_rw - zakladka_x
        start_x = (screen.get_width() - total_w) // 2
        start_y = (screen.get_height() - new_lh) // 2

        # --- KOREKTA PIONOWA (Tego brakowało!) ---
        # Ustawiamy wartość ujemną, żeby fizycznie "podnieść" prawą stronę do góry
        # Zmień tę liczbę (np. -12, -15, -8), aż linie idealnie się zrównają
        korekta_y_prawej = 8

        # Rysujemy lewą stronę bez zmian
        screen.blit(scroll_l_scaled, (start_x, start_y))
        
        # Rysujemy prawą stronę podniesioną o korektę i wsuniętą w lewą
        screen.blit(scroll_r_scaled, (start_x + new_lw - zakladka_x, start_y + korekta_y_prawej))

        # ==========================================
        # 3. TYTUŁ NA GÓRZE
        # ==========================================
        tytul = getattr(w, 'temple_title', "Wydarzenie")
        if hasattr(self, 'custom_font'):
            self.custom_font.render(screen, tytul.upper(), start_x + (total_w // 2) - int(130 * skala), start_y + int(40 * skala), 
                                    spacing=2, palette_name="golden", scale=1.8)

        # ==========================================
        # 4. OPIS GŁÓWNY (TERAZ JEST WYŻEJ)
        # ==========================================
        opis = getattr(w, 'temple_desc', "")
        
        # Zabezpieczenie (na wypadek listy)
        if isinstance(opis, list):
            import random
            opis = random.choice(opis)
            w.temple_desc = opis # Zapisujemy, żeby nie migotało!

        # Zwiększamy nieco czcionkę do większego pergaminu
        font_opis = pygame.font.SysFont("Arial", 22, bold=True)
        kolor_tekstu = (150, 0, 0) if "niegodny" in tytul.lower() or "biada" in tytul.lower() else (0, 100, 0)

        # System łamania długiego tekstu
        slowa = opis.split(' ')
        linie = []
        aktualna_linia = ""
        for slowo in slowa:
            if font_opis.size(aktualna_linia + slowo + " ")[0] < total_w - 120: # Marginesy proporcjonalne
                aktualna_linia += slowo + " "
            else:
                linie.append(aktualna_linia)
                aktualna_linia = slowo + " "
        linie.append(aktualna_linia)

        # Zaczynamy rysować tekst zaraz pod tytułem
        y_offset = start_y + int(70 * skala) 
        for linia in linie:
            txt_surf = font_opis.render(linia, True, kolor_tekstu)
            screen.blit(txt_surf, (start_x + (total_w - txt_surf.get_width()) // 2, y_offset))
            y_offset += 28 # Odstęp między wierszami tekstu

        # ==========================================
        # 5. GRAFIKA (TERAZ JEST NA DOLE, POD TEKSTEM)
        # ==========================================
        effect_img = getattr(w, 'temple_current_effect', None)
        if effect_img:
            # Powiększamy grafikę o 50%, żeby nie zginęła na wielkim pergaminie
            img_w, img_h = effect_img.get_size()
            img_scaled = pygame.transform.smoothscale(effect_img, (int(img_w * 1.5), int(img_h * 1.5)))
            i_w, i_h = img_scaled.get_size()
            
            # Rysujemy ją pod tekstem (wykorzystujemy y_offset z pętli tekstu + mały odstęp)
            screen.blit(img_scaled, (start_x + (total_w - i_w) // 2, y_offset + 15))
            
    def draw_army_panel(self, screen):
        u = self.world.selected_unit
        if not u:
            return 

        # Pobieramy garnizon jednostki (jeśli istnieje)
        garrison = getattr(u, 'garrison', [])
        display_units = [unit for unit in ([u] + garrison) if unit is not None]

        # Pokazujemy panel, jeśli to armia lub po prostu wybrana jednostka
        if len(display_units) >= 1:
            # Pozycja paska (dopasuj y=700, żeby był na samym dole)
            panel_y = 700 
            panel_x = 50
            
            # 1. RYSOWANIE DREWNIANEGO TŁA (Twoja grafika MARKS_S32_35)
            # Rysujemy pierwszy rząd slotów
            screen.blit(self.gfx.army_panel_bg, (panel_x, panel_y))
            # Jeśli masz więcej niż 12 jednostek, rysujemy drugi pasek pod spodem
            if len(display_units) > 12:
                screen.blit(self.gfx.army_panel_bg, (panel_x, panel_y + 32))

            # 2. RYSOWANIE IKON JEDNOSTEK
            self.world.army_slot_rects = []
            
            for i, unit in enumerate(display_units):
                # Obliczamy pozycję ikony (każdy slot w MARKS ma 32x32 px)
                col = i % 10 # Pasek ma 12 slotów
                row = i // 10
                
                slot_x = panel_x + (col * 32)
                slot_y = panel_y + (row * 32)
                
                slot_rect = pygame.Rect(slot_x, slot_y, 32, 32)
                self.world.army_slot_rects.append(slot_rect)

                # RYSOWANIE IKONKI
                # Używamy koloru właściciela jednostki do pobrania grafiki
                color_name = "red" if unit.owner.color == (255, 50, 50) else "blue"
                unit_img = self.gfx.get_unit_image(unit.type, color_name)
                
                if unit_img:
                    # Wyśrodkowanie ikonki w slocie (jeśli ikonka jest mniejsza niż 32)
                    img_x = slot_x + (32 - unit_img.get_width()) // 2
                    img_y = slot_y + (32 - unit_img.get_height()) // 2
                    screen.blit(unit_img, (img_x, img_y))
            # ==========================================
                # ZNACZNIKI ZAZNACZENIA W PANELU
                # ==========================================
                if hasattr(self.world, 'units_to_split') and unit in self.world.units_to_split:
                    # self.mark_grey = biały/szary (ma ruch)
                    # self.mark_red = czerwony (brak ruchu)
                    mark = self.mark_grey if unit.move_points >= 3 else self.mark_red
                        
                    # Skalujemy na mały 16x16, żeby nie zasłonił całego portretu
                    small_mark = pygame.transform.smoothscale(mark, (16, 16))
                    screen.blit(small_mark, (slot_x + 8, slot_y + 8))

    def draw_ui(self, screen):

        # 2. DOLNY PANEL ARMII (Tylko dla 2+ jednostek)
        u = self.world.selected_unit
        if u:
            garrison = getattr(u, 'garrison', [])
            display_units = [unit for unit in ([u] + garrison) if unit is not None]

            # Rysujemy sloty armii TYLKO jeśli jest grupa
            if len(display_units) >= 2:
                # 1. RYSOWANIE PIĘKNEGO DREWNIANEGO PANELU
                if hasattr(self, 'img_army_slots') and self.img_army_slots:
                    # Skalujemy grafikę na szerokość 10 slotów (ok. 760px na 150px)
                    scaled_panel = pygame.transform.scale(self.img_army_slots, (665, 120))
                    screen.blit(scaled_panel, (0, 645))
                else:
                    # Awaryjne tło
                    pygame.draw.rect(screen, (30, 20, 10), pygame.Rect(5, 615, 760, 150))

                # 2. Inicjalizacja stref klikania (zapisujemy w świecie, by myszka to widziała)
                if not hasattr(self.world, 'army_slot_rects'):
                    self.world.army_slot_rects = [pygame.Rect(2 + i * 66, 645, 70, 120) for i in range(10)]

                # 3. Wypełnianie slotów
                for i in range(10):
                    rect = self.world.army_slot_rects[i]

                    if i < len(display_units):
                        unit = display_units[i]
                        
                        # --- GRAFIKA WOJOWNIKA ---
                        frame = (pygame.time.get_ticks() // 150) % 8
                        if hasattr(unit, 'sprites') and unit.sprites:
                            img = unit.sprites[frame % len(unit.sprites)]
                            img = pygame.transform.scale(img, (int(img.get_width() * 1.7), int(img.get_height() * 1.6)))
                            
                            # ===================================================
                            # KOREKTA POZYCJI LUDZIKA
                            # ===================================================
                            przesuniecie_x = 0   
                            przesuniecie_y = 2  
                            
                            rys_x = rect.centerx - img.get_width() // 2 + przesuniecie_x
                            rys_y = rect.y + przesuniecie_y
                            
                            screen.blit(img, (rys_x, rys_y))
                        
                        # ===================================================
                        # TEKST: PUNKTY ŻYCIA (HP) LUB PYTAJNIKI ZAMIAST NAZWY
                        # ===================================================
                        current_player_obj = self.world.players[self.world.current_player]
                        
                        # Sprawdzamy, czy to nasze wojsko (tylko wtedy widzimy dokładne życie)
                        if getattr(unit, 'owner', None) == current_player_obj:
                            hp_val = int(getattr(unit, 'hp', 100))
                            
                            if hp_val > 50:
                                kolor_hp = (100, 255, 100)
                            elif hp_val > 25:
                                kolor_hp = (255, 255, 0)
                            else:
                                kolor_hp = (255, 100, 100)
                                
                            hp_txt = self.font_main.render(f"{hp_val}", True, kolor_hp)
                            hp_shadow = self.font_main.render(f"{hp_val}", True, (0, 0, 0)) 
                        else:
                            # NOWOŚĆ (Mgła wojny): Zamiast HP wroga, wyświetlamy tajemnicze pytajniki!
                            hp_txt = self.font_main.render("???", True, (150, 150, 150))
                            hp_shadow = self.font_main.render("???", True, (0, 0, 0))
                            
                        wysokosc_liczby = 24 
                        
                        # Rysowanie
                        txt_x = rect.centerx - hp_txt.get_width() // 2
                        txt_y = rect.bottom - wysokosc_liczby
                        
                        screen.blit(hp_shadow, (txt_x + 1, txt_y + 1)) # Cień
                        screen.blit(hp_txt, (txt_x, txt_y))            # Właściwy tekst
                        
                        # ===================================================
                        # ZNACZNIKI ZAZNACZENIA W PANELU ARMII
                        # (Ograniczone tylko do gracza)
                        # ===================================================
                        if getattr(unit, 'owner', None) == current_player_obj:
                            if hasattr(self.world, 'units_to_split') and unit in self.world.units_to_split:
                                mark = self.mark_grey if unit.move_points >= 3  else self.mark_red
                                small_mark = pygame.transform.smoothscale(mark, (20, 20))
                                screen.blit(small_mark, (rect.x + 5, rect.y + 5))

        # 3. PRZYCISKI AKCJI (Zawsze widoczne na ekranie)
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

        # Nagłówek (pierwsza linia tekstu np. "Chłopi")
        if lines:
            if hasattr(self, 'custom_font'):
                self.custom_font.render(screen, lines[0].upper(), 120, y, spacing=2, palette_name="golden")
            y += 60

        # Opis
        for line in lines[1:]:
            if hasattr(self, 'custom_font'):
                self.custom_font.render(screen, line, 120, y, spacing=1, palette_name="golden")

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

        self.draw_building_footer(screen)
  
    def draw_castle_on_map(self, screen, castle):
        """
        Rysuje zamek na mapie świata z uwzględnieniem "Pierworodnego" twórcy 
        oraz grafiki okupacji ("take by").
        """
        w = self.world
        
        # 1. Obliczamy pozycję na ekranie względem kamery
        px = castle.x * TILE_SIZE - w.camera_x
        py = castle.y * TILE_SIZE - w.camera_y
        
        # 2. Ustalamy stan (etap) zamku. Domyślnie 3 (pełny). Zniszczony = 4.
        poziom = getattr(castle, 'build_stage', 3)
        if getattr(castle, 'destroyed', False):
            poziom = 4
            
        # 3. Wyciągamy Pierwotnego twórcy i Obecnego właściciela
        orig_owner = getattr(castle, 'original_owner', castle.owner)
        
        orig_owner_obj = w.players[orig_owner] if isinstance(orig_owner, int) else orig_owner
        curr_owner_obj = w.players[castle.owner] if isinstance(castle.owner, int) else castle.owner
        
        orig_color = orig_owner_obj.color_name.lower() if orig_owner_obj else "red"
        curr_color = curr_owner_obj.color_name.lower() if curr_owner_obj else "red"
        
        # 4. Pobieramy słownik z kafelkami dla oryginalnego koloru
        color_dict = w.castle_tiles_by_color.get(orig_color, w.castle_tiles_by_color.get("red", {}))
        
        # 5. INTELIGENTNY WYBÓR GRAFIKI
        if orig_color == curr_color or poziom == 4:
            # Zamek u prawowitego właściciela (lub ruina, która nie ma barw)
            tiles = color_dict.get(poziom, [])
        else:
            # ZAMEK ZDOBYTY: Używamy grafiki okupanta z "take by"
            take_by_dict = color_dict.get("take by", {})
            tiles = take_by_dict.get(curr_color, [])
            
            # System awaryjny: Jeśli np. zapomniałeś dodać [1,1,1,1] dla jakiegoś koloru, załaduje starą bazę
            if not tiles:
                tiles = color_dict.get(poziom, [])

        # 6. Rysujemy 4 kafelki tworzące zamek (wymiar 2x2) na mapie
        if len(tiles) == 4:
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for i in range(4):
                dx, dy = offsets[i]
                screen.blit(tiles[i], (px + dx * TILE_SIZE, py + dy * TILE_SIZE))
        else:
            # Failsafe w postaci kwadratu na skrajne awarie
            owner_color = getattr(castle.owner, 'color', (200, 0, 0)) if getattr(castle, 'owner', None) else (200, 0, 0)
            pygame.draw.rect(screen, owner_color, (px, py, TILE_SIZE * 2, TILE_SIZE * 2))

    def draw_ports_on_map(self, screen):
        w = self.world
        if not hasattr(w, 'ports'): return

        for port in w.ports:
            px = int(port["x"] * TILE_SIZE) - w.camera_x
            py = int(port["y"] * TILE_SIZE) - w.camera_y
            
            # Pomiń rysowanie, jeśli port jest poza ekranem
            if px < -100 or px > screen.get_width() + 100 or py < -100 or py > screen.get_height() + 100:
                continue

            orient = port.get("orientation", 1)
            # Zauważ: pobieramy kafelki ze świata gry (w.port_tiles)
            base_tiles = getattr(w, 'port_tiles', {}).get(f"pos{orient}_base", [])
            ship_tiles = getattr(w, 'port_tiles', {}).get(f"pos{orient}_ship", [])
            
            # 4 kafelki układające się w blok 2x2
            offsets = [(0,0), (1,0), (0,1), (1,1)]
            
            if len(base_tiles) == 4:
                for i in range(4):
                    dx, dy = offsets[i]
                    
                    # Jeśli port ma statek, a my rysujemy DOLNĄ (wodną) połowę (czyli indeks 2 lub 3)
                    if port.get("has_ship", False) and i >= 2 and len(ship_tiles) >= 2:
                        img = ship_tiles[i - 2] # Wybiera obrazek statku
                    else:
                        img = base_tiles[i]     # Zwykła woda lub ląd
                        
                    screen.blit(img, (px + dx*TILE_SIZE, py + dy*TILE_SIZE))

    def draw_unit_stats_table(self, screen, x, y, unit_name, stats_source):
        w = self.world
        
        # --- BLOKADA: Rysuj globalne okienko TYLKO na mapie ---
        # Jeśli jesteśmy w koszarach, garnizonie lub menu, przerywamy funkcję!
        if getattr(w, 'screen', "map") != "map":
            return

        if not stats_source:
            return

        # ========================================================
        # KLUCZOWA ZMIANA: Pobieramy tryb, który ustaliliśmy
        # w controls.py (Czyli uwzględniamy naszą Mgłę Wojny!)
        # ========================================================
        mode = getattr(w, 'info_mode', "COMBAT")

        w.unit_info_window.draw(screen, x, y, stats_source, mode)

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
        if w.screen != "castle": return 

        options = ["Buduj", "ZBURZ ZAMEK", "ROZBUDUJ MURY"]
        w.menu_rects.clear()

        menu_x = getattr(w, 'menu_options_start_x', 800)
        menu_y = getattr(w, 'menu_options_start_y', 100)

        if getattr(w, 'menu_anim_frame', 0) >= 3.0:
            self.draw_parchment_menu(screen, menu_x, menu_y, 200, options, w.menu_rects, mx, my)

            buduj_rect = w.menu_rects.get("Buduj")
            zburz_rect = w.menu_rects.get("ZBURZ ZAMEK")
            rozbuduj_rect = w.menu_rects.get("ROZBUDUJ MURY")

            # --- NOWA LOGIKA ZACZEPIANIA PODMENU ---
            if buduj_rect and buduj_rect.collidepoint(mx, my):
                w.build_open = True
            elif (zburz_rect and zburz_rect.collidepoint(mx, my)) or (rozbuduj_rect and rozbuduj_rect.collidepoint(mx, my)):
                w.build_open = False # Zamyka się tylko, gdy wybierzesz coś innego!

            if getattr(w, "build_open", False):
                self.draw_build_submenu(screen, menu_x, menu_y)
        
    def draw_build_submenu(self, screen, menu_x, menu_y):
        w = self.world
        castle = w.selected_castle
        if not castle: return

        all_buildings = ["hospital", "school", "koszary", "forge", "workshop"]
        to_build = [b.upper() for b in all_buildings] # Pokazujemy pełną listę
        
        # Tworzymy listę budynków, które Zamek już posiada:
        disabled = [b.upper() for b in all_buildings if b.lower() in castle.buildings]

        w.build_rects.clear()
        sub_x = menu_x - 165
        sub_y = menu_y + 20
        
        mx, my = pygame.mouse.get_pos()
        
        # Wysyłamy zmienną disabled_options do rysowania!
        self.draw_parchment_menu(screen, sub_x, sub_y, 180, to_build, w.build_rects, mx, my, disabled_options=disabled)
    
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
    
    def draw_building_footer(self, screen):
        w = self.world
        
        # =========================================================
        # KLUCZOWA ZMIANA: Jeśli jesteśmy w Strażnicy, całkowicie 
        # wychodzimy z tej funkcji, żeby nie rysować starych przycisków!
        # =========================================================
        if w.screen == "Strażnica":
            return
        # =========================================================

        if w.screen == "castle":
            # Tylko zamek ma graficzny przycisk z arkusza Z_IKO
            self.draw_button(screen, "", w.back_button_castle, style="castle")

        elif w.screen in ["garrison", "peasants", "school", "hospital", "forge", "workshop"]:
            # ZMIANA: usunięto "Strażnica" z listy, bo obsługujemy ją wyżej
            btn_rect = getattr(w, 'back_button_garrison', w.back_button_bldg)
            self.draw_button(screen, "", btn_rect, style="garrison_back")
            
        else:
            # Reszta budynków używa standardowego stylu "bldg"
            self.draw_button(screen, "", w.back_button_bldg, style="bldg")

        # Ten warunek zostawiamy bez zmian, bo on rysuje przycisk "ZBURZ"
        if w.selected_castle and getattr(w.selected_castle, 'building_type', "") == "Strażnica":
            self.draw_button(screen, "ZBURZ", w.destroy_button, (100, 40, 40))

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

    #strzałki drogi
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
    # RYSOWANIE BUDYNKÓW (teksty opisowe)

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
        self.draw_building_template(screen, "Kuźnia", lines)

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
            "   Dzięki wykładanym tu naukom, możliwe będzie szkolenie",
            "Twoich wojsk w rzemiośle rycerskim. Wprawieni w sztuce",
            "wojennej weterani bitew horbijskich sprawią, że byle żołdak",
            "w szybkim tempie nauczy się wprawnie posługiwać posiadanym",
            "orężem."
            "",
            "",
            "   Ponadto, dzięki wysiłkom uczonych waldzkich, którzy tu",
            "także przebywają, możliwe będzie osiągnięcie wyższego",
            "poziomu tehnologi w Twoim królestwie",
        ]
        # Wszystkie parametry w jednym miejscu:
        cfg = {
            "pos_tytul": (450, 135), 
            "pos_tekst": (150, 220), 
            "scale_tytul": 2, 
            "scale_tekst": 1.2
        }
        self.draw_building_template(screen, "Szkoła", lines, config=cfg)

    def draw_building_template(self, screen, title, lines, config=None):

        # Domyślne wartości
        c = {
            "pos_tytul": (450, 135), "pos_tekst": (150, 220),
            "scale_tytul": 2.0, "scale_tekst": 1.2,
            "spacing_tytul": 1, "spacing_tekst":0
        }
        if config: c.update(config)

        # Tło
        if hasattr(self, 'bldg_bg'):
            screen.blit(pygame.transform.scale(self.bldg_bg, screen.get_size()), (0, 0))

        # Renderowanie - Zawsze na złoto (palette_name="golden")
        self.custom_font.render(screen, title.upper(), c["pos_tytul"][0], c["pos_tytul"][1], 
                                spacing=c["spacing_tytul"], palette_name="golden", scale=c["scale_tytul"])

        curr_y = c["pos_tekst"][1]
        for line in lines:
            # Używamy .upper() jeśli małe litery w Twoich PNG są pomieszane - to często naprawia "bzdury"
            self.custom_font.render(screen, line, c["pos_tekst"][0], curr_y, 
                                    spacing=c["spacing_tekst"], palette_name="golden", scale=c["scale_tekst"])
            curr_y += int(35 * c["scale_tekst"])

        self.draw_building_footer(screen)
    # -------------------------------------------------------

    def draw_watchtower_interior(self, screen, world):
        castle = world.selected_castle
        if not castle: return

        # 1. Konfiguracja
        skala_tla = 1.4
        przesunięcie_x = 0
        przesunięcie_y = 0

        start_x = 24
        start_y = 61
        odstep_x = 62
        odstep_y = 110
        slot_w, slot_h = 70, 100

        # 2. Ładowanie tła (poprawione!)
        if not hasattr(self, 'tower_bg_img'):
            try:
                sciezka = os.path.join("assets", "minimum", "KEEP_S32", "KEEP_S32_0.png")
                # Wczytujemy do zmiennej tymczasowej 'temp_img'
                temp_img = pygame.image.load(sciezka).convert_alpha()
                
                # UŻYWAMY 'temp_img' DO OBLICZEŃ, A NIE 'img'
                nw = int(temp_img.get_width() * skala_tla)
                nh = int(temp_img.get_height() * skala_tla)
                
                # Zapisujemy do self.tower_bg_img
                self.tower_bg_img = pygame.transform.smoothscale(temp_img, (nw, nh))
                print(f"SUKCES: Załadowano tło strażnicy z: {sciezka}")
                
            except Exception as e:
                print(f"BŁĄD: Nie można załadować tła: {e}")
                self.tower_bg_img = pygame.Surface((560, 450), pygame.SRCALPHA)
                self.tower_bg_img.fill((40, 40, 40, 200)) # Półprzezroczyste szare tło

        bg_x = (screen.get_width() - self.tower_bg_img.get_width()) // 2 + przesunięcie_x
        bg_y = (screen.get_height() - self.tower_bg_img.get_height()) // 2 + przesunięcie_y
        
        # Rysujemy okno strażnicy
        screen.blit(self.tower_bg_img, (bg_x, bg_y))

        # 3. Sloty i jednostki
        world.garrison_slot_rects = []
        for i in range(10):
            row = i // 5
            col = i % 5
            rect = pygame.Rect(bg_x + start_x + col * odstep_x, bg_y + start_y + row * odstep_y, slot_w, slot_h)
            world.garrison_slot_rects.append(rect)

            # Rysowanie jednostek
            if i < len(castle.garrison) and castle.garrison[i]:
                unit = castle.garrison[i]
                img = None
                if hasattr(unit, 'walk_frames') and unit.walk_frames: img = unit.walk_frames[0]
                elif hasattr(unit, 'sprites') and unit.sprites: img = unit.sprites[0]

                if img:
                    u_scale = min(slot_w / img.get_width(), slot_h / img.get_height()) * 0.95
                    nw, nh = int(img.get_width() * u_scale), int(img.get_height() * u_scale)
                    img_scaled = pygame.transform.smoothscale(img, (nw, nh))
                    screen.blit(img_scaled, (rect.x + (slot_w - nw)//2, rect.y + (slot_h - nh)//2))
                
                if unit in world.selected_units:
                    pygame.draw.rect(screen, (255, 215, 0), rect, 3)
                    
        # 1. Ładowanie przycisków (dodaj to do sekcji ładowania tła)
        if not hasattr(self, 'tower_btns'):
            self.tower_btns = {}
            for i in [1, 2, 4]: # 1:powrot, 2:wypusc, 4:zniszcz
                path = os.path.join("assets", "minimum", "KEEP_S32", f"KEEP_S32_{i}.png")
                self.tower_btns[i] = pygame.image.load(path).convert_alpha()

        # 2. Definicja współrzędnych (Względne do środka ekranu lub rogu)
        # Podaję przykładowe koordynaty, dostosuj je wg uznania:
        btn_w, btn_h = 116, 58 
        # Przycisk "Powrót" (strzałka w lewo)
        world.back_btn = pygame.Rect(bg_x + 2, bg_y + 280, btn_w, btn_h)
        # Przycisk "Wypuść" (strzałka w prawo/ikona)
        world.release_btn = pygame.Rect(bg_x + 245, bg_y + 280, btn_w, btn_h)
        # Przycisk "Zniszcz" (ikona z przekreśleniem)
        world.destroy_btn = pygame.Rect(bg_x + 20, bg_y + 30, 27, 27)

        # 3. Rysowanie przycisków
        screen.blit(pygame.transform.smoothscale(self.tower_btns[1], (btn_w, btn_h)), world.back_btn.topleft)
        screen.blit(pygame.transform.smoothscale(self.tower_btns[2], (btn_w, btn_h)), world.release_btn.topleft)
        screen.blit(pygame.transform.smoothscale(self.tower_btns[4], (27, 27)), world.destroy_btn.topleft)
        # Używamy getattr, żeby uniknąć błędu, jeśli prostokąt jeszcze nie istnieje
        for rect_name in ['back_btn', 'release_btn', 'destroy_btn']:
            rect = getattr(world, rect_name, None)
            if isinstance(rect, pygame.Rect):
                pygame.draw.rect(screen, (255, 0, 0), rect, 2)

    def draw_split_preview(self, screen):
        w = self.world
        leader = w.selected_unit
        if not leader: return
        
        if not hasattr(self, 'mark_split'):
            try: 
                self.mark_split = pygame.image.load("assets/minimum/MARKS_S32/MARKS_S32_40.png").convert_alpha()
            except: 
                self.mark_split = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                self.mark_split.fill((0, 255, 0, 100))
                
        walkable_chars = [".", "l", "g", "p", "_", "#", "$", " "]
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                tx, ty = leader.x + dx, leader.y + dy
                
                if 0 <= tx < len(w.map[0]) and 0 <= ty < len(w.map):
                    tile_char = w.map[ty][tx]
                    
                    if tile_char in walkable_chars:
                        
                        # --- 1. BLOKADA WCHODZENIA NA INNE JEDNOSTKI ---
                        # Rozdzielenie to wyrzucenie na puste pole. Jeśli ktoś tu stoi, nie pokazujemy ludzika!
                        zajete = any(other.x == tx and other.y == ty for other in w.units)
                        if zajete:
                            continue

                        # --- 2. INTELIGENTNE SPRAWDZANIE KOSZTU ---
                        base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
                        move_mod = 1.5 if (dx != 0 and dy != 0) else 1.0 
                        koszt_podzialu = int(base_cost * move_mod)
                        
                        can_enter = True
                        if hasattr(w, 'units_to_split'):
                            for u in w.units_to_split:
                                # Jeśli wybrana jednostka ma mniej PA niż potrzeba, blokujemy strzałkę
                                if u.move_points < koszt_podzialu:
                                    can_enter = False
                                    break
                                    
                        # Rysujemy ludzika TYLKO jeśli starczy punktów ruchu!
                        if can_enter:
                            px = tx * TILE_SIZE - w.camera_x
                            py = ty * TILE_SIZE - w.camera_y
                            screen.blit(self.mark_split, (px, py))

    def draw_port_ui(self, screen):
        w = self.world
        port = getattr(w, 'inspected_port', None)
        if not port: return
        
        # 1. PANCERNE ŁADOWANIE OBRAZKÓW (Z Systemem Awaryjnym)
        if not hasattr(self, 'port_ui_empty'):
            try:
                self.port_ui_empty = pygame.image.load("assets/minimum/PORT_S32/PORT_S32_0.png").convert_alpha()
                self.port_ui_full = pygame.image.load("assets/minimum/PORT_S32/PORT_S32_1.png").convert_alpha()
            except Exception as e:
                print(f"Nie znaleziono pliku UI Portu. Uruchamiam okienko awaryjne: {e}")
                surf = pygame.Surface((300, 350), pygame.SRCALPHA)
                surf.fill((40, 30, 20, 230))
                pygame.draw.rect(surf, (180, 140, 60), surf.get_rect(), 3)
                self.port_ui_empty = surf
                self.port_ui_full = surf
                
        # Sprawdzamy ile wojska czeka
        ilosc = port.get("pending_count", 0)
        if ilosc == 0 and port.get("garrison"):
            ilosc = len(port["garrison"])
            
        # 2. Rysowanie tła okienka
        img = self.port_ui_full if ilosc > 0 else self.port_ui_empty
        skala = 1.5
        nw, nh = int(img.get_width() * skala), int(img.get_height() * skala)
        img_scaled = pygame.transform.smoothscale(img, (nw, nh))
        x, y = (screen.get_width() - nw) // 2, (screen.get_height() - nh) // 2
        
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        screen.blit(img_scaled, (x, y))
        
        font = pygame.font.SysFont("Arial", 24, bold=True)
        
        # 3. Wypisywanie OGÓLNEJ LICZBY LUB odliczania do statku
        if ilosc > 0:
            title_txt = font.render("Oczekujące posiłki:", True, (255, 255, 200))
            screen.blit(title_txt, (x + max(30, nw//4 - 20), y + 60))
            
            info_txt = font.render(f"Liczba jednostek: {ilosc}", True, (255, 255, 255))
            screen.blit(info_txt, (x + max(30, nw//4 - 20), y + 110))
        else:
            info_txt = font.render("Port jest pusty.", True, (200, 200, 200))
            screen.blit(info_txt, (x + max(50, nw//4), y + 100))
            if port.get("cooldown", 0) > 0:
                time_txt = font.render(f"Kolejny statek za: {port['cooldown']} tur", True, (150, 150, 150))
                screen.blit(time_txt, (x + max(20, nw//4 - 20), y + 140))

    def get_map_cursor(self, mx, my):
        """Mózg kursorów: analizuje teren, jednostki i wybiera odpowiednią ikonę."""
        w = self.world
        default_cursor = self.cursors["mace"]

        # 1. Kursor w menu taktycznym jest obsługiwany przez klasę walki!
        if w.screen == "combat_tactical":
            return None 
            
        # 2. Wewnątrz budynków (Koszary, Szkoła itd.) pokaż zwykłą myszkę Windows
        if w.screen not in ["map", "trap_info"]:
            pygame.mouse.set_visible(True)
            return None

        # 3. Na interfejsie dolnym i górnym zawsze pokazujemy Buławę
        if my >= 610 or (getattr(w, 'show_top_ui', False) and my <= 45):
            return default_cursor

        TILE_SIZE = 32
        gx = (mx + w.camera_x) // TILE_SIZE
        gy = (my + w.camera_y) // TILE_SIZE

        # Zabezpieczenie poza krawędzią mapy
        if not (0 <= gy < len(w.map) and 0 <= gx < len(w.map[0])):
            return default_cursor

        u = w.selected_unit
        target_u = w.get_unit_at(gx, gy)
        current_player = w.players[w.current_player]
        
        # Funkcja pomocnicza: czy to chłop / złoto?
        def is_non_combat(unit):
            if not unit: return False
            return getattr(unit, 'type_code', '') in ["GOLD", "PEAS"] or getattr(unit, 'type', '') in ["Złoto", "Chłopi", "Chłop"]

        # Szukamy zamku/portu pod kursorem
        target_castle = None
        for c in w.castles:
            size = 2 if getattr(c, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
            if c.x <= gx < c.x + size and c.y <= gy < c.y + size:
                if not getattr(c, 'destroyed', False):
                    target_castle = c
                break

        is_port = False
        if not target_castle and hasattr(w, 'ports'):
            for p in w.ports:
                if p["x"] <= gx <= p["x"] + 1 and p["y"] <= gy <= p["y"] + 1:
                    is_port = True
                    break

        map_obj = w.map[gy][gx]
        is_temple = map_obj in ["S", "&"]

        # ====================================================
        # ANALIZA REGUŁ (Od najwyższego priorytetu)
        # ====================================================
        
        # REGUŁA 10: GO (Potwierdzenie ruchu/akcji)
        # Ma NAJWYŻSZY priorytet - jeśli pole to nasz wyznaczony cel (drugi klik), pokaż GO
        if u and getattr(u, 'target_x', None) == gx and getattr(u, 'target_y', None) == gy:
            return self.cursors["go"]

        # Świątynia / Miejsce Kultu
        if is_temple:
            if not u:
                return default_cursor # Brak jednostki = brak reakcji (zostaje buława)
            else:
                if is_non_combat(u): 
                    return self.cursors["no_temple"] # ZAKAZ DLA CHŁOPA/ZŁOTA
                
                # Zaznaczona normalna jednostka wchodzi do świątyni -> Animacja
                anim_frames = self.cursors.get("castle_anim", [])
                if anim_frames and None not in anim_frames:
                    frame_idx = (pygame.time.get_ticks() // 100) % len(anim_frames)
                    return anim_frames[frame_idx]
                return self.cursors["castle"]

        # Zamek lub Port
        if target_castle or is_port:
            if not u:
                return self.cursors["castle"] # Brak jednostki = statyczny zamek nad każdym portem/zamkiem
            else:
                if target_castle and target_castle.owner != current_player:
                    # WROGI ZAMEK
                    if is_non_combat(u): 
                        return self.cursors["no_castle"] # CHŁOP ZGINIE (ZAKAZ)
                    return self.cursors["attack_castle"] # ATAK NA ZAMEK WROGA
                else:
                    # SWÓJ / PUSTY ZAMEK LUB PORT (Mamy jednostkę -> Animacja wejścia!)
                    anim_frames = self.cursors.get("castle_anim", [])
                    if anim_frames and None not in anim_frames:
                        frame_idx = (pygame.time.get_ticks() // 100) % len(anim_frames)
                        return anim_frames[frame_idx]
                    return self.cursors["castle"] 

        # Opcje z Jednostką (Wróg lub Sojusznik)
        if target_u:
            if target_u.owner != current_player:
                # WROGA JEDNOSTKA
                if u:
                    if is_non_combat(u): 
                        return self.cursors["no_attack"] # CHŁOP NIE UMIE WALCZYĆ
                    return self.cursors["attack"]        # ATAK WROGA
            else:
                # SOJUSZNICZA JEDNOSTKA
                if u and getattr(w, 'merge_mode', False) and target_u != u:
                    return self.cursors["merge"]         # POŁĄCZENIE
        
        # Puste pole i zaznaczona jednostka (Ruch)
        if u:
            return self.cursors["sword"] 

        # Domyślny kursor na mapie (Buława)
        return default_cursor
    
if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])