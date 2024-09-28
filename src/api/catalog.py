from fastapi import APIRouter
import sqlalchemy
from src import database as db
from src.api.inventory import get_potion_inventory

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    potionInventory = get_potion_inventory()
    sellableInventory = []
    print("-----------------------/catalog-----------------------")

    for potion in potionInventory:
        if(potion.quantity > 0):
            sellableInventory.append({
                "sku": potion.sku,
                "name": potion.name,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": potion.potion_type,
            })

    print(sellableInventory)

    return sellableInventory
