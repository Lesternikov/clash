import time

class CombatLog:
    def __init__(self):
        self.entries = []

    def add(self, text):
        print(text)
        self.entries.append(text)

    def show_last(self, n=5):
        for e in self.entries[-n:]:
            print(e)

def attack_animation(attacker, target):
    print(f"{attacker.type} >>> {target.type}")
    time.sleep(0.15)

    print("  *")
    time.sleep(0.15)

    print("  **")
    time.sleep(0.15)

    print("  HIT!")
    time.sleep(0.1)