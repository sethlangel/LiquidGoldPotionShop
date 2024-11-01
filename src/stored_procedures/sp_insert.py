from typing import List
import sqlalchemy
from src import database as db
from src.api.info import get_timestamp
from src.classes import Customer


def insert_customer_visit(customer_id: int, visit_id: int, connection: sqlalchemy.Connection):
        connection.execute(sqlalchemy.text(f"INSERT INTO customer_visit (customer_id, timestamp, visit_id) VALUES ({customer_id}, '{get_timestamp()}', {visit_id})"))

def insert_new_customer(customer_name: str, customer_class: str, customer_level: int, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"INSERT INTO customer (name, level, class) VALUES ('{customer_name}', {customer_level}, '{customer_class}') RETURNING id"))
    return result.mappings().first()['id']

def insert_new_cart(customer_id: int, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"INSERT INTO cart (customer_id) VALUES ({customer_id}) RETURNING id"))
    return result.mappings().first()['id']

def insert_item_into_cart(cart_id: int, potion_id: int, quantity: int, connection: sqlalchemy.Connection):
    connection.execute(sqlalchemy.text(f"INSERT INTO cart_items (cart_id, potion_id, quantity) VALUES ({cart_id}, {potion_id}, {quantity})"))

def log_customer_visit(customers: List[Customer], visit_id: int, connection: sqlalchemy.Connection):
    customers_tuples = [(customer.customer_name, customer.character_class, customer.level) for customer in customers]
    customers_string = ', '.join(f"('{customer_name}', '{customer_class}', {customer_level})" for customer_name, customer_class, customer_level in customers_tuples)

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

def insert_liquid_transaction(description: str, connection: sqlalchemy.Connection) -> int:
    value = connection.execute(sqlalchemy.text("INSERT INTO liquid_transactions (description) VALUES (:description) RETURNING id"), {"description": description})
    return value.mappings().first()["id"]

def insert_liquid_ledger_entry(bulk_list: list[tuple[int, int, int]], connection: sqlalchemy.Connection):
    bulk_str = ", ".join(f"({trans_id}, {id}, {change})" for trans_id, id, change in bulk_list)
    connection.execute(sqlalchemy.text(f"INSERT INTO liquid_ledger_entries (liquid_transactions_id, liquid_id, change) VALUES {bulk_str}"))

def insert_potion_transaction(description: str, connection: sqlalchemy.Connection) -> int:
    value = connection.execute(sqlalchemy.text("INSERT INTO potion_transactions (description) VALUES (:description) RETURNING id"), {"description": description})
    return value.mappings().first()["id"]

def insert_potion_ledger_entry(bulk_list: list[tuple[int, int, int]], connection: sqlalchemy.Connection):
    bulk_str = ", ".join(f"({trans_id}, {id}, {change})" for trans_id, id, change in bulk_list)
    connection.execute(sqlalchemy.text(f"INSERT INTO potion_ledger_entries (potion_transactions_id, potion_id, change) VALUES {bulk_str}"))

def insert_gold_transaction(description: str, cart_id: int | None, connection: sqlalchemy.Connection) -> int:
    value = connection.execute(sqlalchemy.text("INSERT INTO gold_transactions (description, cart_id) VALUES (:description, :cart_id) RETURNING id"), {"description": description, "cart_id": cart_id})
    return value.mappings().first()["id"]

def insert_gold_ledger_entry(transaction_id: int, change: int, connection: sqlalchemy.Connection):
    connection.execute(sqlalchemy.text("INSERT INTO gold_ledger_entries (gold_transaction_id, change) VALUES (:transaction_id, :change)"), {"transaction_id": transaction_id, "change": change})