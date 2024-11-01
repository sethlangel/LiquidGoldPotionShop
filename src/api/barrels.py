from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth, inventory
from src.api.inventory import get_potion_inventory
from src.classes import Barrel
from src.functions import find_available_liquid
from src.stored_procedures.sp_insert import insert_gold_ledger_entry, insert_gold_transaction, insert_liquid_ledger_entry, insert_liquid_transaction
from src.stored_procedures.sp_select import get_liquid_id, get_liquid_inventory, get_store_info
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    try:
        with db.engine.begin() as connection: 
            gold_spent = 0

            liquid_transaction_id = insert_liquid_transaction("Barrel Delivery", connection)
            gold_transaction_id = insert_gold_transaction("Purchase of Barrels", None, connection)

            liquid_ledger_list = []

            for barrel in barrels_delivered:
                ml_quantity = (barrel.ml_per_barrel * barrel.quantity)
                gold_spent += (barrel.price * barrel.quantity)

                liquid_id = get_liquid_id(barrel.potion_type, connection)
                liquid_ledger_list.append((liquid_transaction_id, liquid_id, ml_quantity))
            
            insert_liquid_ledger_entry(liquid_ledger_list, connection)
            insert_gold_ledger_entry(gold_transaction_id, -gold_spent, connection)

            print(f"/barrels/deliver/order_id | Barrels deliverd: {barrels_delivered} order_id: {order_id}")

            return "OK"
    except Exception as e:
        print(f"Error during barrel delivery: {e}")

@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    try:
        with db.engine.begin() as connection: 
            store_info = get_store_info(connection)
            liquid_inventory = get_liquid_inventory(connection)
            potion_inventory = get_potion_inventory(connection)

            print(wholesale_catalog)

            updated_gold = store_info.gold

            liquid_limit = store_info.liquid_capacity * 10000
            liquid_needed = [((liquid_limit // 4) - liquid_inventory[i].quantity) for i in range(len(liquid_inventory))]

            total_liquid_in_potions = [sum(potion.potion_type[i] * potion.quantity for potion in potion_inventory if potion.quantity > 0) for i in range(4)]
            available_liquid_in_ml = find_available_liquid(liquid_inventory)
            grand_total_liquid = [total_liquid_in_potions[i] + available_liquid_in_ml[i] for i in range(len(liquid_inventory))]

            sorted_index = sorted(range(len(grand_total_liquid)), key=lambda i: grand_total_liquid[i])

            print(liquid_needed)
            print(sorted_index)

            sorted_barrels = sorted(
            wholesale_catalog,
            key=lambda barrel: (
                    -barrel.price / barrel.ml_per_barrel,
                    -barrel.potion_type[sorted_index[0]],
                    -barrel.potion_type[sorted_index[1]],
                    -barrel.potion_type[sorted_index[2]],
                    -barrel.potion_type[sorted_index[3]]
                )
            )
            print(sorted_barrels)
            purchase_barrels = []

            for i in range(len(liquid_needed)):
                needed = liquid_needed[i]
                
                if needed > 0:
                    for barrel in sorted_barrels:
                        if barrel.potion_type[i] > 0:
                            max_barrels_to_buy = min(needed // barrel.ml_per_barrel, barrel.quantity)

                            if max_barrels_to_buy > 0 and barrel.ml_per_barrel >= 500:
                                total_cost = barrel.price * max_barrels_to_buy

                                if total_cost > updated_gold:
                                    max_barrels_to_buy = updated_gold // barrel.price

                                if max_barrels_to_buy > 0:
                                    if barrel.ml_per_barrel == 500 and needed > 500:
                                        max_barrels_to_buy = 1

                                    updated_gold -= (barrel.price * max_barrels_to_buy)
                                    liquid_needed[i] -= (barrel.ml_per_barrel * max_barrels_to_buy)

                                    purchase_barrels.append({
                                        "sku": barrel.sku,
                                        "quantity": max_barrels_to_buy
                                    })


            print(f"/barrels/plan: {purchase_barrels}")
            return purchase_barrels
    except Exception as e:
        print(f"Error during barrel purchasing: {e}")
