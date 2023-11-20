import itertools
import json
import math

from tqdm import tqdm

from mainstate import *
from interstate import Interstate


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


def dice_difference(dice1: Dice, dice2: Dice) -> Dice:
    return Dice(dice1.counts[DiceFace.GOLD] - dice2.counts[DiceFace.GOLD],
                dice1.counts[DiceFace.DIAMOND] - dice2.counts[DiceFace.DIAMOND],
                dice1.counts[DiceFace.SKULL] - dice2.counts[DiceFace.SKULL],
                dice1.counts[DiceFace.MONKEY] - dice2.counts[DiceFace.MONKEY],
                dice1.counts[DiceFace.PARROT] - dice2.counts[DiceFace.PARROT],
                dice1.counts[DiceFace.SWORD] - dice2.counts[DiceFace.SWORD])


def add_children_for_mainstate(mainstate: Mainstate, interstates: list[Interstate]):
    for interstate in interstates:
        difference: Dice = dice_difference(mainstate.dice, interstate.dice)
        if difference.abs_sum() not in [2, 3] or difference.negative_values():
            continue
        if difference.counts[DiceFace.SKULL] != 0 and (difference.counts[DiceFace.SKULL] != 1
                                                       or mainstate.card != Card.REROLL_SKULL
                                                       or interstate.card != Card.NONE):
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
        difference: Dice = dice_difference(mainstate.dice, interstate.dice)
        if difference.abs_sum() not in [2, 3] or difference.negative_values() or interstate.card != mainstate.card:
            continue
        assert mainstate not in interstate.children
        interstate.children[mainstate] = number_of_possible_paths(difference)


# def add_childern(mainstates: list[Mainstate], interstates: list[Interstate]):
#     for mainstate, interstate in tqdm(itertools.product(mainstates, interstates)):
#         difference: Dice = dice_difference(mainstate.dice, interstate.dice)
#         if difference.abs_sum() not in [2, 3] or difference.negative_values():
#             continue
#
#         if difference.counts[DiceFace.SKULL] == 0 or (difference.counts[DiceFace.SKULL] == 1
#                                                       and mainstate.card == Card.REROLL_SKULL
#                                                       and interstate.card == Card.NONE):
#             mainstate.children.add(interstate)
#
#         if interstate.card == mainstate.card:
#             assert mainstate not in interstate.children
#             interstate.children[mainstate] = number_of_possible_paths(difference)


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
    mainstates = [Mainstate.fromJSON(x) for x in mainstates_json]
    interstates = [Interstate.fromJSON(x) for x in interstates_json]
    for i in range(len(mainstates)):
        mainstates[i].children = [interstates[j] for j in mainstates_json[i]["children"]]
    for i in range(len(interstates)):
        interstates[i].children = {mainstates[k]: v for k, v in interstates_json[i]["children"].items()}
    return mainstates, interstates


# print("Generating mainstates")
# mainstates = generate_mainstates()
# print("Generating interstates")
# interstates = generate_interstates()
#
# print("Adding children for mainstates")
# for mainstate in tqdm(mainstates):
#     add_children_for_mainstate(mainstate, interstates)
#
# print("Adding children for interstates")
# for interstate in tqdm(interstates):
#     add_children_for_interstate(interstate, mainstates)
#
# print("Saving to files")
# save_nodes("initialized_nodes_", mainstates, interstates)

print("Loading nodes")
mainstates, interstates = load_nodes("initialized_nodes_")

print("Starting optimization loop")
while State.updated:
    print("\tUpdating values...")
    State.updated = False
    for interstate in interstates:
        interstate.update_value()
    for mainstate in mainstates:
        mainstate.update_value()

print("Saving to files")
save_nodes("optimized_nodes", mainstates, interstates)
