from src.controller import BaseCRUD
from src.database import engine
from rich.console import Console
from rich.table import Table
from src.utils import add_row, cls_decorator, render_as_table, apply_discount, points_to_cash, display_data
from src.settings import NEWBIE_LOYALTY_POINTS, POINTS_CONVERSION_RATE
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import os
import time
from src.logger import logger

console = Console()

customer = BaseCRUD('customers')
orders = BaseCRUD('orders')
loyalty_program = BaseCRUD('loyalty_program')
menu_items = BaseCRUD('menu_items')
order_items = BaseCRUD('order_items')
discounts = BaseCRUD('discounts')
order_bills = BaseCRUD('order_bills')
order_discounts = BaseCRUD('order_discounts')
order_payments = BaseCRUD('order_payments')
feedbacks = BaseCRUD('feedbacks')
review_categories = BaseCRUD('review_categories')
complaints = BaseCRUD('complaints')
loyalty_points_logs = BaseCRUD('loyalty_points_logs')

def get_identifier():
    identifier = handle_user_choices("Search By ",[
        ('ID', 'customer_id'),
        ('Mobile Number', 'mobile_no'),
        ('Name (not recommended)', 'name')
    ])
    match identifier:
        case 'customer_id':
            value = int(input("Enter the value : "))
            return identifier, value
        case 'mobile_no':
            value = int(input("Enter the value : "))
            return identifier, value
        case 'name':
            value = str(input("Enter the name : "))
            return identifier, value
        case _:
            return None, None

def check_tier(points):
    loyalty_tiers = BaseCRUD('loyalty_tiers')
    with engine.begin() as conn:
        tier_data = loyalty_tiers.get_all(conn)

    for tier in tier_data:
        if points < tier['max_points']:
           return tier

    return tier_data[len(tier_data)-1]

def redirect_to_register():

    if yes_or_no(info_text='Do you want to register or Not..,'):
        return customer_register()
    else:
        return proceed_to()

def customer_login():

    with Session(engine) as session:

        identifier_col, identifier_value = get_identifier()
        if not identifier_col or not identifier_value:
            print(f"the identifiers issue {identifier_value, identifier_col}")
        customer_data = customer.get_one(session, **{identifier_col: identifier_value})

        if not customer_data:
            print("Customer doesn't exist")
            return redirect_to_register()

        return customer_data

def customer_register():
    try:
        with Session(engine) as register_session:
            data = add_row(customer.table.columns)

            customer_id = customer.add(register_session, **data)

            if not customer_id:
                register_session.rollback()  # Rollback changes if customer_id is invalid
                return None

            customer_data = customer.get_one(register_session, customer_id=customer_id)

            loyalty_id = loyalty_program.add(register_session, customer_id=customer_data['customer_id'], total_points=0,
                                             tier_id=1)

            add_points(register_session, loyalty_id, NEWBIE_LOYALTY_POINTS)

            register_session.commit()  # Commit the transaction

            return customer_data

    except SQLAlchemyError as e:
        register_session.rollback()  # Ensure rollback on error
        print(f"Database error: {e}")
        return None
    except Exception as e:
        register_session.rollback()
        print(f"Unexpected error: {e}")
        return None

def proceed_to():
    return None

def handle_user_choices(title, options):
    """Displays a menu and returns the selected function."""

    table = Table(title=title)
    table.add_column("Choice", justify="right", style="cyan", no_wrap=True)
    table.add_column("Action", style="magenta")

    # Extract option names for display
    for i, (option_name, _) in enumerate(options, start=1):
        table.add_row(str(i), option_name)

    console.print(table)

    # Ask for user input
    choice = console.input("[bold yellow]Enter your choice: [/bold yellow]")

    try:
        choice = int(choice)
        if 1 <= choice <= len(options):
            return options[choice - 1][1]  # Return the function, not execute
        else:
            console.print("[red]Invalid choice. Please select a valid option.[/red]")
            return None
    except ValueError:
        console.print("[red]Please enter a number.[/red]")
        return None

def yes_or_no(info_text):
    console.print(f'[yellow] {info_text} [/yellow]')
    print("Enter Y for Yes, N for No")
    while True:
        choice = str(input("(Y/N): "))
        if choice == 'Y' or choice == 'y':
            return True
        elif choice == 'N' or choice == 'n':
            return False
        else:
            print('Enter a valid choice, either "Y" or "N".')

def show_customers():
    with Session(engine) as session:
        render_as_table("Available Customers", customer.get_all(session))

def get_customer():

    show_customers()
    function = handle_user_choices("Customer Menu", [
        ("Customer Login", customer_login),
        ("Customer Register", customer_register),
        ("Proceed to Order", proceed_to)
    ])
    data = function()

    return data

