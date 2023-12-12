import pandas as pd

from definitions.definitions import Card, DiceFace, Dice
import json
from game.automatic_game import AutomaticGame

df = pd.read_csv('outputs/ideal_moves.csv', index_col=0)
df["card"] = df["card"].apply(lambda x: Card(x))
df["ideal_move"] = df["ideal_move"].apply(lambda x: json.loads(x))


def get_move(dice: Dice, card: Card, pirate_island: bool) -> tuple[Dice, Card]:
    if pirate_island:
        d: Dice = dice.copy()
        d.counts[DiceFace.SKULL] = 0
        return d, card
    ideal_move: pd.Series = df[(df["dice_gold"] == dice.counts[DiceFace.GOLD]) &
                               (df["dice_diamond"] == dice.counts[DiceFace.DIAMOND]) &
                               (df["dice_monkey"] == dice.counts[DiceFace.MONKEY]) &
                               (df["dice_parrot"] == dice.counts[DiceFace.PARROT]) &
                               (df["dice_sword"] == dice.counts[DiceFace.SWORD]) &
                               (df["dice_skull"] == dice.counts[DiceFace.SKULL]) &
                               (df["card"] == card)]["ideal_move"]
    assert ideal_move.shape[0] == 1
    d: dict[str, int] = ideal_move.iloc[0]
    c: Card = Card.NONE if d["SKULL"] == 1 else card
    return Dice(d["GOLD"], d["DIAMOND"], d["SKULL"], d["MONKEY"], d["PARROT"], d["SWORD"]), c


total_score: int = 0
game: AutomaticGame = AutomaticGame()
n_rounds: int = 1000

for _ in range(n_rounds):
    game = AutomaticGame()
    dice, card, game_over, pirate_island = game.get_state()
    while not game.game_over:
        move: tuple[Dice, Card] = get_move(dice, card, pirate_island)
        print(f"\nYour card is {card.name}")
        input("Your dice (ideal reroll):\n" + "\n".join(
            [f"{key.name}: {dice.counts[key]} ({move[0].counts[key]})" for key in dice.counts.keys()]))
        game.act(*move)
        dice, card, game_over, pirate_island = game.get_state()

    if AutomaticGame.get_score(dice, card, pirate_island) <= 0:
        print(f"\n\n\nYour card is {card.name}")
        print("Your dice:\n" + "\n".join(
            [f"{key.name}: {dice.counts[key]}" for key in dice.counts.keys()]))
    print(f"\nYour final score is {AutomaticGame.get_score(dice, card, pirate_island)}")
    total_score += AutomaticGame.get_score(dice, card, pirate_island)

print(f"\nYour average score is {total_score / n_rounds} (total score: {total_score})")
