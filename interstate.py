from definitions import *
from state import State
from mainstate import Mainstate


class Interstate(State):
    index: int = 0

    def __init__(self, dice: Dice, card: Card):
        super().__init__(dice, card)
        assert self.dice.sum() in [5, 6]

        self.children: dict[Mainstate, int] = {}
        self.value: float = 0

        self.instance: int = Interstate.index
        Interstate.index += 1

    def update_value(self):
        children: list[Mainstate] = list(filter(self.no_loop or self.is_higher, self.children.keys()))
        self.value = mean([child.value for child in children for _ in range(self.children[child])])

    def no_loop(self, child: Mainstate) -> bool:
        return child not in self.children.keys()

    def is_higher(self, child: Mainstate) -> bool:
        return child.value > self.value

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
            dice.counts[DiceFace(k)] = v
        card: Card = Card(json["card"])
        interstate: Interstate = Interstate(dice, card)
        interstate.value = json["value"]
        interstate.instance = json["instance"]
        return interstate