def get_menu_list(session):
    stmt = text(
        '''
        SELECT * FROM menu_items as m
        INNER JOIN menu_categories as mc
        ON m.category_id = mc.category_id ORDER BY m.item_id;
        '''
    )
    result = session.execute(stmt).mappings().fetchall()

    return [dict(row) for row in result] if result else []

def create_order(session, customer_id=None):
    """Creates a new order, with or without a customer ID, using session handling and rollbacks."""

    if not yes_or_no(info_text='Do you want to order something?'):
        return None

    # Create order (customer_id can be None)
    order_id = orders.add(session, customer_id=customer_id)

    if not order_id:
        raise ValueError("Failed to create order.")

    # Retrieve order details
    order_data = orders.get_one(session, order_id=order_id)

    return order_data

def clean_up():
    with Session(engine) as session:
        feedbacks.delete_all(session)
        complaints.delete_all(session)
        order_payments.delete_all(session)
        order_items.delete_all(session)
        order_bills.delete_all(session)
        order_discounts.delete_all(session)
        orders.delete_all(session)
        customer.delete_all(session)

        session.commit()

def add_points(session, loyalty_id, no_of_points):

    # Fetch loyalty program data
    loyalty_data = loyalty_program.get_one(session, loyalty_id=loyalty_id)
    if not loyalty_data:
        logger.error(f"Loyalty ID {loyalty_id} not found")
        raise ValueError("Loyalty ID not found")  # Handle missing data

    new_total_points = loyalty_data['total_points'] + no_of_points

    # Get current tier based on new points
    current_tier = check_tier(new_total_points)

    # Update loyalty program
    loyalty_program.update(session, "loyalty_id", loyalty_id,
                           total_points=new_total_points,
                           tier_id=current_tier['tier_id']
                           )

    # Re-fetch updated data
    updated_loyalty_data = loyalty_program.get_one(session, loyalty_id=loyalty_id)

    return dict(updated_loyalty_data)

def add_items(session, order_id):
    menu = get_menu_list(session)
    while True:
        if not yes_or_no(info_text='Do you want to add items ? '):
            break
        render_as_table("Menu", menu)
        user_item_choice = int(input("Enter the item_id to add: "))
        quantity = int(input("How many items(Quantity): "))
        order_items.add(session,
                        order_id=order_id,
                        item_id=user_item_choice,
                        quantity=quantity)
    os.system('cls')
    return order_items.get_all(session, order_id=order_id)

def get_order_total_price(session, order_id):

    ordered_items = order_items.get_all(session, order_id=order_id)

    total_price = 0

    for ot in ordered_items:
        item = menu_items.get_one(session, item_id=ot['item_id'])
        unit_price = item['item_price']
        total_price += (ot['quantity']*unit_price)

    return float(total_price)

def get_loyalty_points(session, customer_id):
    current_loyalty_data = loyalty_program.get_one(session, customer_id=customer_id)
    cost_value = int(points_to_cash(current_loyalty_data['total_points'], POINTS_CONVERSION_RATE))
    current_loyalty_data['cost_value']=cost_value

    return current_loyalty_data

def handle_loyalty_points_claim(session, order_id):
    order = orders.get_one(session, order_id=order_id)
    if not yes_or_no(info_text='Do you want to use your loyalty points? '):
        return

    current_loyalty_data = get_loyalty_points(session, order['customer_id'])
    render_as_table("Loyalty Points Data", [current_loyalty_data])

    while True:
        try:
            points_to_claim = int(input("Enter number of points to claim: "))

            if points_to_claim > current_loyalty_data['total_points']:
                print(f"Insufficient points. You only have {current_loyalty_data['total_points']}.")
                if yes_or_no(info_text='Do you want to abort the claim? '):
                    return None  # Abort

            elif points_to_claim <= 50:
                print("You must claim more than 50 points.")
                if yes_or_no(info_text='Do you want to abort the claim? '):
                    return None  # Abort

            else:
                cost_value = int(points_to_cash(points_to_claim, POINTS_CONVERSION_RATE))
                if yes_or_no(info_text=f'The claim\'s cost value is {cost_value}. Do you confirm? '):
                    order_discounts.add(session,
                                        order_id=order['order_id'],
                                        loyalty_points_used=points_to_claim,
                                        discount_amount=cost_value
                                        )

                    # updating the total points after claiming.
                    new_total_points = int(current_loyalty_data['total_points'] - points_to_claim)
                    loyalty_program.update(session,
                                           'customer_id', current_loyalty_data['customer_id'],
                                           total_points=new_total_points)

                    # logging loyalty points claiming.
                    loyalty_points_logs.add(session,
                                            customer_id=current_loyalty_data['customer_id'],
                                            order_id=order_id,
                                            points_redeemed=points_to_claim)

                    print("loyalty points claim was successful.,")
                else:
                    print("Claim canceled. You can enter a new amount.")  # Allow re-entry

        except ValueError:
            print("Invalid input! Please enter a valid number.")

