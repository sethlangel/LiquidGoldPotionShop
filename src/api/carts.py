from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from .inventory import get_gold_quantity
from ..stored_procedures.sp_insert import insert_customer_visit, insert_new_customer, insert_new_cart, \
    insert_item_into_cart
from ..stored_procedures.sp_select import get_customer_id, get_potion_id, get_shopping_cart
from ..stored_procedures.sp_update import update_potion_inventory, update_gold

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
    for visitingCustomer in customers:
            customer_id = get_customer_id(visitingCustomer.customer_name, visitingCustomer.character_class)
            if customer_id:
                insert_customer_visit(customer_id, visit_id)
            else:
                new_customer_id = insert_new_customer(visitingCustomer.customer_name, visitingCustomer.character_class, visitingCustomer.level)
                insert_customer_visit(new_customer_id, visit_id)

    print(customers)

    return {"success": True}

@router.post("/")
def create_cart(new_cart: Customer):
    customer_id = get_customer_id(new_cart.customer_name, new_cart.character_class)
    cart_id = insert_new_cart(customer_id)

    print(f"/carts/ cart_id: {cart_id}")
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    potion_id = get_potion_id(item_sku)
    insert_item_into_cart(cart_id, potion_id, cart_item.quantity)

    print(f" /carts/cart_id/items/item_sku | item_sku: {item_sku}, quantity: {cart_item}")

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    cart =  get_shopping_cart(cart_id)

    total_potions = 0
    total_gold = 0

    for item in cart:
        total_potions += item.cart_item_quantity
        total_gold += item.cart_item_quantity * item.potion_price

        new_gold_from_potion = get_gold_quantity() + (item.cart_item_quantity * item.potion_price)

        new_potion_quantity = item.potion_inventory_quantity - item.cart_item_quantity

        print(f"/carts/{cart_id}/checkout | Old Potion Quantity: {item.potion_inventory_quantity} Total Bought: {item.cart_item_quantity} New Potion Quantity: {new_potion_quantity} for potion type: {item.potion_type}, Total Sale: {item.cart_item_quantity * item.potion_price} New Gold: {new_gold_from_potion}")
        update_potion_inventory(new_potion_quantity, item.potion_type)

    new_gold_quantity = get_gold_quantity() + total_gold
    update_gold(new_gold_quantity)

    checkout_result = {"total_potions_bought": total_potions, "total_gold_paid": total_gold}

    print(f"/carts/cart_id/checkout | {checkout_result}")
    print(f"/carts/cart_id/checkout | payment: {cart_checkout.payment}")

    return checkout_result
