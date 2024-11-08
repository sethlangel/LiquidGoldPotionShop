from enum import Enum
from pydantic import BaseModel

class PotionInventory(BaseModel):
    id: int
    sku: str
    name: str
    potion_type: list[int]
    price: int
    quantity: int

class LiquidInventory(BaseModel):
    id: int
    sku: str
    potion_type: list[int]
    quantity: int

class Purchases(BaseModel):
    customer: str
    item: str
    cost: int
    time: str

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"

class ShoppingCart(BaseModel):
    cart_item_quantity: int
    potion_id: int
    potion_type: list[int]
    potion_price: int
    potion_inventory_quantity: int

class Audit(BaseModel):
    number_of_potions: int
    ml_in_barrels: int
    gold: int

class StoreInfo(BaseModel):
    number_of_potions: int
    ml_in_barrels: int
    gold: int
    liquid_capacity: int
    potion_capacity: int

class PotionPlan(BaseModel):
    potion_type: list[int]
    quantity: int

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int