def handle_discounts(session, order_id, total_price):
    order = orders.get_one(session, order_id=order_id)
    os.system('cls')
    while True:
        if not yes_or_no(info_text='Do you want to apply discounts ? '):
            break

        # filtering discounts
        filtered_discounts = filter_discounts(total_price=total_price)
        render_as_table("Available discounts for the order", filtered_discounts)

        # selects discounts
        selected_discount_id = int(input("Enter the discount_id to add: "))
        selected_discount = next(
            (d for d in filtered_discounts if d['discount_id'] == selected_discount_id), None
        )
        if not selected_discount:
            print("Invalid discount ID. Please try again.")
            continue

        # applying discount
        final_price = int(apply_discount(
            total_price,
            float(selected_discount['discount_value']),
            selected_discount['type_name']
        ))

        discount_amount = float(total_price - final_price)

        order_discounts.add(session,
                            order_id=order_id,
                            discount_id=selected_discount['discount_id'],
                            discount_amount=discount_amount)

        # order_bills.update(session, 'order_id', order_id,
        #                    discount_applied=discount_amount,
        #                    final_price=final_price)

def calculate_cumulative_discount(discounts_data):
    render_as_table("Applied discounts", discounts_data)

    total_discount_amount = 0
    for discount in discounts_data:
        total_discount_amount += discount['discount_amount']

    return total_discount_amount

def filter_discounts(**filters):
    discounts = get_discounts()

    eligible_discounts = [discount for discount in discounts
                          if discount['min_order_value'] <= filters['total_price']]
    return eligible_discounts

def get_discounts():
    with Session(engine) as session:
        stmt = text(
            '''
            SELECT d.discount_id, d.discount_name, dt.type_name, d.discount_value, d.min_order_value
            FROM discounts as d
            INNER JOIN discount_types as dt
            ON d.type_id = dt.type_id 
            WHERE d.is_active = true;
            '''
        )
        result = session.execute(stmt).mappings().fetchall()

        discounts = [dict(row) for row in result] if result else []

    return discounts

def generate_bill(session, order_id):

    order = orders.get_one(session, order_id=order_id)
    # update the order_status upfront.
    orders.update(session,
                  'order_id', order_id,
                  order_status='completed')

    total_price = get_order_total_price(session, order_id)
    order_bills.add(session,
                    order_id=order_id,
                    total_price=total_price,
                    discount_applied=0.0,
                    final_price=total_price)

    if order['customer_id']:
        handle_loyalty_points_claim(session, order_id)
        handle_discounts(session, order_id, total_price)

        orders_discount_data = order_discounts.get_all(session, order_id=order_id)
        total_discount_applied = calculate_cumulative_discount(orders_discount_data)

        final_price=int(total_price-int(total_discount_applied))
        order_bills.update(session, 'order_id', order_id,
                           discount_applied=total_discount_applied,
                           final_price=final_price)
    return [order_bills.get_one(session, order_id=order_id)]

def initiate_payment(session, order_id):

    # Collect input payment data
    input_data = add_row(order_payments.table.columns, skip_columns=['order_id'])

    # Fetch order bill details
    order_bill = order_bills.get_one(session, order_id=order_id)

    amount_paid = int(input_data['amount_paid'])
    final_price = int(order_bill['final_price'])

    # Validate payment amount
    if amount_paid < 0:
        raise ValueError("Amount paid cannot be negative.")

    if amount_paid > final_price:
        raise ValueError(f"Overpayment not allowed! Maximum allowed: {final_price}, but received: {amount_paid}.")

    # Determine payment status
    payment_status = 'pending'
    if 0 < amount_paid < final_price:
        payment_status = 'partially_paid'
    elif amount_paid == final_price:
        payment_status = 'paid'

    # Update order bill payment status
    order_bills.update(session, 'order_id', order_id, payment_status=payment_status)

    # Add payment record
    order_payments.add(session, order_id=order_id, **input_data)

    return order_payments.get_all(session, order_id=order_id)

