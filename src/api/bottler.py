from fastapi import APIRouter, Depends
from src.api import auth
from src.api.inventory import get_liquid_inventory, get_potion_inventory
from src.classes import PotionPlan
from src.functions import find_available_liquid, find_index_by_potion_type, convert_potion_to_liquid
from src.stored_procedures.sp_select import get_audit, get_store_info
from src.stored_procedures.sp_update import update_liquid_inventory, update_potion_inventory

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionPlan], order_id: int):
    liquid_type_map = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
    liquid_used = [0,0,0,0]

    for potion in potions_delivered:
        liquid_used = [liquid_used[i] + (potion.potion_type[i] * potion.quantity) for i in range(len(potion.potion_type))]
        print(f"/bottle/deliver | Potion Type: {potion.potion_type} | Potion Quantity: {potion.quantity}")
        update_potion_inventory(potion.quantity, potion.potion_type)

    for i, type in enumerate(liquid_type_map):
        print(f"/bottle/deliver | Liquid Used: {liquid_used}")
        print(f"/bottle/deliver | Liquid Used at Index: {-liquid_used[i]} | Type: {type}")
        update_liquid_inventory(-liquid_used[i], type)

    print(f"/bottler/deliver/order_id | potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    potion_inventory = get_potion_inventory()
    liquid_available = find_available_liquid()
    store_info = get_store_info()

    potion_limit = store_info.potion_capacity * 50
    max_to_make = potion_limit // 5

    potions_to_make = []
    total_potion_inventory = store_info.number_of_potions

    for potion in potion_inventory:
        if potion.quantity < max_to_make: 
            max_possible_for_this_potion = max_to_make - potion.quantity
            num_to_make = min(max_to_make, max_possible_for_this_potion)

            for i, liquid_needed in enumerate(potion.potion_type):
                if liquid_needed > 0:
                    can_make = liquid_available[i] // liquid_needed
                    num_to_make = min(num_to_make, can_make)

            if total_potion_inventory + num_to_make > potion_limit:
                num_to_make = potion_limit // 5 - total_potion_inventory

            if num_to_make > 0:
                for i, liquid_needed in enumerate(potion.potion_type):
                    liquid_available[i] -= liquid_needed * num_to_make

                potions_to_make.append({
                    "potion_type": potion.potion_type,
                    "quantity": num_to_make
                })

                total_potion_inventory += num_to_make

    print(potions_to_make)
    return potions_to_make

if __name__ == "__main__":
    print(get_bottle_plan())