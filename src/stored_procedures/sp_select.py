import sqlalchemy
from src import database as db
from src.classes import Audit, LiquidInventory, PotionInventory, Purchases, ShoppingCart, StoreInfo, search_sort_options, search_sort_order

def get_customer_id(customer_name: str, customer_class: str, connection: sqlalchemy.Connection):
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text(
            f"SELECT id FROM customer WHERE name = :name AND class = :class"), {"name": customer_name, "class": customer_class})
        customerResult = result.mappings().first()

        if customerResult:
            return customerResult['id']

        return None

def get_liquid_id(liquid_type, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"SELECT id FROM liquid_stock WHERE potion_type = ARRAY{liquid_type}::int2[]"), {'potion_type': liquid_type})
    return result.mappings().first()['id']
    
def get_potion_id_by_type(potion_type, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"SELECT id FROM potion_stock WHERE potion_type = ARRAY{potion_type}::int2[]"), {'potion_type': potion_type})
    return result.mappings().first()['id']
    
def get_potion_id_by_sku(sku, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"SELECT id FROM potion_stock WHERE sku = :sku"), {'sku': sku})
    return result.mappings().first()['id']

def get_shopping_cart(cart_id: int, connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"SELECT * FROM cart_checkout WHERE cart_id = :cart_id"), {"cart_id": cart_id})
    return [ShoppingCart(**item) for item in result.mappings().all()]
        
def get_liquid_inventory(connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text(f"SELECT * FROM liquid_stock"))
    list = result.mappings().all()
    liquidInventory = [LiquidInventory(**item) for item in list]
    return liquidInventory

def get_potion_inventory(connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text("SELECT * FROM potion_stock"))
    list = result.mappings().all()
    potionInventory = [PotionInventory(**item) for item in list]
    return potionInventory
    
def get_audit(connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text("SELECT * FROM audit"))
    return Audit(**result.mappings().first()) 
    
def get_store_info(connection: sqlalchemy.Connection):
    result = connection.execute(sqlalchemy.text("SELECT * FROM store_data"))
    return StoreInfo(**result.mappings().first()) 

def get_search(potion_name: str, customer_name: str, search_page: int, sort_col: search_sort_options, sort_order: search_sort_order, connection: sqlalchemy.Connection):
    def sort(column):
        if sort_order is search_sort_order.asc:
            return sqlalchemy.asc(column)
        else:
            return sqlalchemy.desc(column)

    if sort_col is search_sort_options.timestamp:
        order_by = sort(db.purchases.c.time)
    elif sort_col is search_sort_options.customer_name:
        order_by = sort(db.purchases.c.customer)
    elif sort_col is search_sort_options.item_sku:
        order_by = sort(db.purchases.c.item)
    elif sort_col is search_sort_options.line_item_total:
        order_by = sort(db.purchases.c.cost)
    else:
        assert False 

    stmt = (
        sqlalchemy.select(
            db.purchases.c.time,
            db.purchases.c.customer,
            db.purchases.c.item,
            db.purchases.c.gold,
        )
        .limit(6)
        .offset(search_page)
        .order_by(order_by, db.purchases.c.time)
    )

    # filter only if name parameter is passed
    if potion_name != "":
        stmt = stmt.where(db.purchases.c.item.ilike(f"%{potion_name}%"))

    if customer_name != "":
        stmt = stmt.where(db.purchases.c.customer.ilike(f"%{customer_name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for i, row in enumerate(result):
            json.append(
                {
                    "line_item_id": i,
                    "customer_name": row.customer,
                    "item_sku": row.item,
                    "line_item_total": row.gold,
                    "timestamp": row.time
                }
            )

        return json