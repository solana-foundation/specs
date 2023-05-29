import csv
from pathlib import Path
import struct
from ..core.chacha20rng import ChaCha20Rng
from ..core.weighted_index import WeightedIndex


class LeaderSchedule:
    def __init__(self, schedule, slots_per_rotation):
        self.schedule = schedule
        self.slots_per_rotation = slots_per_rotation

    @staticmethod
    def derive(epoch, stake_weights, rotations, slots_per_rotation) -> "LeaderSchedule":
        stake_weights = stake_weights.copy()
        # TODO sort by (stake, b58decode(leader_pubkey_str)))
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
    # Read list of epoch stakes
    epoch_stakes_path = (
        Path(__file__).parents[1] / "fixtures" / "epoch-stakes-mainnet-454.csv"
    )
    with open(epoch_stakes_path) as f:
        rows = csv.reader(f)
        next(rows)  # skip header
        weights = list(map(lambda row: (row[0], int(row[1])), rows))

    schedule = LeaderSchedule.derive(
        epoch=454,
        stake_weights=weights,
        rotations=108000,
        slots_per_rotation=4,
    )
    for leader in schedule:
        print(leader)
    # TODO check result against fixture


if __name__ == "__main__":
    test()
