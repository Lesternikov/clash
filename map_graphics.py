import os
import random
import pygame
from pathfinding import Pathfinder

TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

class MapGraphics:
    def __init__(self, world_instance):
        self.world = world_instance
        self.water_layers = [[] for _ in range(13)]
        self.water_frame_index = 0
        self.grass_frame_index = 0
        
        self.edges = {}
        self.centers = {}
        self.terrain_images = {}
        self.road_gfx = {"grass": {}, "swamp": [], "desert_trans": [], ".": {}, "B": {}, "p": {}, "trans": {}}
        self.bridge_gfx = {}
        self.waterfall_gfx = {"N": {}, "S": {}, "W": {}, "E": {}}
        self.river_overlays = {}
        self.treasure_imgs = {}
        self.army_panel_bg = pygame.image.load("assets//minimum/MARKS_S32/MARKS_S32_35.png").convert_alpha()
        # --- Grafiki interfejsu ---
        self.button_images = []
        self.load_ui_assets() # Ładujemy przyciski na starcie
        # -------------------------------

        self.load_additional_tiles()
        self.load_all_assets()
        self.load_road_graphics()
        self.load_all_water_assets()
        self.pathfinder = Pathfinder(self.world)        

        # GRAFIKI PLACU BUDOWY
        # Używamy Twojej funkcji load_single_img, która automatycznie skaluje grafiki do 32x32 pikseli!
        self.build_grass = {
            (0, 0): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_707.png")),
            (1, 0): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_708.png")),
            (0, 1): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_709.png")),
            (1, 1): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_710.png"))
        }
        
        self.build_desert = {
            (0, 0): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_711.png")),
            (1, 0): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_712.png")),
            (0, 1): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_713.png")),
            (1, 1): self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_714.png"))
        }
        

    def load_ui_assets(self):
        
        """Ładuje wszystkie grafiki interfejsu"""
        path_ui = "assets/minimum/MAP_BUTT_S32"
        
        # 1. Standardowe przyciski (0-11)
        button_files = [f"MAP_BUTT_S32_{i}.png" for i in range(12)]
        self.button_images = self._load_button_set(path_ui, button_files)

        # 2. PRZYCISKI BUDOWANIA (15-23)
        # 15,16=Droga, 17,18=Pułapka, 19,20=Wieża(?), 21=Puste(?), 22,23=Wyjście
        build_files = [
            "MAP_BUTT_S32_15.png", "MAP_BUTT_S32_16.png",
            "MAP_BUTT_S32_19.png", "MAP_BUTT_S32_20.png",
            "MAP_BUTT_S32_17.png", "MAP_BUTT_S32_18.png",
            "MAP_BUTT_S32_21.png", "MAP_BUTT_S32_22.png", # Powtórka jako placeholder
            "MAP_BUTT_S32_23.png", "MAP_BUTT_S32_24.png",
            "MAP_BUTT_S32_25.png", "MAP_BUTT_S32_26.png",

        ]
        self.build_button_images = self._load_button_set(path_ui, build_files)


        # 3. Tło panelu armii
        army_bg_path = "assets/minimum/MARKS_S32/MARKS_S32_35.png" 
        if os.path.exists(army_bg_path):
            self.army_panel_bg = pygame.image.load(army_bg_path).convert_alpha()
        else:
            print(f"Błąd: Nie znaleziono tła armii: {army_bg_path}")
            self.army_panel_bg = pygame.Surface((32, 32))
            self.army_panel_bg.fill((101, 67, 33))

    def _load_button_set(self, path, files):
        """Pomocnicza funkcja, żeby nie powtarzać kodu ładowania"""
        images = []
        for filename in files:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                images.append(img)
            else:
                print(f"Błąd: Brak pliku {filename}")
                fallback = pygame.Surface((32, 32))
                fallback.fill((100, 100, 100))
                images.append(fallback)
        return images

    def load_additional_tiles(self):
        base_bg_path = r"D:\clash reverse\assets\normal\BACKGR3_S32_"
        try:
            self.terrain_images["$"] = pygame.image.load(f"{base_bg_path}752.png").convert_alpha()
            self.terrain_images["S"] = pygame.image.load(f"{base_bg_path}733.png").convert_alpha()
            self.terrain_images["&"] = pygame.image.load(f"{base_bg_path}736.png").convert_alpha()
            for key in self.terrain_images:
                self.terrain_images[key] = pygame.transform.scale(self.terrain_images[key], (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Błąd ładowania dodatkowych kafelków: {e}")
        # --- DODAJ TO: Rejestrujemy ruiny pod małym 'r' ---
            ruins_path = os.path.join("assets", "minimum", "BUILDIN1_S32", "BUILDIN1_S32_8.png")
            if os.path.exists(ruins_path):
                img_r = pygame.image.load(ruins_path).convert_alpha()
                self.terrain_images["r"] = pygame.transform.scale(img_r, (TILE_SIZE, TILE_SIZE))

        # --- DODAJ TO: Rejestrujemy nową grafikę pułapki ---
            trap_path = os.path.join("assets", "minimum", "MARKS_S32", "MARKS_S32_6.png")
            if os.path.exists(trap_path):
                img_trap = pygame.image.load(trap_path).convert_alpha()
                self.terrain_images["X"] = pygame.transform.scale(img_trap, (TILE_SIZE, TILE_SIZE))

    def load_all_assets(self):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        
        # ========================================================================
        # 1. TRAWA (Warianty z wagami — czysta trawa dominuje)
        # ========================================================================
        # Ładujemy czyste warianty trawy (np. 715, 715a, 715b)
        clean_grass_0 = self.load_single_img(os.path.join(path_base, "BACKGR3_S32_715.png"))
        clean_grass_1 = self.load_single_img(os.path.join(path_base, "BACKGR3_S32_715a.png"))
        clean_grass_3 = self.load_single_img(os.path.join(path_base, "BACKGR3_S32_715b.png"))
        
        self.grass_variants = [
            # im więcej kopi tym większa szansa na wylosowanie
            clean_grass_0, clean_grass_1, clean_grass_3,
            clean_grass_0, clean_grass_1, clean_grass_3,
            clean_grass_0, clean_grass_1, clean_grass_3,
            clean_grass_0, clean_grass_1, clean_grass_3,
            clean_grass_0, clean_grass_1, clean_grass_3,
            clean_grass_0, clean_grass_1, clean_grass_3,

            # Rzadkie warianty (z kamykami, krzaczkami itp.) - tylko po jednej sztuce na liście:
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_751.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_753.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_3.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_74.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_75.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_76.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_94.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_95.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_96.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_0.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_1.png")),
        ]

        # ========================================================================
        # 2. INNE ASSETY (Woda, Krawędzie itp.)
        # ========================================================================
        self.river_anim = self.load_river_animation() 
        self.sea_anim = self.load_sea_animation()
        self.load_sea_cliffs()

        # Definicja Trawy
        self.edges["."] = self.load_edge_only_set(20) 
        self.centers["."] = self.grass_variants 

        # Definicja Bagna (?) G
        self.edges["G"] = self.load_edge_only_set(187)
        self.centers["G"] = [
            self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32","BACKGR3_S32_699.png")),
            self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32","BACKGR3_S32_700.png"))
        ]
        
        # Wysokie góry
        self.high_mountain_grass_edges = self.load_edge_only_set(187) 
        self.high_mountain_desert_edges = self.load_edge_only_set(211) 
        self.high_mountain_swamp_edges = self.load_edge_only_set(199)  
        
        # Pustynia p
        self.edges["p"] = self.load_edge_only_set(8) 
        self.centers["p"] = [self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32","BACKGR3_S32_4.png"))]

        # Inna Pustynia P
        self.edges["P"] = self.load_edge_only_set(32) 
        self.centers["P"] = [self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32","BACKGR3_S32_44.png"))]

        # ========================================================================
        # 3. LAS (Autotiling Kontekstowy — Rzadki vs Gęsty)
        # ========================================================================
        # Krawędzie lasu (zawsze używane przy przejściu trawa<->las)
        self.edges["l"] = self.load_edge_only_set(45) 
        # Warianty autotilingu krawędzi (styki 45 stopni itp.)
        self.edges["l"][0] = [ 
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_48.png"), 
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_46.png"), 
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_80.png"), 
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_80.png"), 
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_50.png"), 
        ]
        
        # Standardowe wnętrze lasu (Rzadki las — używane na obrzeżach)
        self.centers["l"] = [
            self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_49.png")
        ]

        self.dense_forest_centers = {
            (0, 0): self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_54.png"), # Lewy górny
            (1, 0): self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_55.png"), # Prawy górny
            (0, 1): self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_56.png"), # Lewy dolny
            (1, 1): self.load_single_img("assets/normal/BACKGR3_S32/BACKGR3_S32_57.png")  # Prawy dolny
        }
        # ========================================================================
        
        # Bagno B
        self.edges["B"] = self.load_edge_only_set(24) 
        self.centers["B"] = [self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32", "BACKGR3_S32_7.png"))]

        # Góry trawiaste g
        self.mountain_grass_edges = self.load_edge_only_set(174) 
        self.mountain_desert_edges = self.load_edge_only_set(161) 
        self.mountain_swamp_edges = self.load_edge_only_set(199) 
        self.centers["g"] = [self.load_single_img(os.path.join("assets","normal", "BACKGR3_S32", "BACKGR3_S32_173.png"))]
        self.edges["g"] = self.mountain_grass_edges 
        
        # Świątynie
        self.temple_img = self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_732.png"))
        self.temple2_img = self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_737.png"))

        # Skarby
        self.treasure_imgs = {
            ".": self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_752.png")), 
            "p": self.load_single_img(os.path.join("assets", "normal", "BACKGR3_S32", "BACKGR3_S32_755.png"))  
        }
        
        # Ruiny
        self.ruins_img = self.load_single_img(os.path.join("assets", "minimum", "BUILDIN1_S32", "BUILDIN1_S32_8.png"))

    def load_edge_only_set(self, start_id):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        imgs = []
        for i in range(start_id, start_id + 12):
            imgs.append(self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{i}.png")))
        
        return {
            1: imgs[1], 6: imgs[6], 3: imgs[3], 4: imgs[4],
            0: imgs[0], 2: imgs[2], 5: imgs[5], 7: imgs[7],
            11: imgs[11], 10: imgs[10], 9: imgs[9], 8: imgs[8]
        }

    def load_single_img(self, path, alpha=True):
        TARGET_SIZE = (32, 32)
        if os.path.exists(path):
            img = pygame.image.load(path)
            img = img.convert_alpha() if alpha else img.convert()
            return pygame.transform.scale(img, TARGET_SIZE)
        s = pygame.Surface(TARGET_SIZE)
        s.fill((255, 0, 255))
        return s

    def load_road_graphics(self):
        road_template = {
            6: 0, 12: 1, 3: 2, 9: 3, 5: 4, 10: 5, 7: 6, 13: 7,
            14: 9, 11: 8, 15: 10, 1: 12, 4: 11, 2: 14, 8: 13, 0: 5
        }
        terrain_starts = {".": 819, "B": 834, "p": 851}
        path = os.path.join("assets", "normal", "BACKGR3_S32")

        for terrain, start_id in terrain_starts.items():
            for mask, offset in road_template.items():
                img_id = start_id + offset
                p = os.path.join(path, f"BACKGR3_S32_{img_id}.png")
                self.road_gfx[terrain][mask] = self.load_single_img(p)

        self.road_gfx["trans"]["poziom_trawa_gora_pustynia_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_824.png"))
        self.road_gfx["trans"]["poziom_pustynia_gora_trawa_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_950.png"))
        self.road_gfx["trans"]["pion_trawa_lewo_pustynia_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_954.png"))
        self.road_gfx["trans"]["pion_pustynia_lewo_trawa_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_954.png"))

        self.road_gfx["trans"]["pion_trawa_gora_pustynia_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_953.png"))
        self.road_gfx["trans"]["pion_pustynia_gora_trawa_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_954.png"))
        self.road_gfx["trans"]["poziom_pustynia_lewo_trawa_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_955.png"))
        self.road_gfx["trans"]["poziom_trawa_lewo_pustynia_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_956.png"))

    def load_river_animation(self):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        frames = []
        for i in range(595, 603):
            p = os.path.join(path_base, f"BACKGR3_S32_{i}.png")
            if os.path.exists(p):
                frames.append(self.load_single_img(p))
        if not frames:
            frames.append(pygame.Surface((TILE_SIZE, TILE_SIZE)))
        return frames   
             
    def load_sea_animation(self):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        frames = []
        for i in range(587, 595): 
            p = os.path.join(path_base, f"BACKGR3_S32_{i}.png")
            if os.path.exists(p):
                frames.append(self.load_single_img(p))
        if not frames:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 50, 150)) 
            frames.append(s)
        return frames

    def load_sea_cliffs(self):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        self.sea_cliffs_anim = {}
        mapping = {1: 1, 6: 6, 3: 3, 4: 4, 0: 0, 2: 2, 5: 5, 7: 7, 11: 11, 10: 10, 9: 9, 8: 8}
        start_id = 223
        step = 12 
        
        for edge_id, offset in mapping.items():
            frames = []
            for f in range(8):
                img_id = start_id + offset + (f * step)
                p = os.path.join(path_base, f"BACKGR3_S32_{img_id}.png")
                if not os.path.exists(p):
                    fallback_id = start_id + offset
                    p = os.path.join(path_base, f"BACKGR3_S32_{fallback_id}.png")
                frames.append(self.load_single_img(p))
            self.sea_cliffs_anim[edge_id] = frames

    def load_all_water_assets(self):
        path_base = os.path.join("assets", "normal", "BACKGR3_S32")
        fragments_S = { "TOP_L": 419, "BOT_L": 416, "MID_L": 417, "MID_R": 418, "TOP_R": 420, "BOT_R": 415, "TOP_C": 421, "BOT_C": 422 }
        for name, start_id in fragments_S.items():
            self.waterfall_gfx["S"][name] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{start_id + (f * 16)}.png")) for f in range(8)]
            
        self.waterfall_gfx["N"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{643 + f}.png")) for f in range(8)]
        self.waterfall_gfx["W"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{667 + f}.png")) for f in range(8)]
        self.waterfall_gfx["E"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{659 + f}.png")) for f in range(8)]
        self.waterfall_gfx["S"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{651 + f}.png")) for f in range(8)]

        for kier in ["N", "W", "E"]:
            for seg in ["TOP", "BOT"]:
                self.waterfall_gfx[kier][f"{seg}_C"] = self.waterfall_gfx[kier]["MID_C"]
            for seg in ["TOP", "MID", "BOT"]:
                self.waterfall_gfx[kier][f"{seg}_L"] = self.waterfall_gfx[kier]["MID_C"]
                self.waterfall_gfx[kier][f"{seg}_R"] = self.waterfall_gfx[kier]["MID_C"]

        overlay_starts = {".": 563, "l": 563, "p": 543, "P": 543, "B": 575, "b": 575, "g": 575, "G": 575}
        for terrain_type, start_id in overlay_starts.items():
            self.river_overlays[terrain_type] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{start_id + i}.png")) for i in range(12)]
            
        self.bridge_gfx = {
            "H_L": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_877.png")),
            "H_C": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_878.png")),
            "H_R": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_879.png")),
            "V_T": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_880.png")),
            "V_C": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_881.png")),
            "V_B": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_882.png"))
        }

    # ===================== LOGIKA RYSOWANIA MAPY =====================

    # --- NOWE: FUNKCJA SPRAWDZAJĄCA GĘSTOŚĆ LASU ---
    def is_dense_forest(self, x, y):
        forest_neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                if self.pathfinder.get_bg_tile_at(x + dx, y + dy) == "l": 
                    forest_neighbors += 1
        
        # Twardy wymóg 8 sąsiadów - eliminuje pojedyncze wyrwane kafelki puszczy
        if forest_neighbors < 8: 
            return False
            
        # Szansa na puszczę 2x2 (np. 15%). Zależna od (x, y), żeby nie migała przy przesuwaniu kamery.
        random.seed(x * 1000 + y)
        create_puszcza = random.random() < 0.15 
        random.seed() # reset seeda
        return create_puszcza

    def get_tile_connection_id(self, world, x, y, target_type):
        """Standardowa funkcja autotilingu (styki)"""
        # (Zostawiam bez zmian, bo jest poprawna dla krawędzi)
        friends = {
            "p": ["p", "P","_", "g", "G", "W","S", "&", "$", None], 
            "P": ["P", "p", "g","_", "G", "W", "S", "&", "$", None],
            "B": ["B", "_", "S", "&", "#", "R", "V",".", "l", "p", "W", "g", "G", "S", "&", "$", "R", "#", "_", None],
            "g": ["g" , "P", "W", None],
            "G": ["G", "P", None],
            "_": ["B","G", "g", None],
            "l": ["l", "S", "&","_", "#", "W", None],
            ".": ["_", "S", "&", "#", "R", "V",".", "l", "p", "W", "g", "G", "S", "&", "$", "R", "#", ".","","M", None],
            "M": ["w", "V", "M", "", None],
            "W": ["W", "M", "V", None],
        }
        current_friends = friends.get(target_type, [target_type])

        n  = self.pathfinder.get_bg_tile_at(x, y-1) in current_friends
        e  = self.pathfinder.get_bg_tile_at(x+1, y) in current_friends
        s  = self.pathfinder.get_bg_tile_at(x, y+1) in current_friends
        w  = self.pathfinder.get_bg_tile_at(x-1, y) in current_friends
        ne = self.pathfinder.get_bg_tile_at(x+1, y-1) in current_friends
        nw = self.pathfinder.get_bg_tile_at(x-1, y-1) in current_friends
        se = self.pathfinder.get_bg_tile_at(x+1, y+1) in current_friends
        sw = self.pathfinder.get_bg_tile_at(x-1, y+1) in current_friends

        # Rogi wewnętrzne (skosy)
        if n and w and not nw: return 11
        if n and e and not ne: return 10
        if s and w and not sw: return 9
        if s and e and not se: return 8

        # Rogi zewnętrzne
        if not n and not w: return 0 
        if not n and not e: return 2 
        if not s and not w: return 5 
        if not s and not e: return 7 

        # Krawędzie proste
        if not n: return 1
        if not s: return 6
        if not w: return 3
        if not e: return 4

        return 12
    
    def get_road_tile(self, world, x, y):
        # (Logika dróg bez zmian)
        n = 1 if self.pathfinder.get_tile_at(x, y-1) == "_" else 0
        e = 2 if self.pathfinder.get_tile_at(x+1, y) == "_" else 0
        s = 4 if self.pathfinder.get_tile_at(x, y+1) == "_" else 0
        w = 8 if self.pathfinder.get_tile_at(x-1, y) == "_" else 0
        connections = n + e + s + w

        bg_left   = self.pathfinder.get_bg_tile_at(x-1, y)
        bg_right  = self.pathfinder.get_bg_tile_at(x+1, y)
        bg_up     = self.pathfinder.get_bg_tile_at(x, y-1)
        bg_down   = self.pathfinder.get_bg_tile_at(x, y+1)
        bg_center = self.pathfinder.get_bg_tile_at(x, y)

        pustynia_warianty = ["p", "P", "s"]
        trawa_warianty = ["."]

        if connections == 10: 
            if bg_up in trawa_warianty and bg_down in pustynia_warianty: return self.road_gfx["trans"]["poziom_trawa_gora_pustynia_dol"]
            if bg_up in pustynia_warianty and bg_down in trawa_warianty: return self.road_gfx["trans"]["poziom_pustynia_gora_trawa_dol"]
            if bg_left in pustynia_warianty and bg_right in trawa_warianty: return self.road_gfx["trans"]["poziom_pustynia_lewo_trawa_prawo"]
            if bg_left in trawa_warianty and bg_right in pustynia_warianty: return self.road_gfx["trans"]["poziom_trawa_lewo_pustynia_prawo"]
        elif connections == 5: 
            if bg_left in trawa_warianty and bg_right in pustynia_warianty: return self.road_gfx["trans"]["pion_trawa_lewo_pustynia_prawo"]
            if bg_left in pustynia_warianty and bg_right in trawa_warianty: return self.road_gfx["trans"]["pion_pustynia_lewo_trawa_prawo"]
            if bg_up in trawa_warianty and bg_down in pustynia_warianty: return self.road_gfx["trans"]["pion_trawa_gora_pustynia_dol"]
            if bg_up in pustynia_warianty and bg_down in trawa_warianty: return self.road_gfx["trans"]["pion_pustynia_gora_trawa_dol"]

        logical_terrain = "p" if bg_center in pustynia_warianty else "."
        if bg_center in ["B", "b"]: logical_terrain = "B"

        terrain_dict = self.road_gfx.get(logical_terrain, self.road_gfx["."])
        return terrain_dict.get(connections, terrain_dict.get(10))

    def get_waterfall_context(self, pathfinder, x, y):
        # (Logika wodospadów bez zmian)
        v_up = self.pathfinder.get_bg_tile_at(x, y-1) == "V"
        v_down = self.pathfinder.get_bg_tile_at(x, y+1) == "V"
        v_left = self.pathfinder.get_bg_tile_at(x-1, y) == "V"
        v_right = self.pathfinder.get_bg_tile_at(x+1, y) == "V"

        if v_left or v_right:
            if not v_left: return "S", "TOP_L"
            if not v_right: return "S", "TOP_R"
            return "W", "MID_C" 
        if v_up or v_down:
            if not v_up: return "S", "TOP_C"  
            if not v_down: return "S", "BOT_C" 
            return "S", "MID_C" 
        return "S", "TOP_C"

    def get_bridge_tile(self, pathfinder, x, y):
        # (Logika mostów bez zmian)
        def is_bridge(nx, ny):
            has_road = self.pathfinder.get_tile_at(nx, ny) == "_"
            has_water = self.pathfinder.get_bg_tile_at(nx, ny) in ["W", "V"]
            return has_road and has_water

        bridge_up, bridge_down = is_bridge(x, y-1), is_bridge(x, y+1)
        bridge_left, bridge_right = is_bridge(x-1, y), is_bridge(x+1, y)
        road_up, road_down = self.pathfinder.get_tile_at(x, y-1) == "_", self.pathfinder.get_tile_at(x, y+1) == "_"
        road_left, road_right = self.pathfinder.get_tile_at(x-1, y) == "_", self.pathfinder.get_tile_at(x+1, y) == "_"

        if road_up or road_down:
            if road_up and not bridge_up: return "V_T"     
            if road_down and not bridge_down: return "V_B" 
            return "V_C"

        if road_left or road_right:
            if road_left and not bridge_left: return "H_L"   
            if road_right and not bridge_right: return "H_R" 
            return "H_C"

        return "H_C"

    def get_dominant_land_neighbor(self, pathfinder, x, y, tile_type):
        # (Bez zmian)
        priority = ["B", "b", "p", "P", "s", "l", ".", "g", "G"] 
        for terrain in priority:
            if tile_type == terrain: continue
            for dx, dy in [(0,-1), (0,1), (-1,0), (1,0), (-1,-1), (1,-1), (-1,1), (1,1)]:
                if self.pathfinder.get_bg_tile_at(x + dx, y + dy) == terrain:
                    return terrain
        return "."

    def draw_custom_overlay(self, screen, x, y, pos, overlay_dict, edge_id):
        """Rysuje kafelek ze słownika (może być Surface lub lista do losowania)"""
        data = overlay_dict.get(edge_id)
        if not data: return

        # Jeśli data to lista (standard centers), losujemy
        if isinstance(data, list):
            random.seed(x * 1000 + y)
            img = random.choice(data)
            random.seed() 
        # Jeśli data to pojedynczy Surface (nasza puszcza 2x2), rysujemy wprost
        else:
            img = data
        screen.blit(img, pos)

    def draw_water_tile(self, screen, world, x, y, pos, tile_type):
        # (Animacje wody bez zmian)
        t = pygame.time.get_ticks()
        
        if tile_type == "M" and self.sea_anim:
            f_sea = (t // 200) % len(self.sea_anim)
            screen.blit(self.sea_anim[f_sea], pos)
        elif self.river_anim:
            f_riv = (t // 200) % len(self.river_anim)
            screen.blit(self.river_anim[f_riv], pos)

        if tile_type == "M" and hasattr(self, 'sea_cliffs_anim'):
            edge_id = self.get_tile_connection_id(world, x, y, "M")
            if edge_id != 12: 
                frames = self.sea_cliffs_anim.get(edge_id)
                if frames and len(frames) > 0:
                    idx = (t // 200) % len(frames)
                    screen.blit(frames[idx], pos)

        elif tile_type == "W":
            edge_id = self.get_tile_connection_id(world, x, y, "W") 
            if edge_id != 12:
                neighbor_land = self.get_dominant_land_neighbor(world, x, y, "W") 
                if neighbor_land in self.river_overlays:
                    overlay_img = self.river_overlays[neighbor_land][edge_id]
                    screen.blit(overlay_img, pos)

        if self.pathfinder.get_tile_at(x, y) == "_":
            bridge_part_key = self.get_bridge_tile(world, x, y)
            bridge_img = self.bridge_gfx.get(bridge_part_key)
            if bridge_img:
                screen.blit(bridge_img, pos)

    # ========================================================================
    # GŁÓWNA PĘTLA RYSOWANIA
    # ========================================================================
    def draw_terrain(self, screen, world):
        """Główna pętla renderująca wszystkie kafelki podłoża i obiekty statyczne"""
        tiles_on_screen_x = SCREEN_WIDTH // TILE_SIZE + 1
        tiles_on_screen_y = SCREEN_HEIGHT // TILE_SIZE + 1
        start_x = max(0, world.camera_x // TILE_SIZE)
        start_y = max(0, world.camera_y // TILE_SIZE)
        
        if not world.map or not world.bg_map: return
        
        end_x = min(len(world.map[0]), start_x + tiles_on_screen_x)
        end_y = min(len(world.map), start_y + tiles_on_screen_y)

        current_time = pygame.time.get_ticks()

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                pos = ((x * TILE_SIZE) - world.camera_x, (y * TILE_SIZE) - world.camera_y)
                
                bg_tile = self.pathfinder.get_bg_tile_at(x, y)
                obj_tile = self.pathfinder.get_tile_at(x, y) 

                # ========================================================================
                # --- ZMIANA: TRYB DEBUGOWANIA (Uwzględnia Kwadrat 2x2 Puszczy) ---
                # ========================================================================
                if getattr(world, 'show_only_biome', False):
                    if bg_tile in ["p", "P", "s"]: screen.blit(self.centers["p"][0], pos)
                    elif bg_tile in ["B", "b"]: screen.blit(self.centers["B"][0], pos)
                    elif bg_tile == "W": screen.blit(self.river_anim[0], pos)
                    elif bg_tile == "M": screen.blit(self.sea_anim[0], pos)
                    elif bg_tile in ["G", "g"]: screen.blit(self.centers["g"][0], pos) 
                    elif bg_tile == "l": 
                        # Sprawdzamy gęstość
                        if self.is_dense_forest(x, y):
                            # Pobiera odpowiedni fragment kwadratu na podstawie współrzędnych (modulo)
                            # Dzięki temu puszcza w debugu też tworzy spójny wzór 2x2
                            screen.blit(self.dense_forest_centers[(x % 2, y % 2)], pos)
                        else:
                            screen.blit(self.centers["l"][0], pos)
                    else: screen.blit(self.grass_variants[0], pos)
                    continue 

                # ================= WARSTWA 1: TŁO (Biom) =================
                if bg_tile in ["W", "M"]:
                    self.draw_water_tile(screen, world, x, y, pos, bg_tile)
                elif bg_tile == "V":
                    kier, full_key = self.get_waterfall_context(world, x, y)
                    if kier in self.waterfall_gfx and full_key in self.waterfall_gfx[kier]:
                        wf_frames = self.waterfall_gfx[kier][full_key]
                        if wf_frames and len(wf_frames) > 0:
                            wf_idx = (current_time // 160) % len(wf_frames)
                            screen.blit(wf_frames[wf_idx], pos)
                else:
                    # Domyślny podkład trawy (zawsze pod spodem)
                    screen.blit(self.grass_variants[0], pos)

                    # Rysujemy trawę właściwą (z wagami)
                    grass_edge_id = self.get_tile_connection_id(world, x, y, ".")
                    grass_full_set = self.edges["."].copy()
                    grass_full_set[12] = self.centers.get(".", self.grass_variants)
                    self.draw_custom_overlay(screen, x, y, pos, grass_full_set, grass_edge_id)

                    # Nakładamy inne biomy (Las, Pustynia, Bagno itp.)
                    if bg_tile in self.edges and bg_tile != ".":
                        edge_id = self.get_tile_connection_id(world, x, y, bg_tile)
                        
                        # Specjalna logika dla Gór (zmiana tła krawędzi)
                        if bg_tile in ["g", "G"]:
                            if bg_tile == "G":
                                swamp_set = getattr(self, 'high_mountain_swamp_edges', self.mountain_grass_edges)
                                desert_set = getattr(self, 'high_mountain_desert_edges', self.mountain_grass_edges)
                                grass_set = getattr(self, 'high_mountain_grass_edges', self.mountain_grass_edges)
                            else:
                                swamp_set = getattr(self, 'mountain_swamp_edges', self.mountain_grass_edges)
                                desert_set = getattr(self, 'mountain_desert_edges', self.mountain_grass_edges)
                                grass_set = getattr(self, 'mountain_grass_edges', self.edges["g"])

                            neighbor = self.get_dominant_land_neighbor(world, x, y, bg_tile)
                            if neighbor in ["B", "b"]: current_set = swamp_set.copy()
                            elif neighbor in ["p", "P", "s"]: current_set = desert_set.copy()
                            else: current_set = grass_set.copy()

                            center_img = self.centers.get(bg_tile)
                            if center_img: current_set[12] = center_img
                            self.draw_custom_overlay(screen, x, y, pos, current_set, edge_id)
                        
                        # Logika dla reszty biomów (w tym Lasu)
                        else:
                            full_set = self.edges[bg_tile].copy()
                            
                            # ========================================================================
                            # --- MODYFIKACJA KONTEKSTOWA DLA LASU (KWADRAT PUSZCZY 2x2) ---
                            # ========================================================================
                            # Jeśli rysujemy środek lasu (ID 12) i algorytm wykrył, że las jest gęsty:
                            if bg_tile == "l" and edge_id == 12 and self.is_dense_forest(x, y):
                                # Zamiast losować z listy, pobieramy JEDEN, IDEALNIE DOPASOWANY fragment
                                # kwadratu 2x2 na podstawie współrzędnych x i y.
                                # To gwarantuje, że wzór puszczy będzie spójny i rozciągnięty na cały obszar.
                                full_set[12] = self.dense_forest_centers[(x % 2, y % 2)]
                            else:
                                # Standardowe wnętrze lasu (lub innego biomu) - losujemy warianty
                                full_set[12] = self.centers.get(bg_tile, self.grass_variants)
                            # ========================================================================
                                
                            self.draw_custom_overlay(screen, x, y, pos, full_set, edge_id)

                # ================= WARSTWA 2: OBIEKTY NA MAPIE =================
                raw_obj_tile = world.map[y][x] # Prawdziwy obiekt z mapy, bez "oszukiwania"
                if raw_obj_tile == " ": continue 
                
                # Drogi
                if raw_obj_tile == "_":
                    if bg_tile != "W":
                        road_img = self.get_road_tile(world, x, y)
                        if road_img: screen.blit(road_img, pos)
                # Budynki/Statyczne
                elif raw_obj_tile in ["S", "&"]:
                    if raw_obj_tile == "S": screen.blit(self.temple_img, pos) 
                    elif raw_obj_tile == "&": screen.blit(self.temple2_img, pos) 

                # Skarby (ze zmianą tła pod skarberm p/.)
                elif raw_obj_tile == "$":
                    logical_bg = "p" if bg_tile in ["p", "P", "s"] else "."
                    img = self.treasure_imgs.get(logical_bg, self.treasure_imgs["."])
                    screen.blit(img, pos)
                # Debugowanie Fundamentów
                elif raw_obj_tile == "#":
                    is_left = (x == 0 or world.map[y][x-1] != "#")
                    is_top = (y == 0 or world.map[y-1][x] != "#")
                    if is_left and is_top:
                        big_rect = pygame.Rect(pos[0], pos[1], TILE_SIZE * 2, TILE_SIZE * 2)
                        pygame.draw.rect(screen, (255, 255, 255), big_rect, 4)

                # =======================================================
                # 1. PUŁAPKI (Widoczność i rysowanie tego co pod spodem)
                # =======================================================
                elif raw_obj_tile == "X":
                    # --- NAJPIERW: Rysujemy tło pod pułapką (jeśli to była droga lub skarb) ---
                    oryginalny_obiekt = getattr(world, 'trap_backgrounds', {}).get((x, y), ".")
                    
                    if oryginalny_obiekt == "_":
                        # ZMIANA: Rysujemy teksturę drogi TYLKO na lądzie! (Na rzece most już jest narysowany pod spodem)
                        if bg_tile not in ["W", "V", "M"]:
                            road_img = self.get_road_tile(world, x, y)
                            if road_img: screen.blit(road_img, pos)
                            
                    elif oryginalny_obiekt == "$":
                        logical_bg = "p" if bg_tile in ["p", "P", "s"] else "."
                        img = self.treasure_imgs.get(logical_bg, self.treasure_imgs["."])
                        screen.blit(img, pos)

                    # --- POTEM: Rysujemy właściwą pułapkę (jeśli widoczna) ---
                    trap = getattr(world, 'traps', {}).get((x, y))
                    if trap:
                        current_player = world.players[world.current_player]
                        if trap["owner"] == current_player or current_player in trap.get("detected_by", set()):
                            if "X" in self.terrain_images:
                                screen.blit(self.terrain_images["X"], pos)
                            else: # Failsafe
                                pygame.draw.line(screen, (200,0,0), (pos[0]+6, pos[1]+6), (pos[0]+26, pos[1]+26), 3)
                                pygame.draw.line(screen, (200,0,0), (pos[0]+26, pos[1]+6), (pos[0]+6, pos[1]+26), 3)

    def draw_construction_sites(self, screen, world):
        """Rysuje kompletne place budowy zamków niezależnie od krawędzi ekranu"""
        if not world.map: 
            return

        for y in range(len(world.map)):
            for x in range(len(world.map[0])):
                if self.pathfinder.get_tile_at(x, y) == "#":
                    
                    px = (x * TILE_SIZE) - world.camera_x
                    py = (y * TILE_SIZE) - world.camera_y
                    
                    # Rysujemy tylko, jeśli chociaż kawałek placu jest na ekranie
                    margin = TILE_SIZE * 2
                    if not (-margin < px < SCREEN_WIDTH + margin and -margin < py < SCREEN_HEIGHT + margin):
                        continue

                    bg_tile = self.pathfinder.get_bg_tile_at(x, y)
                    if bg_tile in ["p", "P", "s"]:
                        zestaw = getattr(self, 'build_desert', None)
                    else:
                        zestaw = getattr(self, 'build_grass', None)
                        
                    if zestaw:
                        if (0, 0) in zestaw: screen.blit(zestaw[(0, 0)], (px, py))
                        if (1, 0) in zestaw: screen.blit(zestaw[(1, 0)], (px + TILE_SIZE, py))
                        if (0, 1) in zestaw: screen.blit(zestaw[(0, 1)], (px, py + TILE_SIZE))
                        if (1, 1) in zestaw: screen.blit(zestaw[(1, 1)], (px + TILE_SIZE, py + TILE_SIZE))

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        