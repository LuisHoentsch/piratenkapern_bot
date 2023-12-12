from definitions.definitions import *
from definitions.state import State
from definitions.mainstate import Mainstate


class Interstate(State):

    def __init__(self, dice: Dice, card: Card):
        super().__init__(dice, card)
        assert self.dice.sum() in [5, 6]

        self.children: dict[Mainstate, int] = {}
        self.value: float = -1000

        self.instance: int = State.index
        State.index += 1

    def update_value(self):
        children: list[Mainstate] = list(filter(lambda child: self not in child.children or child.value > self.value,
                                                self.children.keys()))
        m: float = mean([child.value for child in children for _ in range(self.children[child])])

        assert int(m) >= int(self.value) - 1  # m >= self.value
        if m > self.value:
            self.value = m
            State.updated = True

    def toJSON(self):
        return {
            "instance": self.instance,  # int
            "dice": self.dice.toJSON(),  # dict[int, int]
            "card": self.card.value,  # int
            "value": self.value,  # float
            "children": {child.instance: self.children[child] for child in self.children.keys()}  # dict[int, int]
        }

    @staticmethod
    def fromJSON(json: dict) -> "Interstate":
        dice: Dice = Dice(0, 0, 0, 0, 0, 0)
        for k, v in json["dice"].items():
            dice.counts[DiceFace(int(k))] = v
        card: Card = Card(json["card"])
        interstate: Interstate = Interstate(dice, card)
        interstate.value = json["value"]
        interstate.instance = json["instance"]
        return interstate
