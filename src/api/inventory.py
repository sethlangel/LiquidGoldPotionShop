import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
from src.classes import LiquidInventory, PotionInventory

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

def get_gold_quantity():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM store_info"))
        list = result.mappings().all()
        return list[0]["gold"]


def get_liquid_inventory():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM liquid_inventory"))
        list = result.mappings().all()
        liquidInventory = [LiquidInventory(**item) for item in list]
        return liquidInventory

def get_potion_inventory():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        list = result.mappings().all()
        potionInventory = [PotionInventory(**item) for item in list]
        return potionInventory

#-------------------- API Endpoints --------------------

@router.get("/audit")
def get_audit_report():
    liquidInv = get_liquid_inventory()
    potionInv = get_potion_inventory()
    totalGold = get_gold_quantity()

    totalPotions = 0
    totalLiquid = 0

    for liquid in liquidInv:
        totalLiquid += liquid.quantity

    for potion in potionInv:
        totalPotions += potion.quantity

    return {"number_of_potions": totalPotions, "ml_in_barrels": totalLiquid, "gold": totalGold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 1,
        "ml_capacity": 1
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
