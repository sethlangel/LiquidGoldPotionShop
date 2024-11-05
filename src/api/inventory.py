import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.stored_procedures.sp_select import get_audit, get_store_info
from src import database as db
from src.stored_procedures.sp_update import update_capacities

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def audit():
    with db.engine.begin() as connection:
        return get_audit(connection)

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        store_data = get_store_info(connection)

        if store_data.gold // 2 > 2000:
            return {
                "potion_capacity": 1,
                "ml_capacity": 1
            } 
        
        return {}

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

    with db.engine.begin() as connection:
        update_capacities(connection)

    return "OK"
