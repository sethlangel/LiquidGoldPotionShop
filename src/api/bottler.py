from fastapi import APIRouter, Depends
from src.api import auth
from src.classes import PotionPlan
from src.functions import find_available_liquid, find_index_by_potion_type, convert_potion_to_liquid
from src.stored_procedures.sp_insert import insert_liquid_ledger_entry, insert_liquid_transaction, insert_potion_ledger_entry, insert_potion_transaction
from src.stored_procedures.sp_select import get_audit, get_liquid_inventory, get_potion_id_by_type, get_potion_inventory, get_store_info
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionPlan], order_id: int):
    try:
        with db.engine.begin() as connection:
            liquid_type_map = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
            liquid_used = [0,0,0,0]

            potion_transaction_id = insert_potion_transaction("Bottling", connection)
            liquid_transaction_id = insert_liquid_transaction("Bottling", connection)

            potion_ledger_list = []
            liquid_ledger_list = []

            for potion in potions_delivered:
                liquid_used = [liquid_used[i] + (potion.potion_type[i] * potion.quantity) for i in range(len(potion.potion_type))]
                print(f"/bottle/deliver | Potion Type: {potion.potion_type} | Potion Quantity: {potion.quantity}")
                print(potion_transaction_id)
                potion_id = get_potion_id_by_type(potion.potion_type, connection)
                potion_ledger_list.append((potion_transaction_id, potion_id, potion.quantity))
                

            for i, type in enumerate(liquid_type_map):
                print(f"/bottle/deliver | Liquid Used at Index: {-liquid_used[i]} | Type: {type}")
                liquid_id = i + 1 #Little weird but since I have liquid type ordered this works.
                liquid_ledger_list.append((liquid_transaction_id, liquid_id, -liquid_used[i]))
                
            insert_potion_ledger_entry(potion_ledger_list, connection)
            insert_liquid_ledger_entry(liquid_ledger_list, connection)

            print(f"/bottler/deliver/order_id | potions delievered: {potions_delivered} order_id: {order_id}")

            return "OK"
        
    except Exception as e:
        print(f"Error during bottle delivery: {e}")

@router.post("/plan")
def get_bottle_plan():
    #Need to find away to figure out what potions I am trying to bottle with new bool.
    try:
        with db.engine.begin() as connection: 
            potion_inventory = get_potion_inventory(connection) 
            liquid_inventory = get_liquid_inventory(connection)
            liquid_available = find_available_liquid(liquid_inventory)
            store_info = get_store_info(connection)

            potion_limit = store_info.potion_capacity * 50
            max_to_make = potion_limit // 6

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
                        num_to_make = potion_limit // 6 - total_potion_inventory

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
    except Exception as e:
        print(f"Error during bottling plan: {e}")


if __name__ == "__main__":
    print(get_bottle_plan())