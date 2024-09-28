from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.dialects.mysql import pymysql
from .catalog import get_catalog
from src.api import auth
from enum import Enum
import uuid
import sqlalchemy
from src import database as db
from .inventory import get_liquid_inventory, get_potion_inventory, get_gold_quantity

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return {"success": True}


@router.post("/")
def create_cart(new_cart: Customer):
    print("-----------------------/carts/-----------------------")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("INSERT INTO shopping_cart DEFAULT VALUES RETURNING id"))
        rows = result.fetchall()
        cart_id = rows[0][0]
        print(f"cart_id: {cart_id}")
        return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    print("-----------------------/carts/cart_id/items/item_sku-----------------------")
    print(f"item_sku: {item_sku}, quantity: {cart_item}")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE shopping_cart SET item_sku = :item_sku, quantity = :quantity WHERE id = :cart_id"), {"item_sku": item_sku, "quantity": cart_item.quantity, "cart_id": cart_id})

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    print("-----------------------/carts/cart_id/checkout-----------------------")
    print(f"payment: {cart_checkout.payment}")
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM shopping_cart WHERE id = :cart_id"), {"cart_id": cart_id})
        dic = result.mappings().all()

        catalog = get_catalog()

        potionInventory = get_potion_inventory()
        gold = get_gold_quantity()

        totalPotions = 0

        for item in dic:
            totalPotions += int(item["quantity"])

        totalGold = catalog[0]["price"] * totalPotions

        newTotalGreenPots = inv["number_of_potions"] - totalPotions
        newTotalGold = inv["gold"] + totalGold

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :potions, gold = :gold"), {"potions": newTotalGreenPots, "gold": newTotalGold})

        checkoutResult = {"total_potions_bought": totalPotions, "total_gold_paid": totalGold}
        print(checkoutResult)
        return checkoutResult
