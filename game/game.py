from definitions.definitions import *


class Game:
    
    def __init__(self, card: Card, dice: Dice):
        self.card: Card = card
        assert dice.sum() == 8
        
        self.game_over: bool = False
        self.new_skull: bool = False
        self.pirate_island = False
        self.last_throw: Dice | None = None
        self.dice: Dice = Dice(0, 0, 0, 0, 0, 0)

        self.throw(dice)
        
    def act(self, reroll: Dice, card: Card):
        if self.game_over:
            raise Exception("Game is already over")
        if reroll.counts[DiceFace.SKULL] > 1 or reroll.counts[DiceFace.SKULL] == 1 and not (self.card == Card.REROLL_SKULL and card == Card.NONE):
            raise Exception("Cannot reroll skulls")
        if reroll.sum() not in [0, 2, 3, 4, 5, 6, 7, 8]:
            raise Exception("Invalid number of dice rerolled")
        if reroll.sum() == 0:
            self.game_over = True
            return
        self.card = card
        self.dice = Dice.dice_difference(self.dice, reroll)

    def throw(self, rolled_dice: Dice):
        if self.game_over:
            return
        self.dice = Dice.dice_sum(self.dice, rolled_dice)
        assert self.dice.sum() == 8
        self.last_throw = rolled_dice
        self.update_game_over()

    def update_game_over(self):
        skulls = self.dice.counts[DiceFace.SKULL]
        if self.card == Card.SKULL:
            skulls += 1
        if self.card == Card.TWO_SKULLS:
            skulls += 2

        if self.pirate_island and self.new_skull:
            self.game_over = True
            return
        if skulls > 3:
            self.game_over = True
            return
        if skulls == 3 and self.card != Card.REROLL_SKULL:
            self.game_over = True
            return

    def get_state(self) -> tuple[Dice, Card, bool, bool]:
        return self.dice, self.card, self.game_over, self.pirate_island

    @staticmethod
    def get_score(dice: Dice, card: Card, pirate_island: bool) -> int:
        reward: int = 0
        bonus: bool = True

        counts: dict[DiceFace, int] = dice.counts.copy()

        if card == Card.GOLD:
            counts[DiceFace.GOLD] += 1
        elif card == Card.DIAMOND:
            counts[DiceFace.DIAMOND] += 1
        elif card == Card.MONKEYS_PARROTS:
            counts[DiceFace.MONKEY] += counts[DiceFace.PARROT]
            counts[DiceFace.PARROT] = 0
        elif card == Card.SKULL:
            counts[DiceFace.SKULL] += 1
        elif card == Card.TWO_SKULLS:
            counts[DiceFace.SKULL] += 2

        if pirate_island:
            return 100 * counts[DiceFace.SKULL]

        if counts[DiceFace.SKULL] >= 3:
            # if self.card == Card.SAVE:
            #     raise NotImplementedError
            for k in counts.keys():
                counts[k] = 0
                bonus = False

        if card == Card.TWO_SWORDS:
            if counts[DiceFace.SWORD] >= 2:
                reward += 300
            else:
                return -300
        elif card == Card.THREE_SWORDS:
            if counts[DiceFace.SWORD] >= 3:
                reward += 500
            else:
                return -500
        elif card == Card.FOUR_SWORDS:
            if counts[DiceFace.SWORD] >= 4:
                reward += 1000
            else:
                return -1000

        reward += (counts[DiceFace.GOLD] + counts[DiceFace.DIAMOND]) * 100

        for key in counts.keys():
            if key in [DiceFace.PARROT, DiceFace.SWORD, DiceFace.MONKEY] and counts[key] in [1, 2]:
                bonus = False
            elif key == DiceFace.SKULL:
                continue
            else:
                reward += REWARDS_TABLE[counts[key]]
        if dice.counts[DiceFace.SKULL] > 0:
            bonus = False

        return ((card == Card.DOUBLE) + 1) * (reward + bonus * 500)
