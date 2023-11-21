import json
import math
import pandas as pd

from tqdm import tqdm

from definitions.mainstate import *
from definitions.interstate import Interstate


def distribute_balls(total_balls, total_cups) -> list[tuple[int, int, int, int, int, int]]:
    def distribute_recursive(remaining_balls, remaining_cups, current_distribution) -> None:
        if remaining_cups == 0:
            if remaining_balls == 0:
                distributions.append(tuple(current_distribution))
            return

        for balls_in_cup in range(min(remaining_balls, total_balls) + 1):
            distribute_recursive(
                remaining_balls - balls_in_cup,
                remaining_cups - 1,
                current_distribution + [balls_in_cup]
            )

    distributions = []
    distribute_recursive(total_balls, total_cups, [])
    return distributions


def generate_combinations(n: int) -> list[Dice]:
    p = distribute_balls(n, 6)
    return [Dice(*x) for x in p]


def generate_mainstates() -> list[Mainstate]:
    combinations: list[Dice] = generate_combinations(8)
    return [Mainstate(dice, card) for dice in combinations for card in Card]


def generate_interstates() -> list[Interstate]:
    combinations: list[Dice] = generate_combinations(6) + generate_combinations(5)
    return [Interstate(dice, card) for dice in combinations for card in Card]


def add_children_for_mainstate(mainstate: Mainstate, interstates: list[Interstate]):
    for interstate in interstates:
        difference: Dice = Dice.dice_difference(mainstate.dice, interstate.dice)
        if difference.abs_sum() not in [2, 3] or difference.negative_values():
            continue
        if difference.counts[DiceFace.SKULL] > 1:
            continue
        if difference.counts[DiceFace.SKULL] == 1 and not (mainstate.card == Card.REROLL_SKULL and interstate.card == Card.NONE):
            continue
        if mainstate.card != interstate.card and (mainstate.card != Card.REROLL_SKULL or interstate.card != Card.NONE):
            continue
        mainstate.children.add(interstate)


def number_of_possible_paths(difference: Dice) -> int:
    l = difference.counts.values()
    n = sum(l)
    r = 1
    for k in l:
        r *= math.comb(n, k)
        n -= k
    return r


def add_children_for_interstate(interstate: Interstate, mainstates: list[Mainstate]):
    for mainstate in mainstates:
        difference: Dice = Dice.dice_difference(mainstate.dice, interstate.dice)
        if difference.abs_sum() not in [2, 3] or difference.negative_values() or interstate.card != mainstate.card:
            continue
        assert mainstate not in interstate.children
        interstate.children[mainstate] = number_of_possible_paths(difference)


def save_nodes(prefix: str, mainstates: list[Mainstate], interstates: list[Interstate]):
    with open(prefix + "mainstates.json", "w") as f:
        f.write(json.dumps([state.toJSON() for state in mainstates]))
    with open(prefix + "interstates.json", "w") as f:
        f.write(json.dumps([state.toJSON() for state in interstates]))


def load_nodes(prefix: str) -> tuple[list[Mainstate], list[Interstate]]:
    with open(prefix + "mainstates.json", "r") as f:
        mainstates_json = json.loads(f.read())
    with open(prefix + "interstates.json", "r") as f:
        interstates_json = json.loads(f.read())
    mainstates: dict[int, Mainstate] = {x["instance"]: Mainstate.fromJSON(x) for x in mainstates_json}  # TODO: list instead?
    interstates: dict[int, Interstate] = {x["instance"]: Interstate.fromJSON(x) for x in interstates_json}
    for i in range(len(mainstates)):
        mainstates[i].children = [interstates[j] for j in mainstates_json[i]["children"]]
    for i in range(len(interstates)):
        interstates[i].children = {mainstates[int(k)]: v for k, v in interstates_json[i]["children"].items()}
    return list(mainstates.values()), list(interstates.values())


def to_move_df(mainstates: list[Mainstate]) -> pd.DataFrame:
    rows_list = []
    for mainstate in mainstates:
        rows_list.append({
            "dice_gold": mainstate.dice.counts[DiceFace.GOLD],
            "dice_diamond": mainstate.dice.counts[DiceFace.DIAMOND],
            "dice_skull": mainstate.dice.counts[DiceFace.SKULL],
            "dice_monkey": mainstate.dice.counts[DiceFace.MONKEY],
            "dice_parrot": mainstate.dice.counts[DiceFace.PARROT],
            "dice_sword": mainstate.dice.counts[DiceFace.SWORD],
            "card": mainstate.card.value,
            "value": mainstate.value,
            "ideal_move": json.dumps({k.name: v for k, v in mainstate.ideal_move().counts.items()})
        })
    return pd.DataFrame(rows_list)


if __name__ == '__main__':
    generate: bool = True
    if generate:
        print("Generating mainstates")
        mainstates = generate_mainstates()
        print("Generating interstates")
        interstates = generate_interstates()

        print("Adding children for mainstates")
        for mainstate in tqdm(mainstates):
            add_children_for_mainstate(mainstate, interstates)

        print("Adding children for interstates")
        for interstate in tqdm(interstates):
            add_children_for_interstate(interstate, mainstates)

        print("Saving to files")
        save_nodes("outputs/nodes_", mainstates, interstates)
    else:
        print("Loading nodes")
        mainstates, interstates = load_nodes("outputs/nodes_")

    print("Starting optimization loop")
    while State.updated:
        print("\tUpdating values...")
        State.updated = False
        for interstate in interstates:
            interstate.update_value()
        for mainstate in mainstates:
            mainstate.update_value()

    print("Saving to files")
    save_nodes("outputs/nodes_", mainstates, interstates)

    df_ideal_moves = to_move_df(mainstates)
    df_ideal_moves.to_csv("outputs/ideal_moves.csv")
