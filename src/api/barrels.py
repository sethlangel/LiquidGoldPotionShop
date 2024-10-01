from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth, inventory
from src.api.inventory import get_liquid_inventory, get_potion_inventory, get_gold_quantity
from src.stored_procedures.sp_update import update_liquid_inventory, update_gold

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
    liquidInventory = get_liquid_inventory()

    for barrel in barrels_delivered:
        index = -1
        for i, obj in enumerate(liquidInventory):
            if obj.potion_type == barrel.potion_type:
                index = i
                break

        newMlQuantity = (barrel.ml_per_barrel * barrel.quantity) + liquidInventory[index].quantity
        newGoldQuantity = get_gold_quantity() - (barrel.price * barrel.quantity)

        print(f"/barrels/deliver/order_id | New barrel quantity: {newMlQuantity} for liquid type: {barrel.potion_type}, Gold spent: {barrel.price * barrel.quantity}, New gold quantity: {newGoldQuantity}")

        update_liquid_inventory(newMlQuantity, barrel.potion_type)
        update_gold(newGoldQuantity)

    print(f"/barrels/deliver/order_id | Barrels deliverd: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    liquidInventory = get_liquid_inventory()
    potionInventory = get_potion_inventory()

    gold = get_gold_quantity()

    print(wholesale_catalog)

    purchaseBarrels = []

    for potion in potionInventory:
        for barrel in wholesale_catalog:
            if potion.sku == "green_potion" and potion.quantity < 10:
                if barrel.sku == "SMALL_GREEN_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })
            if potion.sku == "red_potion" and potion.quantity < 10:
                if barrel.sku == "SMALL_RED_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })
            if potion.sku == "blue_potion" and potion.quantity < 10:
                if barrel.sku == "SMALL_BLUE_BARREL" and gold > barrel.price:
                    purchaseBarrels.append({
                        "sku": barrel.sku,
                        "quantity": 1
                    })

    print(f"/barrels/plan: {purchaseBarrels}")
    return purchaseBarrels