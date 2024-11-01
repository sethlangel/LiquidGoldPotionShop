import sqlalchemy
from src import database as db

def update_cart_payment_method(cart_id: int, payment_method: str, connection: sqlalchemy.Connection):
    connection.execute(sqlalchemy.text(f"""UPDATE cart 
                                        SET payment_method = '{payment_method}' 
                                        WHERE id = {cart_id}"""))
