from typing import List

from src.stored_procedures.sp_select import get_liquid_inventory


def find_index_by_potion_type(list, target_potion_type):
    for index, item in enumerate(list):
        if item.potion_type == target_potion_type:
            return index
    return -1

def convert_potion_to_liquid(potion_type: list[int]):
    return [x // x for x in potion_type]

def find_available_liquid(liquid_inventory) -> List[int]:
    liquid_available = [0,0,0,0]
    for liquid in liquid_inventory:
        liquid_available = [liquid_available[i] + (liquid.potion_type[i] * liquid.quantity) for i in range(len(liquid.potion_type))]

    return liquid_available