from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth, inventory
from src.api.inventory import get_liquid_inventory, get_potion_inventory, get_gold_quantity
from src.classes import Barrel
from src.stored_procedures.sp_select import get_store_info
from src.stored_procedures.sp_update import update_liquid_inventory, update_gold

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    gold_spent = 0

    for barrel in barrels_delivered:
        ml_quantity = (barrel.ml_per_barrel * barrel.quantity)
        gold_spent += (barrel.price * barrel.quantity)

        print(f"/barrels/deliver/order_id | barrel quantity bought: {ml_quantity} for liquid type: {barrel.potion_type}, Gold spent: {barrel.price * barrel.quantity}")

        update_liquid_inventory(ml_quantity, barrel.potion_type)
        
    update_gold(-gold_spent)
    print(f"/barrels/deliver/order_id | Barrels deliverd: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    store_info = get_store_info()
    liquid_inventory = get_liquid_inventory()
    liquid_limit = store_info.liquid_capacity * 10000

    updated_gold = store_info.gold

    max_to_buy = liquid_limit // 4
    liquid_needed = [max_to_buy - liquid_inventory[i].quantity for i in range(len(liquid_inventory))]
    sorted_barrels = sorted(wholesale_catalog, key=lambda barrel: barrel.price / barrel.ml_per_barrel)

    purchase_barrels = []

    for i, needed in enumerate(liquid_needed):
        if needed <= 0:
            continue

        for barrel in sorted_barrels:
            if barrel.potion_type[i] == 1 and needed > 0 and barrel.ml_per_barrel >= 500:
                max_barrels_to_buy = min(needed // barrel.ml_per_barrel, barrel.quantity)
                
                if max_barrels_to_buy > 0:
                    total_cost = barrel.price * max_barrels_to_buy
                    
                    if total_cost > updated_gold:
                        max_barrels_to_buy = updated_gold // barrel.price

                    if max_barrels_to_buy > 0:
                        updated_gold -= (barrel.price * max_barrels_to_buy)
                        needed -= (barrel.ml_per_barrel * max_barrels_to_buy)

                        purchase_barrels.append({
                            "sku": barrel.sku,
                            "quantity": max_barrels_to_buy
                        })

                if needed <= 0:
                    break

    print(f"/barrels/plan: {purchase_barrels}")
    return purchase_barrels
