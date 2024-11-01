from fastapi import APIRouter
from src.api.inventory import get_potion_inventory
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    try:
        with db.engine.begin() as connection:
            potionInventory = get_potion_inventory(connection)
            sellableInventory = []

            for potion in potionInventory:
                if(potion.quantity > 0):
                    sellableInventory.append({
                        "sku": potion.sku,
                        "name": potion.name,
                        "quantity": potion.quantity,
                        "price": potion.price,
                        "potion_type": potion.potion_type,
                    })

            print(f"/catalog | {sellableInventory}")

            return sellableInventory
    except Exception as e:
        print(f"Error at catalog: {e}")