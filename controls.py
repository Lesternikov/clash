import pygame
import sys
from settings import UNIT_STATS, UNIT_NAMES, TERRAIN_TYPES, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, COLOR_TO_ID, SCREEN_HEIGHT, SCREEN_WIDTH
import main

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
                # Zamiast self.screen używamy self.world.screen
                if event.key == pygame.K_ESCAPE:
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
                        self.world.check_unit_info(mx, my)
                    
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

        # 1. PRIORYTET: Ekrany specjalne
        if w.screen == "trap_info":
            w.handle_trap_info_click(mx, my)
            return
        
        if w.screen == "court":
            w.court.handle_court_click(mx, my)
            return

        if w.screen == "map":
            if self.handle_ui_click(mx, my): return 
            w.handle_map_logic_combined(mx, my, button) # Tylko sprawdza pułapki/drogi
            # Dodaj to wywołanie ręcznie, bo usunęliśmy je ze świata!
            self.handle_map_click(mx, my, button) 
            return

        # NOWE: obsługa ekranów które nie wymagają selected_castle
        if w.screen == "peasants":
            w.handle_peasants_click(mx, my)
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
            w.handle_recruitment_click(mx, my)
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
            w.handle_peasants_click(mx, my)
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
        tile_x = (mx + self.world.camera_x) // TILE_SIZE
        tile_y = (my + self.world.camera_y) // TILE_SIZE

        # --- PRAWY PRZYCISK (Podgląd statystyk) ---
        if button == 3:
            # POPRAWKA: dodano self.world.
            target_unit = self.world.get_unit_at(tile_x, tile_y) 
            if target_unit:
                self.world.inspected_unit = target_unit
            return 

        # --- LEWY PRZYCISK ---
        if button == 1:
            # 1. Zmiana zaznaczonej JEDNOSTKI
            for player in self.world.players:
                for unit in player.units:
                    if unit.x == tile_x and unit.y == tile_y:
                        if unit.owner == self.world.players[self.world.current_player]:
                            self.world.selected_unit = unit # POPRAWKA: self.world
                            unit.target_x = unit.target_y = None
                            unit.planned_path = []
                            print(f"Wybrano jednostkę: {unit.type}")
                            return

            # 2. RUCH (Jeśli kliknięto w pole, a mamy kogoś wybranego)
            if self.world.selected_unit:
                u = self.world.selected_unit # POPRAWKA: self.world
                
                # Potwierdzenie ruchu (Drugi klik w to samo miejsce)
                if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                    # POPRAWKA: Przekazujemy self.world, żeby jednostka mogła wejść w interakcję z mapą
                    u.move_along_path(self.world) 
                    self.world.check_unit_castle_entry(u) # POPRAWKA: self.world.
                    return

                # Pierwszy klik - wyliczenie trasy
                u.target_x, u.target_y = tile_x, tile_y
                # POPRAWKA: dodano self.world.
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
                    
    def handle_castle_click(self, mx, my):
        if not self.selected_castle: return
        castle = self.selected_castle
        built = set(b.lower() for b in castle.buildings)

        # 1. MENU BUDOWANIA (Najwyższy priorytet)
        if self.menu_open:
            for name, rect in self.build_rects.items():
                if rect.collidepoint(mx, my):
                    if castle.build(name):
                        self.menu_open = False
                    return
            return

        # 2. PRZYCISKI SYSTEMOWE
        if self.back_button.collidepoint(mx, my): return  # obsłużone wyżej
        if self.menu_button.collidepoint(mx, my):
            self.menu_open = not self.menu_open
            return

        # 3. MASKA KOLORÓW - jedyne źródło prawdy o kliknięciu w budynek
        clicked_id = self.castle_gfx.get_building_at_pos(mx, my, castle)

        if not clicked_id:
            return  # kliknięto w puste miejsce

        print(f"DEBUG handle_castle_click: clicked_id = {clicked_id}")

        if clicked_id in ("garrison", "koszary"):
            self.screen = "garrison"

        elif clicked_id == "peasants":
            self.screen = "peasants"

        elif clicked_id == "court":
            self.screen = "court"

        elif clicked_id in ("hospital", "workshop", "forge", "school"):
            if clicked_id in built:
                self.screen = clicked_id
            else:
                print(f"Budynek '{clicked_id}' nie jest jeszcze zbudowany.")

    def handle_ui_click(self, mx, my, button=1):
        # 1. SPRAWDZANIE GÓRNEGO PASKA
        if self.world.show_top_ui:
            # Dropdowny (System/Mapa)
            if self.world.handle_dropdown_clicks(mx, my):
                return True
            
            # Przyciski na pasku
            if self.world.top_ui_full_area.collidepoint(mx, my):
                if self.world.btn_system.collidepoint(mx, my):
                    self.active_dropdown = "System" if self.active_dropdown != "System" else None
                elif self.world.btn_mapa.collidepoint(mx, my):
                    self.active_dropdown = "Mapa" if self.active_dropdown != "Mapa" else None
                elif self.world.next_turn_button.collidepoint(mx, my):
                    self.world.next_turn()
                return True

        # 2. SPRAWDZANIE DOLNEJ STREFY (y >= 610)
        if my >= 610:
            u = self.world.selected_unit
            if not u:
                return False # Brak jednostki = dół wolny dla mapy

            # --- A. PRZYCISKI AKCJI (zawsze aktywne gdy jednostka wybrana) ---
            # Sprawdzamy, czy myszka jest DOKŁADNIE nad małym przyciskiem
            for i, rect in enumerate(self.world.action_buttons):
                if rect.collidepoint(mx, my):
                    if button == 1: 
                        self.handle_action_button_click(i)
                    return True # Kliknąłeś w konkretny przycisk - blokujemy mapę

            # --- B. PANEL ARMII (Garnizon) ---
            garrison = getattr(u, 'garrison', [])
            display_units = [unit for unit in ([u] + garrison) if unit is not None]

            if len(display_units) >= 2:
                # Jeśli jest armia, wyświetla się duży brązowy panel.
                # Sprawdzamy sloty jednostek:
                if hasattr(self, 'army_slot_rects'):
                    for i, rect in enumerate(self.army_slot_rects):
                        if rect.collidepoint(mx, my):
                            if i < len(display_units):
                                # Logika kliknięcia w jednostkę...
                                print(f"Kliknięto slot {i}")
                            return True # Kliknięto w obszar slotu - blokujemy mapę
                
                # Jeśli jest armia (panel widoczny), blokujemy CAŁY dół (0 do 1024)
                # żeby nie klikać mapy pod brązowym tłem panelu.
                if mx < 1024: 
                    return True

            # --- C. WOLNA STREFA ---
            # Jeśli jednostka jest sama (len < 2) i NIE kliknąłeś w przycisk akcji,
            # to pozwalamy na kliknięcie w mapę (np. budowanie drogi na dole).
            return False

        return False
    
    def handle_action_button_click(self, index):
        """Obsługuje kliknięcia w 6 przycisków akcji po prawej stronie panelu."""
        u = self.world.selected_unit
        if not u:
            return

        print(f"Kliknięto przycisk akcji nr: {index} dla jednostki {u.type}")

        # Przykładowa logika przycisków (możesz ją dostosować do swoich potrzeb):
        if index == 0: # Przycisk 1: Buduj (jeśli to budowniczy)
            if u.type == "BUDOW":
                self.world.road_build_mode = not getattr(self.world, 'road_build_mode', False)
                print("Tryb budowy drogi:", self.world.road_build_mode)
        
        elif index == 1: # Przycisk 2: Rozwiąż jednostkę / Usuń
            print("Akcja: Rozwiąż jednostkę (do zaimplementowania)")
            
        elif index == 5: # Przycisk 6: Czekaj / Koniec akcji
            self.world.selected_unit = None