import mysql.connector
from mysql.connector import errorcode
import dateparser
from config import *
import csv



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

# mycursor.execute("SELECT * FROM 04_operation-plan_order-order")
#
# # myresult = mycursor.fetchall()
#
# columns = [col[0] for col in mycursor.description]
# rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]

with open('../csv/loading_data_table4_new.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            line_count += 1
            r0 = int(row[0])
            r1 = int(float(row[1]))
            r2 = int(float(row[2]))
            print(f'Row  {r0} ; {r1} ; {r2}')

            # print(date_converted)
            # print(x['latest_desired_delivery_date'])
            try:
                sql = "UPDATE `04_operation-plan_order-order` SET `load` = %s, `load_color` = %s WHERE id = %s"
                val = (r1, r2, r0)
                mycursor.execute(sql, val)
                db_conn.commit()
            except Exception as e:
                print(e)
                print(sql)
                break

    db_conn.close()

    print(f'Processed {line_count} lines.')


