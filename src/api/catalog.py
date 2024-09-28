from fastapi import APIRouter
import sqlalchemy
from src import database as db
from src.api.inventory import get_inventory

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    print("-----------------------/catalog-----------------------")

    inv = get_inventory()

    catalog = [
            {
                "sku": "GREEN_POTION_1",
                "name": "green potion",
                "quantity": inv["number_of_potions"],
                "price": 25,
                "potion_type": [0, 100, 0, 0],
            }
        ]

    print(catalog)

    return catalog
