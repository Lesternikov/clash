import random
import pygame
import os

class LootManager:
    def __init__(self, assets_path="assets/minimum/TEMPLE_S32"):
        self.assets_path = assets_path
        # Dzielimy na dwie niezależne bazy
        self.temple_loot = []
        self.digging_loot = []
        self._initialize_loot()

    def _initialize_loot(self):
        # 1. ŚWIĄTYNIA (Tu możesz dodać swoje 20 przedmiotów ze świątyni)
        temple_data = [
            (0, "BIADA CI!",["Zaiste, jesteś wielkim grześnikiem. Bóg w odpowiedzi na twe modły"
            "poraził Cię gromem z jsnego nieba. Będziesz gnił w piekle przez całą wieczność."]),
            (1, "ODDZIAŁ", ["Zaiste, liczne ofiary, które skłądałęś przed świętym posągiem, sprawiły"
            "że bogowie patrzą na ciebie łąskawym okiem. Na dowód tego zesłali "
            "ci nowy oddział.",
            "Alleluja Chwalmy Pana za jego łaski! Bóg w swej dobroci, spowodował, "
            "że pod Twą chorągiew oddał się nowy oddział."]),
            (2, "PIERŚCIEŃ MOCY", ["Przeszukując zakamarki świątyni natrafiłeś na zawinięty w chustę"
            "pierścień. Jego moagiczna moc uzdrowi twoje oddziały z wojennych "
            "ran"]),
            (3, "MEDALION TUREOKA", ["Przeszukując zakamarki świątyni odnalazłeś medalion Tureoka."
            "Pomoże on odzyskać Twoim oddziałom pełnię sił."]),
            (4, "KIELICH AMBROZJI", ["Znaki na ołtarzu wskazały Ci schowek, w którym znalazłeś kielich"
            "wypełniony świętym nektarem. Uzdrowi on wszystkie Twe jednostki."]),
            (5, "RĘKAWICA SIŁY", ["Bogowie przyjęcli Twą ofiarę i zesłąli Ci wspaniały dar. RĘKAWICA SIŁY"
            "mocno wpłynie na umiejętności Twych rycerzy."]),
            (6, "MIECZ PALLADYNÓW",["Bóg spojrzał łąskawym okiem na Twe modły i ofiarowałCi MIECZ "
            "PALLADYNÓW. Moc z niego płynąca znacznie poprawi umiejętności"
            "bitwene twych rycerzy."]),
            (7, "KSIĘGA WYZNAŃ", ["Znalazłeś bardzo starą księgę. To KSIĘGA WYZNAŃ. Z jej strof wypływa"
            "magiczna moc, która przyczyni się do zwiększenia morale Twoich "
            "jednostek."]),
            (8, "HEŁM ZDOBYWCÓW", ["Twe modły zostały wysłuchane. Światło płynące z ołtarza wskazało"
            "Ci schowek z ukrytym HEŁMEM ZDOBYWCÓW. Pomoże on odzyskać "
            "Twoim oddiałom pełnię sił."]),
            (9, "ZŁOTY TOPÓR", ["Bogowie ofiarowali Ci ZŁOTY TOPÓR. Bijący z niego blask napełnia wiarą"
            "w zwycięstwo Twych wojowników. Nie lękają się już nikogo, są żądni"
            "krwi."]),
            (10, "TARCZA TREGÓW", ["W ukrytej wnęce odnalazłeś TARCZĘ TREGÓW. Jej moc przyczyniłą się"
            "do znaczengo polepszenia umiejętności bitewnych Twojego wojska."]),
            (11,"CUDOWNE CIŻEMKI", ["Odnalazłeś CUDOWNE CIŻEMKI. Na ich piętach znajdowało się wyryte "
            "zaklęcie. Dzięki niemu znużenie twych jednostek znikło bez śladu."]),
            (12,"KLEPSYDRA", ["Za ofiarnym ołtarzem znalazłęś KLEPSYDRĘ, Ku twemu zdziwieniu w "
            "momencie gdy ją obróciłęś wojenne rany Twoich jednostek zagoiły"
            "się błyskawicznym tempie."]),
            (13,"ZŁOTO", ["Stary druid wskazał ci miejsce, w któym ukryto mieszek diamentów."
            "Ich wartość przekracza 200 sztuk złota.", 
            "Od starego mnicha otrzymałeś mieszek wypchany diamentami wartymi "
            "ponad 200 sztuk złota. Jest przekonany, że dar ten wykorzystasz w "
            "zbożnym celu."]),
            (14,"DIAMENT", ["Stary mnich wręczył Ci diament warty 50 sztuk złota. Wierzy on, że "
            "kwotę tę wykorzystasz głosząc wśród pogan słowo Boże.", 
            "Opiekun świętego miejsca wręczył Ci siament wart 100 sztuk złota. Ma"
            "nadzieję, że szybko rozprawisz się z najeźdzcą."]),
            (15,"ZŁOTO", ["Modląc się wzrok Twój przykuła niewielka szczelina w ścianie. "
            "Odnalazłeś tam szkatułkę wypełnioną kosztownośćiami wartymi 100"
            "sztuk złota.", "Tutejszy driud słysząc twe gorliwe modł ofiarował Ci 50 sztuk"
            "złota. Wierzę, że nie dopuścisz do przejęcia naszych ziem przez "
            "intruzów, złoto powinno Ci w tym pomóc."]),
            (19,"CZARNY DIAMENT", ["Znalazłeś wspaniale lśniący CZARNY DIAMENT. Chciwość zawitała wsród"
            "Twoich wojowników, a to bardzo źle wpływa na morale."]),
            (20,"MIECZ GŁUPCÓW", ["Znalazłeś wspaniale lśniący miecz. Każdy z Twoich rycerzy chciał stać "
            "się wyłącznym właścicielem tego oręża.Wybuchła więc bójka, któa "
            "zamieniłą się w krwawą jatkę. MIECZ GŁUPCÓW bardzo źle wpłynął na "
                                "morale Twoich jednostek"]),
            (21,"KSIĘGA PLAG", ["Pod ołtarzem odnalazłeś starą księgę. Czytając jej stronice "
            "zorientowałęś się, że wypowiadasz słowa klątwy. KSIĘGA PLAG nie "
            "powinna być oglądana przez zwykłęgo śmiertelnika!!!"]),
            (25, "DAR BOGÓW", ["Twoje ofiary nie przyniosły pożądanego skutku. Bogowie zignorowali "
            "twe modły."]),
            (26,"DAR MODLITWY", ["Szczera modlitwa dodała siłTwoim żołnierzom. Czujesz, jak twe ciało"
            "wypełnia nieziemska moc, a znużenie znika bez śladu."]),
        ]
        
        # 2. KOPANIE (Tu Twoje 20 przedmiotów ze skarbów)
        digging_data = [
            (15,"ZŁOTO",  ["Miałęś już zrezygnować z poszukiwań, gdy nagle łopata uderzyła w "
            "wieko starego kufra. Wprawnym ruchem wyłamałeś kłódkę i znalazłeś"
            "w środku 300 sztuk złota.",
            "Głuchy dźwięk wydobył się przy kolejnym uderzeniu łopatą. Natrafiłeś"
            "na bardzo zmuszałą skrzynię. Gdy już ją otwarłeś Twoim oczom"
            "ukazały się kosztowności warte 200 sztuk złota.",
            "Twoje wysiłki nie poszł na marne. Na dnie dołu znalazłeś mieszek z "
            "monetami, a jest ich około 50."]),
            (16,"SKARB", ["W grudach ziemi coś zalśniło. Jeszcze kilka uderzeń łopaty i stajesz si ę "
            "posiadaczem szkatuły wypełnionej kosztownośćiami wartymi 100 sztuk"
            "złota.", 
            "Znalazłeś zbutwiałą skrzynię. Mecne uderzenie łopatą w kłódkę i"
            "Twoim oczom ukazałsię skarb warty 50 sztuk złota."]),
            # PUSTE (Brak grafiki)
            (27, "     ", [
                "Ktoś byłszybszy, miejsce zostało już dokładnie przeszukane, a to co "
                "ukryte już dawno ma nowego właściciela. ",
                "Cał dzień zmarnowałeś na kopaniu. Jedynym skarbem jaki znalazłeś"
                "okazał się zbutwiały pień drzewa,",
                "Niestety, ktoś wprowadził cię w błąd. W tym miejscu nie ma żadnych"
                "skarbów."])
        ]

        # Funkcja pomocnicza do ładowania
        # Funkcja pomocnicza do ładowania
        def load_data(data_list, target_list):
            for img_id, title, desc in data_list:
                img = None
                if img_id > 0:
                    path = os.path.join(self.assets_path, f"TEMPLE_S32_{img_id}.png")
                    try: 
                        img = pygame.image.load(path).convert_alpha()
                    except: 
                        pass
                
                # TUTAJ JEST POPRAWKA - dodajemy "img_id": img_id
                target_list.append({
                    "img_id": img_id, 
                    "img": img, 
                    "title": title, 
                    "desc": desc
                })

        load_data(temple_data, self.temple_loot)
        load_data(digging_data, self.digging_loot)

    def get_temple_loot(self):
        return random.choice(self.temple_loot)

    def get_digging_loot(self):
        return random.choice(self.digging_loot)
# Funkcja pomocnicza do ładowania
    def load_data(data_list, target_list):
        for img_id, title, desc in data_list:
            img = None
            if img_id > 0:
                path = os.path.join(self.assets_path, f"TEMPLE_S32_{img_id}.png")
                try: img = pygame.image.load(path).convert_alpha()
                except: pass
            # DODAJEMY "img_id": img_id, ŻEBY ŚWIAT WIEDZIAŁ CO WYLOSOWAŁ
            target_list.append({"img_id": img_id, "img": img, "title": title, "desc": desc})