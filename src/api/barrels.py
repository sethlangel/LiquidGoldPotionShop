from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth, inventory
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)



class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    print("-----------------------/barrels/deliver/order_id-----------------------")
    print(f"Barrels deliverd: {barrels_delivered} order_id: {order_id}")
    inv = inventory.get_inventory()
    currentGold = inv["gold"]

    for barrel in barrels_delivered:
        if barrel.sku == "SMALL_GREEN_BARREL":
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {barrel.ml_per_barrel * barrel.quantity}, gold = {currentGold - (barrel.quantity * barrel.price)}"))
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print("-----------------------/barrels/plan-----------------------")

    inv = inventory.get_inventory()
    print(wholesale_catalog)

    barrels_to_buy = inv["gold"] // 100

    barrelPurchase = [
                    {
                        "sku": "SMALL_GREEN_BARREL",
                        "quantity": barrels_to_buy,
                    }
                ]

    for barrel in wholesale_catalog:
        if(barrel.sku == "SMALL_GREEN_BARREL"):
            if(inv["number_of_potions"] < 50 and barrels_to_buy > 0):
                print(barrelPurchase)
                return barrelPurchase
    print([])
    return []
