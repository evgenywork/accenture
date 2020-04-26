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
rg_date = '2020-04-15'
rg_id = 'G_UPAH'
sql = "SELECT * FROM `04_operation-plan_order-order` WHERE date(start_plan_date) = %s and resource_group_id=%s"
val = (rg_date, rg_id)
mycursor.execute(sql, val)

resource_groups = dictfetchall(mycursor)

'''
SELECT * FROM accenture.03_operation
 WHERE (date(start_date_new) = '2020-04-15' 
 OR date(end_date) = '2020-04-15') AND resource_group_id='G_UPAH';'''

for resource_group in resource_groups:
    operations = []
    sql_operations = '''
    SELECT * FROM 03_operation 
 WHERE (date(start_date_new) = %s  
 OR date(end_date) = %s) AND resource_group_id = %s '''
    val = (rg_date, rg_date, rg_id)
    mycursor.execute(sql_operations, val)

    operations_dict = dictfetchall(mycursor)
    print(operations_dict)
    rg_data = {}
    for operation in operations_dict:
        val = (rg_date, rg_id)
        print("OPERATION ID")
        print(operation['operation_id'].split('.')[0])
        operation_id = operation['operation_id'].split('.')[0]

        sql_get_order = f'''SELECT * FROM 01_orders WHERE order_id = (SELECT downstream_customer_orders 
        FROM 02_plan_order WHERE plan_order_id = '{operation_id}')
        '''

        mycursor.execute(sql_get_order, operation_id)

        orders = dictfetchall(mycursor)
        order = orders[0]

        operations.append({
            'operation_id': operation['operation_id'],
            'operation_description': operation['operation_description'],
            'sequence_nr': operation['sequence_nr'],
            'allow_standart_resources': operation['allow_standart_resources'],
            'start_date_new': operation['start_date_new'].isoformat(),
            'end_date': operation['end_date'].isoformat(),
            'production_time': operation['production_time'],
            'input_quantity': operation['input_quantity'],
            'output_quantity': operation['output_quantity'],
            'scheduling_space': operation['scheduling_space'],
            'operation_code': operation['operation_code'],
            'routing_step_id': operation['routing_step_id'],
            'order_id': order['order_id'],
            'product_id': order['product_id'],
            'product_name': order['product_name'],


        })
    rg_data = {
        'resourceGroupId': resource_group['resource_group_id'],
        'start_plan_date': resource_group['start_plan_date'].isoformat(),
        'available_capacity': resource_group['available_capacity'],
        'free_capacity': resource_group['free_capacity'],
        'percentage': resource_group['load'],
        'color': resource_group['load_color'],
        'has_finite_capacity': resource_group['has_finite_capacity'],
        'operations': operations,
    }

print(resource_groups)

db_conn.close()

with open("order_detail.json", "w", encoding='utf-8') as json_file:
    json.dump(rg_data, json_file, ensure_ascii=False)
print("Done writing JSON serialized Unicode Data as-is into file")
