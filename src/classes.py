from pydantic import BaseModel

class PotionInventory(BaseModel):
    sku: str
    name: str
    potion_type: list[int]
    price: int
    quantity: int

class LiquidInventory(BaseModel):
    sku: str
    name: str
    potion_type: list[int]
    quantity: int