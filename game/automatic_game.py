import random

from game.game import *


class AutomaticGame(Game):

    @staticmethod
    def throw_n_dice(n: int) -> Dice:
        l: list[DiceFace] = []
        for _ in range(n):
            l.append(random.choice(list(DiceFace)))
        return Dice.from_list_of_faces(l)

    def __init__(self):
        super().__init__(random.choice(list(Card)), AutomaticGame.throw_n_dice(8))

    def act(self, dice: Dice, card: Card):
        super().act(dice, card)
        super().throw(AutomaticGame.throw_n_dice(8 - self.dice.sum()))
