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
                # --- NOWY WARUNEK: Zamknięcie ekranu INFO dowolnym klawiszem ---
                if self.world.screen == "unit_info":
                    # Wracamy do zapisanego ekranu lub awaryjnie do rekrutacji
                    self.world.screen = getattr(self.world, 'previous_screen', 'recruitment')
                    self.world.inspected_unit = None  # <--- DODAJ TĘ LINIJĘ
                    continue # Pomija resztę pętli, aby jedno kliknięcie nie robiło dwóch rzeczy

                # --- DEBUG: MAGIGCZNY KLAWISZ F1 ---
                if event.key == pygame.K_F1:
                    print("DEBUG: Teleportacja do koszar!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "recruitment"
                            break
                if event.key == pygame.K_F2:
                    print("DEBUG: Teleportacja do wioski!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "peasants"
                            break
                if event.key == pygame.K_F4:
                    print("DEBUG: Teleportacja do SZKOŁY!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "school" 
                            break

                if event.key == pygame.K_F3:
                    print("DEBUG: Teleportacja do dworu!")
                    for c in self.world.castles:
                        if c.owner == self.world.players[self.world.current_player]:
                            self.world.selected_castle = c
                            self.world.screen = "court"
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
                # --- Zamykanie ekranu INFO dowolnym przyciskiem myszy ---
                if self.world.screen == "unit_info":
                    self.world.screen = getattr(self.world, 'previous_screen', 'recruitment')
                    self.world.inspected_unit = None  
                    continue 
                
                # =======================================================
                # NOWOŚĆ: OBSŁUGA ROLKI MYSZY (Scrool)
                # =======================================================
                if event.button == 4 or event.button == 5:
                    if self.world.screen == "recruitment" and hasattr(self.world, 'recruitment_manager'):
                        self.world.recruitment_manager.handle_scroll_wheel(event)
                    elif self.world.screen == "peasants" and hasattr(self.world, 'peasant_menu'):
                        self.world.peasant_menu.handle_scroll_wheel(event, self.world)
                    
                    continue # Ważne: przerywamy dalszą logikę, rolka obsłużona!
                # =======================================================

                mx, my = event.pos
                
                # OBSŁUGA PRAWIEGO PRZYCISKU (WCIŚNIĘCIE)
                if event.button == 3: 
                    self.world.inspected_unit = None
                    self.world.inspected_port = None

                    if self.world.screen == "garrison":
                        self.check_unit_info(mx, my)
                    
                    elif self.world.screen == "map":
                        # 1. Sprawdzanie jednostek w dolnym panelu
                        if my >= 610 and hasattr(self.world, 'army_slot_rects'):
                            u = self.world.selected_unit
                            if u:
                                garrison = [u] + getattr(u, 'garrison', [])
                                display_units = [unit for unit in garrison if unit is not None]
                                for i, rect in enumerate(self.world.army_slot_rects):
                                    if rect.collidepoint(mx, my) and i < len(display_units):
                                        self.world.inspected_unit = display_units[i]
                                        break
                        
                        # 2. Sprawdzanie portu na mapie
                        TILE_SIZE = 32  
                        tile_x = (mx + self.world.camera_x) // TILE_SIZE
                        tile_y = (my + self.world.camera_y) // TILE_SIZE
                        
                        if hasattr(self.world, 'ports'):
                            for port in self.world.ports:
                                if port["x"] <= tile_x <= port["x"] + 1 and port["y"] <= tile_y <= port["y"] + 1:
                                    self.world.inspected_port = port
                                    self.world.inspected_unit = None 
                                    break # Znaleziono port, nie szukamy dalej

                # Wywołanie logiki kliknięć (dla lewego przycisku)
                # Jeśli trzymamy prawym na porcie, blokujemy zwykłe sprawdzanie jednostek pod nim
                if not (event.button == 3 and getattr(self.world, 'inspected_port', None)):
                    self.handle_mouse_click(mx, my, event.button)

            # --- 4. PUSZCZENIE MYSZY ---
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    # Gdy puszczamy prawy przycisk, zerujemy wyświetlanie i jednostek, i portów
                    self.world.inspected_unit = None
                    self.world.inspected_port = None

    def handle_mouse_click(self, mx, my, button):
        if button != 1 and button != 3: return
        w = self.world 

        # Zamknięcie okienka świątyni kliknięciem gdziekolwiek
        if w.screen == "temple_event":
            w.screen = "map"
            return

        # --- NOWE: OKIENKO WALKI ZBIERA KLIKNIĘCIA ---
        if w.screen == "combat_setup":
            if button == 1:
                w.combat_menu.handle_click(mx, my, w)
            return # Kończymy, żeby gracz nie "przeklikał" przez tło

        # --- DODANE: Obsługa okienka ZBURZ ZAMEK (TAK/NIE) ---
        if getattr(w, 'demolish_confirm', False):
            if hasattr(w, 'demolish_yes') and w.demolish_yes.collidepoint(mx, my):
                w.demolish_castle(w.selected_castle)
            elif hasattr(w, 'demolish_no') and w.demolish_no.collidepoint(mx, my):
                w.demolish_confirm = False
            return
        # ----------------------------------------------------

        # ====================================================
        # ---> DODAJ TO: Obsługa kliknięć w oknie przed walką
        # ====================================================
        if w.screen == "combat_setup":
            if button == 1:
                w.combat_menu.handle_click(mx, my, w)
            return # Ważne: Zatrzymujemy sprawdzanie reszty mapy!
        
        if w.screen == "combat_tactical":
            if button == 1 and hasattr(w, 'tactical_combat'):
                w.tactical_combat.handle_click(mx, my)
            return

        # 1. PRIORYTET: Ekrany specjalne
        if w.screen == "trap_info":
            w.handle_trap_info_click(mx, my)
            return
        
        if w.screen == "court":
            w.court.handle_court_click(mx, my)
            return

        # 2. Jeśli jesteśmy na mapie, używamy poprawionej logiki
        if w.screen == "map":
            if self.handle_ui_click(mx, my, button): return # Przekazujemy button!
            if self.handle_map_logic_combined(mx, my, button): return 
            
            # Prawym przyciskiem tylko info, lewym zaznaczenie
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

        # KLUCZOWA ZMIANA: Wyłączamy stary, lewy-dolny przycisk dla Strażnicy!
        if w.screen != "Strażnica":
            back_rect = pygame.Rect(650, 530, 120, 40) if w.screen == "court" else getattr(w, 'back_button', pygame.Rect(0,0,0,0))
            
            if isinstance(back_rect, pygame.Rect) and back_rect.collidepoint(mx, my):
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
                return # Przerywamy dalsze sprawdzanie

        # 4. LOGIKA GŁÓWNEGO MENU ZAMKU
        if w.screen == "castle":
            w.handle_castle_click(mx, my)
            return

        # 5. LOGIKA POD-EKRANÓW
        if w.screen == "recruitment":
            w.recruitment_manager.handle_click(mx, my)
            return
        
        # ==========================================================
        # 5.1 EKRAN ZAMKU: STARY GARNIZON
        # ==========================================================
        elif w.screen == "garrison":
            # Stare wypuszczanie wojsk w prawym dolnym rogu (jeśli go używasz w zamku)
            is_release = False
            if hasattr(w, 'release_tower') and isinstance(w.release_tower, pygame.Rect):
                if w.release_tower.collidepoint(mx, my):
                    is_release = True
            if is_release:
                w.release_selected_units()
                return

            w.handle_garrison_click(mx, my, button)
            return

        # ==========================================================
        # 5.2 EKRAN STRAŻNICY (NOWY INTERFEJS)
        # ==========================================================
        elif w.screen == "Strażnica":
            # Używamy NOWYCH zmiennych (tych ze środka ekranu z renderer.py)
            
            # 1. Przycisk POWRÓT (na czerwonym prostokącie z renderer.py)
            if hasattr(w, 'back_btn') and w.back_btn.collidepoint(mx, my):
                w.screen = "map"
                w.selected_castle = None
                return
            
            # 2. Przycisk WYPUŚĆ (na czerwonym prostokącie)
            if hasattr(w, 'release_btn') and w.release_btn.collidepoint(mx, my):
                w.release_selected_units()
                return
            
            # 3. Przycisk ZNISZCZ (na czerwonym prostokącie)
            if hasattr(w, 'destroy_btn') and w.destroy_btn.collidepoint(mx, my):
                w.destroy_straznica(w.selected_castle)
                w.screen = "map"
                w.selected_castle = None
                return
            
            # 4. Sloty na wojsko
            if hasattr(w, 'handle_straznica_click'):
                w.handle_straznica_click(mx, my, button)
            else:
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
        # 1. ZAWSZE na początku ruchu usuwamy podgląd!
        self.world.inspected_unit = None 

        if self.world.screen == "garrison":
            start_x, start_y = 100, 120
            offset_x, offset_y = 130, 210
            slot_w, slot_h = 100, 180
            cols = 6

            # Sprawdzamy, czy mysz jest nad którymś ze slotów
            if hasattr(self.world, 'selected_castle') and self.world.selected_castle:
                for i in range(len(self.world.selected_castle.garrison)):
                    row = i // cols
                    col = i % cols
                    x = start_x + col * offset_x
                    y = start_y + row * offset_y
                    rect = pygame.Rect(x, y, slot_w, slot_h)

                    if rect.collidepoint(mx, my):
                        unit = self.world.selected_castle.garrison[i]
                        if unit:
                            self.world.inspected_unit = unit
                            break
    def handle_map_click(self, mx, my, button):
        # Wyjście z ekranu INFO po kliknięciu
        if self.world.screen == "unit_info":
            # Wracamy do zapisanego poprzedniego ekranu (np. 'recruitment')
            self.world.screen = getattr(self.world, 'previous_screen', 'castle')
            return
        
        # Przeliczamy kliknięcie na współrzędne kafelków
        tile_x = (mx + self.world.camera_x) // TILE_SIZE
        tile_y = (my + self.world.camera_y) // TILE_SIZE

       # --- PRAWY PRZYCISK: TYLKO INFORMACJA (O pojedynczych jednostkach) ---
        if button == 3:
            target_unit = self.world.get_unit_at(tile_x, tile_y) 
            if target_unit:
                # Sprawdzamy czy to armia (czy ma kogoś w garnizonie)
                garrison = getattr(target_unit, 'garrison', [])
                has_passengers = any(p is not None for p in garrison)
                
                # Jeśli to armia, NIC NIE RÓB (nie zaznaczaj, nie otwieraj info)
                if has_passengers:
                    print("To jest armia! Statystyki sprawdzaj w dolnym panelu.")
                else:
                    # Jeśli to pojedyncza jednostka, pokazujemy statystyki
                    self.world.inspected_unit = target_unit
            return # Zwracamy, żeby nie zaznaczyć jednostki lewym przyciskiem

       # --- LEWY PRZYCISK ---
        if button == 1:
            # 0. TRYB PODZIAŁU ARMII (Najwyższy priorytet na mapie)
            if hasattr(self.world, 'units_to_split') and len(self.world.units_to_split) > 0:
                self.world.execute_army_split(tile_x, tile_y)
                return
            # 1. Sprawdzamy, czy kliknęliśmy w jakąś naszą jednostkę
            target_unit = self.world.get_unit_at(tile_x, tile_y)
            
            if target_unit and target_unit.owner == self.world.players[self.world.current_player]:
                
                # A. SCENARIUSZ: Przycisk POŁĄCZ JEST WŁĄCZONY i klikamy w inną naszą jednostkę
                if self.world.selected_unit and target_unit != self.world.selected_unit and getattr(self.world, 'merge_mode', False):
                    u = self.world.selected_unit
                    
                    # --- 1. DRUGI KLIK -> Wyruszamy na połączenie ---
                    if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                        print("Wyruszam do połączenia armii!")
                        u.move_along_path(self.world)
                        return 
                        
                    # --- 2. PIERWSZY KLIK -> Wyznaczenie trasy do kolegi ---
                    u.target_x, u.target_y = tile_x, tile_y
                    
                    # Szukamy standardowej trasy
                    u.planned_path = self.world.pathfinder.find_path(u, tile_x, tile_y)
                    
                    # Jeśli nie ma trasy (bo algorytm uważa, że na pole sojusznika nie da się wejść):
                    if not u.planned_path:
                        # A) Jeśli jesteśmy bezpośrednio obok niego - trasa to po prostu wejście w niego
                        if abs(u.x - tile_x) <= 1 and abs(u.y - tile_y) <= 1:
                            u.planned_path = [(tile_x, tile_y)]
                            print("Jesteś obok. Kliknij jeszcze raz, aby połączyć.")
                        # B) Jeśli jest daleko, szukamy trasy na pole OBOK sojusznika
                        else:
                            sasiedzi = [
                                (tile_x-1, tile_y), (tile_x+1, tile_y), (tile_x, tile_y-1), (tile_x, tile_y+1),
                                (tile_x-1, tile_y-1), (tile_x+1, tile_y+1), (tile_x-1, tile_y+1), (tile_x+1, tile_y-1)
                            ]
                            najlepsza_trasa = None
                            
                            for nx, ny in sasiedzi:
                                if 0 <= nx < len(self.world.map[0]) and 0 <= ny < len(self.world.map):
                                    t = self.world.pathfinder.find_path(u, nx, ny)
                                    if t is not None:
                                        if najlepsza_trasa is None or len(t) < len(najlepsza_trasa):
                                            najlepsza_trasa = t
                                            
                            if najlepsza_trasa is not None:
                                # Doklejamy "ręcznie" ostatni krok - wskoczenie w pole sojusznika
                                u.planned_path = najlepsza_trasa + [(tile_x, tile_y)]
                                print("Trasa wyznaczona obok. Kliknij jeszcze raz, aby połączyć.")
                            else:
                                u.target_x = u.target_y = None
                                print("BŁĄD: Nie można dojść do sojusznika!")
                    else:
                        print("Trasa wyznaczona bezpośrednio. Kliknij jeszcze raz, aby połączyć.")
                    return

                # B. SCENARIUSZ: Przycisk POŁĄCZ JEST WYŁĄCZONY (albo klikamy tę samą jednostkę) -> ZAZNACZAMY JĄ
                self.world.selected_unit = target_unit
                self.world.units_to_split = [] # <--- NOWOŚĆ: Resetowanie krzyżyków!
                target_unit.target_x = target_unit.target_y = None
                target_unit.planned_path = []
                self.world.merge_mode = False # Na wszelki wypadek resetujemy tryb
                print(f"Wybrano jednostkę: {target_unit.type}")
                return

            # ========================================================
            # 2. STANDARDOWA LOGIKA RUCHU (Kliknięcie w ziemię/wroga)
            # ========================================================
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
            # 3. WEJŚCIE DO MENU ZAMKU/STRAŻNICY (Z blokadą właściciela i rozmiarem)
            for castle in self.world.castles:
                # Ubezpieczamy się przed spacjami w nazwie
                b_type = str(getattr(castle, 'building_type', 'Zamek')).strip()
                size = 2 if b_type in ["Zamek", "Twierdza"] else 1
                
                if castle.x <= tile_x < castle.x + size and castle.y <= tile_y < castle.y + size:
                    if not getattr(castle, 'destroyed', False):
                        
                        print(f"\n--- KLIKNIĘTO BUDYNEK ---")
                        print(f"Typ: '{b_type}', W budowie?: {getattr(castle, 'under_construction', False)}")
                        
                        # ========================================================
                        # --- NOWA BLOKADA: Z użyciem flagi under_construction ---
                        # ========================================================
                        if getattr(castle, 'under_construction', False):
                            print(f"Blokada! {b_type} jest w trakcie budowy. Musisz poczekać na ukończenie!")
                            return # Przerywamy całkowicie kliknięcie!
                        # ========================================================

                        # SPRAWDZENIE WŁAŚCICIELA 
                        current_player_obj = self.world.players[self.world.current_player]
                        
                        if castle.owner == current_player_obj:
                            self.world.selected_castle = castle
                            
                            # --- ROZDZIELENIE EKRANÓW JUŻ NA MAPIE ---
                            if b_type == "Strażnica":
                                self.world.screen = "Strażnica"
                                print("Sukces: Otwieram menu Strażnicy!")
                                return
                            else:
                                self.world.screen = "castle"
                                if hasattr(self.world, 'recruitment_manager'):
                                    self.world.recruitment_manager.selected_patent_index = None
                                print("Sukces: Otwieram menu Zamku!")
                                return
                        else:
                            print("Odmowa: To nie jest Twój budynek!")     
    def handle_ui_click(self, mx, my, button=1):
        w = self.world
        
        # 0. ZAWSZE najpierw sprawdzamy rozwinięte zwoje (blokuje to klikanie "przez" pergamin)
        if self.handle_dropdown_clicks(mx, my):
            return True

        # 1. GÓRNY PASEK
        if getattr(w, 'show_top_ui', False):
            if w.top_ui_full_area.collidepoint(mx, my):
                if hasattr(w, 'btn_system') and w.btn_system.collidepoint(mx, my):
                    w.active_dropdown = "System" if w.active_dropdown != "System" else None
                    return True
                elif hasattr(w, 'btn_mapa') and w.btn_mapa.collidepoint(mx, my):
                    w.active_dropdown = "Mapa" if w.active_dropdown != "Mapa" else None
                    return True
                elif hasattr(w, 'next_turn_button') and w.next_turn_button.collidepoint(mx, my):
                    w.next_turn()
                    return True
            else:
                # Jeśli zjechaliśmy myszką z paska i kliknęliśmy obok - zwijamy
                if getattr(w, 'active_dropdown', None):
                    w.active_dropdown = None

        # 2. PRZYCISK "MENU" W ZAMKU (Zielony baner na łańcuchach)
        if w.screen == "castle":
            if hasattr(w, 'menu_button') and w.menu_button.collidepoint(mx, my):
                w.menu_open = not getattr(w, 'menu_open', False)
                return True

        # 3. DOLNA STREFA (Przyciski akcji, Armia)
        if my >= 610:
            for i, rect in enumerate(w.action_buttons):
                if rect.collidepoint(mx, my):
                    if button == 1:
                        if getattr(w, 'build_menu_open', False):
                            w.execute_build_action(i, w.selected_unit)
                        else:
                            self.handle_action_button_click(i)
                    return True 

            u = w.selected_unit
            if u:
                garrison = getattr(u, 'garrison', [])
                display_units = [unit for unit in ([u] + garrison) if unit is not None]

                if len(display_units) >= 2:
                    if hasattr(w, 'army_slot_rects'):
                        for i, rect in enumerate(w.army_slot_rects):
                            if i < len(display_units) and rect.collidepoint(mx, my):
                                clicked_u = display_units[i]
                                
                                if button == 1:
                                    # LEWY PRZYCISK: Zaznaczanie do podziału
                                    if not hasattr(w, 'units_to_split'): w.units_to_split = []
                                    if clicked_u in w.units_to_split:
                                        w.units_to_split.remove(clicked_u)
                                    else:
                                        w.units_to_split.append(clicked_u)
                                elif button == 3:
                                    # PRAWY PRZYCISK: Pokaż statystyki jednostki
                                    w.inspected_unit = clicked_u
                                    
                                return True
                    
                    if mx < 800: 
                        return True

        return False # Zezwól na kliknięcie w mapę
    
    def handle_action_button_click(self, index):
        """Obsługuje kliknięcia w 6 przycisków akcji (0-5)."""
        u = self.world.selected_unit

        # --- KROK 1: PRIORYTET DLA MENU BUDOWANIA ---
        if getattr(self.world, 'build_menu_open', False):
            if u: 
                self.world.execute_build_action(index, u)
            return 

        # --- KROK 2: STANDARDOWE AKCJE ---
        
        # Indeks 0: Powrót/System
        if index == 0:
            self.handle_tryb_mapy_button()
            return

        # Indeks 1: Przełączanie jednostek
        if index == 1:
            print("Szukam kolejnego oddziału...")
            self.world.select_next_active_unit() 
            return
            
        # Indeks 2: Przełączanie zamków
        elif index == 2:
            print("Szukam kolejnego zamku...")
            # Natychmiastowe odznaczenie jednostki (Włączenie trybu świata)
            if self.world.selected_unit:
                self.world.selected_unit.target_x = None
                self.world.selected_unit.target_y = None
                self.world.selected_unit.planned_path = []
                self.world.selected_unit = None
            
            self.world.merge_mode = False
            self.world.select_next_building() 
            return

        # ==============================================================
        # BLOKADA: Akcje 3, 4, 5 ABSOLUTNIE WYMAGAJĄ zaznaczonej jednostki!
        # ==============================================================
        if not u:
            print(f"Zablokowano kliknięcie w przycisk {index} - brak wybranej jednostki!")
            self.world.merge_mode = False # Twardy reset dla bezpieczeństwa
            return

        # Indeks 3: POŁĄCZ ARMIE
        if index == 3: 
            self.world.merge_mode = not getattr(self.world, 'merge_mode', False)
            print(f"Tryb łączenia: {self.world.merge_mode}")

        # Indeks 4: BUDOWANIE (Otwieranie menu)
        elif index == 4: 
            if self.world.has_builder(u):
                self.world.build_menu_open = True
                print("Otwarto menu budowania.")
            else:
                print("Brak budowniczego w oddziale!")

        # Indeks 5: UKRYCIE W LESIE
        elif index == 5: 
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

        # Zabezpieczenie przed kliknięciem poza granice mapy (TO ROZWIĄZUJE PROBLEM)
        if gy < 0 or gy >= len(self.world.map) or gx < 0 or gx >= len(self.world.map[0]):
            return False

        # =========================================================
        # INTERAKCJA ZE ŚWIĄTYNIĄ I MIEJSCEM KULTU
        # =========================================================
        if self.world.map[gy][gx] in ["S", "&"]: 
            unit = self.world.selected_unit
            if unit:
                dx = abs(unit.x - gx)
                dy = abs(unit.y - gy)
                
                # --- Sytuacja A: Jednostka stoi obok ---
                if dx <= 1 and dy <= 1:
                    # NOWOŚĆ: Obliczanie kosztu wejścia
                    koszt_wejscia = 4 if dx == 1 and dy == 1 else 3
                    
                    if unit.move_points >= koszt_wejscia:
                        unit.move_points -= koszt_wejscia # Zabieramy punkty!
                        self.world.visit_temple(unit, gx, gy)
                    else:
                        print(f"Za mało punktów ruchu, aby wejść! Wymagane: {koszt_wejscia}, Posiadane: {unit.move_points}")
                    
                    # Czyścimy ścieżkę niezależnie od tego, czy weszliśmy czy zabrakło nam MP
                    unit.planned_path = []
                    unit.target_x = None
                    unit.target_y = None
                    return True
                    
                # --- Sytuacja B: Wyznaczamy marsz i automatycznie odbieramy w tej samej turze ---
                else:
                    # DRUGI KLIK - Potwierdzenie marszu
                    if gx == getattr(unit, 'target_x', None) and gy == getattr(unit, 'target_y', None):
                        unit.move_along_path(self.world)
                        
                        # Sprawdzamy nową pozycję OD RAZU po dojściu
                        new_dx = abs(unit.x - gx)
                        new_dy = abs(unit.y - gy)
                        
                        if new_dx <= 1 and new_dy <= 1:
                            koszt_wejscia = 4 if new_dx == 1 and new_dy == 1 else 3
                            
                            if unit.move_points >= koszt_wejscia:
                                unit.move_points -= koszt_wejscia
                                self.world.visit_temple(unit, gx, gy)
                            else:
                                print(f"Doszedłeś pod drzwi, ale brakło sił na wejście! Wymagane: {koszt_wejscia}")
                                
                            unit.planned_path = []
                            unit.target_x = None
                            unit.target_y = None
                        return True

                    # PIERWSZY KLIK - Trasa
                    sasiedzi = [(gx-1, gy), (gx+1, gy), (gx, gy-1), (gx, gy+1)]
                    najlepsza_trasa = None
                    
                    for nx, ny in sasiedzi:
                        if 0 <= nx < len(self.world.map[0]) and 0 <= ny < len(self.world.map):
                            # Korzystamy z Pathfindera
                            if hasattr(self.world, 'pathfinder') and hasattr(self.world.pathfinder, 'is_walkable'):
                                if self.world.pathfinder.is_walkable(nx, ny, unit):
                                    path = self.world.pathfinder.find_path(unit, nx, ny)
                                    if path and (najlepsza_trasa is None or len(path) < len(najlepsza_trasa)):
                                        najlepsza_trasa = path
                                        
                    if najlepsza_trasa is not None:
                        unit.target_x, unit.target_y = gx, gy
                        unit.planned_path = najlepsza_trasa + [(gx, gy)] # Rysuje X na świątyni
                        print(f"Podchodzę do świątyni...")
                    else:
                        unit.target_x = None
                        unit.target_y = None
                        unit.planned_path = []
                        print("Brak dojścia do świątyni!")
                        
            return True # Przerywamy dalsze kliknięcia
        
        # 1. Tryby specjalne (Budowa dróg / pułapek)
        if getattr(self.world, 'trap_build_mode', False):
            self.world.execute_trap_build(gx, gy)
            return True  # <--- ZWRACA TRUE (Blokuje pojawienie się stóp)
        
        if getattr(self.world, 'road_build_mode', False):
            self.world.execute_road_build(gx, gy)
            return True  # <--- ZWRACA TRUE
            
        # 2. Kliknięcie w interaktywne obiekty mapy (Pułapka X)
        if self.world.map[gy][gx] == "X":
            trap = getattr(self.world, 'traps', {}).get((gx, gy))
            if trap:
                current_player = self.world.players[self.world.current_player]
                # Pozwalamy kliknąć w X tylko jeśli jest to nasza pułapka ALBO jeśli ją wykryliśmy!
                if trap["owner"] == current_player or current_player in trap.get("detected_by", set()):
                    self.world.screen = "trap_info"
                    self.world.active_trap_pos = (gx, gy)
                    return True
            # Jeśli pułapki nie widzimy, traktujemy to jak kliknięcie w zwykłą ziemię
            return False
            
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

        """Obsługuje kliknięcia we WSZYSTKIE rozwinięte pergaminy w grze."""
        w = self.world

        # ==========================================
        # A. SPRAWDZANIE ZWOJÓW GÓRNEGO PASKA
        # ==========================================
        if getattr(w, 'active_dropdown', None):
            buttons_to_check = getattr(w, 'system_buttons', {}) if w.active_dropdown == "System" else getattr(w, 'mapa_buttons', {})
            
            # WYDRUK KONTROLNY: Zobaczmy, ile przycisków widzi Python
            print(f"TEST: Próbuję kliknąć w menu '{w.active_dropdown}'. Znaleziono {len(buttons_to_check)} przycisków.")
            
            for name, rect in buttons_to_check.items():
                if rect.collidepoint(mx, my):
                    print(f"BINGO! Kliknięto w opcję: {name}")
                    
                    if name == "Koniec":
                        import pygame, sys
                        pygame.quit()
                        sys.exit()
                    elif name == "Siatka":
                        w.show_grid = not getattr(w, 'show_grid', False)
                    
                    w.active_dropdown = None
                    return True
            
            print("PUDŁO: Kliknięcie nie trafiło w żaden czerwony prostokąt!")

        # ==========================================
        # B. SPRAWDZANIE ZIELONEGO MENU W ZAMKU
        # ==========================================
        if getattr(w, 'menu_open', False):
            if getattr(w, 'build_open', False):
                for name, rect in getattr(w, 'build_rects', {}).items():
                    if rect.collidepoint(mx, my):
                        print(f"BINGO ZAMEK: Zlecono budowę: {name}")
                        w.build_open = False
                        w.menu_open = False
                        return True

            for name, rect in getattr(w, 'menu_rects', {}).items():
                if rect.collidepoint(mx, my):
                    print(f"BINGO ZAMEK: Akcja -> {name}")
                    if name == "ZBURZ ZAMEK":
                        w.demolish_confirm = True
                        w.menu_open = False
                        return True
                    elif name == "Buduj":
                        return True
                        
            if mx < getattr(w, 'menu_options_start_x', 800) - 170:
                w.menu_open = False
                w.build_open = False

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
            
            # NAJPIERW sprawdzamy czy myszka trafiła w ten budynek
            if rect.collidepoint(mx, my) and not getattr(castle, 'destroyed', False):
                
                # --- BLOKADA W DRUGIEJ FUNKCJI ---
                # DOPIERO TERAZ sprawdzamy czy TEN kliknięty budynek jest w budowie
                if getattr(castle, 'under_construction', False):
                    print(f"Zablokowano wejście (handle_castle_entry)! Budynek w budowie.")
                    return False # Przerywamy wejście do budynku
                # ---------------------------------
                
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
        
    