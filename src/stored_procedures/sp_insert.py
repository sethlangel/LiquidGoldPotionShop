import sqlalchemy
from src import database as db
from src.api.info import get_timestamp


def insert_customer_visit(customer_id: int, visit_id: int):
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.text(f"INSERT INTO customer_visit (customer_id, timestamp, visit_id) VALUES ({customer_id}, '{get_timestamp()}', {visit_id})"))

def insert_new_customer(customer_name: str, customer_class: str, customer_level: int):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(f"INSERT INTO customer (name, level, class) VALUES ('{customer_name}', {customer_level}, '{customer_class}') RETURNING id"))
        return result.mappings().first()['id']

def insert_new_cart(customer_id: int):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(f"INSERT INTO cart (customer_id) VALUES ({customer_id}) RETURNING id"))
        return result.mappings().first()['id']

def insert_item_into_cart(cart_id: int, potion_id: int, quantity: int):
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.text(f"INSERT INTO cart_items (cart_id, potion_id, quantity) VALUES ({cart_id}, {potion_id}, {quantity})"))