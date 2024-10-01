import sqlalchemy
from src import database as db


def update_liquid_inventory(new_quantity: int, liquid_type: list[int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            f"UPDATE liquid_inventory SET quantity = {new_quantity} WHERE potion_type = ARRAY{liquid_type}::int2[]"))


def update_potion_inventory(new_quantity: int, potion_type: list[int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            f"UPDATE potion_inventory SET quantity = {new_quantity} WHERE potion_type = ARRAY{potion_type}::int2[]"))


def update_gold(new_quantity: int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE store_info SET gold = {new_quantity}"))