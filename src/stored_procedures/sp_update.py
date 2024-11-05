import sqlalchemy
from src import database as db

def update_cart_payment_method(cart_id: int, payment_method: str, connection: sqlalchemy.Connection):
    connection.execute(sqlalchemy.text(f"""UPDATE cart 
                                        SET payment_method = '{payment_method}' 
                                        WHERE id = {cart_id}"""))
    
def update_capacities(connection: sqlalchemy.Connection):
    connection.execute(sqlalchemy.text("""UPDATE store_info SET potion_capacity = potion_capacity + 1, liquid_capacity = liquid_capacity + 1"""))
