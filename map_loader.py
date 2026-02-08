def load_map(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    grid = [list(line) for line in lines]
    return grid


def load_fac_objects(path):
    objects = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line.startswith("("):
                continue

            parts = line.strip("()").split()

            # ignorujemy wpisy typu:
            # (zamek w budowie 0)
            if len(parts) < 3:
                continue

            name = parts[0]

            try:
                x = int(parts[1])
                y = int(parts[2])
            except ValueError:
                continue

            objects.setdefault(name, []).append((x, y))

    return objects

