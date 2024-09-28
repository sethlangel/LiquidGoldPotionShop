from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth, inventory
import sqlalchemy
from src import database as db
from src.api.inventory import get_liquid_inventory, get_potion_inventory, get_gold_quantity

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
    """ """
    liquidInventory = get_liquid_inventory()
    currentGold = get_gold_quantity()
    print("-----------------------/barrels/deliver/order_id-----------------------")
    print(f"Barrels deliverd: {barrels_delivered} order_id: {order_id}")

    for barrel in barrels_delivered:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(f"UPDATE liquid_inventory SET quantity = {barrel.ml_per_barrel * barrel.quantity}, gold = {currentGold - (barrel.quantity * barrel.price)}"))
            print(result)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print("-----------------------/barrels/plan-----------------------")

    liquidInventory = get_liquid_inventory()
    potionInventory = get_potion_inventory()

    gold = get_gold_quantity()

    print(wholesale_catalog)

    purchaseBarrels = []

    for potion in potionInventory:
        for barrel in wholesale_catalog:
            if potion.name == "green_potion" and potion.quantity < 1:
                if barrel.sku == "SMALL_GREEN_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })
            if potion.name == "red_potion" and potion.quantity < 1:
                if barrel.sku == "SMALL_RED_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })
            if potion.name == "blue_potion" and potion.quantity < 1:
                if barrel.sku == "SMALL_BLUE_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })

    print(purchaseBarrels)
    return purchaseBarrels