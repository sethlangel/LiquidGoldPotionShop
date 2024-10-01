def find_index_by_potion_type(list, target_potion_type):
    for index, item in enumerate(list):
        if item.potion_type == target_potion_type:
            return index
    return -1

def convert_potion_to_liquid(potion_type: list[int]):
    return [x // 100 for x in potion_type]

def convert_liquid_to_potion(liquid_type: list[int]):
    return [x * 100 for x in liquid_type]