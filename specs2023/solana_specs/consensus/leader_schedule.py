import csv
from pathlib import Path
import struct
from ..core.base58 import b58encode, b58decode
from ..core.chacha20rng import ChaCha20Rng
from ..core.weighted_index import WeightedIndex


class LeaderSchedule:
    def __init__(self, schedule, slots_per_rotation):
        self.schedule = schedule
        self.slots_per_rotation = slots_per_rotation

    @staticmethod
    def derive(epoch, stake_weights, rotations, slots_per_rotation) -> "LeaderSchedule":
        stake_weights = stake_weights.copy()
        stake_weights.sort(key=lambda x: (x[1], x[0]), reverse=True)
        weighted_index = WeightedIndex(map(lambda x: x[1], stake_weights))

        rng = ChaCha20Rng(struct.pack("<Q", epoch) + b"\x00" * 24)
        schedule = []
        for _ in range(rotations):
            schedule.append(stake_weights[weighted_index.sample(rng)][0])

        return LeaderSchedule(schedule, slots_per_rotation)

    def lookup(self, slot):
        if slot >= len(self.schedule) * self.slots_per_rotation:
            return None
        return self.schedule[slot // self.slots_per_rotation]

    def __iter__(self):
        return map(
            lambda x: self.lookup(x),
            range(len(self.schedule) * self.slots_per_rotation),
        )


def test():
    fixtures = Path(__file__).parents[1] / "fixtures"
    epoch_stakes_path = fixtures / "epoch-stakes-mainnet-454.csv"
    leader_schedule_path = fixtures / "leader-schedule-454.txt"

    # Read list of epoch stakes
    with open(epoch_stakes_path) as f:
        rows = csv.reader(f)
        next(rows)  # skip header
        weights = list(map(lambda row: (b58decode(row[0]), int(row[1])), rows))

    schedule = LeaderSchedule.derive(
        epoch=454,
        stake_weights=weights,
        rotations=108000,
        slots_per_rotation=4,
    )
    # Read expected leader schedule
    with open(leader_schedule_path) as f:
        expected_schedule = map(lambda s: b58decode(s.strip()), iter(f))
        for i, tuple in enumerate(zip(schedule, expected_schedule)):
            got, expected = tuple
            assert got == expected, f"at {i} got: {got}, expected: {expected}"


if __name__ == "__main__":
    test()
