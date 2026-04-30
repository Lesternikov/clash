import pygame
import sys
from settings import UNIT_STATS, UNIT_NAMES, TERRAIN_TYPES, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, COLOR_TO_ID, SCREEN_HEIGHT, SCREEN_WIDTH


class ControlsHandler:
    def __init__(self, world_instance):
        self.world = world_instance
        # Definicje przycisków, żeby nie było błędu przy klikaniu
        self.action_buttons = [pygame.Rect(870, 450 + i * 40, 140, 35) for i in range(6)]
        self.army_slot_rects = [pygame.Rect(10 + i * 75, 620, 70, 140) for i in range(10)]
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- 1. KLAWIATURA ---
            elif event.type == pygame.KEYDOWN:
                # --- DEBUG: MAGIGCZNY KLAWISZ F1 ---
                if event.key == pygame.K_F1:
                    print("DEBUG: Teleportacja do koszar!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "recruitment"
                            break
                if event.key == pygame.K_F2:
                    print("DEBUG: Teleportacja do koszar!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "peasants"
                            break
                # Zamiast self.screen używamy self.world.screen
                if event.key == pygame.K_ESCAPE:
                    self.world.road_build_mode = False
                    self.world.trap_build_mode = False
                    self.world.build_menu_open = False
                    if self.world.screen in ["recruitment", "garrison", "forge", "workshop", "hospital", "school", "peasants", "court"]:
                        self.world.screen = "castle"
                        self.world.inspected_unit = None
                    elif self.world.screen == "castle":
                        self.world.screen = "map"
                    elif getattr(self.world, 'demolish_confirm', False):
                        self.world.demolish_confirm = False

                elif event.key == pygame.K_SPACE:
                    if self.world.selected_unit:
                        self.world.selected_unit = None
                    else:
                        self.world.next_turn()

                elif event.key == pygame.K_g:
                    if self.world.screen == "map":
                        self.world.show_grid = not self.world.show_grid
                        print(f"Siatka: {self.world.show_grid}")
                elif event.key == pygame.K_b:
                    # Dodaj tę flagę w __init__: self.show_only_biome = False
                    self.show_only_biome = not getattr(self, 'show_only_biome', False)
                    print(f"Widok samej mapy biomów: {self.show_only_biome}")
                elif event.key == pygame.K_h:  # Klawisz 'M' przełącza podgląd maski
                    self.debug_show_masks = not self.debug_show_masks
                    print(f"DEBUG: Podgląd masek: {self.debug_show_masks}")
            # --- 3. WCIŚNIĘCIE MYSZY ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if event.button == 3: # Prawy przycisk
                    self.world.inspected_unit = None
                    
                    if self.world.screen == "garrison":
                        self.check_unit_info(mx, my)
                    
                    elif self.world.screen == "map":
                        if my >= 610 and hasattr(self.world, 'army_slot_rects'):
                            u = self.world.selected_unit
                            if u:
                                garrison = [u] + getattr(u, 'garrison', [])
                                display_units = [unit for unit in garrison if unit is not None]
                                for i, rect in enumerate(self.world.army_slot_rects):
                                    if rect.collidepoint(mx, my) and i < len(display_units):
                                        self.world.inspected_unit = display_units[i]
                                        break
                        
                        if not self.world.inspected_unit:
                            self.world.inspected_unit = self.world.get_unit_at_pixel(mx, my)

                # Wywołanie logiki kliknięć (tutaj self.handle_mouse_click to metoda TEJ klasy)
                self.handle_mouse_click(mx, my, event.button)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.world.inspected_unit = None

    def handle_mouse_click(self, mx, my, button):
        if button != 1 and button != 3: return
        w = self.world # Skrót dla wygody

        # --- DODANE: Obsługa okienka ZBURZ ZAMEK (TAK/NIE) ---
        if getattr(w, 'demolish_confirm', False):
            if hasattr(w, 'demolish_yes') and w.demolish_yes.collidepoint(mx, my):
                w.demolish_castle(w.selected_castle)
            elif hasattr(w, 'demolish_no') and w.demolish_no.collidepoint(mx, my):
                w.demolish_confirm = False
            return
        # ----------------------------------------------------

        # 1. PRIORYTET: Ekrany specjalne
        if w.screen == "trap_info":
            w.handle_trap_info_click(mx, my)
            return
        
        if w.screen == "court":
            w.court.handle_court_click(mx, my)
            return

        if w.screen == "map":
            if self.handle_ui_click(mx, my): return 
            
            # --- ZMIANA: Zatrzymujemy kliknięcie, jeśli wykonano akcję budowy ---
            if self.handle_map_logic_combined(mx, my, button): 
                return 
            
            self.handle_map_click(mx, my, button) 
            return

        # NOWE: obsługa ekranów które nie wymagają selected_castle
        if w.screen == "peasants":
            w.peasant_menu.handle_click(mx, my, w)
            return

        if not w.selected_castle: return   # teraz blokuje tylko resztę
        
        # ==========================================================
        # 3. OBSŁUGA PRZYCISKU POWRÓT (Zintegrowana z animacją)
        # ==========================================================

        # Ustalamy, który prostokąt sprawdzamy (specjalny dla Dworu lub standardowy)
        back_rect = pygame.Rect(650, 530, 120, 40) if w.screen == "court" else w.back_button
        
        if back_rect.collidepoint(mx, my):
            if getattr(self, 'back_anim_timer', 0) == 0:
                if w.screen == "recruitment":
                    w.back_destination = "garrison"
                elif w.screen == "peasants":
                    w.back_destination = "castle"
                elif w.screen in ["forge", "hospital", "school", "workshop", "court", "garrison"]:
                    w.back_destination = "castle"
                elif w.screen == "castle":
                    w.back_destination = "map"
                
                w.back_anim_timer = pygame.time.get_ticks()
                print(f"Start animacji. Cel: {w.back_destination}")

            return # Zawsze przerywamy dalsze kliknięcia, jeśli trafiliśmy w POWRÓT
            
        # 4. LOGIKA GŁÓWNEGO MENU ZAMKU / STRAŻNICY
        if w.screen == "castle":
            if w.selected_castle and w.selected_castle.building_type == "Strażnica":
                if hasattr(self, 'garrison_button') and w.garrison_button.collidepoint(mx, my):
                    w.screen = "garrison"
                return 
            
            w.handle_castle_click(mx, my)
            return

        # 5. LOGIKA POD-EKRANÓW (Tylko te, które mają PRAWDZIWĄ mechanikę)
        if w.screen == "recruitment":
            w.recruitment_manager.handle_click(mx, my) # Obsługa kliknięć z nowego modułu
            return
        
        elif w.screen == "garrison":
            # Sprawdzamy, czy to Rect ZANIM wywołamy collidepoint
            is_release = False
            if hasattr(w, 'release_tower') and isinstance(w.release_tower, pygame.Rect):
                if w.release_tower.collidepoint(mx, my):
                    is_release = True
            if is_release:
                print("Akcja: Wypuszczanie zaznaczonych jednostek na mapę")
                w.release_selected_units()
                return

            # 2. Przycisk ZBURZ / ZNISZCZ (Tylko dla Strażnicy)
            if hasattr(self, 'destroy_button') and w.destroy_button.collidepoint(mx, my):
                if w.selected_castle and w.selected_castle.building_type == "Strażnica":
                    print("Akcja: Burzenie Strażnicy")
                    w.destroy_straznica(w.selected_castle)
                    return

            # 3. Jeśli nie przyciski akcji, to sprawdzamy kliknięcie w kafelki jednostek
            w.handle_garrison_click(mx, my, button)
            return

        # 6. BLOKADA DLA RESZTY (Forge, Hospital, School, Workshop, Court, Peasants)
        # Skoro mają tylko tekst i powrót (który obsłużyliśmy wyżej), 
        # po prostu blokujemy kliknięcia, żeby nie "przebijały" na mapę.
        if w.screen == "peasants":
            w.peasant_menu.handle_click(mx, my, w)
            return

        info_screens = ["forge", "hospital", "school", "workshop", "court"]
        if w.screen in info_screens:
            return
        
    def handle_mouse_up(self, mx, my):
        if self.active_dropdown:
            options = self.menu_options[self.active_dropdown]
            start_x = self.btn_system.x if self.active_dropdown == "System" else self.btn_mapa.x
            
            # Sprawdzamy, na której opcji puściliśmy przycisk
            for i, opt in enumerate(options):
                rect = pygame.Rect(start_x, 40 + (i * self.option_height), 150, self.option_height)
                if rect.collidepoint(mx, my):
                    print(f"Wybrano z menu {self.active_dropdown}: {opt}")
                    self.execute_menu_command(self.active_dropdown, i)
                    break
            
            # Po puszczeniu myszki zawsze zamykamy menu
            self.active_dropdown = None
    def handle_mouse_motion(self, mx, my):
        # Resetujemy podgląd, jeśli nie znajdziemy jednostki
        self.inspected_unit = None

        if self.screen == "garrison":
            start_x, start_y = 100, 120
            offset_x, offset_y = 130, 210
            slot_w, slot_h = 100, 180
            cols = 6

            # Sprawdzamy, czy mysz jest nad którymś ze slotów
            for i in range(len(self.selected_castle.garrison)):
                row = i // cols
                col = i % cols
                x = start_x + col * offset_x
                y = start_y + row * offset_y
                rect = pygame.Rect(x, y, slot_w, slot_h)

                if rect.collidepoint(mx, my):
                    unit = self.selected_castle.garrison[i]
                    if unit:
                        self.inspected_unit = unit
                        break
    def handle_map_click(self, mx, my, button):
        # Przeliczamy kliknięcie na współrzędne kafelków
        tile_x = (mx + self.world.camera_x) // TILE_SIZE
        tile_y = (my + self.world.camera_y) // TILE_SIZE

        # --- PRAWY PRZYCISK (Podgląd statystyk) ---
        if button == 3:
            target_unit = self.world.get_unit_at(tile_x, tile_y) 
            if target_unit:
                self.world.inspected_unit = target_unit
            return 

        # --- LEWY PRZYCISK ---
        if button == 1:
            # ========================================================
            # 1. TRYB ŁĄCZENIA JEDNOSTEK (Tylko jeśli world.merge_mode jest ON)
            # ========================================================
            if getattr(self.world, 'merge_mode', False) and self.world.selected_unit:
                target_unit = self.world.get_unit_at(tile_x, tile_y)
                
                # Jeśli kliknięto w sojusznika (i to nie jest ta sama jednostka)
                if target_unit and target_unit.owner == self.world.selected_unit.owner and target_unit != self.world.selected_unit:
                    u = self.world.selected_unit
                    
                    # Drugi klik w sojusznika -> Wykonanie marszu do połączenia
                    if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                        print("Wyruszam do połączenia armii!")
                        u.move_along_path(self.world)
                        # Po ruchu sprawdzamy, czy doszło do fuzji (logika merge jest w move_unit)
                        return # Bardzo ważne: kończymy tutaj, żeby nie zmienić zaznaczenia!
                        
                    # Pierwszy klik w sojusznika -> Wyznaczenie trasy
                    u.target_x, u.target_y = tile_x, tile_y
                    u.planned_path = self.world.pathfinder.find_path(u, tile_x, tile_y)
                    
                    if not u.planned_path:
                        u.target_x = u.target_y = None
                        print("BŁĄD: Nie można dojść do sojusznika!")
                    else:
                        print("Trasa do sojusznika wyznaczona. Kliknij jeszcze raz, aby połączyć.")
                    return # Kończymy, żeby nie przełączyło jednostki na tę klikniętą!

            # ========================================================
            # 2. STANDARDOWA LOGIKA (Wybór lub normalny ruch)
            # ========================================================
            # Sprawdzamy czy na polu stoi jakaś jednostka gracza
            clicked_unit = self.world.get_unit_at(tile_x, tile_y)
            if clicked_unit and clicked_unit.owner == self.world.players[self.world.current_player]:
                # Wybieramy nową jednostkę
                self.world.selected_unit = clicked_unit
                clicked_unit.target_x = clicked_unit.target_y = None
                clicked_unit.planned_path = []
                print(f"Wybrano jednostkę: {clicked_unit.type}")
                return

            # Jeśli mamy kogoś wybranego i kliknęliśmy w puste pole (lub wroga)
            if self.world.selected_unit:
                u = self.world.selected_unit
                
                # Potwierdzenie zwykłego ruchu (Drugi klik)
                if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                    u.move_along_path(self.world) 
                    self.world.check_unit_castle_entry(u)
                    return

                # Pierwszy klik - wyliczenie trasy marszu
                u.target_x, u.target_y = tile_x, tile_y
                u.planned_path = self.world.pathfinder.find_path(u, tile_x, tile_y)
                
                if not u.planned_path:
                    u.target_x = u.target_y = None
                    print("Nie można tam dojść!")
                return

            # 3. WEJŚCIE DO MENU ZAMKU/STRAŻNICY
            for castle in self.world.castles:
                size = 2 if castle.building_type in ["Zamek", "Twierdza"] else 1
                if castle.x <= tile_x < castle.x + size and castle.y <= tile_y < castle.y + size:
                    if not getattr(castle, 'destroyed', False):
                        self.world.selected_castle = castle # POPRAWKA: self.world
                        if castle.building_type == "Strażnica":
                            self.world.screen = "garrison" # POPRAWKA: self.world
                        else:
                            self.world.screen = "castle" # POPRAWKA: self.world
                        return
                    
    def handle_ui_click(self, mx, my, button=1):
        # 1. SPRAWDZANIE GÓRNEGO PASKA (System/Mapa/Tura)
        if self.world.show_top_ui:
            if self.handle_dropdown_clicks(mx, my): return True
            if self.world.top_ui_full_area.collidepoint(mx, my):
                if self.world.btn_system.collidepoint(mx, my): self.active_dropdown = "System"
                elif self.world.btn_mapa.collidepoint(mx, my): self.active_dropdown = "Mapa"
                elif self.world.next_turn_button.collidepoint(mx, my): self.world.next_turn()
                return True

       # --- 2. SPRAWDZANIE DOLNEJ STREFY (y >= 620) ---
        if my >= 610: # Obniżyłem lekko próg, by łapało też ramkę (zgodnie z draw_ui)
            # --- A. PRZYCISKI AKCJI ---
            for i, rect in enumerate(self.world.action_buttons):
                if rect.collidepoint(mx, my):
                    if button == 1:
                        # KLUCZOWA ZMIANA:
                        if getattr(self.world, 'build_menu_open', False):
                            # Jeśli menu budowy jest otwarte, wykonaj akcję budowy (0-5)
                            self.world.execute_build_action(i, self.world.selected_unit)
                        else:
                            # Standardowe zachowanie (Ruch, Atak, otwarcie menu budowy)
                            self.handle_action_button_click(i)
                    return True # Zablokuj mapę pod przyciskiem

            # --- B. PANEL ARMII (Po lewej stronie) ---
            u = self.world.selected_unit
            if u:
                garrison = getattr(u, 'garrison', [])
                display_units = [unit for unit in ([u] + garrison) if unit is not None]

                if len(display_units) >= 2:
                    # Sprawdzamy kliknięcia w konkretne jednostki w armii
                    if hasattr(self.world, 'army_slot_rects'):
                        for i, rect in enumerate(self.world.army_slot_rects):
                            if rect.collidepoint(mx, my):
                                print(f"Kliknięto jednostkę w armii: {display_units[i].type}")
                                # Tutaj w przyszłości dodasz kod na WYCIĄGANIE oddziału z armii
                                # np. self.world.split_army(u, display_units[i])
                                return True # Zablokuj mapę
                    
                    # Jeśli kliknąłeś w drewniane tło panelu (mx < 800), ale nie w jednostkę
                    if mx < 800: 
                        return True # Zablokuj mapę pod brązowym panelem

        return False # Zezwól na kliknięcie w mapę
    
    def handle_action_button_click(self, index):
        """Obsługuje kliknięcia w 6 przycisków akcji (0-5)."""
        u = self.world.selected_unit

        # --- KROK 1: PRIORYTET DLA MENU BUDOWANIA ---
        # Jeśli menu jest otwarte, WSZYSTKIE 6 przycisków przejmuje execute_build_action
        if getattr(self.world, 'build_menu_open', False):
            if u: # Budowanie wymaga jednostki
                self.world.execute_build_action(index, u)
            return # Ważne: kończymy tutaj, nie sprawdzamy standardowych akcji!

       # --- KROK 2: STANDARDOWE AKCJE (Gdy build_menu_open == False) ---
        
        # Indeks 0: Powrót/System
        if index == 0:
            self.handle_tryb_mapy_button()
            return

        # Indeksy 1 i 2: Przełączanie jednostek/zamków
        if index == 1:
            print("Szukam kolejnego oddziału...")
            self.world.select_next_active_unit() # Zmieniona nazwa na tę z world.py
            return
            
        elif index == 2:
            print("Szukam kolejnego zamku...")
            self.world.select_next_building() # Zmieniona nazwa na tę z world.py
            return

        # Pozostałe akcje wymagają zaznaczonej jednostki
        if not u:
            return

        if index == 3: # POŁĄCZ
            self.world.merge_mode = not getattr(self.world, 'merge_mode', False)
            print(f"Tryb łączenia: {self.world.merge_mode}")

        elif index == 4: # BUDUJ (Otwieranie menu)
            if self.world.has_builder(u):
                self.world.build_menu_open = True
                print("Otwarto menu budowania.")
            else:
                print("Brak budowniczego w oddziale!")

        elif index == 5: # UKRYCIE
            if u.type == "Generał" or getattr(u, 'level', 0) >= 6:
                if self.world.is_far_from_enemies(u, 8):
                    u.is_hidden = True
                    print(f"Oddział {u.type} został ukryty.")
                else:
                    print("Zbyt blisko wroga!")
            else:
                print("Wymagany Generał lub 6 lvl.")
    
    def handle_camera(self):
        w = self.world  # Alias dla wygody
        keys = pygame.key.get_pressed()
        
        # --- ZMIANA PRĘDKOŚCI KAMERY ---
        scroll_speed = 30  # <--- Zmień tę liczbę, aby przyspieszyć/zwolnić (np. 10, 15, 20)
        
        # Osobne flagi dla ruchu w poziomie (X) i pionie (Y)
        moving_x = False
        moving_y = False

        # === OGRANICZENIA MAPY (GRANICE KAFELKOWE) ===
        # Zakładamy, że kafelki mają 32x32 piksele
        TILE_SIZE = 32
        
        # Pobieramy prawdziwą wielkość mapy z listy w świecie (np. 100 na 100)
        if hasattr(w, 'map') and w.map:
            map_width_tiles = len(w.map[0])
            map_height_tiles = len(w.map)
        else:
            # Awaryjnie, gdyby mapy nie było, ustawiamy sztywny rozmiar
            map_width_tiles = 100
            map_height_tiles = 100

        # Pobieramy rozmiar okna dynamicznie
        screen_w = pygame.display.get_surface().get_width()
        screen_h = pygame.display.get_surface().get_height()

        # Obliczamy maksymalny wychył kamery. 
        max_x = (map_width_tiles * TILE_SIZE) - screen_w
        max_y = (map_height_tiles * TILE_SIZE) - screen_h

        # Zabezpieczenie: nie pozwala kamerze spaść poniżej 0
        max_x = max(0, max_x)
        max_y = max(0, max_y)

        # Twarda blokada (Clamp)
        w.camera_x = max(0, min(w.camera_x, max_x))
        w.camera_y = max(0, min(w.camera_y, max_y))
        
        # --- RUCH W POZIOMIE (Oś X) ---
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            w.camera_x -= scroll_speed
            moving_x = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            w.camera_x += scroll_speed
            moving_x = True

        # --- RUCH W PIONIE (Oś Y) ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            w.camera_y -= scroll_speed
            moving_y = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            w.camera_y += scroll_speed
            moving_y = True

        # === NIEZALEŻNE DOCIĄGANIE (Snapping) ===
        # Puszczasz klawisze lewo/prawo? Wyrównujemy tylko oś X!
        if not moving_x:
            w.camera_x = round(w.camera_x / TILE_SIZE) * TILE_SIZE
            
        # Puszczasz klawisze góra/dół? Wyrównujemy tylko oś Y!
        if not moving_y:
            w.camera_y = round(w.camera_y / TILE_SIZE) * TILE_SIZE

        # Ponowne, ostateczne ograniczenie mapy (aby uniknąć wyjazdu za krawędź po dociągnięciu)
        w.camera_x = max(0, min(w.camera_x, max_x))
        w.camera_y = max(0, min(w.camera_y, max_y))

    def handle_map_logic_combined(self, mx, my, button):
        # --- NOWOŚĆ: Jeśli to prawy klik, nie rób nic więcej na mapie ---
        if button == 3:
            return False
            
        gx = (mx + self.world.camera_x) // TILE_SIZE
        gy = (my + self.world.camera_y) // TILE_SIZE

        # 1. Tryby specjalne (Budowa dróg / pułapek)
        if getattr(self.world, 'trap_build_mode', False):
            self.world.execute_trap_build(gx, gy)
            return True  # <--- ZWRACA TRUE (Blokuje pojawienie się stóp)
        
        if getattr(self.world, 'road_build_mode', False):
            self.world.execute_road_build(gx, gy)
            return True  # <--- ZWRACA TRUE
            
        # 2. Kliknięcie w interaktywne obiekty mapy (Pułapka X)
        if self.world.map[gy][gx] == "X":
            self.world.screen = "trap_info"
            self.world.active_trap_pos = (gx, gy)
            return True  # <--- ZWRACA TRUE
            
        return False # Zwykłe kliknięcie, pozwól grze działać dalej
            
    def handle_tryb_mapy_button(self):
        """Resetuje interfejs do stanu 'Globus'."""
        self.world.selected_unit = None
        self.world.selected_castle = None
        self.world.build_menu_open = False
        self.world.merge_mode = False
        # --- TE 2 LINIE TRZEBA DODAĆ ---
        self.world.road_build_mode = False 
        self.world.trap_build_mode = False 
        print("Tryb mapy: Odznaczono wszystko.")
    
    
    def handle_dropdown_clicks(self, mx, my):
        #tu jest dokłana obsługa
        # def execute_menu_command(self, menu, index):
        # Sprawdzamy menu System
        #if menu == "System":
         #   if index == 5:  # "Koniec" (szósta opcja, więc indeks 5)
          #      print("Zamykanie gry...")
           #     pygame.quit()
            #    import sys
             #   sys.exit()
                
           # elif index == 2: # Zapisz grę
            #    print("Zapisywanie stanu gry...")
                # Tutaj w przyszłości dodasz self.world.save_game()
                    
        # Sprawdzamy menu Mapa
       # elif menu == "Mapa":
        #    opcja = self.world.menu_options['Mapa'][index]
         #   print(f"Wybrano opcję mapy: {opcja}")
            
          #  if index == 3: # "Nic"
           #     print("Ukrywam elementy mapy...")

        """Obsługuje kliknięcia wewnątrz rozwiniętych list System i Mapa."""
        if not self.world.active_dropdown:
            return False

        # Pobieramy przyciski dla aktualnie otwartego menu
        buttons_to_check = {}
        if self.world.active_dropdown == "System":
            buttons_to_check = getattr(self.world, 'system_buttons', {})
        elif self.world.active_dropdown == "Mapa":
            buttons_to_check = getattr(self.world, 'mapa_buttons', {})

        # Sprawdzamy kolizję dla każdej opcji w słowniku
        for name, rect in buttons_to_check.items():
            if rect.collidepoint(mx, my):
                print(f"DEBUG {self.world.active_dropdown}: Wybrano opcję -> {name}")
                
                # Tymczasowe zamykanie gry dla testów
                pygame.quit()
                import sys
                sys.exit()
                return True
                        
        return False
 
                           
    def handle_castle_entry(self, mx, my):
        """Sprawdza kliknięcie w budynki na mapie. Zwraca True, jeśli wejdzie do środka."""
        for castle in self.world.castles:
            # POBIERAMY TYP: Jeśli to Strażnica, obszar to 1x1, inaczej 2x2
            b_type = str(castle.building_type).strip()
            size = TILE_SIZE if b_type == "Strażnica" else TILE_SIZE * 2
            
            # Tworzymy prostokąt kolizji o odpowiednim rozmiarze
            rect = pygame.Rect(
                (castle.x * TILE_SIZE) - self.world.camera_x, 
                (castle.y * TILE_SIZE) - self.world.camera_y, 
                size, size
            )
            
            if rect.collidepoint(mx, my) and not getattr(castle, 'destroyed', False):
                self.world.selected_castle = castle
                self.world.selected_unit = None
                # Wybór odpowiedniego ekranu
                self.world.screen = "Strażnica" if b_type == "Strażnica" else "castle"
                print(f"Wejście do: {b_type} na {castle.x},{castle.y}")
                return True
        return False
   
    def check_unit_info(self, mx, my):
        self.world.inspected_unit = None # Reset na start
        
        # 1. Najpierw sprawdź garnizon (jeśli jesteś w zamku)
        if self.world.screen == "garrison":
            castle = self.world.selected_castle
            if castle:
                start_x, start_y = 100, 120
                offset_x, offset_y = 130, 210
                col = (mx - start_x) // offset_x
                row = (my - start_y) // offset_y
                if 0 <= col < 6 and 0 <= row < 2:
                    idx = row * 6 + col
                    if idx < len(castle.garrison):
                        self.world.inspected_unit = castle.garrison[idx]

        # 2. Jeśli nie garnizon, sprawdź mapę
        if not self.world.inspected_unit:
            self.world.inspected_unit = self.world.get_unit_at(mx, my)

        # 3. Jeśli coś znalazłeś, ustal tryb
        if self.world.inspected_unit:
            if self.world.inspected_unit.type_code in ["GOLD", "PEAS", "SPECK", "SPECM"]:
                self.world.info_mode = "SIMPLE"
            else:
                self.world.info_mode = "COMBAT"

    
    def handle_tryb_mapy_button(self):
        """Resetuje interfejs do stanu 'Globus'."""
        self.world.selected_unit = None
        self.world.selected_castle = None
        self.world.build_menu_open = False
        self.world.merge_mode = False
        print("Tryb mapy: Odznaczono wszystko.")

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        
    