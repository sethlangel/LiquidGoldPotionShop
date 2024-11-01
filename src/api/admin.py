from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.stored_procedures.sp_insert import insert_gold_ledger_entry, insert_gold_transaction, insert_liquid_ledger_entry, insert_liquid_transaction, insert_potion_ledger_entry, insert_potion_transaction
from src.stored_procedures.sp_select import get_liquid_inventory, get_potion_inventory, get_store_info

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    
    with db.engine.begin() as connection:
        store_data = get_store_info(connection)
        potion_inventory = get_potion_inventory(connection)
        liquid_inventory = get_liquid_inventory(connection)

        print(store_data.gold)
        print(-store_data.gold + 100)

        gold_transaction_id = insert_gold_transaction("Reset", None, connection)
        potion_transaction_id = insert_potion_transaction("Reset", connection)
        liquid_transaction_id = insert_liquid_transaction("Reset", connection)

        potion_bulk_list = []
        liquid_bulk_list = []

        for potion in potion_inventory:
            potion_bulk_list.append((potion_transaction_id, potion.id, -potion.quantity))

        for liquid in liquid_inventory:
            liquid_bulk_list.append((liquid_transaction_id, liquid.id, -liquid.quantity))

        insert_gold_ledger_entry(gold_transaction_id, -store_data.gold + 100, connection)
        insert_potion_ledger_entry(potion_bulk_list, connection)
        insert_liquid_ledger_entry(liquid_bulk_list, connection)

    return "OK"

