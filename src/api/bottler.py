from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from .inventory import get_inventory
from src.api import auth
import sqlalchemy
from src import database as db

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
    """ """
    print("-----------------------/bottler/deliver/order_id-----------------------")
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    inv = get_inventory()

    amountOfGreenMl = inv["ml_in_barrels"]
    amountOfPotions = inv["number_of_potions"]

    for potion in potions_delivered:
        if potion.quantity > 0:
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {amountOfGreenMl - (potion.quantity * 100)}, num_green_potions = {amountOfPotions + potion.quantity}"))
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    print("-----------------------/bottler/plan-----------------------")
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    inv = get_inventory()

    if inv["ml_in_barrels"] > 100:
        numToMake = inv["ml_in_barrels"] // 100
        potionToSell = [{"potion_type": [0,100,0,0], "quantity": numToMake}]
        print(potionToSell)
        return potionToSell

    print([])
    return []

if __name__ == "__main__":
    print(get_bottle_plan())
