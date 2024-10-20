from typing import List
import sqlalchemy
from src import database as db
from src.api.info import get_timestamp
from src.classes import Customer


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

def log_customer_visit(customers: List[Customer], visit_id: int):
    customers_tuples = [(customer.customer_name, customer.character_class, customer.level) for customer in customers]
    customers_string = ', '.join(f"('{customer_name}', '{customer_class}', {customer_level})" for customer_name, customer_class, customer_level in customers_tuples)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"""WITH incoming_customers AS (
       SELECT *
       FROM (VALUES {customers_string} ) AS incoming_customers (NAME, class, level) ), new_customer AS (
            INSERT INTO customer (
                    NAME,
                    class,
                    level
                )
            SELECT NAME,
                   class,
                   level
            FROM incoming_customers
            WHERE NOT EXISTS (
                        SELECT 1
                        FROM customer
                        WHERE customer.NAME = incoming_customers.NAME) returning id 
                    )
            SELECT id
            FROM customer
            WHERE NAME IN (
                        SELECT NAME
                        FROM incoming_customers
                        )
            UNION ALL
            SELECT id
            FROM new_customer"""))
        
        customer_id_list = result.mappings().all()

        visit_data_tuples = [(customer["id"], get_timestamp(), visit_id) for customer in customer_id_list]
        visit_data_string = ", ".join(f"({customer_id}, '{timestamp}', {visit_id})" for customer_id, timestamp, visit_id in visit_data_tuples)
        
        connection.execute(sqlalchemy.text(f"INSERT INTO customer_visit (customer_id, timestamp, visit_id) VALUES {visit_data_string}"))
