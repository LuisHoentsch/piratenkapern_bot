from definitions import *
from state import State


class Mainstate(State):
    index: int = 0

    def __init__(self, dice: Dice, card: Card):
        super().__init__(dice, card)
        assert self.dice.sum() == 8

        self.children: set[State] = set()  # why cant I use Interstate? Circular import?
        self.value: float = self.fold_value()

        self.instance: int = Mainstate.index
        Mainstate.index += 1

    def ideal_move(self) -> Dice:
        ideal_next_states: list[State] = list(filter(lambda x: x.value == self.value, self.children))
        if len(ideal_next_states) == 0:
            return Dice(0, 0, 0, 0, 0, 0)
        else:
            return Dice.dice_difference(self.dice, ideal_next_states[0].dice)

    def fold_value(self) -> int:
        skulls: int = self.dice.counts[DiceFace.SKULL]

        if self.card == Card.REROLL_SKULL:
            skulls -= 1
        elif self.card == Card.TWO_SKULLS:
            skulls += 2
        elif self.card == Card.SKULL:
            skulls += 1

        reward: int = 0
        bonus: bool = True

        counts: dict[DiceFace, int] = self.dice.counts.copy()

        if self.card == Card.GOLD:
            counts[DiceFace.GOLD] += 1
        elif self.card == Card.DIAMOND:
            counts[DiceFace.DIAMOND] += 1
        elif self.card == Card.MONKEYS_PARROTS:
            counts[DiceFace.MONKEY] += counts[DiceFace.PARROT]
            counts[DiceFace.PARROT] = 0

        if skulls >= 3:
            # if self.card == Card.SAVE:
            #     raise NotImplementedError
            for k in counts.keys():
                counts[k] = 0
                bonus = False

        if self.card == Card.TWO_SWORDS:
            if counts[DiceFace.SWORD] >= 2:
                reward += 300
            else:
                return -300
        elif self.card == Card.THREE_SWORDS:
            if counts[DiceFace.SWORD] >= 3:
                reward += 500
            else:
                return -500
        elif self.card == Card.FOUR_SWORDS:
            if counts[DiceFace.SWORD] >= 4:
                reward += 1000
            else:
                return -1000

        reward += (counts[DiceFace.GOLD] + counts[DiceFace.DIAMOND]) * 100

        for key in counts.keys():
            if key == DiceFace.SKULL or (key in [DiceFace.PARROT, DiceFace.SWORD, DiceFace.MONKEY] and counts[key] < 3):
                bonus = False
            else:
                reward += REWARDS_TABLE[counts[key]]

        return ((self.card == Card.DOUBLE) + 1) * (reward + bonus * 500)

    def update_value(self):
        if len(self.children) > 0:
            m = max([child.value for child in self.children])
            if m > self.value:
                self.value = m
                State.updated = True

    def toJSON(self) -> dict:
        return {
            "instance": self.instance,  # int
            "dice": self.dice.toJSON(),  # dict[int, int]
            "card": self.card.value,  # int
            "value": self.value,  # float
            "children": [child.instance for child in self.children]  # list of ints
        }

    @staticmethod
    def fromJSON(json: dict) -> "Mainstate":
        dice: Dice = Dice(0, 0, 0, 0, 0, 0)
        for k, v in json["dice"].items():
            dice.counts[DiceFace(int(k))] = v
        card: Card = Card(json["card"])
        mainstate: Mainstate = Mainstate(dice, card)
        mainstate.value = json["value"]
        mainstate.instance = json["instance"]
        return mainstate
