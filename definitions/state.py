from definitions.definitions import *


class State:
    updated: bool = True

    def __init__(self, dice: Dice, card: Card):
        self.dice: Dice = dice
        self.card: Card = card
        self.value: float = 0
        self.children: set[State] | dict[State] = set()
        self.instance: int = -1

    def update_value(self):
        raise NotImplementedError

    def toJSON(self):
        raise NotImplementedError
