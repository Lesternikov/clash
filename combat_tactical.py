import pygame
import os
import heapq

class TacticalCombat:
    def __init__(self, world, attacker, defender):
        self.world = world
        self.attacker = attacker
        self.defender = defender
        
        # 1. POBRANIE WYMIARÓW EKRANU
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()

        # --- SYSTEM TUR ---
        self.active_player = self.attacker.owner  

        # =========================================================
        # 2. ŁADOWANIE KURSORÓW I ZNACZNIKÓW
        # =========================================================
        self.cursor_scale = 1.2 
        self.cursor_select = self._load_and_scale(["assets/minimum/MOUSE_S32/MOUSE_S32_2.png"], self.cursor_scale)
        self.cursor_move = self._load_and_scale(["assets/minimum/MOUSE_S32/MOUSE_S32_3.png"], self.cursor_scale)
        self.cursor_attack = self._load_and_scale(["assets/minimum/MOUSE_S32/MOUSE_S32_4.png"], self.cursor_scale)
        self.cursor_no = self._load_and_scale(["assets/minimum/MOUSE_S32/MOUSE_S32_10.png"], self.cursor_scale)
        
        self.shield_icon = self._load_and_scale(["assets/minimum/MARKS_S32/MARKS_S32_16.png"], 1.5)

        self.selected_unit = None
        self.selected_pos = None
        self.reachable_tiles = {}

        # =========================================================
        # 3. ŁADOWANIE RAMKI
        # =========================================================
        self.panel_scale = 1.6  
        
        self.frame_0 = self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_0.png"], self.panel_scale)
        self.frame_1 = self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_1.png"], self.panel_scale)
        self.frame_2 = self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_2.png"], self.panel_scale)
        self.frame_3 = self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_3.png"], self.panel_scale)

        w0 = self.frame_0.get_width() if self.frame_0 else 200
        h0 = self.frame_0.get_height() if self.frame_0 else 200
        w1 = self.frame_1.get_width() if self.frame_1 else 250
        h2 = self.frame_2.get_height() if self.frame_2 else 200

        ui_total_w = w0 + w1
        ui_total_h = h0 + h2

        self.ui_x = max(0, (self.screen_width - ui_total_w) // 2)
        self.ui_y = max(0, (self.screen_height - ui_total_h) // 2)

        self.pos_f0 = (self.ui_x, self.ui_y)                 
        self.pos_f1 = (self.ui_x + w0, self.ui_y)            
        self.pos_f2 = (self.ui_x, self.ui_y + h0)            
        self.pos_f3 = (self.ui_x + w0, self.ui_y + h0)       

        border_left = int(33 * self.panel_scale)
        border_top = int(17 * self.panel_scale)
        border_bottom = int(14 * self.panel_scale)
        panel_width = int(160 * self.panel_scale) 

        self.arena_rect = pygame.Rect(
            self.ui_x + border_left,
            self.ui_y + border_top,
            ui_total_w - border_left - panel_width,
            ui_total_h - border_top - border_bottom
        )

        # =========================================================
        # 4. PRZYCISKI AKCJI (Na prawym panelu)
        # =========================================================
        self.action_btns_gfx = {
            "ODWROT": (self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_9.png"], self.panel_scale),
                       self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_10.png"], self.panel_scale)),
            "ATAK_WRECZ": (self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_3.png"], self.panel_scale),
                           self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_4.png"], self.panel_scale)),
            "ATAK_DYSTANS": (self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_7.png"], self.panel_scale),
                             self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_8.png"], self.panel_scale)),
            "OBRONA": (self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_5.png"], self.panel_scale),
                       self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_6.png"], self.panel_scale)),
            "NASTEPNA_JEDNOSTKA": (self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_1.png"], self.panel_scale),
                                   self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_2.png"], self.panel_scale))
        }

        self.btn_offsets = {
            "ODWROT": (227, 400),
            "ATAK_WRECZ": (164, 369),
            "ATAK_DYSTANS": (164, 400),
            "OBRONA": (164, 431),
            "NASTEPNA_JEDNOSTKA": (227, 369) 
        }

        self.action_rects = {}
        for action, offset in self.btn_offsets.items():
            normal_img, _ = self.action_btns_gfx[action]
            if normal_img:
                bw, bh = normal_img.get_size()
                bx = self.pos_f1[0] + int(offset[0] * self.panel_scale)
                by = self.pos_f1[1] + int(offset[1] * self.panel_scale)
                self.action_rects[action] = pygame.Rect(bx, by, bw, bh)
            else:
                self.action_rects[action] = pygame.Rect(0, 0, 0, 0)

        # =========================================================
        # 5. NOWOŚĆ: BAZA TŁA I ANIMACJI DLA KAŻDEGO SLOTU!
        # =========================================================
        # Zamiast wczytywać wyrywkowo, ładujemy do pamięci wszystko, co dałeś (ok. 120 klatek)
        self.anim_cache = {}
        for i in range(120): 
            path = f"assets/minimum/FR_ANIM_S32/FR_ANIM_S32_{i}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha() 
                if self.panel_scale != 1.0:
                    new_w = int(img.get_width() * self.panel_scale)
                    new_h = int(img.get_height() * self.panel_scale)
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                self.anim_cache[i] = img

        # 🟢 TUTAJ USTAWIASZ BAZOWE INDEKSY DLA KAŻDEGO Z 6 PÓŁ! 🟢
        # Liczba oznacza "czystą" klatkę panelu. Kolejne 8 klatek (+1 do +8) to zamykanie.
        self.slot_base_indices = {
            "slot_1": 36,  # Ruch (Tymczasowo szary dym. Jeśli masz klatkę biegnącego ludzika, wpisz jej numer np. 108)
            "slot_2": 81,  # Atak (Biceps)
            "slot_3": 90,  # Dystans (Łuk)
            "slot_4": 99,  # Obrona (Magia/Klejnot)
            "slot_5": 45,  # Morale (Uśmiechnięta twarz)
            "slot_6": 0,    # Doświadczenie (Biały posąg)
        }

        # Zostawiamy Twoje offsety, żeby rysowało się tam gdzie trzeba!
        self.anim_offsets = {
            "slot_1": (164, 144),
            "slot_2": (164, 177),
            "slot_3": (164, 211),
            "slot_4": (164, 315),
            "slot_5": (164, 279),
            "slot_6": (164, 245)
        }

        # Stany odtwarzacza: "open" = 0, "closed" = 8, "closing" animuje od 0 do 8.
        self.panel_anim_state = "closed" 
        self.panel_anim_idx = 8 
        self.last_anim_tick = 0

        # =========================================================
        # 6. POZOSTAŁE GRAFIKI STATYSTYK I CZCIONKI
        # =========================================================
        self.stat_gfx = {
            "hp_sword": self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_10.png"], self.panel_scale),
            "arrow": self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_11.png"], self.panel_scale),
            "exp_sword": self._load_and_scale(["assets/minimum/FRAME_S32/FRAME_S32_13.png"], self.panel_scale)
        }

        # 🟢 TUTAJ PRZESUWASZ STATYSTYKI JEDNOSTKI! 🟢
        # top_... oznaczają odległość od lewej-górnej krawędzi GÓRNEJ ramki (pos_f1)
        # bot_... oznaczają odległość od lewej-górnej krawędzi DOLNEJ ramki (pos_f3)
        self.stat_offsets = {
            "top_hp_sword": (200, 26),
            "top_hp_text": (268, 64),
            
            "top_moves_text": (250, 105),   # Obok gościa w biegu
            "top_attack_text": (258, 145),  # Obok bicepsa
            "top_defense_text": (258, 215), # Obok tarczy
            
            "top_arrows_start": (200, 180), # Obok łuku (Tu rysują się strzały)
            
            "bot_morale_face": (164, 36),
            "bot_morale_text": (258, 40),
            
            "bot_exp_statue": (154, 0),    # Wielkie okno na dole
            "bot_exp_swords": (220, 12)    # Mieczyki doświadczenia obok posągu
        }
        
        self.font_stats = pygame.font.SysFont("Times New Roman", int(22 * self.panel_scale), bold=True)
        self.font_hp = pygame.font.SysFont("Times New Roman", int(14 * self.panel_scale), bold=True) # Mniejsza dla HP
        self.font_pa = pygame.font.SysFont("Times New Roman", int(26 * self.panel_scale), bold=True) # Większa dla PA


        # =========================================================
        # 7. POP-UP ODWROTU I TŁO "NASTĘPNA TURA"
        # =========================================================
        self.show_retreat_popup = False
        self.rect_confirm = pygame.Rect(0, 0, 0, 0)
        self.rect_cancel = pygame.Rect(0, 0, 0, 0)
        
        self.popup_bgs = {
            "red": self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_0.png"], self.panel_scale),
            "blue": self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_1.png"], self.panel_scale),
            "yellow": self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_2.png"], self.panel_scale),
            "white": self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_3.png"], self.panel_scale),
            "green": self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_4.png"], self.panel_scale),
        }
        
        self.btn_confirm_gfx = (
            self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_5.png"], self.panel_scale),
            self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_6.png"], self.panel_scale)
        )
        self.btn_cancel_gfx = (
            self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_7.png"], self.panel_scale),
            self._load_and_scale(["assets/minimum/OKNO1_S32/OKNO1_S32_8.png"], self.panel_scale)
        )

        self.show_top_ui = False
        self.top_trigger_area = pygame.Rect(self.screen_width - 250, 0, 250, 15) 
        self.btn_next_turn_img = self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_13.png"], self.panel_scale)
        self.btn_next_turn_bg = self._load_and_scale(["assets/minimum/BUTTONS_S32/BUTTONS_S32_12.png"], self.panel_scale)

        if self.btn_next_turn_img:
            btn_turn_w = self.btn_next_turn_img.get_width()
            btn_turn_h = self.btn_next_turn_img.get_height()
        else:
            btn_turn_w = int(220 * self.panel_scale)
            btn_turn_h = int(50 * self.panel_scale)
            
        self.btn_next_turn = pygame.Rect(self.screen_width - btn_turn_w - 10, 0, btn_turn_w, btn_turn_h)
        self.font_turn = pygame.font.SysFont("Arial", int(20 * self.panel_scale), bold=True)

        # =========================================================
        # 8. INICJALIZACJA ARENY I ARMII
        # =========================================================
        self.tile_size = int(103) 
        self.grid_width = 16  
        self.grid_height = 7 
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.bg_tile = self._create_desert_tile()
        
        self.att_army = self._get_full_army(attacker)
        self.def_army = self._get_full_army(defender)
        
        self.arena_units = {}
        self._deploy_armies()
        self._auto_select_unit() # Zaznacza jednostkę od razu na starcie!

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
        color_id = "1" if unit.owner and getattr(unit.owner, 'color_name', 'red') == "red" else "2"
        prefix = unit.type.upper()[:5] 
        if unit.type == "Budowniczy": prefix = "BUDOW"
        if unit.type == "Generał": prefix = "GENER" 
        
        folder_name = f"{prefix}{color_id}_S32"  
        file_name = f"{prefix}{color_id}_16.png"  
        
        path = os.path.join("assets", "normal", folder_name, file_name)
        path_alt = os.path.join("assets", "normal", folder_name, f"{prefix}{color_id}_S32_16.png")
        
        for p in [path, path_alt]:
            if os.path.exists(p):
                return pygame.image.load(p).convert_alpha()
                
        if hasattr(unit, 'walk_frames') and unit.walk_frames:
            return unit.walk_frames[0]
        elif hasattr(unit, 'sprites') and unit.sprites:
            return unit.sprites[0]
            
        return None

    def _create_desert_tile(self):
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill((230, 240, 250)) 
        pygame.draw.rect(surface, (180, 190, 200), (0, 0, self.tile_size, self.tile_size), 1)
        srodek = self.tile_size // 2
        pygame.draw.line(surface, (150, 160, 180), (srodek - 5, srodek), (srodek + 5, srodek), 1)
        pygame.draw.line(surface, (150, 160, 180), (srodek, srodek - 5), (srodek, srodek + 5), 1)
        return surface

    def _get_full_army(self, leader):
        army = [leader]
        if hasattr(leader, 'garrison') and leader.garrison:
            army.extend([u for u in leader.garrison if u is not None])
        return army

    def _deploy_armies(self):
        start_y = max(0, (self.grid_height - len(self.att_army)) // 2)
        idx = 0
        for x in range(3): 
            for y in range(start_y, self.grid_height):
                if idx < len(self.att_army):
                    self.arena_units[(x, y)] = self.att_army[idx]
                    idx += 1
                else: break
        
        start_y_def = max(0, (self.grid_height - len(self.def_army)) // 2)
        idx = 0
        for x in range(self.grid_width - 1, self.grid_width - 4, -1):
            for y in range(start_y_def, self.grid_height):
                if idx < len(self.def_army):
                    self.arena_units[(x, y)] = self.def_army[idx]
                    idx += 1
                else: break

        for u in self.att_army + self.def_army:
            u.combat_ap = getattr(u, 'moves', 5)
            u.combat_defending = False
            u.combat_charge = False
            
            # --- ZMIANA: ROZDZIELENIE ZDOLNOŚCI OD STANU WCIŚNIĘCIA ---
            ranged_types = ["Łucznik", "Kusznik", "Leśnik", "Katapulta", "Kusznik z gildii", "Elf"]
            if u.type in ranged_types:
                u.can_shoot = True
                u.combat_ranged = True # Domyślnie włączone dla strzelców
            else:
                u.can_shoot = False
                u.combat_ranged = False

    # =========================================================
    # SILNIK LOGIKI MYSZY I ŚCIEŻEK
    # =========================================================
    def _find_unit_pos(self, unit):
        for pos, u in self.arena_units.items():
            if u == unit: return pos
        return None

    def _auto_select_unit(self):
        """Automatycznie szuka i zaznacza pierwszą z brzegu jednostkę gracza."""
        my_units = [u for pos, u in self.arena_units.items() if u.owner == self.active_player]
        if my_units:
            active_units = [u for u in my_units if u.combat_ap > 0]
            if active_units:
                self._select_unit(active_units[0])
                pos = self._find_unit_pos(active_units[0])
                if pos: self.center_camera_on(pos[0], pos[1])
            else:
                self._select_unit(my_units[0])
                pos = self._find_unit_pos(my_units[0])
                if pos: self.center_camera_on(pos[0], pos[1])

    def _select_next_unit(self):
        """Przeskakuje na kolejną jednostkę, która ma jeszcze PA."""
        my_units = [u for pos, u in self.arena_units.items() if u.owner == self.active_player and u.combat_ap > 0]
        if my_units:
            current_idx = -1
            if self.selected_unit in my_units:
                current_idx = my_units.index(self.selected_unit)
            next_unit = my_units[(current_idx + 1) % len(my_units)]
            self._select_unit(next_unit)
            pos = self._find_unit_pos(next_unit)
            if pos: self.center_camera_on(pos[0], pos[1])
        else:
            print("Wszystkie jednostki straciły PA! Kliknij Następna Tura.")
            # Czyścimy zielone pola po kliknięciu Obrony (gdy AP spada do 0)
            if self.selected_unit:
                self.reachable_tiles = self._calculate_reachable_tiles(self.selected_pos, self.selected_unit.combat_ap)

    def _select_unit(self, new_unit):
        """Zaznacza jednostkę, odświeża interfejs."""
        # Zezwalamy systemowi na odznaczenie (np. przy śmierci lub zmianie tury)
        if new_unit is None:
            self.selected_unit = None
            self.panel_anim_state = "closed"
            self.panel_anim_idx = 8
            self.selected_pos = None
            self.reachable_tiles = {}
            return
            
        # Zablokowanie LEWEGO kliknięcia we wroga
        if new_unit.owner != self.active_player:
            return 
            
        if self.selected_unit == new_unit and self.panel_anim_state == "open":
            return 
            
        self.selected_unit = new_unit
        self.panel_anim_state = "open"
        self.panel_anim_idx = 0  
                
        self.selected_pos = self._find_unit_pos(new_unit)
        self.reachable_tiles = self._calculate_reachable_tiles(self.selected_pos, new_unit.combat_ap)

    def _calculate_reachable_tiles(self, start_pos, max_ap):
        reachable = {start_pos: 0}
        queue = [(0, start_pos)]
        
        while queue:
            current_cost, current_pos = heapq.heappop(queue)
            if current_cost > reachable.get(current_pos, float('inf')):
                continue
                
            moves = [(0,-1,5), (0,1,5), (-1,0,5), (1,0,5), (-1,-1,7), (1,-1,7), (-1,1,7), (1,1,7)]
            for dx, dy, step_cost in moves:
                nx, ny = current_pos[0] + dx, current_pos[1] + dy
                
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    if (nx, ny) in self.arena_units and (nx, ny) != start_pos:
                        continue 
                        
                    new_cost = current_cost + step_cost
                    if new_cost <= max_ap:
                        if new_cost < reachable.get((nx, ny), float('inf')):
                            reachable[(nx, ny)] = new_cost
                            heapq.heappush(queue, (new_cost, (nx, ny)))
        return reachable

    def _can_attack(self, enemy_pos):
        # Strzelcy mogą atakować na odległość
        if getattr(self.selected_unit, 'combat_ranged', False):
            return True 
            
        # Jednostki walczące wręcz MUSZĄ stać na sąsiadującym polu!
        if self.selected_pos:
            dx = abs(self.selected_pos[0] - enemy_pos[0])
            dy = abs(self.selected_pos[1] - enemy_pos[1])
            # Maksymalna odległość to 1 kratka w osi X i Y
            if dx <= 1 and dy <= 1:
                return True
                
        return False

    def execute_attack(self, attacker, target_pos, defender):
        attacker.combat_ap -= 5 
        
        att_str = getattr(attacker, 'attack', 5)
        def_base = getattr(defender, 'defense', 5)
        
        if getattr(defender, 'combat_defending', False):
            def_base += 2 if def_base > 10 else 1
            
        dmg_dealt = 10.0 * (att_str / max(1, def_base))
        
        def_str = getattr(defender, 'attack', 5)
        att_def = getattr(attacker, 'defense', 5)
        
        if getattr(attacker, 'combat_ranged', False):
            retaliation_dmg = 0
        else:
            retaliation_dmg = 5.0 * (def_str / max(1, att_def))

        if getattr(attacker, 'combat_charge', False):
            dmg_dealt *= 1.25     
            retaliation_dmg *= 0.50 
            
        dmg_dealt = int(max(1, dmg_dealt))
        retaliation_dmg = int(max(0, retaliation_dmg))
        
        defender.hp -= dmg_dealt
        attacker.hp -= retaliation_dmg

        # --- BLOKADA UJEMNEGO ŻYCIA ---
        defender.hp = max(0, defender.hp)
        attacker.hp = max(0, attacker.hp)

        print(f"STARCIE! {attacker.type} uderza za {dmg_dealt} DMG! (Otrzymuje {retaliation_dmg} kontrataku)")
        
        if defender.hp <= 0:
            print(f"-> {defender.type} GINIE!")
            del self.arena_units[target_pos]
            if defender in self.att_army: self.att_army.remove(defender)
            if defender in self.def_army: self.def_army.remove(defender)
            
        if attacker.hp <= 0:
            print(f"-> Atakujący {attacker.type} GINIE od kontrataku!")
            del self.arena_units[self.selected_pos]
            if attacker in self.att_army: self.att_army.remove(attacker)
            if attacker in self.def_army: self.def_army.remove(attacker)
            self._select_unit(None)
            self._auto_select_unit() # Natychmiast wybiera kolejną dostępną jednostkę

        self.check_combat_end()

    def check_combat_end(self):
        """Sprawdza, czy jedna z armii została całkowicie wybita."""
        if not self.att_army or not self.def_army:
            self.resolve_and_close(retreated=False)

    def resolve_and_close(self, retreated=False, retreating_player=None):
        """Kończy walkę, przydziela kary za ucieczkę, nagrody za wygraną i zamyka arenę."""
        import random
        
        # 1. Aplikowanie kar za ucieczkę i dobijanie ciężko rannych (< 16 HP)
        for army, player in [(self.att_army, self.attacker.owner), (self.def_army, self.defender.owner)]:
            is_retreating = retreated and player == retreating_player
            survivors = []
            
            for u in army:
                if is_retreating:
                    u.hp -= random.randint(16, 26)
                    u.morale = max(0, getattr(u, 'morale', 10) - 5)
                    u.fatigue = min(100, getattr(u, 'fatigue', 0) + 10)
                    
                if u.hp >= 16:
                    survivors.append(u)
                else:
                    u.hp = 0 # Zginął od ran lub w walce
                    
            if army is self.att_army:
                self.att_army = survivors
            else:
                self.def_army = survivors

        # 2. Nagrody dla wygranych
        winner_army = None
        if retreated:
            winner_army = self.def_army if retreating_player == self.attacker.owner else self.att_army
        else:
            if self.att_army and not self.def_army:
                winner_army = self.att_army
            elif self.def_army and not self.att_army:
                winner_army = self.def_army

        if winner_army:
            for u in winner_army:
                if u.hp > 0:
                    u.experience = min(12, getattr(u, 'experience', 0) + 9) # +3 poziomy
                    u.morale = min(20, getattr(u, 'morale', 10) + 4)
                    
                    is_in_castle = False
                    if winner_army is self.def_army and getattr(self.world, 'combat_target_castle', None):
                        is_in_castle = True
                        
                    if not is_in_castle: # Obrońcy w zamku nie męczą się walką!
                        u.fatigue = min(100, getattr(u, 'fatigue', 0) + 10)

        # 3. Zapisanie zmian na mapę główną (Odświeżenie liderów bez zmiany ich kratek!)
        def update_world_army(original_leader, surviving_list):
            if not surviving_list:
                original_leader.x, original_leader.y = -1, -1
                if original_leader in self.world.units:
                    self.world.units.remove(original_leader)
                if original_leader.owner and original_leader in original_leader.owner.units:
                    original_leader.owner.units.remove(original_leader)
                
                # ---> EGZORCYZMY ZOMBIE: Wyrywamy martwego lidera z myszki! <---
                if self.world.selected_unit == original_leader:
                    self.world.selected_unit = None
            else:
                new_leader = surviving_list[0]
                new_leader.x, new_leader.y = original_leader.x, original_leader.y
                new_leader.garrison = [None] * 10
                
                for i, u in enumerate(surviving_list[1:]):
                    if i < 10:
                        new_leader.garrison[i] = u
                        u.x, u.y = -1, -1
                        
                if new_leader != original_leader:
                    if original_leader in self.world.units: self.world.units.remove(original_leader)
                    if original_leader.owner and original_leader in original_leader.owner.units: original_leader.owner.units.remove(original_leader)
                    if new_leader not in self.world.units: self.world.units.append(new_leader)
                    if new_leader.owner and new_leader not in new_leader.owner.units: new_leader.owner.units.append(new_leader)
                    
                    # ---> PRZEKAZANIE MYSZKI: Zaznaczamy nowego lidera, jeśli stary padł, a armia żyje! <---
                    if self.world.selected_unit == original_leader:
                        self.world.selected_unit = new_leader

        update_world_army(self.attacker, self.att_army)
        update_world_army(self.defender, self.def_army)
        
        # 4. Jeśli to był atak na plac budowy i obrońcy zginęli (Zrównanie z ziemią)
        target_castle = getattr(self.world, 'combat_target_castle', None)
        if target_castle and getattr(target_castle, 'under_construction', False):
            if not self.def_army and self.att_army:
                print("Plac budowy został zniszczony przez zwycięzców!")
                target_castle.destroyed = True
                if target_castle in self.world.castles:
                    self.world.castles.remove(target_castle)
                
                size = 2 if getattr(target_castle, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
                for dy in range(size):
                    for dx in range(size):
                        self.world.map[target_castle.y + dy][target_castle.x + dx] = "."

        # Zamykamy ekran walki i wracamy na mapę
        self.world.combat_target_castle = None
        self.world.combat_attacker = None
        self.world.combat_defender = None
        self.world.screen = "map"
        pygame.mouse.set_visible(True) # <--- TA LINIJKA PRZYWRACA MYSZKĘ!

    def _get_cursor_for_mouse(self, mx, my):
        if self.show_retreat_popup:
            return self.cursor_select
            
        if self.arena_rect.collidepoint(mx, my):
            col = (mx - self.arena_rect.x + self.camera_x) // self.tile_size
            row = (my - self.arena_rect.y + self.camera_y) // self.tile_size
            
            if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
                target_pos = (col, row)
                target_unit = self.arena_units.get(target_pos)
                
                if target_unit:
                    if target_unit.owner == self.active_player:
                        return self.cursor_select 
                    else:
                        if self.selected_unit and self.selected_pos:
                            if self._can_attack(target_pos):
                                return self.cursor_attack 
                            else:
                                return self.cursor_no 
                        else:
                            return self.cursor_no
                else:
                    if self.selected_unit and self.selected_pos:
                        if target_pos in self.reachable_tiles:
                            return self.cursor_move 
                        else:
                            return self.cursor_no 
                    else:
                        return self.cursor_no 
                        
        return self.cursor_select 

    def handle_camera(self):
        keys = pygame.key.get_pressed()
        speed = 15
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.camera_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.camera_x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.camera_y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.camera_y += speed

        max_x = max(0, (self.grid_width * self.tile_size) - self.arena_rect.width)
        max_y = max(0, (self.grid_height * self.tile_size) - self.arena_rect.height)

        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    def center_camera_on(self, x, y):
        target_px = x * self.tile_size
        target_py = y * self.tile_size
        self.camera_x = target_px - (self.arena_rect.width // 2) + (self.tile_size // 2)
        self.camera_y = target_py - (self.arena_rect.height // 2) + (self.tile_size // 2)
        max_x = max(0, (self.grid_width * self.tile_size) - self.arena_rect.width)
        max_y = max(0, (self.grid_height * self.tile_size) - self.arena_rect.height)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    # =========================================================
    # SILNIK RYSOWANIA
    # =========================================================
    def _draw_text_with_shadow(self, screen, text, x, y, color=(255, 255, 255), font=None):
        if font is None:
            font = self.font_stats 
            
        txt_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, (0, 0, 0))
        screen.blit(shadow_surf, (x + 2, y + 2))
        screen.blit(txt_surf, (x, y))

    def _draw_unit_stats_overlay(self, screen, unit):
        """Rysuje teksty i nakładki (ikony miecza, strzał) na już narysowanych tłach z _anim_cache."""
        if self.panel_anim_state != "open":
            return # Nie rysujemy statystyk, gdy wisi nad nimi gęsty dym!
            
        hp = unit.hp
        max_hp = getattr(unit, 'max_hp', 100)
        hp_pct = max(0.0, min(1.0, hp / max_hp))
        
        attack = getattr(unit, 'attack', 5)
        defense = getattr(unit, 'defense', 5)
        moves = getattr(unit, 'combat_ap', 0)
        
        exp = getattr(unit, 'experience', 0)
        morale = getattr(unit, 'morale', 10)
        
       # --- Miecz HP (Ciemny miecz przykrywa jasny panel od lewej strony!) ---
        hp_sword_img = self.stat_gfx.get("hp_sword")
        if hp_sword_img:
            ox, oy = self.stat_offsets["top_hp_sword"]
            base_x = self.pos_f1[0] + int(ox * self.panel_scale)
            base_y = self.pos_f1[1] + int(oy * self.panel_scale)
            
            sword_w, sword_h = hp_sword_img.get_size()
            missing_hp_pct = 1.0 - hp_pct # Obliczamy ile % życia brakuje
            
            # Szerokość ciemnego miecza zależy od tego, ile życia brakuje
            missing_w = int(sword_w * missing_hp_pct)
            
            if missing_w > 0:
                # Rysujemy tylko lewy kawałek ciemnego miecza (od ostrza w stronę rękojeści)
                missing_area = pygame.Rect(0, 0, missing_w, sword_h)
                screen.blit(hp_sword_img, (base_x, base_y), missing_area)

        # --- Liczby PA, Atak, Obrona ---
        tox, toy = self.stat_offsets["top_moves_text"]
        self._draw_text_with_shadow(screen, f"{moves}", self.pos_f1[0] + int(tox * self.panel_scale), self.pos_f1[1] + int(toy * self.panel_scale), font=self.font_pa)

        tox, toy = self.stat_offsets["top_attack_text"]
        self._draw_text_with_shadow(screen, f"{attack}", self.pos_f1[0] + int(tox * self.panel_scale), self.pos_f1[1] + int(toy * self.panel_scale))

        tox, toy = self.stat_offsets["top_defense_text"]
        def_color = (0, 255, 0) if getattr(unit, 'combat_defending', False) else (255, 255, 255)
        self._draw_text_with_shadow(screen, f" {defense}", self.pos_f1[0] + int(tox * self.panel_scale), self.pos_f1[1] + int(toy * self.panel_scale), def_color)

        # --- Strzały (Ranged) ---
        if getattr(unit, 'combat_ranged', False):
            arrow_img = self.stat_gfx.get("arrow")
            if arrow_img:
                level = (exp // 3) + 1
                ox, oy = self.stat_offsets["top_arrows_start"]
                base_x = self.pos_f1[0] + int(ox * self.panel_scale)
                base_y = self.pos_f1[1] + int(oy * self.panel_scale)
                for i in range(level):
                    screen.blit(arrow_img, (base_x, base_y + i * int(15 * self.panel_scale)))

        # --- Morale Text (Twarz jest w tle, rysujemy tylko cyfrę) ---
        tox, toy = self.stat_offsets["bot_morale_text"]
        self._draw_text_with_shadow(screen, f"{morale}", self.pos_f3[0] + int(tox * self.panel_scale), self.pos_f3[1] + int(toy * self.panel_scale))

        # --- Małe Mieczyki (Posąg jest w tle) ---
        level = (exp // 3) + 1
        swords_count = (exp % 3) + 1
        if exp >= 12: swords_count = 3
        
        sword_img = self.stat_gfx.get("exp_sword")
        if sword_img:
            ox, oy = self.stat_offsets["bot_exp_swords"]
            base_x = self.pos_f3[0] + int(ox * self.panel_scale)
            base_y = self.pos_f3[1] + int(oy * self.panel_scale)
            for i in range(swords_count):
                screen.blit(sword_img, (base_x + i * int(20 * self.panel_scale), base_y))

    def draw(self, screen):
        screen.fill((0, 0, 0)) 
        mx, my = pygame.mouse.get_pos()
        
        self.handle_camera()
        screen.set_clip(self.arena_rect)
        
        # 1. TŁO ARENY
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                px = self.arena_rect.x + (x * self.tile_size) - self.camera_x
                py = self.arena_rect.y + (y * self.tile_size) - self.camera_y
                
                if px + self.tile_size > self.arena_rect.left and px < self.arena_rect.right and \
                   py + self.tile_size > self.arena_rect.top and py < self.arena_rect.bottom:
                    screen.blit(self.bg_tile, (px, py))
                    
        # 2. PODŚWIETLENIE ZASIĘGU
        if self.selected_pos and self.reachable_tiles:
            for (rx, ry) in self.reachable_tiles.keys():
                if (rx, ry) == self.selected_pos: continue
                px = self.arena_rect.x + (rx * self.tile_size) - self.camera_x
                py = self.arena_rect.y + (ry * self.tile_size) - self.camera_y
                
                if px + self.tile_size > self.arena_rect.left and px < self.arena_rect.right and \
                   py + self.tile_size > self.arena_rect.top and py < self.arena_rect.bottom:
                    s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    s.fill((0, 255, 0, 40)) 
                    screen.blit(s, (px, py))
                
        # 3. JEDNOSTKI I ZAZNACZENIE
        for (x, y), unit in self.arena_units.items():
            px = self.arena_rect.x + (x * self.tile_size) - self.camera_x
            py = self.arena_rect.y + (y * self.tile_size) - self.camera_y
            
            if self.selected_pos == (x, y):
                border_color = (0, 255, 0) if unit.owner == self.active_player else (255, 0, 0)
                pygame.draw.rect(screen, border_color, (px, py, self.tile_size, self.tile_size), 3)

            img = self._get_tactical_unit_image(unit)
                
            if img:
                skala_ludzika = self.tile_size / max(img.get_width(), img.get_height()) * 0.95
                new_w = int(img.get_width() * skala_ludzika)
                new_h = int(img.get_height() * skala_ludzika)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
                
                if unit in self.def_army:
                    img = pygame.transform.flip(img, True, False)
                    
                img_x = px + (self.tile_size - new_w) // 2
                img_y = py + (self.tile_size - new_h) // 2
                screen.blit(img, (img_x, img_y))
                
                # Tarcza widoczna TYLKO dla jednostek obecnie grającego gracza:
                if getattr(unit, 'combat_defending', False) and self.shield_icon and unit.owner == self.active_player:
                    screen.blit(self.shield_icon, (px + 5, py + 5))

            else:
                color = unit.owner.color if unit.owner else (255, 255, 255)
                pygame.draw.rect(screen, color, (px + 4, py + 4, self.tile_size - 8, self.tile_size - 8))

        screen.set_clip(None)

        # 4. RYSOWANIE PUSTEJ RAMKI (PODKŁAD)
        if self.frame_0: screen.blit(self.frame_0, self.pos_f0)
        if self.frame_1: screen.blit(self.frame_1, self.pos_f1)
        if self.frame_2: screen.blit(self.frame_2, self.pos_f2)
        if self.frame_3: screen.blit(self.frame_3, self.pos_f3)
        
        # 5. ODTWARZACZ TŁA DLA 6 SLOTÓW (Dynamiczne rysowanie odpowiednich klatek)
        if self.panel_anim_state == "closing":
            now = pygame.time.get_ticks()
            if now - self.last_anim_tick > 30: # 30ms na klatkę, przyjemne tempo zamknięcia
                self.last_anim_tick = now
                self.panel_anim_idx += 1
                
                if self.panel_anim_idx >= 8:
                    self.panel_anim_idx = 8
                    self.panel_anim_state = "closed"
                    self._select_unit(None) # Ostateczne czyszczenie, gdy kłęby dymu opadną!
                    self._auto_select_unit() # <--- TA LINIJKA ZAZNACZA JEDNOSTKĘ PO ODDANIU TURY

        # Rysujemy 6 paneli używając słownika anim_offsets i slot_base_indices
        for slot_key, offset in self.anim_offsets.items():
            dx = int(offset[0] * self.panel_scale)
            dy = int(offset[1] * self.panel_scale)
            
            # Pobieramy bazowy numer grafiki (np. 36 dla Bicepsa, 81 dla Łuku)
            base_idx = self.slot_base_indices.get(slot_key, 99)
            
            # Jeśli jednostka otwarta, uaktualniamy Morale i Exp dynamicznie
            if self.selected_unit:
                if slot_key == "slot_5":
                    m = getattr(self.selected_unit, 'morale', 10)
                    if m <= 5: base_idx = 72
                    elif m <= 10: base_idx = 54
                    else: base_idx = 45
                elif slot_key == "slot_6":
                    exp = getattr(self.selected_unit, 'experience', 0)
                    lvl = (exp // 3) + 1
                    if lvl == 1: base_idx = 0
                    elif lvl == 2: base_idx = 9
                    elif lvl >= 3: base_idx = 18 
                    if lvl >= 4: base_idx = 27

            # panel_anim_idx wynosi od 0 (otwarte tło) do 8 (dym)
            current_frame = base_idx + self.panel_anim_idx
            
            img = self.anim_cache.get(current_frame)
            if not img:
                img = self.anim_cache.get(99) # Awaryjny dym
                
            if img:
                screen.blit(img, (self.pos_f1[0] + dx, self.pos_f1[1] + dy))
            
        # 6. RYSOWANIE TEKSTÓW I IKON NA WIERZCHU (Tylko gdy otwarte i wybrane)
        if self.selected_unit and self.panel_anim_state == "open":
            self._draw_unit_stats_overlay(screen, self.selected_unit)
            
        # 7. PRZYCISKI AKCJI (Na samym wierzchu)
        is_mouse_pressed = pygame.mouse.get_pressed()[0]
        for action, rect in self.action_rects.items():
            normal_img, pressed_img = self.action_btns_gfx[action]
            if normal_img:
                is_active = False
                if self.selected_unit:
                    if action == "ATAK_WRECZ" and getattr(self.selected_unit, 'combat_charge', False):
                        is_active = True
                    elif action == "ATAK_DYSTANS" and getattr(self.selected_unit, 'combat_ranged', False):
                        is_active = True

                if (rect.collidepoint(mx, my) and is_mouse_pressed and pressed_img) or (is_active and pressed_img):
                    screen.blit(pressed_img, rect.topleft)
                else:
                    screen.blit(normal_img, rect.topleft)

        # 8. NASTĘPNA TURA
        if self.top_trigger_area.collidepoint(mx, my) or self.btn_next_turn.collidepoint(mx, my):
            self.show_top_ui = True
        else:
            self.show_top_ui = False

        if self.show_top_ui:
            is_hovered = self.btn_next_turn.collidepoint(mx, my)
            
            if self.btn_next_turn_bg:
                bg_scaled = pygame.transform.smoothscale(self.btn_next_turn_bg, (self.btn_next_turn.width, self.btn_next_turn.height))
                screen.blit(bg_scaled, self.btn_next_turn.topleft)
                
            if self.btn_next_turn_img:
                screen.blit(self.btn_next_turn_img, self.btn_next_turn.topleft)
                if is_hovered:
                    pygame.draw.rect(screen, (255, 215, 0), self.btn_next_turn, 2)
            else:
                color = (50, 150, 50) if is_hovered else (30, 100, 30)
                pygame.draw.rect(screen, color, self.btn_next_turn)

        # 9. POP-UP ODWROTU
        if self.show_retreat_popup:
            self._draw_retreat_popup(screen, mx, my)

        # 10. PODMIANA KURSORA
        cursor = self._get_cursor_for_mouse(mx, my)
        if cursor:
            pygame.mouse.set_visible(False)
            screen.blit(cursor, (mx, my))
        else:
            pygame.mouse.set_visible(True)

        # =========================================================
        # 11. NOWOŚĆ: OKIENKO PODGLĄDU POD PRAWYM PRZYCISKIEM
        # =========================================================
        if getattr(self.world, 'inspected_unit', None):
            mode = getattr(self.world, 'info_mode', "COMBAT")
            # Wywołujemy DOKŁADNIE to samo okno pergaminu, co renderer!
            self.world.unit_info_window.draw(screen, 150, 200, self.world.inspected_unit, mode)

    def _draw_retreat_popup(self, screen, mx, my):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        curr_player = self.world.players[self.world.current_player]
        bg_img = self.popup_bgs.get(curr_player.color_name.lower())
        if not bg_img: bg_img = self.popup_bgs.get("red") 
        if not bg_img: return

        bg_w, bg_h = bg_img.get_size()
        bg_x = (self.screen_width - bg_w) // 2
        bg_y = (self.screen_height - bg_h) // 2
        screen.blit(bg_img, (bg_x, bg_y))

        font_small = pygame.font.SysFont("Times New Roman", int(20 * self.panel_scale), italic=True)
        font_name = pygame.font.SysFont("Times New Roman", int(38 * self.panel_scale), bold=True)
        font_title = pygame.font.SysFont("Times New Roman", int(32 * self.panel_scale), bold=True)

        txt_gracz = font_small.render("Gracz", True, (255, 255, 255))
        txt_name = font_name.render(curr_player.name, True, (255, 255, 255))
        txt_odwrot = font_title.render("Odwrót", True, (255, 255, 255))

        def render_with_shadow(txt_surf, x, y):
            shadow = txt_surf.copy()
            shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(shadow, (x + 2, y + 2))
            screen.blit(txt_surf, (x, y))

        render_with_shadow(txt_gracz, bg_x + (bg_w - txt_gracz.get_width())//2, bg_y + int(35 * self.panel_scale))
        render_with_shadow(txt_name, bg_x + (bg_w - txt_name.get_width())//2, bg_y + int(55 * self.panel_scale))
        render_with_shadow(txt_odwrot, bg_x + (bg_w - txt_odwrot.get_width())//2, bg_y + int(105 * self.panel_scale))

        norm_y, press_y = self.btn_confirm_gfx
        norm_n, press_n = self.btn_cancel_gfx

        if norm_y and norm_n:
            bw, bh = norm_y.get_size()
            self.rect_confirm = pygame.Rect(bg_x + int(40 * self.panel_scale), bg_y + int(145 * self.panel_scale), bw, bh)
            self.rect_cancel = pygame.Rect(bg_x + bg_w - bw - int(40 * self.panel_scale), bg_y + int(145 * self.panel_scale), bw, bh)

            is_mouse_pressed = pygame.mouse.get_pressed()[0]

            if self.rect_confirm.collidepoint(mx, my) and is_mouse_pressed and press_y:
                screen.blit(press_y, self.rect_confirm.topleft)
            else:
                screen.blit(norm_y, self.rect_confirm.topleft)

            if self.rect_cancel.collidepoint(mx, my) and is_mouse_pressed and press_n:
                screen.blit(press_n, self.rect_cancel.topleft)
            else:
                screen.blit(norm_n, self.rect_cancel.topleft)

    def handle_click(self, mx, my, button=1):
        # 1. OBSŁUGA POP-UPU
        if getattr(self, 'show_retreat_popup', False):
            if button == 1: # Tylko Lewy przycisk działa w interfejsie
                if self.rect_confirm.collidepoint(mx, my):
                    pressed_img = self.btn_confirm_gfx[1]
                    if pressed_img:
                        screen = pygame.display.get_surface()
                        screen.blit(pressed_img, self.rect_confirm.topleft)
                        pygame.display.flip()
                        pygame.time.delay(100)
                        
                    print("TAKTYKA: Potwierdzono ucieczkę! Powrót na mapę.")
                    pygame.mouse.set_visible(True) 
                    self.world.combat_attacker = None
                    self.world.combat_defender = None
                    self.world.screen = "map"
                    self.show_retreat_popup = False
                    
                elif self.rect_cancel.collidepoint(mx, my):
                    pressed_img = self.btn_cancel_gfx[1]
                    if pressed_img:
                        screen = pygame.display.get_surface()
                        screen.blit(pressed_img, self.rect_cancel.topleft)
                        pygame.display.flip()
                        pygame.time.delay(100)
                        
                    print("TAKTYKA: Zmiana zdania, wracamy do walki.")
                    self.show_retreat_popup = False

                    self.resolve_and_close(retreated=True, retreating_player=self.active_player)
                    
            return True 

        # 2. PRZYCISKI BOCZNE
        if button == 1:
            for action, rect in self.action_rects.items():
                if rect.collidepoint(mx, my):
                    
                    if action == "ODWROT":
                        pressed_img = self.action_btns_gfx["ODWROT"][1]
                        if pressed_img:
                            screen = pygame.display.get_surface()
                            screen.blit(pressed_img, rect.topleft)
                            pygame.display.flip()
                            pygame.time.delay(100) 
                        self.show_retreat_popup = True
                        
                    elif action == "NASTEPNA_JEDNOSTKA":
                        self._select_next_unit()

                    elif action == "ATAK_WRECZ" and self.selected_unit:
                        self.selected_unit.combat_charge = not getattr(self.selected_unit, 'combat_charge', False)
                        if self.selected_unit.combat_charge:
                            self.selected_unit.combat_ranged = False 
                        print(f"Szarża/Walka wręcz dla {self.selected_unit.type}: {self.selected_unit.combat_charge}")
                        
                    elif action == "ATAK_DYSTANS" and self.selected_unit:
                        if getattr(self.selected_unit, 'can_shoot', False):
                            self.selected_unit.combat_ranged = not getattr(self.selected_unit, 'combat_ranged', False)
                            if self.selected_unit.combat_ranged:
                                self.selected_unit.combat_charge = False 
                            print(f"Atak dystansowy dla {self.selected_unit.type}: {self.selected_unit.combat_ranged}")
                        else:
                            print(f"{self.selected_unit.type} to jednostka walcząca wręcz! Zostaw tę opcję dla łuczników.")
                        
                    elif action == "OBRONA" and self.selected_unit:
                        if self.selected_unit.combat_ap >= 5:
                            self.selected_unit.combat_ap = 0
                            self.selected_unit.combat_defending = True
                            print(f"Jednostka {self.selected_unit.type} wznosi tarczę!")
                            self._select_next_unit() 
                        else:
                            print("Za mało PA na obronę! Wymagane 5.")
                            
                    return True
            
        # 3. ZAKOŃCZENIE TURY
        if button == 1 and self.show_top_ui and self.btn_next_turn.collidepoint(mx, my):
            if self.active_player == self.attacker.owner:
                self.active_player = self.defender.owner
                print("\n=== TURA OBROŃCY ===")
            else:
                self.active_player = self.attacker.owner
                print("\n=== TURA ATAKUJĄCEGO ===")
                
            for u in self.att_army + self.def_army:
                if u.owner == self.active_player:
                    u.combat_ap = getattr(u, 'moves', 5)
                    
            if self.selected_unit and self.anim_cache:
                self.panel_anim_state = "closing"
                self.panel_target_unit = self.selected_unit 
                self.panel_anim_idx = 0
                self.last_anim_tick = pygame.time.get_ticks()
            else:
                self._select_unit(None)
                
            return True
            
        # 4. KLIKANIE NA ARENĘ (RUCH, ATAK LUB PODGLĄD)
        if self.arena_rect.collidepoint(mx, my):
            col = (mx - self.arena_rect.x + self.camera_x) // self.tile_size
            row = (my - self.arena_rect.y + self.camera_y) // self.tile_size
            
            if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
                target_pos = (col, row)
                target_unit = self.arena_units.get(target_pos)
                
                if target_unit:
                    # 🟢 PRAWY PRZYCISK MYSZY: Włącza pergamin informacyjny
                    if button == 3: 
                        self.world.inspected_unit = target_unit
                        if target_unit.owner == self.active_player:
                            self.world.info_mode = "COMBAT"
                        else:
                            self.world.info_mode = "ENEMY"
                        return True
                        
                    # 🟢 LEWY PRZYCISK MYSZY: Akcje walki
                    elif button == 1:
                        if target_unit.owner == self.active_player:
                            self._select_unit(target_unit)
                        else:
                            if self.selected_unit and self.selected_unit.owner == self.active_player and self.selected_pos:
                                if self._can_attack(target_pos):
                                    if self.selected_unit.combat_ap >= 5:
                                        self.selected_unit.combat_defending = False 
                                        self.execute_attack(self.selected_unit, target_pos, target_unit)
                                        if self.selected_unit and self.selected_unit.hp > 0:
                                            self.reachable_tiles = self._calculate_reachable_tiles(self.selected_pos, self.selected_unit.combat_ap)
                                    else:
                                        print("Za mało PA na atak! (Wymagane minimum 5 PA)")
                                else:
                                    print("Wróg poza zasięgiem!")
                                    
                else:
                    # 🟢 LEWY PRZYCISK: Zwykły Ruch
                    if button == 1 and self.selected_unit and self.selected_unit.owner == self.active_player and self.selected_pos:
                        if target_pos in self.reachable_tiles:
                            self.selected_unit.combat_defending = False 
                            cost = self.reachable_tiles[target_pos]
                            del self.arena_units[self.selected_pos]
                            self.arena_units[target_pos] = self.selected_unit
                            self.selected_pos = target_pos
                            self.selected_unit.combat_ap -= cost
                            self.reachable_tiles = self._calculate_reachable_tiles(self.selected_pos, self.selected_unit.combat_ap)
            return True

        return False
    
if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])