def get_feedback(session, customer_id=None, order_id=None, item_id=None):
    skip_columns = ['customer_id', 'order_id', 'item_id', 'category_id', 'created_at']
    # if not customer_id:
    #     skip_columns.append('customer_id')
    #
    # if not order_id:
    #     skip_columns.append('order_id')
    #
    # if not item_id:
    #     skip_columns.append('item_id')

    input_data = add_row(feedbacks.table.columns, skip_columns=skip_columns)

    render_as_table("Feedback Categories", review_categories.get_all(session))
    selected_category_id = int(input("Enter the category_id : "))

    input_data['category_id'] = selected_category_id
    input_data['customer_id']= customer_id
    input_data['order_id']=order_id
    input_data['item_id']= item_id

    feedbacks.add(session, **input_data)

def get_complaint(session, customer_id=None, order_id=None, item_id=None):
    skip_columns = ['customer_id', 'order_id', 'item_id', 'category_id', 'created_at']

    input_data = add_row(complaints.table.columns, skip_columns=skip_columns)

    render_as_table("Complaints Categories", review_categories.get_all(session))
    selected_category_id = int(input("Enter the category_id : "))

    input_data['category_id'] = selected_category_id
    input_data['customer_id']= customer_id
    input_data['order_id']=order_id
    input_data['item_id']= item_id

    complaints.add(session, **input_data)

def get_reward_points(purchase_amount, earn_rate):
    return int(purchase_amount*earn_rate)

def update_reward_points(session, order, customer):
    order_bill = order_bills.get_one(session, order_id=order['order_id'])
    total_price = int(order_bill['total_price'])
    logger.info(order_bill)
    if order_bill['payment_status'] == 'paid' and total_price > 10:
        points_earned = get_reward_points(total_price, POINTS_CONVERSION_RATE)
        logger.info(f"Customer {customer['customer_id']} earned {points_earned} points for order {order['order_id']}.")

        existing_log = loyalty_points_logs.get_one(session, order_id=order['order_id'])

        # updating the total points in the loyalty program table.
        loyalty_data = loyalty_program.get_one(session, customer_id=customer['customer_id'])
        new_total_points = int(loyalty_data['total_points']) + points_earned
        loyalty_program.update(session,
                               'customer_id', customer['customer_id'],
                               total_points=new_total_points)

        # logging the points transaction
        if existing_log:
            loyalty_points_logs.update(session, 'order_id', order['order_id'], points_earned=points_earned)
            logger.info(f"Updated reward points for order {order['order_id']} to {points_earned}.")
        else:

            loyalty_points_logs.add(session,
                                    customer_id=customer['customer_id'],
                                    order_id=order['order_id'],
                                    points_earned=points_earned)
            logger.info(f"Added new reward points log for order {order['order_id']}, customer {customer['customer_id']}.")

        return f"You have earned {points_earned} points at this transactions ."

    return ""

def get_complaints(session, customer, order):
    if yes_or_no(info_text="Do you want to have any complaint for this order ? "):
        get_complaint(session, customer_id=customer['customer_id'], order_id=order['order_id'])

    if yes_or_no(info_text="Do you want to have any personal complaint ? "):
        get_complaint(session, customer_id=customer['customer_id'])

    if yes_or_no(info_text="Do you want to leave a anonymous complaint ? "):
        get_complaint(session)

def get_feedbacks(session, customer, order):
    if yes_or_no(info_text="Do you want to leave a feedback for this order ? "):
        get_feedback(session, customer_id=customer['customer_id'], order_id=order['order_id'])

    if yes_or_no(info_text="Do you want to leave a personal feedback ? "):
        get_feedback(session, customer_id=customer['customer_id'])

    if yes_or_no(info_text="Do you want to leave a anonymous feedback ? "):
        get_feedback(session)

def start_transaction():

    # Main Session
    with Session(engine) as session:
        try:
            logger.info(f"Session Started sucessfully {session}")
            # Get Customer
            customer = get_customer()

            display_data(customer)

            # Create Order
            order = create_order(session, customer['customer_id'] if customer else None)

            display_data(customer, order)

            if not order:
                print("Transaction can't be continued without placing an order")
                raise Exception("Transaction Aborted")

            # add items to the order
            items = add_items(session, order['order_id'])



            display_data(customer, order, items)

            # prepare bill
            bill=generate_bill(session, order['order_id'])
            display_data(customer, order, items, bill)

            # do payment
            payment_details=initiate_payment(session, order['order_id'])
            display_data(customer, order, items, bill, payment_details)

            # now reward points for order
            reward=update_reward_points(session, order, customer)
            display_data(customer, order, items, bill, reward)

            get_feedbacks(session, customer, order)

            get_complaints(session, customer, order)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f'Error occured {e}')

while True:
    os.system("cls")
    if not yes_or_no(info_text="Do you want to continue"):
        break
    start_transaction()



