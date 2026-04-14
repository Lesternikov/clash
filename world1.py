
    def setup_terrain_mapping(self, image_list):
        """Mapuje listę 13 obrazków na konkretne sytuacje na mapie."""
        if len(image_list) < 13: 
            # Failsafe: jeśli masz mniej obrazków, używamy środka jako zamiennika
            return {i: image_list[-1] if image_list else None for i in range(13)}
        
        return {
            # --- ROGI WYPUKŁE (Zewnętrzne) ---
            0: image_list[0],  # Lewy Górny (LG)
            2: image_list[2],  # Prawy Górny (PG)
            5: image_list[5],  # Lewy Dolny (LD)
            7: image_list[7],  # Prawy Dolny (PD)

            # --- KRAWĘDZIE PROSTE ---
            1: image_list[1],  # Góra
            6: image_list[6],  # Dół
            3: image_list[3],  # Lewo
            4: image_list[4],  # Prawo

            # --- ROGI WKLĘSŁE (Skosy/Zatoczki) ---
            8: image_list[8],  # Wklęsły Prawy Dolny
            9: image_list[9],  # Wklęsły Lewy Dolny
            10: image_list[10], # Wklęsły Prawy Górny
            11: image_list[11], # Wklęsły Lewy Górny

            # --- ŚRODEK ---
            12: image_list[12]  # Pełny kafelek (image_list[12] to trzynasty element)
        }
    
    def load_single_img(self, path, alpha=True):
        """Pomocnik do bezpiecznego ładowania"""
        if os.path.exists(path):
            img = pygame.image.load(path)
            return img.convert_alpha() if alpha else img.convert()
        # Jeśli nie ma pliku, stwórz różowy kwadrat błędu
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((255, 0, 255))
        return s
            
    def load_goryn_graphics(self):
        import os
        import pygame
        
        # Ścieżka do folderu z górkami
        goryn_path = os.path.join("assets", "goryn")
        
        # range(165, 168) wczyta pliki: 165, 166, 167
        for i in range(165, 168):
            file_name = f"BACKGR1_S32_{i}.png"
            full_path = os.path.join(goryn_path, file_name)
            
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                self.goryn_images.append(img)
            else:
                print(f"Ostrzeżenie: Brak grafiki gór {file_name}")
    def load_pustynia_graphics(self):
         # Tworzymy słownik/listę na 12 konkretnych obrazków brzegów
        self.pustynia_layers = [None] * 12
        
        # 1. Ładowanie brzegów (8-19 to 12 plików: 8,9,10,11,12,13,14,15,16,17,18,19)
        start_id = 8
        for i in range(start_id, 21): # Zmienione na 20, żeby wczytać 12 plików
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                
                idx = i - start_id
                if idx < 12:
                    self.pustynia_layers[idx] = img

        # 2. Ładowanie środka (u Ciebie pliki 0 i 1)
        self.deep_pustynia_frames = [] 
        for i in range(4, 6):
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                self.deep_pustynia_frames.append(img)
        
        # Jeśli środek nie jest animowany, weź po prostu pierwszy:
        full_pustynia = self.deep_pustynia_frames[0] if self.deep_pustynia_frames else None

        # 3. Mapping (teraz przechowuje pojedyncze obrazki, nie listy)
        self.pustynia_tile_mapping = {
            0: self.pustynia_layers[0],  # Róg wypukły LG
            1: self.pustynia_layers[1],  # Góra
            2: self.pustynia_layers[2],  # Róg wypukły PG
            3: self.pustynia_layers[3],  # Lewo
            4: self.pustynia_layers[4],  # Prawo
            5: self.pustynia_layers[5],  # Róg wypukły LD
            6: self.pustynia_layers[6],  # Dół
            7: self.pustynia_layers[7],  # Róg wypukły PD
            8: self.pustynia_layers[8],  # Róg wklęsły PD
            9: self.pustynia_layers[9],  # Róg wklęsły LD
            10: self.pustynia_layers[10], # Róg wklęsły PG
            11: self.pustynia_layers[11], # Róg wklęsły LG
            12: full_pustynia             # Pełna trawa
        }

    def load_animated_water(self):
        self.water_layers = [[] for _ in range(12)]
        
        # 1. Ładowanie brzegów (223-414)
        start_id = 223
        for i in range(start_id, 415):
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (32, 32))
                group_index = (i - start_id) % 12
                self.water_layers[group_index].append(img)

        # 2. Ładowanie głębokiego morza (TYLKO TUTAJ)
        self.deep_water_frames = [] # Używajmy konsekwentnie tej nazwy
        for i in range(587, 595):
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (32, 32))
                self.deep_water_frames.append(img)
        
        print(f"Załadowano animacje wody i {len(self.deep_water_frames)} klatek morza.")
        # Dodaj to na końcu funkcji load_animated_water
        self.water_tile_mapping = {
            0: self.water_layers[0],  # Róg wypukły LG
            1: self.water_layers[1],  # Góra
            2: self.water_layers[2],  # Róg wypukły PG
            3: self.water_layers[3],  # Lewo
            4: self.water_layers[4],  # Prawo
            5: self.water_layers[5],  # Róg wypukły LD
            6: self.water_layers[6],  # Dół
            7: self.water_layers[7],  # Róg wypukły PD
            8: self.water_layers[8],  # Róg wklęsły PD
            9: self.water_layers[9],  # Róg wklęsły LD
            10: self.water_layers[10], # Róg wklęsły PG
            11: self.water_layers[11], # Róg wklęsły LG
            12: self.deep_water_frames # Pełne morze
        }

    def load_grass_graphics(self):
        # Tworzymy słownik/listę na 12 konkretnych obrazków brzegów
        self.grass_layers = [None] * 12
        
        # 1. Ładowanie brzegów (8-19 to 12 plików: 8,9,10,11,12,13,14,15,16,17,18,19)
        start_id = 20
        for i in range(start_id, 32): # Zmienione na 20, żeby wczytać 12 plików
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                
                idx = i - start_id
                if idx < 12:
                    self.grass_layers[idx] = img

        # 2. Ładowanie środka (u Ciebie pliki 0 i 1)
        self.deep_grass_frames = [] 
        for i in range(0, 2):
            path = os.path.join("assets", "BACKGR3_S32", f"BACKGR3_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                self.deep_grass_frames.append(img)
        
        # Jeśli środek nie jest animowany, weź po prostu pierwszy:
        full_grass = self.deep_grass_frames[0] if self.deep_grass_frames else None

        # 3. Mapping (teraz przechowuje pojedyncze obrazki, nie listy)
        self.grass_tile_mapping = {
            0: self.grass_layers[8],  # Róg wypukły LG
            1: self.grass_layers[8],  # Góra
            2: self.grass_layers[8],  # Róg wypukły PG
            3: self.grass_layers[4],  # Lewo
            4: self.grass_layers[8],  # Prawo
            5: self.grass_layers[5],  # Róg wypukły LD
            6: self.grass_layers[8],  # Dół
            7: self.grass_layers[7],  # Róg wypukły PD
            8: self.grass_layers[9],  # Róg wklęsły PD
            9: self.grass_layers[8],  # Róg wklęsły LD
            10: self.grass_layers[8], # Róg wklęsły PG
            11: self.grass_layers[8], # Róg wklęsły LG
            12: full_grass             # Pełna trawa
        }

    def load_tree_graphics(self):
        
        trees_path = os.path.join("assets", "trees")
        for i in range(45, 58):
            file_name = f"BACKGR1_S32_{i}.png"
            full_path = os.path.join(trees_path, file_name)
            
            if os.path.exists(full_path):
                # Ładujemy i skalujemy do 32x32
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (32, 32))
                self.tree_images.append(img)
            else:
                print(f"Ostrzeżenie: Brak grafiki {file_name}")

    def get_tile_connection_id(self, x, y, target_type):
        # Sprawdzamy, czy sąsiad jest TAKIM SAMYM typem terenu
        U = self.map[y-1][x] == target_type if y > 0 else True
        D = self.map[y+1][x] == target_type if y < len(self.map)-1 else True
        L = self.map[y][x-1] == target_type if x > 0 else True
        R = self.map[y][x+1] == target_type if x < len(self.map[0])-1 else True

        # Skosy (ważne dla rogów wklęsłych)
        UL = self.map[y-1][x-1] == target_type if (y > 0 and x > 0) else True
        UR = self.map[y-1][x+1] == target_type if (y > 0 and x < len(self.map[0])-1) else True
        DL = self.map[y+1][x-1] == target_type if (y < len(self.map)-1 and x > 0) else True
        DR = self.map[y+1][x+1] == target_type if (y < len(self.map)-1 and x < len(self.map[0])-1) else True

        # --- LOGIKA DOPASOWANIA INDEKSU (0-12) ---
        # ROGI WEWNĘTRZNE (Zatoczki - brakuje tylko jednego skosu)
        if U and L and not UL: return 11
        if U and R and not UR: return 10
        if D and L and not DL: return 9
        if D and R and not DR: return 8

        # ROGI ZEWNĘTRZNE (Cypelki - brak dwóch boków)
        if not U and not L: return 0
        if not U and not R: return 2
        if not D and not L: return 5
        if not D and not R: return 7

        # KRAWĘDZIE PROSTE
        if not U: return 1
        if not D: return 6
        if not L: return 3
        if not R: return 4

        return 12 # Pełny środek
