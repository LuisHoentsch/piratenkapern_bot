from definitions.definitions import *
from definitions.state import State
from game.game import Game


class Mainstate(State):

    def __init__(self, dice: Dice, card: Card):
        super().__init__(dice, card)
        assert self.dice.sum() == 8

        self.children: set[State] = set()  # TODO: why cant I use Interstate? Circular import?
        self.value: float = self.fold_value()

        self.instance: int = State.index
        State.index += 1

    def ideal_move(self) -> Dice:
        ideal_next_states: list[State] = list(filter(lambda x: x.value == self.value, self.children))
        if len(ideal_next_states) == 0:
            return Dice(0, 0, 0, 0, 0, 0)
        else:
            return Dice.dice_difference(self.dice, ideal_next_states[0].dice)

    def fold_value(self) -> int:
        return Game.get_score(self.dice, self.card, False)

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
