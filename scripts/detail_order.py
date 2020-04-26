import mysql.connector
from mysql.connector import errorcode
import dateparser
from config import *
from pytz import unicode
from services import *
import json
import sys

try:

    db_conn = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME,
        port=DB_PORT,
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

mycursor = db_conn.cursor()

order_id = '40373189/2'
sql_get_order = f"SELECT * FROM 01_orders WHERE order_id='{order_id}'"
mycursor.execute(sql_get_order)

orders = dictfetchall(mycursor)
order_data = {}
for order in orders:

    plan_orders = []
    sql_get_plan_order = f"SELECT * FROM 02_plan_order WHERE downstream_customer_orders='{order_id}'"

    mycursor.execute(sql_get_plan_order)
    plan_orders_data = dictfetchall(mycursor)

    for plan_order in plan_orders_data:

        operations = []
        operation_id = str(plan_order['plan_order_id'])
        # query = "SELECT * FROM blah WHERE email LIKE %s limit 10"
        # cursor.execute(query, ("%" + p + "%",))
        sql_get_operations = f"SELECT * FROM 03_operation WHERE operation_id LIKE '{operation_id}%' "
        print(sql_get_operations)
        mycursor.execute(sql_get_operations)
        operations_data = mycursor.fetchall()
        print(operations_data)

        for operation in operations_data:
            operations.append({
                'operation_id': operation[1],
                'operation_description': operation[2],
                'sequence_nr': operation[3],
                'allow_standart_resources': operation[4],
                'start_date_new': operation[6].isoformat(),
                'end_date': operation[7].isoformat(),
                'production_time': operation[8],
                'input_quantity': operation[9],
                'scheduling_space': operation[10],
                'resource_group_id': operation[11],
                'operation_code': operation[12],
                'routing_step_id': operation[13],

            })

        plan_orders.append({
            'plan_order_id': plan_order['plan_order_id'],
            'order_position': plan_order['order_position'],
            'product_name': plan_order['product_name'],
            'vid_product': plan_order['vid_product'],
            'quantity': plan_order['quantity'],
            'stockin_point_id': plan_order['stockin_point_id'],
            'planned_status': plan_order['planned_status'],
            'start_order_process': plan_order['start_order_process'].isoformat(),
            'finish_order_process': plan_order['finish_order_process'].isoformat(),
            'last_process_date': plan_order['last_process_date'].isoformat(),
            'full_product_id': plan_order['full_product_id'],
            'routing_id': plan_order['routing_id'],
            'downstream_customer_orders': plan_order['downstream_customer_orders'],
            'operations': operations,

        })

    order_data = {
        'order_id': order['order_id'],
        'quantity': order['quantity'],
        'min_quantity': order['min_quantity'],
        'max_quantity': order['max_quantity'],
        'has_sales_budget_reservation': order['has_sales_budget_reservation'],
        'requires_order_combination': order['requires_order_combination'],
        'nr_of_active_routing_chain_upstream': order['nr_of_active_routing_chain_upstream'],
        'selected_shipping_shop': order['selected_shipping_shop'],
        'view_gp': order['view_gp'],
        'delivery_type': order['delivery_type'],
        'img_planned_status': order['img_planned_status'],
        'routing_id': order['routing_id'],
        'order_plant_name': order['order_plant_name'],
        'product_id': order['product_id'],
        'product_name': order['product_name'],
        'latest_desired_delivery_date_new': order['latest_desired_delivery_date_new'].isoformat(),
        'product_specification_id': order['product_specification_id'],
        'resource_group_id': order['resource_group_id'],
        'plan_orders': plan_orders
    }

db_conn.close()

with open("detail_order.json", "w", encoding='utf-8') as json_file:
    json.dump(order_data, json_file, ensure_ascii=False)
print("Done writing JSON serialized Unicode Data as-is into file")
