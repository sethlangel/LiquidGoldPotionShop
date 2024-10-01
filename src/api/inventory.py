import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.stored_procedures.sp_select import get_liquid_inventory, get_potion_inventory, get_gold_quantity

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_audit_report():
    liquid_inv = get_liquid_inventory()
    potion_inv = get_potion_inventory()
    total_gold = get_gold_quantity()

    total_potions = 0
    total_liquid = 0

    for liquid in liquid_inv:
        total_liquid += liquid.quantity

    for potion in potion_inv:
        total_potions += potion.quantity

    return {"number_of_potions": total_potions, "ml_in_barrels": total_liquid, "gold": total_gold}

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
