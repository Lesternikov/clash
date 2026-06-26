import re
#przeróbka brzydkich grafik
def generuj_palete_z_plikow(plik_zrodla, plik_celu, plik_wynikowy):
    wzorzec_koloru = r"\(\s*\d+,\s*\d+,\s*\d+,\s*\d+\s*\)"
    paleta = {}
    konflikty = 0

    print("=" * 50)
    print("MASZYNA DO ŁĄCZENIA RAPORTÓW")
    print("=" * 50)
    print(f"Czytam pliki: {plik_zrodla} oraz {plik_celu}...")

    try:
        # Otwieramy oba wielkie pliki naraz
        with open(plik_zrodla, 'r', encoding='utf-8') as f_zrodlo, \
             open(plik_celu, 'r', encoding='utf-8') as f_cel:
            
            # zip() czyta obie linie jednocześnie
            for linia_z, linia_c in zip(f_zrodlo, f_cel):
                
                # Ignorujemy nagłówki i puste linie (interesują nas tylko te z "Piksel")
                if "Piksel" not in linia_z:
                    continue
                
                match_z = re.search(wzorzec_koloru, linia_z)
                match_c = re.search(wzorzec_koloru, linia_c)
                
                if match_z and match_c:
                    kolor_zrodlowy = match_z.group(0)
                    kolor_docelowy = match_c.group(0)
                    
                    # MAGIA: Jeśli tego koloru źródłowego jeszcze nie mamy w słowniku, to go dodajemy.
                    # Jeśli już jest (bo to powtarzający się piksel tła), po prostu go ignorujemy!
                    if kolor_zrodlowy not in paleta:
                        paleta[kolor_zrodlowy] = kolor_docelowy
                    else:
                        # Opcjonalnie: sprawdzamy, czy stary kolor nie ma nagle nowej przypisanej wartości
                        if paleta[kolor_zrodlowy] != kolor_docelowy:
                            konflikty += 1

    except FileNotFoundError:
        print("BŁĄD: Nie znalazłem plików tekstowych! Upewnij się, że nazwałeś je ZRODLO.txt i CEL.txt")
        return

    print(f"Zakończono czytanie. Znaleziono {len(paleta)} unikalnych kolorów!")
    if konflikty > 0:
        print(f"UWAGA: Wykryto {konflikty} konfliktów (ten sam stary kolor próbował zmienić się w dwa różne nowe).")
        print("Skrypt zachował pierwsze dopasowanie.")

    # Zapisujemy gotowy kod słownika do nowego pliku
    with open(plik_wynikowy, 'w', encoding='utf-8') as f_wynik:
        for zrodlo, cel in paleta.items():
            f_wynik.write(f"{zrodlo}: {cel},\n")

    print("-" * 50)
    print(f"GOTOWE! Twoja gotowa do wklejenia paleta znajduje się w pliku: {plik_wynikowy}")
    print("-" * 50)

if __name__ == "__main__":
    # Nazwy plików, które łączymy
    PLIK_A = "ZRODLO.txt"
    PLIK_B = "CEL.txt"
    GOTOWA_PALETA = "GOTOWA_PALETA.txt"
    
    generuj_palete_z_plikow(PLIK_A, PLIK_B, GOTOWA_PALETA)