from fastapi import APIRouter
from src.api.inventory import get_potion_inventory

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    potionInventory = get_potion_inventory()
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
