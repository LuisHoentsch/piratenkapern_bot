from enum import Enum
from numbers import Number

REWARDS_TABLE = [0, 0, 0, 100, 200, 500, 1000, 2000, 4000, 8000]


class DiceFace(Enum):
    GOLD = 1
    DIAMOND = 2
    SKULL = 3
    MONKEY = 4
    PARROT = 5
    SWORD = 6


class Card(Enum):
    GOLD = 1
    DIAMOND = 2
    SKULL = 3
    TWO_SKULLS = 4
    DOUBLE = 5
#    SAVE = 6
    MONKEYS_PARROTS = 7
    TWO_SWORDS = 8
    THREE_SWORDS = 9
    FOUR_SWORDS = 10
    REROLL_SKULL = 11
    NONE = 12


class Dice:
    def __init__(self, gold: int, diamond: int, skull: int, monkey: int, parrot: int, sword: int):
        self.counts: dict[DiceFace, int] = {DiceFace.GOLD: gold, DiceFace.DIAMOND: diamond, DiceFace.SKULL: skull,
                                            DiceFace.MONKEY: monkey, DiceFace.PARROT: parrot, DiceFace.SWORD: sword}

    def sum(self) -> int:
        return sum(self.counts.values())

    def abs_sum(self) -> int:
        return sum([abs(self.counts[k]) for k in self.counts.keys()])

    def negative_values(self) -> bool:
        return any([self.counts[face] < 0 for face in DiceFace])

    def toJSON(self) -> dict[int, int]:
        return {
            k.value: v for k, v in self.counts.items()
        }


def mean(l: list[Number]) -> float:
    return sum(l) / len(l)
