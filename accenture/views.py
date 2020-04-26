import sys

from django.contrib.auth.models import User, Group
from django.http import HttpResponse, Http404, JsonResponse

import mysql.connector
from mysql.connector import errorcode
from api.config import *
from pytz import unicode
from .services import *
import json


# Create your views here.
def index(request):
    return HttpResponse('<p>test</>', content_type='application/html')


def get_main_json(request):
    """
    API endpoint that allows groups to be viewed or edited.
    """
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

    sql = '''
    SELECT distinct(rt_steps.resource_group_id) as rg_id, 
    rt_steps.plant_id as pl_id, rs_gr.rg_name as rg_n, rs_gr.long_name as l_name FROM 
    06_routing_steps as rt_steps
    left join resource_groups as rs_gr on rt_steps.resource_group_id = rs_gr.resource_group_id 
    where rt_steps.plant_id != 0  AND rt_steps.plant_id != 50 
    AND rt_steps.resource_group_id in ('G_CMO2', 'G_ATO2', 'G_UNRO2', 'G_DSO2', 'G_VSO2', 'G_MFO2', 'G_VAO2', 'G_OTGRO2',
    'G_VTOT', 'G_OTGRT', 'G_AR3T', 'G_STG1T', 'G_AEIPT', 'G_TKT', 'G_ARG2T', 'G_UPAT', 'G_AR10T', 'G_ARG1T', 'G_AZPT', 'G_AR7T', 'G_ANOG2T',
    'G_MPG', 'G_APRRG', 'G_OTGRG', 'G_APORG', 'G_ST200G', 'G_UPAG', 'G_ANGC1H', 'G_KPH', 'G_STRS1H', 'G_ANGC3H', 'G_NTAH', 'G_UPAH', 'G_APPH', 'G_ANOH', 'G_APOR', 'G_APRR', 'G_OTGRH', 'G_DSH', 'G_ST203H',
    'G_ANOD', 'G_APHKRD', 'G_UPAD', 'G_APGKRD', 'G_APD', 'G_ANGCD', 'G_DSD', 'G_NORD', 'G_RSTD', 'G_OTGRD', 'G_APPD', 'G_NTAD', 'G_ST140D', 'G_AOAD') 
    group by rt_steps.resource_group_id, rt_steps.plant_id order by rt_steps.plant_id
    '''
    mycursor.execute(sql)

    groups_plants = dictfetchall(mycursor)

    mycursor.execute("SELECT * FROM plants WHERE plant_id != 6  order by plant_id")

    plants = dictfetchall(mycursor)
    # print(plants)

    # mycursor.execute("SELECT * FROM `04_operation-plan_order-order` order by id")
    # resources_dates = dictfetchall(mycursor)
    # print(plants)

    plants_data = []

    for plant in plants:
        resource_groups = []
        for groups_plant in groups_plants:
            groups_start_dates = []
            if groups_plant['pl_id'] == plant['plant_id']:

                sql = f"SELECT * FROM `04_operation-plan_order-order` where resource_group_id='{groups_plant['rg_id']}' order by id"
                # val = (groups_plant['rg_id'])
                try:

                    mycursor.execute(sql)
                    resources_dates = dictfetchall(mycursor)
                except Exception as e:
                    print(e)
                    print(sql)
                    # print(val)
                    sys.exit()

                for dt in resources_dates:
                    groups_start_dates.append({
                        'start_plan_date': dt['start_plan_date'].isoformat(),
                        # 'available_capacity': dt['available_capacity'],
                        # 'free_capacity': dt['free_capacity'],
                        # 'has_finite_capacity': dt['has_finite_capacity'],
                        'percentage': dt['load'],
                        'color': dt['load_color'],
                    })

                resource_groups.append({
                    'resourceGroupId': groups_plant['rg_id'],
                    'resourceGroupName': groups_plant['rg_n'],
                    'resourceGroupDescription': groups_plant['l_name'],
                    'dates': groups_start_dates,
                })

        plants_data.append({
            'plant_id': plant['plant_id'],
            'plant_name': plant['plant_name'],
            'plant_description': plant['plant_description'],
            'resourceGroups': resource_groups
        })

    db_conn.close()
    # with open("unicodeFile.json", "w", encoding='utf-8') as json_file:
    #     html_resp = json.dumps(plants_data, json_file, ensure_ascii=False)
    # print(html_resp)
    print(plants_data)
    return JsonResponse(plants_data, safe=False)


def get_rg_by_id_date(request, resource_group_id, rg_date):
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
    # rg_date = '2020-04-15'
    # rg_id = 'G_UPAH'
    rg_date = str(rg_date)
    rg_id = str(resource_group_id)
    sql = f"SELECT * FROM `04_operation-plan_order-order` WHERE date(start_plan_date) = '{rg_date}' and resource_group_id='{rg_id}'"
    val = (rg_date, rg_id)
    mycursor.execute(sql)

    resource_groups = dictfetchall(mycursor)
    print("SUCCESS")

    for resource_group in resource_groups:
        operations = []
        sql_operations = f'''
        SELECT * FROM 03_operation 
     WHERE (date(start_date_new) = '{rg_date}'  
     OR date(end_date) = '{rg_date}' ) AND resource_group_id = '{rg_id}' '''
        val = (rg_date, rg_date, rg_id)
        mycursor.execute(sql_operations)

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

            mycursor.execute(sql_get_order)

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
    return JsonResponse(rg_data, safe=False)


def get_order_by_id_json(request, order_id):
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

    # order_id = '40373189/2'
    order_id = str(order_id)
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
    return JsonResponse(order_data, safe=False)
