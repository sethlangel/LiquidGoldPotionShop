from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.api.inventory import get_liquid_inventory, get_potion_inventory
from src.functions import find_index_by_potion_type, convert_potion_to_liquid, convert_liquid_to_potion
from src.stored_procedures.sp_update import update_liquid_inventory, update_potion_inventory

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    potion_inventory = get_potion_inventory()
    liquid_inventory = get_liquid_inventory()

    for potion in potions_delivered:
        new_potion_quantity = potion_inventory[find_index_by_potion_type(liquid_inventory, potion.potion_type)].quantity + potion.quantity

        liquid_type = convert_potion_to_liquid(potion.potion_type)
        new_liquid_quantity = liquid_inventory[find_index_by_potion_type(liquid_inventory, liquid_type)].quantity - potion.quantity * 100

        update_liquid_inventory(new_liquid_quantity, liquid_type)
        update_potion_inventory(new_potion_quantity, potion.potion_type)

    print(f"/bottler/deliver/order_id | potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    liquid_inventory = get_liquid_inventory()
    potions_to_make = []

    for liquid in liquid_inventory:
        potion_type = convert_liquid_to_potion(liquid.potion_type)

        if liquid.quantity > 100:
            num_to_make = liquid.quantity // 100

            potions_to_make.append({"potion_type": potion_type, "quantity": num_to_make})

    print(f"/bottler/plan: {potions_to_make}")

    return potions_to_make

if __name__ == "__main__":
    print(get_bottle_plan())