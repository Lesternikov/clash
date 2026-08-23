TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
# Rozmiar Twojej logicznej mapy (listy w self.map)

MAP_WIDTH = 100 
MAP_HEIGHT = 100

UNIT_NAMES = {
    "PEON": "Posp. ruszenie",
    "INFL": "Lekka piechota",
    "INFH": "Ciężka piechota",
    "SPRL": "Pikinier",
    "SPRH": "Halbardnik",
    "CAVL": "Lekka jazda",
    "CAVH": "Ciężka jazda",
    "RYC": "Rycerstwo",
    "DRAG": "Dragon",
    "ARCH": "Łucznik",
    "KUSZA": "Kusznik",
    "MUSZK": "Muszkieter",
    "KATAP": "Katapulta",
    "TARAN": "Taran",
    "ARMAT": "Armata",
    "LESN": "Leśnik",
    "GORAL": "Góral",
    "BUDOW": "Budowniczy", # <-- tutaj brakowało przecinka
    "WORM": "Czerw",
    "SLON": "Słoń",
    "CYKL": "Cyklop",
    "TROL": "Troll",
    "SCORP": "Skorpion",
    "SZK": "Szkielet",
    "MAG": "Mag",
    "DUCH": "Duch",
    "ORZEL": "Orzeł",
    "PEGAZ": "Pegaz",
    "SKRZ": "Skrzydlak",
    "WAZKA": "Ważka",
    "SMOK": "Smok",
    "PEAS": "Chłopi", # <-- tutaj brakowało przecinka
    "SPECK": "Generał Kobieta",
    "SPECM": "Generał",
    "GOLD": "Złoto",
}
NAME_TO_CODE = {name: code for code, name in UNIT_NAMES.items()}
COLOR_TO_ID = {
    "red": 1,
    "blue": 2,
    "yellow": 3,
    "white": 4,
    "green": 5
}
UNIT_STATS = {
    "Posp. ruszenie":{"hp":100,"moves":24,"attack":1,"defense":1,"exp":0,"morale":10,"fatigue":0,"patent_cost":0,"production_cost": 2,"production_time":1, "description":"""Chłopi\n 
        Chłopi zajmują się
        zwykle uprawą roli.
        Używani do walki
        nie stanowią specja-
        lnie wartościowego
        materiału. Jednostki
        złożone z chłopstwa
        są jednymi z najsłab-
        szych na polu bitwy."""},

    "Lekka piechota": {"hp": 100, "moves":20, "attack": 5, "defense": 4,"exp":0,"morale":10,"fatigue":0,"patent_cost":10,"production_cost":3 ,"production_time":2,"description":"""Lekka piechota\n
        Lekka piechota
        stanowi formację 
        stojącą dość nisko 
        w hierarchii od- 
        działów, jednak 
        gdy zdobędzie bitew- 
        ne doświadczenie 
        stanie się naprawdę 
        groźnym orężem w 
        Twoich rękach. """},

    "Ciężka piechota": {"hp": 100, "moves":20, "attack": 9, "defense": 6,"exp":0,"morale":10,"fatigue":0,"patent_cost":30 ,"production_cost":10 ,"production_time":2, "description":"""Ciężka Piechota\n
        Ciężka piechota -
        najsilniej uzbrojona 
        jednostka piesza. Jest 
        to formacja elitarna, 
        skuteczna zarówno w 
        ataku, jak i w obronie. 
        Na pewno przysłuży 
        Ci się w niejednej bitwie."""},

    "Pikinier": {"hp": 100, "moves":24, "attack": 3, "defense": 5,"exp":0,"morale":10,"fatigue":0,"patent_cost":30 ,"production_cost":5 ,"production_time":2,"description":"""Pikinierzy\n
        Pikinierzy - piesze oddziały
        uzbrojone w długie piki. 
        Większość z żołnierzy służą- 
        cych w tych oddziałach wywo- 
        dzi się z Kalmyrii - małego, 
        górskiego państewka, leżącego 
        między dwoma wielkimi pas- 
        mami gór - Segen i Tegen. 
        Pikinierzy doskonale nadają 
        się do ochrony wartościowych 
        jednostek podczas bitwy."""},

    "Halbardnik": {"hp": 100, "moves":22, "attack": 5, "defense": 5,"exp":0,"morale":10,"fatigue":0,"patent_cost":50 ,"production_cost":10 ,"production_time":3, "description":"""Halabardnicy\n
        Halabardnicy - ciężka
        piechota uzbrojona w 
        halabardy-oręż bardzo 
        skuteczny, zwłaszcza 
        podczas obrony. 
         
         
        Serajscy halabardnicy 
        nieraz spowodują, że 
        szala zwycięstwa przechyli 
        się na Twoją stronę, panie."""},

    "Lekka jazda": {"hp": 100, "moves":36, "attack": 8, "defense": 5,"exp":0,"morale":10,"fatigue":0,"patent_cost":100,"production_cost": 3,"production_time":3, "description":"""Lekka jazda\n
        Lekka jazda - konnica
        charakteryzująca się 
        dużą mobilnością. Jej 
        ulubioną taktyką walki 
        jest szybki atak i na- 
        tychmiastowa ucieczka. 
        W oddziałach tych 
        służą najemnicy wywo- 
        dzący się z koczowniczych 
        plemion wędrujących po 
        stepach Tajmuru."""},

    "Ciężka jazda": {"hp": 100, "moves":32, "attack": 14, "defense": 8,"exp":0,"morale":10,"fatigue":0,"patent_cost":200 ,"production_cost":10 ,"production_time":4, "description":"""Ciężka Jazda\n
        Ciężka jazda jest najsil- 
        niejszą z jednostek konnych. 
        Rycerze służący w tych od- 
        działach to najlepsi jeźdźcy 
        wybrani spośród synów szla- 
        checkich. Wiele lat dosko- 
        nalili swój kunszt wojenny 
        w walce i na turniejach 
        rycerskich, a teraz służą 
        pod Twoimi rozkazami, panie. """},

    "Rycerstwo":{"hp":100,"moves":30,"attack":12,"defense": 7,"exp":0,"morale":10,"fatigue":0,"patent_cost":150 ,"production_cost":8 ,"production_time":4,"description":"""Rycerstwo\n
        Rycerstwo - zaciężne
        oddziały rycerzy polo- 
        peskich. Długie lance 
        i przytwierdzone do ra- 
        mion skrzydła napeł- 
        niają trwogą nawet 
        najodważniejszego wro- 
        ga. Rycerstwo doprowa- 
        dzi Cię do szybkiego 
        zwycięstwa. Panie, nie 
        zlekceważ tej potęgi.""" },

    "Dragon":{"hp":100,"moves":32,"attack":10,"melee_attack": 6,"defense":4,"range": 3, "tags": ["ranged"],"exp":0,"morale":10,"fatigue":0,"patent_cost":150 ,"production_cost":5 ,"production_time":4, "description":"""Dragoni\n
        Dragoni - kawaleria uzbrojona
        w pistolety, które jednak mają
        dość ograniczony zasięg rażenia.
        Dragoni rekrutują się z na-
        jemników pochodzących głó-
        wnie z krajów północy tzn.
        Bardii, Kardylii i Derbii.
        Są to ludzie wytrzymali i
        ieustępliwi, a co najważ-
        niejsze bardzo, ale to bardzo
        waleczni."""},

    "Łucznik": {"hp": 100, "moves":24, "attack": 3,"melee_attack": 6, "defense": 1, "range": 3, "tags": ["ranged"],"exp":0,"morale":10,"fatigue":0,"patent_cost":60,"production_cost":10 ,"production_time":2, "description":"""Łucznicy\n
        Oddziały łuczników
        przybyły prosto z 
        Galaghelu, by służyć 
        Ci swym sokolim 
        wzrokiem, panie. Choć 
        ich wartość bojowa w 
        bezpośrednim starciu 
        jest niewielka, to w 
        walce na odległość 
        rozbiją nawet 
        najsilniejsze oddziały."""},

    "Kusznik": {"hp": 100, "moves":20, "attack": 5, "melee_attack": 8, "defense": 2, "range": 4, "tags": ["ranged"],"exp": 0, "morale": 10, "fatigue": 0, "patent_cost": 240, "production_cost": 12, "production_time": 4, "description": """Kusznicy\n"
        Kusznicy - ich bełty
        przebijają nawet naj-
        grubszy pancerz, zada-
        jąc śmierć szybciej niż
        strzała łucznika. Ćwiczeni
        na polach Faraghelu ra-
        dzą sobie dobrze zarówno
        w walce na odległość, jak
        i w bezpośrednim starciu."""},

    "Muszkieter": {"hp": 100, "moves":24, "attack": 4,"melee_attack": 11, "defense": 3, "range": 4, "tags": ["ranged"],"exp":0,"morale":10,"fatigue":0,"patent_cost":290 ,"production_cost":14 ,"production_time":4, "description":"""Muszkieterzy\n
        Muszkieterzy - oddziały
        sprowadzone z dalekiej
        Baarii, kraju leżącego
        na niewielkiej wyspie
        u wybrzeży starego kon-
        tynentu. Podstawą uz-
        brojenia tych formacji
        jest oczywiście muszkiet
        skuteczniejszy zarówno
        od łuku jak i od kuszy."""},

    "Katapulta":{"hp": 100, "moves":20, "attack": 16, "defense": 1, "range": 5, "tags": ["ranged"],    "exp": 0, "morale": 10, "fatigue": 0,"patent_cost": 300, "production_cost": 18, "production_time": 4, "description":"""Katapulta\n 
        Katapulta - machina potrafią-
        ca miotać na dalekie dystanse
        kamienne głazy. Niestety
        katapulta jest
        bardzo wrażliwa
        na ciosy przeci-
        wnika. W sy-
        tuacji, gdy zna-
        jdzie się w polu rażenia wrogich oddziałów, stanowi
        łatwy łup."""},

    "Taran":{"hp":100,"moves":20,"attack":20,"defense":10,"exp":0,"morale":10,"fatigue":0,"patent_cost":50 ,"production_cost":10 ,"production_time":3, "description":"""Taran\n
        Taran jest rodzajem maszyny oblężniczej, służącej
        do zdobywania murów. W zwykłej walce jest 
        bezużyteczny, lecz podciągnięty pod zamek wroga 
        umożliwi przedarcie się na najbardziej ufortyfiko- 
        wane dziedzińce.""" },

    "Armata":{"hp":100,"moves":16,"attack":20,"defense":1,"range": 5, "tags": ["ranged"],"exp":0,"morale":10,"fatigue":0,"patent_cost":400 ,"production_cost": 20,"production_time":5, "description":"""Armata\n
        Armaty potrafią wys-
        trzeliwać żelazne kule
        na wielkie odległości,
        są więc najskuteczniej-
        szą bronią w walce na
        dystans. Podobnie jak
        katapulta, armata jest
        bardzo wrażliwa na ciosy
        przeciwnika, toteż podczas
        bitwy łatwo ją utracić."""},

    "Leśnik":{"hp":100,"moves":24,"attack":8,"melee_attack": 11,"defense":4,"range": 4, "tags": ["ranged"],"exp":0,"morale":10,"fatigue":0,"patent_cost":100 ,"production_cost":10 ,"production_time":3, "description":"""Leśnicy\n
        Leśnicy - specjalne
        jednostki złożone z 
        dzikich ludzi wycho- 
        wanych w puszczy, 
        świetnie czują się w 
        lasach. Leśnicy uz- 
        brojeni są w krótki 
        jednosieczny miecz 
        i łuk. Ich wszechstro- 
        nność to atut godny 
        uwagi, panie."""},
        
    "Góral": {"hp": 100, "moves":26, "attack": 8, "defense": 6,"exp":0,"morale":10,"fatigue":0,"patent_cost":80 ,"production_cost": 8,"production_time":3, "description":"""Górale\n
        Górale-synowie
        pasterzy owiec 
        zwerbowani 
        do Twojej armii. Ich 
        znajomość górskich 
        szlaków powoduje, 
        że w szybkim 
        tempie pokonują 
        każdy łańcuch górski."""},

    "Budowniczy":{"hp":100,"moves":126,"attack":1,"defense":1,"exp":0,"morale":10,"fatigue":0,"patent_cost":80 ,"production_cost":6 ,"production_time":3, "description":"""Budowniczy\n
        Budowniczy - formacje nie-
        zbędne przy konstruowaniu 
        zamków, dróg, mostów itd. 
        Są nieodzowni przy powię- 
        kszaniu Twych posiadłości 
        panie. Dzięki umiejętności 
        kopania wilczych dołów po- 
        trafią unieszkodliwić nie- 
        w bezpośrednim starciu są 
        bezbronni."""},
        
    "Czerw":{"hp":100,"moves":18,"attack":14,"defense":9,"exp":0,"morale":6,"fatigue":0,"patent_cost":250 ,"production_cost":10 ,"production_time":3, "description":"""Czerw\n
        Czerw to ogromne stworzenie. Choć pozbawiony oczu
        i kończyn, potrafi odnaleźć wroga dzięki świetnemu
        węchowi i wyczuwaniu wibracji ziemi. Jego ojczyzną
        są błota Billdel. Walczy pożerając wszystko na swej
        drodze. Posiadając tego stwora dysponujesz siłą porów-
        nywalną do kawalerii."""},    

    "Słoń": {"hp": 100, "moves":20, "attack": 14, "defense":10,"exp":0,"morale":6,"fatigue":0,"patent_cost":300 ,"production_cost":10 ,"production_time":4, "description":"""Słoń\n
        Słoń - już od
        starożytnych
        czasów używano
        go do walki.
        Hodowany w
        Afryce przez
        plemię Karhullów
        jest bitwie bardzo
        niebezpieczny, dzięki
        swym ogromnym rozmiarom i wytrzymałości. Atakujący
        słoń jest trudny do zatrzymania - czyni to z niego jedno z
        najgroźniejszych stworzeń na polu walki."""},

    "Cyklop":{"hp":100,"moves":26,"attack":10,"melee_attack": 10,"defense":6,"range": 3, "tags": ["ranged"],"exp":0,"morale":6,"fatigue":0,"patent_cost":280 ,"production_cost": 10,"production_time":3, "description":"""Cyklop\n
        Cyklop zamieszkuje
        małe wysepki Morza
        Kalwadyjskiego. Jest
        to potężny, humano-
        idalny stwór o jednym
        oku i silnie umięśnio-
        nym, pokrytym licznym
        owłosieniem ciele. Zaletą
        cyklopa jest jego wszech-
        stronność: dobry zarówno podczas ataku, jak i obrony.
        W czasie bitwy nie rozstaje się ze swoim koszem peł-
        nym kamieni, którymi nader celnie ciska."""},

    "Troll":{"hp":100,"moves":22,"attack":13,"defense":10,"exp":0,"morale":6,"fatigue":0,"patent_cost":270 ,"production_cost": 10,"production_time":4, "description":"""Troll\\n
        Troll określany zawsze dwoma
        słowami - ogromny i bezlitosny - 
        podobny jest nieco do człowieka, 
        jednak znacznie od niego głu- 
        pszy. Ma to wszelako i swe do- 
        bre strony, czyni z niego dobre- 
        go żołnierza. Trolle są stworze- 
        nami pochodzącymi z gór 
        Barskich. Lubują się w walce 
        często używając niepospolitej 
        broni, jaką jest wielki, kamien- 
        ny młot, skuteczny zwłaszcza 
        podczas natarcia."""},

    "Skorpion":{"hp":100,"moves":26,"attack":12,"defense":8,"exp":0,"morale":6,"fatigue":0,"patent_cost":290 ,"production_cost": 10,"production_time":3, "description":"""Skorpion\n
        Skorpion - olbrzymi (osiągający nawet
        trzy metry długości) pajęczak
        zamieszkuje
        gorące i suche
        krainy, pospolity
        zwłaszcza w rejonach
        Pustyni Nubijskiej.
        Bronią skorpiona
        jest umieszczone na końcu ogona, śmiercionośne żądło.
        W walce dobrze spisuje się podczas manewrów i
        ataku, jego słabszą stroną jest obrona.""" },    

    "Szkielet":{"hp":100,"moves":22,"attack":13,"defense":10,"exp":0,"morale":6,"fatigue":0,"patent_cost":280 ,"production_cost":15 ,"production_time":4, "description":"""Szkielet\n
        Szkielet - przywrócone do życia
        ciało dawno zmarłych wojowników.
        Szkielet walczy bardzo skutecznie,
        jest jedną z najsilniejszych
        postaci na polu walki. Nie
        posiada ciała, co uwalnia
        go od ograniczeń nakłada-
        nych żywym ludziom.
        Trudno go unicestwić, gdyż
        magia i doświadczenie nabyte
        za życia czynią go niesamo-
        wicie odporną istotą.""" },

    "Mag":{"hp":100,"moves":40,"attack":10,"melee_attack": 15,"defense":10, "range": 6, "tags": ["ranged"],"exp":0,"morale":6,"fatigue":0,"patent_cost":400 ,"production_cost":20 ,"production_time":5,"description":"""Mag\n
        Mag - jego znajo-
        mość magii będzie
        bardzo przydatna
        podczas bitwy. Mag
        potrafi miotać ogniste
        kule na wielkie odle-
        głości. W bezpośred-
        nim starciu dobry w
        ataku i obronie. Mag
        jest bardzo szybkim wojownikiem.""" },

    "Duch":{"hp":100,"moves":24,"attack":10,"defense":8,"exp":0,"morale":6,"fatigue":0,"patent_cost":380 ,"production_cost":8 ,"production_time":3,"descryption":"""Upiór\n
        Upiór - niewidoczny dla
        zwykłego śmiertelnika
        (można zobaczyć go tylko
        dzięki pozornie pustej zbroi,
        w którą lubi się przyodziewać).
        Skuteczność walki upiora
        porównywalna jest ze
        skutecznością dragonów,
        jednak zbroja i ciężki topór
        czynią go dużo wolniejszym.""" },

    "Orzeł":{"hp":100, "moves":34, "attack":9, "defense":6,"exp":0,"morale":6,"fatigue":0,"patent_cost":300 ,"production_cost":5 ,"production_time":3, "description":"""Orzeł\n
        Orzeł to wielki ptak drapieżny, panie... Dzięki
        specjalnej hodowli przystosowany do walki z
        każdym innym rodzajem wojsk. Porusza się bardzo
        szybko, lecz jego słabą stroną jest obrona."""},

    "Pegaz":{"hp":100, "moves":30, "attack":12, "defense":8,"exp":0,"morale":6,"fatigue":0,"patent_cost":350 ,"production_cost":8 ,"production_time":3, "description":"""Pegaz\n
        Pegaz - uskrzydlony koń,
        bardzo rzadkie zwie-
        rzę uważane nawet przez
        niektórych za mityczne. Tere-
        nami występowania pegazów
        są niedostępne stoki Gór
        Seladańskich, gdzie żyje
        jeszcze kilka stad tych pięk-
        nych stworzeń. Pegaz w boju
        przypomina cechami sko-
        rpiona, jest jednak szybszy."""},

    "Skszydlak":{"hp":100,"moves":24,"attack":10,"melee_attack": 10,"defense":10,"range": 4, "tags": ["ranged"],"exp":0,"morale":6,"fatigue":0,"patent_cost":400 ,"production_cost":16 ,"production_time":5,"description":"""Skrzydlak\n
        Skrzydlak to przedziwny stwór. Spłaszczone ciało, ogromna,
        ziejąca ogniem paszcza, wielkie skrzydła i długi, ostro
        zakończony ogon sprawiają, że widok lecącego skrzydlaka
        jest wprost przerażający. Nie wiadomo jak stworzenie
        to się rozmnaża, nie widziano nigdy żywego skrzydlaka
        na ziemi. Twierdzi się stąd, że całe życie spędza w powietrzu.
        Mając skrzydlaka na swych usługach zyskujesz jedną z
        najsilniejszych i najwszechstronniejszych jednostek.""",},

    "Ważka":{"hp":100,"moves":32,"attack":8,"defense":5,"exp":0,"morale":6,"fatigue":0,"patent_cost":380 ,"production_cost":5 ,"production_time":2, "description":"""Ważka mamucia\n
        Ważka mamucia,
        zamieszkuje rozle- 
        wiska rzeki Bhag. 
        Jest największym 
        znanym owadem, 
        osiąga bowiem 
        rozmiary drapieżnego 
        ptaka. Bronią ważki 
        jest kolec jadowy. Stworzenie to posiada dwie 
        pary skrzydeł, co sprawia, że jest ono na polu 
        walki bardzo ruchliwe."""},

    "Smok":{"hp":100,"moves":36,"attack":18, "melee_attack": 15,"defense":15,"exp":0,"morale":6,"fatigue":0,"patent_cost":550 ,"production_cost":20 ,"production_time":5, "description":"""Smok\n
        Smok - pradawny gad
        zaopatrzony w parę błoniastych
        skrzydeł to pozostałość starych
        czasów. Smok jest wielkim i
        silnym zwierzęciem. Jego ciało
        pokrywa twarda łuska, wnę-
        trzności zaś zdolne są do wyt-
        warzania ognistych podmu-
        chów. Te umiejętności spra-
        wiają, że smok nie ma sobie
        równych przeciwników zarów-
        no w powietrzu, jak i na ziemi.""" },

    "Generał":{"hp":100,"moves":36},

    "Złoto":{"hp":100,"moves":36},

    "Chłopi":{"hp": 100, "moves":36},
   }

TERRAIN_TYPES = {
    # --- NIEPRZEJEZDNE (Brak klucza 'cost' = blokada) ---
    "W": {"name": "woda", "color": (0, 199, 255)},
    "M": {"name": "morze", "color": (0, 0, 128)},
    "G": {"name": "góry wysokie", "color": (85, 85, 85)},
    "B": {"name": "bagna", "color": (139, 0, 0)},
    "&": {"name": "kult", "color": (139, 69, 19)},
    "S": {"name": "świątynia", "color": (255, 255, 255)},

    # --- PRZEJEZDNE (Mają 'cost') ---
    ".": {"name": "trawa", "color": (34, 139, 34), "cost": 4},
    "l": {"name": "las", "color": (0, 100, 0), "cost": 6},
    "p": {"name": "pustynia", "color": (210, 105, 30), "cost": 5},
    "P": {"name": "pustynia sucha", "color": (237, 201, 175), "cost": 5},
    "g": {"name": "góry niskie", "color": (119, 119, 119), "cost": 8},
    "_": {"name": "droga", "color": (185, 185, 185), "cost": 3},
    "$": {"name": "złoto", "color": (255, 215, 0), "cost": 4},
    "#": {"name": "zamek", "color": (34, 139, 34), "cost": 4},
}

