from PIL import Image
from collections import Counter

# Wczytujemy Twoją minimapę
img = Image.open("!Karkhan.png").convert("RGB")

# Bezpieczne pobieranie pikseli
piksele = list(img.getdata())
colors = Counter(piksele)

# Zapisujemy wynik do pliku tekstowego
with open("kolory.txt", "w", encoding="utf-8") as f:
    f.write("Najpopularniejsze kolory na mapie !Karkhan.png:\n")
    f.write("-" * 60 + "\n")
    
    # Wyciągamy 30 najczęstszych kolorów
    for color, count in colors.most_common(30):
        r, g, b = color
        
        if g > r and g > b:
            typ = "Zieleń (Trawa lub Las)"
        elif b > r and b > g:
            typ = "Niebieski (Woda)"
        elif r > g and r > b:
            typ = "Czerwony/Brązowy (Pustynia/Bagno)"
        elif r == g == b:
            typ = "Szary/Czarny (Góry/Drogi)"
        else:
            typ = "Inny"
            
        linia = f"RGB: {str(color): <15} | Wystąpień: {count: <6} | Prawdopodobnie: {typ}\n"
        f.write(linia)
        print(linia.strip())

print("\nSukces! Pełna lista została zapisana do pliku kolory.txt")