from pathlib import Path

# wczytanie pliku FAC
text = Path("0.FAC").read_text(encoding="latin-1")

print("=== POCZĄTEK PLIKU FAC ===\n")

for line in text.splitlines()[:200]:
    print(line)
