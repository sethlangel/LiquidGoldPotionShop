import sqlalchemy
from src import database as db


def update_liquid_inventory(new_quantity: int, liquid_type: list[int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            f"UPDATE liquid_inventory SET quantity = quantity + {new_quantity} WHERE potion_type = ARRAY{liquid_type}::int2[]"))


def update_potion_inventory(new_quantity: int, potion_type: list[int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            f"UPDATE potion_inventory SET quantity = quantity + {new_quantity} WHERE potion_type = ARRAY{potion_type}::int2[]"))


def update_gold(new_quantity: int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE store_info SET gold = gold + {new_quantity}"))

def update_cart_payment_method(cart_id: int, payment_method: str):
    print(cart_id)
    print(payment_method)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"""UPDATE cart 
                                           SET payment_method = '{payment_method}' 
                                           WHERE id = {cart_id}"""))