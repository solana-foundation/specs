from collections import deque
import pandas as pd


class TowerEntry:
    def __init__(self, slot, lockout, expired):
        self.slot = slot
        self.lockout = lockout
        self.expired = expired

    def __repr__(self) -> str:
        return f"{self.slot} {self.lockout}"


class Tower:
    def __init__(self) -> None:
        self.root = None
        self.stack = deque()

    def update(self, slot):
        # On Tower update, remove all expired entries
        n = len(self.stack)
        expired_slots = []
        for i, entry in enumerate(self.stack):
            expiration_slot = entry.slot + 2**entry.lockout
            if slot > expiration_slot:
                entry.expired = True  # Mark the entry to be removed
                expired_slots.append(i)

        # Remove all expired towers
        for i in expired_slots:
            curr_lockout = self.stack[i].lockout
            for j in range(i + 1, n):
                lockout = self.stack[j].lockout
                if curr_lockout - lockout == 1:
                    self.stack[j].expired = True
                curr_lockout = lockout
        self.stack = deque([entry for entry in self.stack if not entry.expired])

        # Add the new slot to the tower
        n = len(self.stack)
        self.stack.append(TowerEntry(slot, 1, False))
        # Double the lockout period of the longest contiguous sequence
        for i in range(n, 0, -1):
            curr_exp = self.stack[i].lockout
            prev_exp = self.stack[i - 1].lockout
            expiration_slot = self.stack[i - 1].slot + 2 ** self.stack[i - 1].lockout
            if curr_exp == prev_exp and slot < expiration_slot:
                self.stack[i - 1].lockout += 1
            else:
                break

        if len(self.stack) == 32:
            entry = self.stack.popleft()
            self.root = entry.slot

    def print(self):
        df = pd.DataFrame(
            [
                (e.slot, e.lockout, 2**e.lockout, e.slot + (2**e.lockout))
                for e in self.stack
            ],
            columns=["slot", "level", "lockout", "expiration_slot"],
        ).sort_index(ascending=False)
        print(df.to_string(index=False))


if __name__ == "__main__":
    t = Tower()
    t.update(1)
    t.update(2)
    t.update(3)
    t.update(4)
    t.print()
    """
    ╔══════╤═══════╤═════════╤═════════════════╗
    ║ slot │ level │ lockout │ expiration_slot ║
    ╠══════╪═══════╪═════════╪═════════════════╣
    ║ 4    │ 1     │ 2       │ 6               ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 3    │ 2     │ 4       │ 7               ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 2    │ 3     │ 8       │ 10              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 1    │ 4     │ 16      │ 17              ║
    ╚══════╧═══════╧═════════╧═════════════════╝
    """

    t.update(9)
    t.print()
    """
    ╔══════╤═══════╤═════════╤═════════════════╗
    ║ slot │ level │ lockout │ expiration_slot ║
    ╠══════╪═══════╪═════════╪═════════════════╣
    ║ 9    │ 1     │ 2       │ 11              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 2    │ 3     │ 8       │ 10              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 1    │ 4     │ 16      │ 17              ║
    ╚══════╧═══════╧═════════╧═════════════════╝
    """

    t.update(10)
    t.print()
    """
    ╔══════╤═══════╤═════════╤═════════════════╗
    ║ slot │ level │ lockout │ expiration_slot ║
    ╠══════╪═══════╪═════════╪═════════════════╣
    ║ 10   │ 1     │ 2       │ 12              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 9    │ 2     │ 4       │ 13              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 2    │ 3     │ 8       │ 10              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 1    │ 4     │ 16      │ 17              ║
    ╚══════╧═══════╧═════════╧═════════════════╝
    """

    t.update(11)
    t.print()
    """
    ╔══════╤═══════╤═════════╤═════════════════╗
    ║ slot │ level │ lockout │ expiration_slot ║
    ╠══════╪═══════╪═════════╪═════════════════╣
    ║ 11   │ 1     │ 2       │ 13              ║
    ╟──────┼───────┼─────────┼─────────────────╢
    ║ 1    │ 4     │ 16      │ 17              ║
    ╚══════╧═══════╧═════════╧═════════════════╝
    """
