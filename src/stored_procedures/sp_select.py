import sqlalchemy
from src import database as db
from src.classes import Audit, LiquidInventory, PotionInventory, ShoppingCart, StoreInfo

def get_customer_id(customer_name: str, customer_class: str):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(
            f"SELECT id FROM customer WHERE name = '{customer_name}' AND class = '{customer_class}'"))
        customerResult = result.mappings().first()

        if customerResult:
            return customerResult['id']

        return None

def get_potion_id(sku: str):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(f"SELECT id FROM potion_inventory WHERE sku = '{sku}'"))
        return result.mappings().first()['id']

def get_shopping_cart(cart_id: int):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(f"""SELECT cart_id, 
                                              cart_items.quantity AS cart_item_quantity, 
                                              potion_inventory.id AS potion_id, 
                                              potion_inventory.potion_type AS potion_type, 
                                              potion_inventory.price AS potion_price, 
                                              potion_inventory.quantity AS potion_inventory_quantity 
                                              FROM cart 
                                              JOIN cart_items 
                                              ON cart.id = cart_items.cart_id JOIN potion_inventory 
                                              ON cart_items.potion_id = potion_inventory.id 
                                              WHERE cart.id = {cart_id}"""))
        return [ShoppingCart(**item) for item in result.mappings().all()]

def get_gold_quantity():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"SELECT gold FROM store_info"))
        list = result.mappings().all()
        return list[0]["gold"]


def get_liquid_inventory():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"SELECT * FROM liquid_inventory ORDER BY id ASC"))
        list = result.mappings().all()
        liquidInventory = [LiquidInventory(**item) for item in list]
        return liquidInventory

def get_potion_inventory():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory"))
        list = result.mappings().all()
        potionInventory = [PotionInventory(**item) for item in list]
        return potionInventory
    
def get_audit():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                                    SELECT(SELECT SUM(quantity) FROM potion_inventory) AS number_of_potions,
                                                    (SELECT SUM(quantity) FROM liquid_inventory) AS ml_in_barrels,
                                                    gold AS gold
                                                    FROM
                                                    store_info
                                                    LIMIT 1;
                                                    """))
        return Audit(**result.mappings().first()) 
    
def get_store_info():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT(SELECT SUM(quantity) FROM potion_inventory) AS number_of_potions,
                                                        (SELECT SUM(quantity) FROM liquid_inventory) AS ml_in_barrels,
                                                        gold AS gold, 
                                                        liquid_capacity,
                                                        potion_capacity
                                                        FROM
                                                        store_info
                                                        LIMIT
                                                        1;
                                                    """))
        return StoreInfo(**result.mappings().first()) 